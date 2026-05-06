from __future__ import annotations

import asyncio
from typing import Optional

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramForbiddenError,
    TelegramServerError,
)

from core.types.protocols import LoggerProtocol
from publishers.delivery_result import DeliveryResult, DeliveryStatus


MAX_TEXT_LENGTH = 4096


class TelegramGateway:
    """
    Production-safe Telegram gateway:

    - error taxonomy classification
    - floodwait propagation
    - timeout-safe
    - media-ready design
    """

    def __init__(
        self,
        bot: Bot,
        logger: LoggerProtocol,
        *,
        timeout: float = 10.0,
    ) -> None:
        self._bot = bot
        self._logger = logger.bind(component="telegram_gateway")
        self._timeout = timeout

    async def close(self) -> None:
        await self._bot.session.close()

    def _safe_text(self, text: str) -> str:
        return text[:MAX_TEXT_LENGTH]

    async def send_text(
        self,
        chat_id: int,
        text: str,
        *,
        thread_id: Optional[int] = None,
        parse_mode: ParseMode | None = ParseMode.HTML,
        trace_id: str | None = None,
    ) -> DeliveryResult:
        text = self._safe_text(text)

        try:
            async with asyncio.timeout(self._timeout):
                msg = await self._bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    message_thread_id=thread_id,
                    parse_mode=parse_mode,
                )

            return DeliveryResult(
                status=DeliveryStatus.SUCCESS,
                message_id=msg.message_id,
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except TelegramRetryAfter as e:
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error="floodwait",
                retry_after=e.retry_after,
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except TelegramNetworkError as e:
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error=str(e),
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except TelegramServerError as e:
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error=str(e),
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except TelegramForbiddenError as e:
            return DeliveryResult(
                status=DeliveryStatus.FATAL,
                error=str(e),
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except TelegramBadRequest as e:
            return DeliveryResult(
                status=DeliveryStatus.FATAL,
                error=str(e),
                trace_id=trace_id,
                chat_id=chat_id,
            )

        except asyncio.TimeoutError:
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error="timeout",
                trace_id=trace_id,
                chat_id=chat_id,
            )
