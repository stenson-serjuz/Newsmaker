from __future__ import annotations

import asyncio

from bootstrap.application import Application


async def main() -> None:
    app = Application()

    await app.start()

    try:
        await app.run()
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
