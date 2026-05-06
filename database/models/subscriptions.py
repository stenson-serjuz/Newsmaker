from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, Index, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from database.models.base import Base, UUIDMixin
from database.models.enums import TariffEnum, SubscriptionStateEnum


class Subscription(Base, UUIDMixin):
    __tablename__ = "subscriptions"

    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    tariff: Mapped[TariffEnum] = mapped_column(SAEnum(TariffEnum), nullable=False)
    state: Mapped[SubscriptionStateEnum] = mapped_column(
        SAEnum(SubscriptionStateEnum),
        nullable=False,
        default=SubscriptionStateEnum.ACTIVE,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_subscriptions_chat_source", "chat_id", "source_id", unique=True),
    )
