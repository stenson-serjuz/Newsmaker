from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Index

from database.models.base import Base, UUIDMixin


class Publication(Base, UUIDMixin):
    __tablename__ = "publications"

    source_id: Mapped[int] = mapped_column(index=True)
    external_id: Mapped[str] = mapped_column(String(255))

    content_hash: Mapped[str] = mapped_column(String(64), index=True)

    __table_args__ = (
        Index("ix_publications_source_external", "source_id", "external_id", unique=True),
    )
