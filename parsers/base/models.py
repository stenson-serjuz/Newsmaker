from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RawItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    external_id: str
    title: str
    content: str
    url: str
    published_at: datetime | None = None
    media_url: str | None = None


class NormalizedItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    external_id: str
    title: str
    content: str
    url: str

    content_hash: str

    published_at: datetime | None
    fetched_at: datetime

    media_url: str | None = None
