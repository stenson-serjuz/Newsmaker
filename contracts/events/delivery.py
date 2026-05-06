from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DeliveryMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    shard_id: int
    created_at: int
