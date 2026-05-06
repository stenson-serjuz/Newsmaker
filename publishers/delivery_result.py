from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict


class DeliveryStatus(str, Enum):
    SUCCESS = "success"
    RETRYABLE = "retryable"
    FATAL = "fatal"


class DeliveryResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: DeliveryStatus
    message_id: int | None = None
    error: str | None = None
