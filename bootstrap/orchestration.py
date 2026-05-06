from __future__ import annotations

import asyncio

from bootstrap.container import Container


class RuntimeOrchestrator:
    """
    Runtime orchestration:

    - bot polling
    - worker lifecycle supervision
    """

    def __init__(self, container: Container) -> None:
        self._c = container

    async def run(self) -> None:
        bot = self._c.bot
        dp = self._c.dispatcher

        # polling + workers run together
        await asyncio.gather(
            dp.start_polling(bot),
            self._monitor_workers(),
        )

    async def _monitor_workers(self) -> None:
        while True:
            for w in self._c.workers:
                if w.state.name == "FAILED":
                    raise RuntimeError(f"Worker failed: {w}")
            await asyncio.sleep(5)
