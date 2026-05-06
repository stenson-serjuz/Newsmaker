from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Index

from database.models.base import Base, UUIDMixin


class Subscription(Base, UUIDMixin):
    __tablename__ = "subscriptions"

    chat_id: Mapped[int] = mapped_column(index=True)
    source_id: Mapped[int] = mapped_column(index=True)

    tariff: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_subscriptions_chat_source", "chat_id", "source_id", unique=True),
    )
