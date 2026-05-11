from __future__ import annotations

from aiogram import Bot


class TelegramSender:
    def __init__(
        self,
        bot: Bot,
    ) -> None:
        self._bot = bot

    async def send(
        self,
        chat_id: int,
        text: str,
    ) -> None:
        await self._bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
