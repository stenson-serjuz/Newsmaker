import asyncio

from bootstrap.container import Container
from bootstrap.lifecycle import LifecycleManager
from bootstrap.wiring import Wiring


async def main() -> None:
    container = Container()
    lifecycle = LifecycleManager(container)

    await lifecycle.startup()

    wiring = Wiring(container)
    logger = wiring.get_logger().bind(component="main")

    logger.info("application_started")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.warning("application_cancelled")
        raise
    finally:
        await lifecycle.shutdown()
        logger.info("application_stopped")


if __name__ == "__main__":
    asyncio.run(main())
