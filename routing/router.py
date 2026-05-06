from __future__ import annotations

from typing import Sequence

from routing.targets import Target
from routing.audience_resolver import AudienceResolver
from core.types.protocols import LoggerProtocol


class Router:
    """
    Routes events → targets.

    No Telegram logic here.
    """

    def __init__(
        self,
        resolver: AudienceResolver,
        logger: LoggerProtocol,
    ) -> None:
        self._resolver = resolver
        self._logger = logger.bind(component="router")

    async def route(
        self,
        *,
        source_id: int,
        city: str | None,
        is_government: bool,
        category: str | None,
    ) -> Sequence[Target]:
        targets = await self._resolver.resolve(
            source_id=source_id,
            city=city,
            is_government=is_government,
            category=category,
        )

        self._logger.info("routing_completed", targets=len(targets))

        return targets
