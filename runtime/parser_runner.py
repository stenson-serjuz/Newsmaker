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

        source = await self._sources._repo.get(source_id)

        if not source:
            raise ValueError("source_not_found")

        parser = await self._sources.bind_parser(source_id)

        ctx = ParserContext(
            source_id=source.id,
            url=str(source.url),
        )

        try:
            items = await parser.parse(ctx)

            self._logger.info(
                "parser_items_parsed",
                source_id=str(source_id),
                count=len(items),
            )
            
            await self._dispatcher.dispatch(source.id, items)

            await self._sources.mark_success(source.id)

        except Exception as e:
            await self._sources.mark_failure(source.id)

            self._logger.error(
                "parser_failed",
                source_id=str(source.id),
                error=str(e),
            )

        finally:
            duration = time.monotonic() - start

            self._logger.info(
                "parser_completed",
                source_id=str(source.id),
                duration=duration,
            )
