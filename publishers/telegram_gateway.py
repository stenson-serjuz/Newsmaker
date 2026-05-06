from __future__ import annotations

import asyncio
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramNetworkError

from core.types.protocols import LoggerProtocol
from publishers.delivery_result import DeliveryResult, DeliveryStatus


class TelegramGateway:
    """
    Ownership:
    - wraps aiogram Bot
    - handles Telegram-specific errors
    - does NOT implement retry policy (only classification)
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

    async def send_text(
        self,
        chat_id: int,
        text: str,
        thread_id: Optional[int] = None,
    ) -> DeliveryResult:
        try:
            async with asyncio.timeout(self._timeout):
                msg = await self._bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    message_thread_id=thread_id,
                )

            return DeliveryResult(
                status=DeliveryStatus.SUCCESS,
                message_id=msg.message_id,
            )

        except TelegramRetryAfter as e:
            self._logger.warning("floodwait", retry_after=e.retry_after)
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error=f"floodwait:{e.retry_after}",
            )

        except TelegramNetworkError as e:
            return DeliveryResult(
                status=DeliveryStatus.RETRYABLE,
                error=str(e),
            )

        except TelegramBadRequest as e:
            return DeliveryResult(
                status=DeliveryStatus.FATAL,
                error=str(e),
            )
