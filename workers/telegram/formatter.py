from __future__ import annotations

import html
import re


class TelegramFormatter:
    MAX_LENGTH = 3500

    def format_from_row(
        self,
        row: dict,
    ) -> str:
        title = self._clean(
            row.get(
                "enriched_title",
            )
            or row.get("title")
            or "Без заголовка"
        )

        summary = self._clean(
            row.get(
                "summary",
            )
            or row.get(
                "enriched_content",
            )
            or row.get("content")
            or ""
        )

        url = (
            row.get("url")
            or ""
        ).strip()

        category = (
            row.get("category")
            or "news"
        )

        city = (
            row.get("city")
            or ""
        )

        urgency = (
            row.get("urgency")
            or "normal"
        )

        text = (
            f"📰 <b>{title}</b>\n\n"
        )

        if city:
            text += (
                f"📍 {html.escape(city)}\n"
            )

        text += (
            f"🏷 #{html.escape(category)}"
        )

        if urgency in (
            "high",
            "breaking",
        ):
            text += (
                f"  🚨 #{html.escape(urgency)}"
            )

        text += "\n\n"

        if summary:
            text += (
                self._truncate(summary)
            )

        if url:
            safe_url = html.escape(url)

            text += (
                "\n\n"
                f"🔗 "
                f"<a href=\"{safe_url}\">"
                f"Источник"
                f"</a>"
            )

        return text.strip()

    def _clean(
        self,
        value: str,
    ) -> str:
        value = html.escape(value)

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = re.sub(
            r"http\S+",
            "",
            value,
        )

        return value.strip()

    def _truncate(
        self,
        text: str,
    ) -> str:
        if len(text) <= self.MAX_LENGTH:
            return text

        return (
            text[
                : self.MAX_LENGTH
            ].rsplit(
                " ",
                1,
            )[0]
            + "..."
        )
