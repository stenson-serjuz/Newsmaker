from __future__ import annotations

import asyncio

from bootstrap.container import Container


async def main():
    container = Container()
    container.init_all()

    workers = container.workers

    await asyncio.gather(*(w.start() for w in workers))


if __name__ == "__main__":
    asyncio.run(main())
