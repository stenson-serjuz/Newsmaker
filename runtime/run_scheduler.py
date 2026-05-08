# runtime/run_scheduler.py

from __future__ import annotations

import asyncio

from bootstrap.container import Container
from core.logging.logger import get_logger


logger = get_logger()


async def main() -> None:
    """
    Scheduler runtime is temporarily disabled.

    REAL ROOT CAUSE:
    ----------------
    runtime.scheduler.Scheduler requires:

        provider.list_active()
        runner.run(...)

    But the uploaded project currently contains no real
    provider wiring and no real runner wiring.

    The previous implementation attempted:

        scheduler = container.scheduler

    which is stale/outdated because Container cannot safely
    construct Scheduler from the current project structure.

    WHY THIS PATCH IS CORRECT:
    --------------------------
    - prevents Railway crash loop
    - preserves bot runtime
    - preserves postgres runtime
    - preserves redis runtime
    - preserves dispatcher runtime
    - preserves current DI/container architecture
    - avoids fake scheduler/provider/runner abstractions
    - avoids speculative architecture rewrites

    Scheduler subsystem can be restored later once the real
    provider and runner implementations are added.
    """

    logger.warning(
        "scheduler_runtime_disabled",
        reason=(
            "runtime.scheduler.Scheduler dependencies "
            "are incomplete in current project structure"
        ),
    )

    # Keep process alive without crashing Railway runtime.
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
