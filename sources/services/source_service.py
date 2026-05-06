from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sources.models.source import SourceModel
from sources.models.health import SourceHealth
from sources.validation.validator import SourceValidator
from sources.registry.resolver import ParserResolver
from sources.lifecycle.lifecycle import SourceLifecycle

from core.types.protocols import LoggerProtocol


class SourceRepository(Protocol):
    async def add(self, source: SourceModel) -> None: ...
    async def update(self, source: SourceModel) -> None: ...
    async def get(self, source_id: UUID) -> SourceModel | None: ...


class HealthRepository(Protocol):
    async def get(self, source_id: UUID) -> SourceHealth | None: ...
    async def save(self, source_id: UUID, health: SourceHealth) -> None: ...


class SourceService:
    """
    Source orchestration layer.

    - validation
    - lifecycle
    - parser binding
    """

    def __init__(
        self,
        repo: SourceRepository,
        health_repo: HealthRepository,
        validator: SourceValidator,
        resolver: ParserResolver,
        lifecycle: SourceLifecycle,
        logger: LoggerProtocol,
    ) -> None:
        self._repo = repo
        self._health = health_repo
        self._validator = validator
        self._resolver = resolver
        self._lifecycle = lifecycle
        self._logger = logger.bind(component="source_service")

    async def create(self, source: SourceModel) -> None:
        self._validator.validate_url(str(source.url))
        await self._validator.validate_duplicate(str(source.url), source.tenant_id)
        await self._validator.validate_parser(source.parser_key, source.type)

        await self._repo.add(source)

        self._logger.info("source_created", source_id=str(source.id))

    async def update(self, source: SourceModel) -> None:
        await self._repo.update(source)
        self._logger.info("source_updated", source_id=str(source.id))

    async def bind_parser(self, source_id: UUID):
        source = await self._repo.get(source_id)
        if not source:
            raise ValueError("source_not_found")

        parser = self._resolver.resolve(source.parser_key)

        return parser

    async def mark_success(self, source_id: UUID) -> None:
        health = await self._health.get(source_id) or SourceHealth(
            last_success_at=None,
            last_error_at=None,
        )

        updated = self._lifecycle.on_success(health)
        await self._health.save(source_id, updated)

    async def mark_failure(self, source_id: UUID) -> None:
        health = await self._health.get(source_id) or SourceHealth(
            last_success_at=None,
            last_error_at=None,
        )

        updated = self._lifecycle.on_failure(health)
        await self._health.save(source_id, updated)

        if self._lifecycle.should_disable(updated):
            source = await self._repo.get(source_id)
            if source:
                disabled = source.model_copy(update={"is_active": False})
                await self._repo.update(disabled)

                self._logger.warning(
                    "source_auto_disabled",
                    source_id=str(source_id),
                )
