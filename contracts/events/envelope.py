from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Dict, Any


class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: int
    event_id: str

    payload: Dict[str, Any]
    metadata: Dict[str, Any]
