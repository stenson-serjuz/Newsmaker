from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Optional


class RetryMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    attempt: int = 0
    max_attempts: int = 5
    next_attempt_at: Optional[int] = None
    last_error: Optional[str] = None
