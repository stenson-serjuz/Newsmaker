from __future__ import annotations

from pydantic import BaseModel, ConfigDict, HttpUrl
from uuid import UUID
from typing import Optional

from database.models.enums import SourceTypeEnum


class SourceModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    tenant_id: UUID | None  # None = global (superuser-owned)

    name: str
    type: SourceTypeEnum
    url: HttpUrl

    parser_key: str

    is_active: bool = True
