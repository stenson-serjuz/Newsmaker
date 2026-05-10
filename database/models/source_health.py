from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from database.models.base import Base, TimestampMixin


class SourceHealthRecord(Base, TimestampMixin):
    __tablename__ = "source_health"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )

    last_success_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    is_degraded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
