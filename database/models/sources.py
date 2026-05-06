from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Index

from database.models.base import Base, UUIDMixin


class Source(Base, UUIDMixin):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50))

    url: Mapped[str] = mapped_column(String(500))
    parser: Mapped[str] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_sources_type_active", "type", "is_active"),
    )
