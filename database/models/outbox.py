from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import JSONB

from database.models.base import Base, UUIDMixin
from database.models.enums import OutboxStatusEnum


class Outbox(Base, UUIDMixin):
    __tablename__ = "outbox"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    status: Mapped[OutboxStatusEnum] = mapped_column(
        SAEnum(OutboxStatusEnum),
        nullable=False,
        index=True,
    )

    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)

    next_attempt_at: Mapped[datetime | None]
    sent_at: Mapped[datetime | None]
    failed_at: Mapped[datetime | None]

    trace_id: Mapped[str | None]

    error: Mapped[str | None]

    schema_version: Mapped[int] = mapped_column(default=1, nullable=False)

    __table_args__ = (
        Index("ix_outbox_status_next", "status", "next_attempt_at"),
    )
