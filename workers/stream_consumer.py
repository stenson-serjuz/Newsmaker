from __future__ import annotations

import asyncio
import os

from redis.asyncio import Redis

from core.logging.logger import get_logger

from infrastructure.queue.consumer import (
    StreamConsumer,
)


logger = get_logger()


async def main() -> None:
    redis = Redis.from_url(
        os.environ["REDIS_URL"],
        encoding="utf-8",
        decode_responses=True,
    )

    consumer = StreamConsumer(
        redis=redis,
        stream="events_stream",
        group="telegram_group",
        consumer_name="worker-1",
    )

    await consumer.start()

    logger.info(
        "stream_consumer_started",
    )

    async for message_id, event in consumer.consume():
        logger.info(
            "event_received",
            message_id=message_id,
            event_id=event.event_id,
            payload=event.payload,
        )

        await consumer.ack(message_id)

        logger.info(
            "event_acked",
            message_id=message_id,
        )


if __name__ == "__main__":
    asyncio.run(main())
