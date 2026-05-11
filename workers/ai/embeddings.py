from __future__ import annotations

import os

from openai import AsyncOpenAI


class EmbeddingService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=os.environ[
                "OPENAI_API_KEY"
            ],
        )

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        response = await (
            self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000],
            )
        )

        return response.data[0].embedding
