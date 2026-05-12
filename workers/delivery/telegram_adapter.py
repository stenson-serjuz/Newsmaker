from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile


DEFAULT_IMAGE = (
    Path(__file__)
    .resolve()
    .parent.parent.parent
    / "assets"
    / "default_news.jpg"
)


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
        media_url: str | None = None,
    ) -> None:
        caption = text[:1024]

        if media_url:
            try:
                await self._bot.send_photo(
                    chat_id=int(target),
                    photo=media_url,
                    caption=caption,
                    parse_mode="HTML",
                )

                return

            except Exception:
                pass

        await self._bot.send_photo(
            chat_id=int(target),
            photo=FSInputFile(
                DEFAULT_IMAGE,
            ),
            caption=caption,
            parse_mode="HTML",
        )
