from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Enum as SAEnum, Index

from database.models.base import Base, UUIDMixin
from database.models.enums import SourceTypeEnum


class Source(Base, UUIDMixin):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    type: Mapped[SourceTypeEnum] = mapped_column(
        SAEnum(SourceTypeEnum),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    parser: Mapped[str] = mapped_column(String(100), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_sources_type_active", "type", "is_active"),
    )
