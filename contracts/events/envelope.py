from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any

from contracts.events.retry import RetryMetadata
from contracts.events.delivery import DeliveryMetadata


class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: int
    event_id: str

    trace_id: str | None = None

    payload: Dict[str, Any]

    metadata: Dict[str, Any] = Field(default_factory=dict)

    retry: RetryMetadata = Field(default_factory=RetryMetadata)
    delivery: DeliveryMetadata
