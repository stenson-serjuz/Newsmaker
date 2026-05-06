from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class SourceHealth(BaseModel):
    model_config = ConfigDict(frozen=True)

    last_success_at: Optional[datetime]
    last_error_at: Optional[datetime]

    failure_count: int = 0

    is_degraded: bool = False
