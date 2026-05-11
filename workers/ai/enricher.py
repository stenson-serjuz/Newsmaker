from __future__ import annotations


class AIEnricher:
    async def enrich(
        self,
        *,
        title: str,
        content: str,
    ) -> dict:
        summary = content[:500]

        return {
            "enriched_title": title,
            "enriched_content": content,
            "summary": summary,
            "language": "ru",
            "category": "news",
        }
