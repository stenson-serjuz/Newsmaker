from __future__ import annotations

import asyncio
import os
import time
import uuid

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from aiogram import Bot

from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool

from workers.repositories.event_processing_repository import (
    EventProcessingRepository,
)

from workers.repositories.delivery_repository import (
    DeliveryRepository,
)

from workers.repositories.dead_letter_repository import (
    DeadLetterRepository,
)

from workers.repositories.delivery_target_repository import (
    DeliveryTargetRepository,
)

from workers.services.retry_policy import (
    RetryPolicy,
)

from workers.delivery.router import (
    DeliveryRouter,
)

from workers.delivery.telegram_adapter import (
    TelegramAdapter,
)

from workers.telegram.formatter import (
    TelegramFormatter,
)


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

    telegram = TelegramAdapter(bot)

    formatter = TelegramFormatter()

    events = EventProcessingRepository(pool)

    delivery = DeliveryRepository(pool)

    dead_letter = DeadLetterRepository(pool)

    target_repo = DeliveryTargetRepository(
        pool,
    )

    router = DeliveryRouter(
        target_repo,
    )

    policy = RetryPolicy()

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

        for row in reserved:
            started = time.monotonic()

            try:
                text = formatter.format_from_row(
                    row,
                )

                targets = await router.resolve(
                    category=row.get(
                        "category",
                    ),
                    language=row.get(
                        "language",
                    ),
                    tariff="free",
                )

                if not targets:
                    logger.warning(
                        "no_delivery_targets",
                        event_id=row["event_id"],
                    )

                    await events.mark_failed(
                        row["event_id"],
                    )

                    continue

                for target in targets:
                    if (
                        target["target_type"]
                        != "telegram"
                    ):
                        continue

                    await telegram.send(
                        target=target[
                            "target_key"
                        ],
                        text=text,
                        media_url=row.get(
                            "media_url",
                        ),
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
                    target_count=len(targets),
                )

            except Exception as e:
                retry_count = (
                    row["retry_count"] + 1
                )

                if policy.should_dead_letter(
                    retry_count,
                ):
                    await dead_letter.move_to_dead_letter(
                        event_id=row["event_id"],
                        payload=row,
                        error=str(e),
                    )

                    await events.mark_failed(
                        row["event_id"],
                    )

                    await delivery.mark_failed(
                        row["event_id"],
                        str(e),
                    )

                    logger.error(
                        "event_moved_to_dead_letter",
                        event_id=row["event_id"],
                        error=str(e),
                    )

                else:
                    delay = policy.next_delay(
                        retry_count,
                    )

                    next_retry_at = (
                        datetime.now(
                            timezone.utc,
                        )
                        + timedelta(
                            seconds=delay,
                        )
                    )

                    await events.mark_retry(
                        event_id=row["event_id"],
                        retry_count=retry_count,
                        next_retry_at=next_retry_at,
                        error=str(e),
                    )

                    await delivery.mark_failed(
                        row["event_id"],
                        str(e),
                    )

                    logger.warning(
                        "event_retry_scheduled",
                        event_id=row["event_id"],
                        retry_count=retry_count,
                        delay=delay,
                    )


if __name__ == "__main__":
    asyncio.run(main())
