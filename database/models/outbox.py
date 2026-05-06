from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Index

from database.models.base import Base, UUIDMixin


class Outbox(Base, UUIDMixin):
    __tablename__ = "outbox"

    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(50), index=True)

    __table_args__ = (
        Index("ix_outbox_status", "status"),
    )
