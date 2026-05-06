from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Optional


class Target(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    thread_id: Optional[int] = None
    tenant_id: int
