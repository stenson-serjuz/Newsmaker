from enum import Enum


class TariffEnum(str, Enum):
    NEWS = "news"
    CITY = "city"
    DIASPORA = "diaspora"


class SubscriptionStateEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class SourceTypeEnum(str, Enum):
    RSS = "RSS"
    CITY = "city"
    GOVERNMENT = "government"


class OutboxStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
