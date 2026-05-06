from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Boolean, Index

from database.models.base import Base, UUIDMixin, TimestampMixin


class Chat(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chats"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tenant_id: Mapped[int] = mapped_column(index=True)

    __table_args__ = (
        Index("ix_chats_tenant_active", "tenant_id", "is_active"),
    )
