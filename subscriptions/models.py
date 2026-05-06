from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional


class Tariff(str, Enum):
    NEWS = "news"
    CITY = "city"
    DIASPORA = "diaspora"


class SubscriptionState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Subscription(BaseModel):
    model_config = ConfigDict(frozen=True)

    chat_id: int
    tenant_id: int

    tariff: Tariff
    state: SubscriptionState

    city: Optional[str] = None
    categories: tuple[str, ...] = ()
