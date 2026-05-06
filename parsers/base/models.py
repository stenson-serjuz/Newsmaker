from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional


class RawItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    external_id: str
    title: str
    content: str
    url: str

    published_at: Optional[datetime] = None
    media_url: Optional[str] = None


class NormalizedItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: UUID

    external_id: str
    title: str
    content: str
    url: str

    content_hash: str

    published_at: Optional[datetime]
    fetched_at: datetime

    media_url: Optional[str] = None

    def ensure_utc(self) -> "NormalizedItem":
        def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        return self.model_copy(
            update={
                "published_at": _to_utc(self.published_at),
                "fetched_at": _to_utc(self.fetched_at),
            }
        )
