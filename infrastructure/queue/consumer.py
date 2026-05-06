from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

from contracts.events.envelope import EventEnvelope
from core.types.protocols import LoggerProtocol


class StreamConsumer:
    def __init__(
        self,
        redis: Redis,
        stream: str,
        group: str,
        consumer_name: str,
        logger: LoggerProtocol,
        *,
        idle_timeout_ms: int = 60000,
        block_ms: int = 2000,
    ) -> None:
        self._redis = redis
        self._stream = stream
        self._group = group
        self._consumer = consumer_name
        self._logger = logger.bind(component="stream_consumer")

        self._idle_timeout = idle_timeout_ms
        self._block_ms = block_ms

        self._running = False
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self._running = True
        self._stop_event.clear()

    async def stop(self) -> None:
        self._running = False
        self._stop_event.set()

    async def consume(self, count: int = 10) -> AsyncIterator[tuple[str, EventEnvelope]]:
        if not self._running:
            raise RuntimeError("Consumer not started")

        while self._running:
            try:
                messages = await self._redis.xreadgroup(
                    groupname=self._group,
                    consumername=self._consumer,
                    streams={self._stream: ">"},
                    count=count,
                    block=self._block_ms,
                )

                if not messages:
                    if self._stop_event.is_set():
                        break
                    continue

                for _, entries in messages:
                    for msg_id, data in entries:
                        try:
                            event = EventEnvelope.model_validate_json(data["data"])
                        except Exception as e:
                            self._logger.error(
                                "malformed_event",
                                error=str(e),
                                raw=data,
                            )
                            continue

                        yield msg_id, event

            except asyncio.CancelledError:
                self._logger.info("consumer_cancelled")
                raise

            except (ConnectionError, TimeoutError) as e:
                self._logger.warning(
                    "redis_transient_error",
                    error=str(e),
                )
                await asyncio.sleep(1)

    async def ack(self, message_id: str) -> None:
        await self._redis.xack(self._stream, self._group, message_id)

    async def reclaim_pending(self, count: int = 10) -> list[str]:
        """
        Reclaim abandoned messages and return message ids for reprocessing.
        """
        pending = await self._redis.xpending_range(
            self._stream,
            self._group,
            min="-",
            max="+",
            count=count,
        )

        reclaimed: list[str] = []

        for item in pending:
            msg_id = item["message_id"]
            idle = item["idle"]

            if idle >= self._idle_timeout:
                await self._redis.xclaim(
                    self._stream,
                    self._group,
                    self._consumer,
                    min_idle_time=self._idle_timeout,
                    message_ids=[msg_id],
                )
                reclaimed.append(msg_id)

        if reclaimed:
            self._logger.info(
                "messages_reclaimed",
                count=len(reclaimed),
            )

        return reclaimed
