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
        title = (
            row["enriched_title"]
            or row["title"]
        )

        summary = (
            row["summary"]
            or row["content"][:1000]
        )

        category = (
            row["category"]
            or "news"
        )

        url = row["url"]

        return (
            f"#{category}\n\n"
            f"<b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"<a href='{url}'>Источник</a>"
        )
