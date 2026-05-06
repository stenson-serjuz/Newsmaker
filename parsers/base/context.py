from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from typing import Optional, Mapping, Any


@dataclass(frozen=True)
class ParserConfig:
    timeout: float = 10.0
    max_items: int = 100


@dataclass(frozen=True)
class ParserContext:
    source_id: UUID
    url: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    metadata: Mapping[str, Any] | None = None
