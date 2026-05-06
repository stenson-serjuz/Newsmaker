from __future__ import annotations

import time
from uuid import UUID

from parsers.base.context import ParserContext
from sources.services.source_service import SourceService


class ParserRunner:
    """
    Executes parser + normalization pipeline.
    """

    def __init__(
        self,
        source_service: SourceService,
        dispatcher,
        logger,
    ) -> None:
        self._sources = source_service
        self._dispatcher = dispatcher
        self._logger = logger.bind(component="parser_runner")

    async def run(self, source_id: UUID) -> None:
        start = time.monotonic()

        parser = await self._sources.bind_parser(source_id)

        ctx = ParserContext(
            source_id=source_id,
            url="",  # resolved via source repo later
        )

        try:
            items = await parser.parse(ctx)

            await self._dispatcher.dispatch(source_id, items)

            await self._sources.mark_success(source_id)

        except Exception as e:
            await self._sources.mark_failure(source_id)

            self._logger.error(
                "parser_failed",
                source_id=str(source_id),
                error=str(e),
            )

        finally:
            duration = time.monotonic() - start
            self._logger.info(
                "parser_completed",
                source_id=str(source_id),
                duration=duration,
            )
