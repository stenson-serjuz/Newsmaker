from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Mapping

from contracts.events.retry import RetryMetadata
from contracts.events.delivery import DeliveryMetadata


class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: int
    event_id: str

    trace_id: str | None = None

    payload: Mapping[str, str | int | float | bool | None]

    metadata: Mapping[str, str | int | float | bool | None]

    retry: RetryMetadata
    delivery: DeliveryMetadata
