from __future__ import annotations

from bootstrap.container import Container
from bootstrap.startup import startup
from core.logging.logger import get_logger


logger = get_logger()


class Application:
    def __init__(self) -> None:
        logger.info("application_init_started")

        self.container = Container()

        logger.info("container_created")

    async def start(self) -> None:
        logger.info("application_start_enter")

        self.container.init_all()

        logger.info("container_init_all_completed")

        await startup(self.container)

        logger.info("bootstrap_startup_completed")

    async def run(self) -> None:
        logger.info("application_run_enter")

        bot = self.container.bot
        dispatcher = self.container.dispatcher

        logger.info("dispatcher_polling_starting")

        await dispatcher.start_polling(bot)

        logger.info("dispatcher_polling_finished")
