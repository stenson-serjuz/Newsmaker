from __future__ import annotations

import asyncio

from core.types.protocols import LoggerProtocol
from publishers.telegram_gateway import TelegramGateway
from publishers.rate_limiter import RateLimiter
from publishers.access_filter import AccessFilter
from publishers.delivery_result import DeliveryResult, DeliveryStatus


class Publisher:
    """
    Responsibilities:
    - enforce access
    - apply rate limiting
    - call gateway
    - classify result

    Does NOT:
    - implement retry orchestration
    """

    def __init__(
        self,
        gateway: TelegramGateway,
        limiter: RateLimiter,
        access_filter: AccessFilter,
        logger: LoggerProtocol,
    ) -> None:
        self._gateway = gateway
        self._limiter = limiter
        self._access = access_filter
        self._logger = logger.bind(component="publisher")

    async def publish_text(
        self,
        chat_id: int,
        text: str,
        *,
        thread_id: int | None = None,
        trace_id: str | None = None,
    ) -> DeliveryResult:
        log = self._logger.bind(chat_id=chat_id, trace_id=trace_id)

        if not await self._access.is_allowed(chat_id):
            log.warning("access_denied")
            return DeliveryResult(status=DeliveryStatus.FATAL, error="access_denied")

        await self._limiter.acquire(chat_id)

        try:
            result = await self._gateway.send_text(
                chat_id=chat_id,
                text=text,
                thread_id=thread_id,
            )
        except asyncio.CancelledError:
            raise

        log.info(
            "delivery_result",
            status=result.status,
            error=result.error,
        )

        return result
