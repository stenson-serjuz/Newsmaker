from __future__ import annotations

from bootstrap.container import Container
from core.logging.logger import get_logger


logger = get_logger()


async def startup(container: Container) -> None:
    logger.info("startup_enter")

    logger.info("postgres_starting")

    await container.postgres.start()

    logger.info("postgres_started")

    logger.info("redis_starting")

    await container.redis.start()

    logger.info("redis_started")

    logger.info("startup_completed")
