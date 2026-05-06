from typing import TypeAlias, NewType
from uuid import UUID

TraceId: TypeAlias = str
EventId: TypeAlias = str
ChatId = NewType("ChatId", int)
SourceId = NewType("SourceId", int)

JsonDict: TypeAlias = dict[str, object]
