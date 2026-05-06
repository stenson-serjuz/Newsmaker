from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator, Optional

from redis.asyncio import Redis
from redis.exceptions import ResponseError

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
    ) -> None:
        self._redis = redis
        self._stream = stream
        self._group = group
        self._consumer = consumer_name
        self._logger = logger.bind(component="stream_consumer")

        self._idle_timeout = idle_timeout_ms
        self._running = False

    async def ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(
                self._stream,
                self._group,
                id="0",
                mkstream=True,
            )
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def consume(
        self,
        count: int = 10,
        block_ms: int = 5000,
    ) -> AsyncIterator[tuple[str, EventEnvelope]]:
        if not self._running:
            raise RuntimeError("Consumer not started")

        while self._running:
            try:
                messages = await self._redis.xreadgroup(
                    groupname=self._group,
                    consumername=self._consumer,
                    streams={self._stream: ">"},
                    count=count,
                    block=block_ms,
                )

                if not messages:
                    continue

                for _, entries in messages:
                    for msg_id, data in entries:
                        event = EventEnvelope.model_validate_json(data["data"])
                        yield msg_id, event

            except asyncio.CancelledError:
                self._logger.info("consumer_cancelled")
                raise

    async def ack(self, message_id: str) -> None:
        await self._redis.xack(self._stream, self._group, message_id)

    async def reclaim_pending(self, count: int = 10) -> None:
        """
        XPENDING + XCLAIM flow
        """
        pending = await self._redis.xpending_range(
            self._stream,
            self._group,
            min="-",
            max="+",
            count=count,
        )

        now = int(time.time() * 1000)

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
