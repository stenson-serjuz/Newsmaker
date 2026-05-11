from __future__ import annotations

import asyncio
import os

from redis.asyncio import Redis

from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool
from infrastructure.queue.consumer import StreamConsumer

from workers.repositories.news_event_repository import (
    NewsEventRepository,
)


logger = get_logger()


async def main() -> None:
    pool = PostgresPool(
        dsn=os.environ["POSTGRES_DSN"],
        logger=logger,
    )

    await pool.start()

    redis = Redis.from_url(
        os.environ["REDIS_URL"],
        encoding="utf-8",
        decode_responses=True,
    )

    consumer = StreamConsumer(
        redis=redis,
        stream="events_stream",
        group="persistence_group",
        consumer_name="persistence_worker",
    )

    await consumer.start()
    
    repo = NewsEventRepository(pool)

    logger.info("persistence_worker_started")

    async for message_id, event in consumer.consume():
        try:
            await repo.save(event)

            await consumer.ack(message_id)

            logger.info(
                "event_saved",
                message_id=message_id,
                event_id=event.event_id,
            )

        except Exception as e:
            logger.error(
                "event_save_failed",
                error=str(e),
                message_id=message_id,
            )

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
