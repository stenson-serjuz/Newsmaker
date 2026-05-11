from __future__ import annotations

from contracts.events.envelope import EventEnvelope


class TelegramFormatter:
    def format(
        self,
        event: EventEnvelope,
    ) -> str:
        payload = event.payload

        title = payload["title"]
        content = payload["content"]
        url = payload["url"]

        return (
            f"<b>{title}</b>\n\n"
            f"{content[:1000]}\n\n"
            f"<a href='{url}'>Источник</a>"
        )

    def format_from_row(
        self,
        row: dict,
    ) -> str:
        return (
            f"<b>{row['title']}</b>\n\n"
            f"{row['content'][:1000]}\n\n"
            f"<a href='{row['url']}'>Источник</a>"
        )
