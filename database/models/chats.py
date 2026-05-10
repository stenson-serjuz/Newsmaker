from __future__ import annotations
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Boolean, Index

from database.models.base import Base, UUIDMixin, TimestampMixin


class Chat(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chats"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))

    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_chats_tenant_active", "tenant_id", "is_active"),
    )
