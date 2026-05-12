from __future__ import annotations

import json
import os
import re

from openai import AsyncOpenAI


class AIEnricher:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=os.environ.get(
                "OPENAI_API_KEY",
                "",
            ),
        )

    async def enrich(
        self,
        *,
        title: str,
        content: str,
    ) -> dict:
        if not os.environ.get(
            "OPENAI_API_KEY",
        ):
            return self._fallback(
                title=title,
                content=content,
            )

        try:
            prompt = f"""
You are an AI news editor.

Return JSON:

{{
  "title": "...",
  "summary": "...",
  "language": "...",
  "category": "...",
  "urgency": "...",
  "city": "...",
  "priority_score": 0,
  "tags": ["..."]
}}

News title:
{title}

News content:
{content[:4000]}
"""

            response = await (
                self._client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    response_format={
                        "type": "json_object",
                    },
                )
            )

            raw = (
                response
                .choices[0]
                .message.content
            )

            data = json.loads(raw)

            return {
                "enriched_title": data.get(
                    "title",
                    title,
                ),
                "enriched_content": content,
                "summary": data.get(
                    "summary",
                    content[:500],
                ),
                "language": data.get(
                    "language",
                    "ru",
                ),
                "category": data.get(
                    "category",
                    "news",
                ),
                "urgency": data.get(
                    "urgency",
                    "normal",
                ),
                "city": data.get(
                    "city",
                ),
                "priority_score": data.get(
                    "priority_score",
                    50,
                ),
                "tags": data.get(
                    "tags",
                    [],
                ),
            }

        except Exception:
            return self._fallback(
                title=title,
                content=content,
            )

    def _fallback(
        self,
        *,
        title: str,
        content: str,
    ) -> dict:
        cleaned = self._clean(content)

        summary = cleaned[:500]

        return {
            "enriched_title": title,
            "enriched_content": cleaned,
            "summary": summary,
            "language": "ru",
            "category": "news",
            "urgency": "normal",
            "city": None,
            "priority_score": 30,
            "tags": [],
        }

    def _clean(
        self,
        text: str,
    ) -> str:
        text = re.sub(
            r"http\S+",
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()
