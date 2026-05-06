from __future__ import annotations

import asyncio

from bootstrap.container import Container
from runtime.runtime_manager import RuntimeManager


async def main():
    container = Container()
    container.init_all()

    runtime = RuntimeManager(
        scheduler=container.scheduler,
        logger=container.logger,
    )

    await runtime.start()

    try:
        await asyncio.Event().wait()
    finally:
        await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
