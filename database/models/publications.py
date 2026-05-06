from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Index

from database.models.base import Base, UUIDMixin


class Publication(Base, UUIDMixin):
    __tablename__ = "publications"

    source_id: Mapped[str] = mapped_column(nullable=False, index=True)

    external_id: Mapped[str] = mapped_column(String(255), nullable=False)

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    delivery_state: Mapped[str] = mapped_column(String(50), nullable=False)

    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)

    __table_args__ = (
        Index("ix_pub_source_external", "source_id", "external_id", unique=True),
        Index("ix_pub_hash", "content_hash"),
    )
