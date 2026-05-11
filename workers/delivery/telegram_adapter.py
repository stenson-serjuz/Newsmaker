from __future__ import annotations

from aiogram import Bot


class TelegramAdapter:
    def __init__(
        self,
        bot: Bot,
    ) -> None:
        self._bot = bot

    async def send(
        self,
        target: str,
        text: str,
    ) -> None:
        await self._bot.send_message(
            chat_id=int(target),
            text=text,
            parse_mode="HTML",
        )
