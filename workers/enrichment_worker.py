from __future__ import annotations

import asyncio

from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool

from workers.repositories.enrichment_repository import (
    EnrichmentRepository,
)

from workers.ai.enricher import AIEnricher


logger = get_logger()


async def main() -> None:
    pool = PostgresPool(
        dsn="YOUR_DSN",
        logger=logger,
    )

    await pool.start()

    repo = EnrichmentRepository(pool)

    enricher = AIEnricher()

    logger.info(
        "enrichment_worker_started",
    )

    while True:
        rows = await repo.reserve_events()

        if not rows:
            await asyncio.sleep(3)
            continue

        for row in rows:
            try:
                result = await enricher.enrich(
                    title=row["title"],
                    content=row["content"],
                )

                await repo.complete(
                    row["event_id"],
                    enriched_title=result[
                        "enriched_title"
                    ],
                    enriched_content=result[
                        "enriched_content"
                    ],
                    summary=result["summary"],
                    language=result["language"],
                    category=result["category"],
                    urgency=result["urgency"],
                    city=result["city"],
                    priority_score=result[
                        "priority_score"
                    ],
                    tags=result["tags"],
                )

                logger.info(
                    "event_enriched",
                    event_id=row["event_id"],
                )

            except Exception:
                await repo.fail(
                    row["event_id"],
                )


if __name__ == "__main__":
    asyncio.run(main())
