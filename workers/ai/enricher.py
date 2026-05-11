from __future__ import annotations

import os

from openai import AsyncOpenAI


class AIEnricher:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=os.environ[
                "OPENAI_API_KEY"
            ],
        )

    async def enrich(
        self,
        *,
        title: str,
        content: str,
    ) -> dict:
        prompt = f"""
You are a professional news editor.

Tasks:
1. Rewrite headline professionally
2. Create concise summary
3. Detect language
4. Detect category

Return JSON:
{{
  "title": "...",
  "summary": "...",
  "language": "...",
  "category": "..."
}}

News title:
{title}

News content:
{content[:4000]}
"""

        response = await self._client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI news editor."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={
                "type": "json_object",
            },
            temperature=0.3,
        )

        result = response.choices[
            0
        ].message.content

        import json

        data = json.loads(result)

        return {
            "enriched_title": data["title"],
            "enriched_content": content,
            "summary": data["summary"],
            "language": data["language"],
            "category": data["category"],
        }
