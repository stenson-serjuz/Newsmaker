from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID

from database.models.base import Base, UUIDMixin


class Topic(Base, UUIDMixin):
    __tablename__ = "topics"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )

    telegram_thread_id: Mapped[int] = mapped_column(Integer, nullable=False)

    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    chat = relationship("Chat")

    __table_args__ = (
        Index("ix_topics_chat_thread", "chat_id", "telegram_thread_id", unique=True),
    )
