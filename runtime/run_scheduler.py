from __future__ import annotations

import asyncio
import os

from redis.asyncio import Redis

from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool
from infrastructure.queue.producer import StreamProducer

from runtime.scheduler import Scheduler
from runtime.runtime_manager import RuntimeManager
from runtime.parser_runner import ParserRunner
from runtime.event_dispatcher import EventDispatcher

from runtime.providers.active_source_provider import (
    ActiveSourceProvider,
)

from runtime.dedup.publication_dedup_service import (
    PublicationDedupService,
)

from sources.services.source_service import SourceService

from sources.repositories.source_repository import (
    SourceRepositoryImpl,
)

from sources.repositories.health_repository import (
    HealthRepositoryImpl,
)

from sources.validation.validator import SourceValidator

from sources.lifecycle.lifecycle import SourceLifecycle

from sources.registry.resolver import ParserResolver

from bootstrap.parsers import (
    build_parser_registry,
    build_parser_compatibility,
)


logger = get_logger()


async def main() -> None:
    logger.info("scheduler_runtime_starting")

    # -------------------------------------------------------------------------
    # DATABASE
    # -------------------------------------------------------------------------

    pool = PostgresPool(
        dsn=os.environ["POSTGRES_DSN"],
        logger=logger,
    )

    await pool.start()

    # -------------------------------------------------------------------------
    # REDIS
    # -------------------------------------------------------------------------

    redis = Redis.from_url(
        os.environ["REDIS_URL"],
        encoding="utf-8",
        decode_responses=True,
    )

    producer = StreamProducer(redis)

    # -------------------------------------------------------------------------
    # PARSERS
    # -------------------------------------------------------------------------

    parser_registry = build_parser_registry()

    parser_compat = build_parser_compatibility()

    resolver = ParserResolver(parser_registry)

    # -------------------------------------------------------------------------
    # REPOSITORIES
    # -------------------------------------------------------------------------

    source_repo = SourceRepositoryImpl(pool)

    health_repo = HealthRepositoryImpl(pool)

    dedup = PublicationDedupService(pool)

    # -------------------------------------------------------------------------
    # DOMAIN SERVICES
    # -------------------------------------------------------------------------

    validator = SourceValidator(
        repo=source_repo,
        compatibility=parser_compat,
    )

    lifecycle = SourceLifecycle()

    source_service = SourceService(
        repo=source_repo,
        health_repo=health_repo,
        validator=validator,
        resolver=resolver,
        lifecycle=lifecycle,
        logger=logger,
    )

    # -------------------------------------------------------------------------
    # PROVIDERS
    # -------------------------------------------------------------------------

    provider = ActiveSourceProvider(
        source_repo=source_repo,
        health_repo=health_repo,
    )

    # -------------------------------------------------------------------------
    # DISPATCHER
    # -------------------------------------------------------------------------

    dispatcher = EventDispatcher(
        producer=producer,
        dedup=dedup,
        logger=logger,
    )

    # -------------------------------------------------------------------------
    # RUNNER
    # -------------------------------------------------------------------------

    runner = ParserRunner(
        source_service=source_service,
        dispatcher=dispatcher,
        logger=logger,
    )

    # -------------------------------------------------------------------------
    # SCHEDULER
    # -------------------------------------------------------------------------

    scheduler = Scheduler(
        provider=provider,
        runner=runner,
        interval=60.0,
        concurrency=5,
    )

    runtime = RuntimeManager(
        scheduler=scheduler,
        logger=logger,
    )

    # -------------------------------------------------------------------------
    # START
    # -------------------------------------------------------------------------

    await runtime.start()

    logger.info("scheduler_runtime_started")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
