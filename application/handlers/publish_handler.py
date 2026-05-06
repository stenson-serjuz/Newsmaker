from __future__ import annotations

from typing import Any

from publishers.publisher import Publisher
from routing.router import Router


class PublishHandler:
    """
    Worker-side handler:
    event → routing → publish
    """

    def __init__(
        self,
        router: Router,
        publisher: Publisher,
        logger,
    ) -> None:
        self._router = router
        self._publisher = publisher
        self._logger = logger.bind(component="publish_handler")

    async def handle(self, event: dict[str, Any]) -> None:
        targets = await self._router.resolve(event)

        for target in targets:
            try:
                await self._publisher.publish(
                    chat_id=target.chat_id,
                    thread_id=target.thread_id,
                    text=self._format(event),
                )
            except Exception as e:
                self._logger.error(
                    "publish_failed",
                    error=str(e),
                    chat_id=target.chat_id,
                )

    def _format(self, event: dict[str, Any]) -> str:
        return f"<b>{event['external_id']}</b>\n\n{event['content'][:500]}"
