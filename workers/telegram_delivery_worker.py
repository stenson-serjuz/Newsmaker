from __future__ import annotations

import asyncio
import os
import time
import uuid

from aiogram import Bot

from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool

from workers.repositories.event_processing_repository import (
    EventProcessingRepository,
)

from workers.repositories.subscription_repository import (
    SubscriptionRepository,
)

from workers.repositories.delivery_repository import (
    DeliveryRepository,
)

from workers.telegram.sender import TelegramSender
from workers.telegram.formatter import TelegramFormatter


logger = get_logger()


async def main() -> None:
    pool = PostgresPool(
        dsn=os.environ["POSTGRES_DSN"],
        logger=logger,
    )

    await pool.start()

    bot = Bot(
        token=os.environ["BOT_TOKEN"],
    )

    sender = TelegramSender(bot)

    formatter = TelegramFormatter()

    events = EventProcessingRepository(pool)

    subscriptions = SubscriptionRepository(pool)

    delivery = DeliveryRepository(pool)

    worker_id = str(uuid.uuid4())

    logger.info(
        "telegram_delivery_worker_started",
        worker_id=worker_id,
    )

    while True:
        reserved = await events.reserve_events(
            worker_id=worker_id,
            limit=10,
        )

        if not reserved:
            await asyncio.sleep(3)
            continue

        chat_ids = (
            await subscriptions.get_active_chat_ids()
        )

        for row in reserved:
            started = time.monotonic()

            try:
                text = formatter.format_from_row(row)

                for chat_id in chat_ids:
                    await sender.send(
                        chat_id=chat_id,
                        text=text,
                    )

                latency = int(
                    (
                        time.monotonic()
                        - started
                    ) * 1000
                )

                await events.mark_sent(
                    row["event_id"],
                )

                await delivery.mark_sent(
                    row["event_id"],
                    latency_ms=latency,
                )

                logger.info(
                    "telegram_delivery_success",
                    event_id=row["event_id"],
                )

            except Exception as e:
                await events.mark_failed(
                    row["event_id"],
                )

                await delivery.mark_failed(
                    row["event_id"],
                    str(e),
                )

                logger.error(
                    "telegram_delivery_failed",
                    event_id=row["event_id"],
                    error=str(e),
                )


if __name__ == "__main__":
    asyncio.run(main())
