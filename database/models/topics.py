from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Index

from database.models.base import Base, UUIDMixin


class Topic(Base, UUIDMixin):
    __tablename__ = "topics"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    telegram_thread_id: Mapped[int] = mapped_column(Integer)

    chat = relationship("Chat")

    __table_args__ = (
        Index("ix_topics_chat_thread", "chat_id", "telegram_thread_id", unique=True),
    )
