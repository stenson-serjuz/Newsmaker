import asyncio
import signal

from bootstrap.container import Container
from bootstrap.lifecycle import LifecycleManager
from bootstrap.wiring import Wiring


class ShutdownSignal:
    def __init__(self) -> None:
        self._event = asyncio.Event()

    def trigger(self) -> None:
        self._event.set()

    async def wait(self) -> None:
        await self._event.wait()


def _setup_signals(shutdown: ShutdownSignal) -> None:
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown.trigger)


async def main() -> None:
    container = Container()
    lifecycle = LifecycleManager(container)
    shutdown = ShutdownSignal()

    _setup_signals(shutdown)

    await lifecycle.startup()

    wiring = Wiring(container)
    logger = wiring.get_logger().bind(component="main")

    logger.info("application_started")

    try:
        await shutdown.wait()
    except asyncio.CancelledError:
        logger.warning("application_cancelled")
        raise
    finally:
        await lifecycle.shutdown()
        logger.info("application_stopped")


if __name__ == "__main__":
    asyncio.run(main())
