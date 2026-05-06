from __future__ import annotations

import asyncio

from core.types.protocols import LoggerProtocol
from publishers.telegram_gateway import TelegramGateway
from publishers.rate_limiter import RateLimiter
from publishers.access_filter import AccessFilter
from publishers.delivery_result import DeliveryResult, DeliveryStatus


class Publisher:
    """
    Hardened publisher:

    - access control
    - rate limiting
    - delivery orchestration
    - structured observability
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
        attempt: int = 0,
    ) -> DeliveryResult:
        log = self._logger.bind(chat_id=chat_id, trace_id=trace_id, attempt=attempt)

        if not await self._access.is_allowed(chat_id):
            log.warning("access_denied")
            return DeliveryResult(
                status=DeliveryStatus.FATAL,
                error="access_denied",
                trace_id=trace_id,
                chat_id=chat_id,
                attempt=attempt,
            )

        delay = await self._limiter.acquire(chat_id)

        if delay > 0:
            log.debug("rate_limited", delay=delay)

        try:
            result = await self._gateway.send_text(
                chat_id=chat_id,
                text=text,
                thread_id=thread_id,
                trace_id=trace_id,
            )

        except asyncio.CancelledError:
            raise

        except Exception as e:
            log.error("unexpected_publish_error", error=str(e))
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error=str(e),
                trace_id=trace_id,
                chat_id=chat_id,
                attempt=attempt,
            )

        log.info(
            "delivery_result",
            status=result.status,
            error=result.error,
            retry_after=result.retry_after,
        )

        return result
