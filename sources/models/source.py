from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import HttpUrl

from database.models.enums import SourceTypeEnum


class SourceModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    id: UUID

    name: str
    type: SourceTypeEnum

    url: HttpUrl

    parser_key: str

    is_active: bool = True
    is_degraded: bool = False
