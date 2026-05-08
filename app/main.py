from __future__ import annotations

import asyncio

from bootstrap.application import Application
from core.logging.logger import get_logger


logger = get_logger()


async def main() -> None:
    logger.info("app_runtime_starting")

    app = Application()

    logger.info("application_created")

    await app.start()

    logger.info("application_start_completed")

    await app.run()

    logger.info("application_run_completed")


if __name__ == "__main__":
    asyncio.run(main())
