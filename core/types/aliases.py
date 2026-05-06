from typing import TypeAlias, NewType, Union, Mapping
from uuid import UUID

TraceId: TypeAlias = str
EventId: TypeAlias = str
ChatId = NewType("ChatId", int)
SourceId = NewType("SourceId", int)

JSONScalar: TypeAlias = Union[str, int, float, bool, None]
JSONType: TypeAlias = Union[
    JSONScalar,
    Mapping[str, "JSONType"],
    list["JSONType"],
]
