from __future__ import annotations

from dataclasses import dataclass


MAX_CALLBACK_LENGTH = 64


@dataclass(frozen=True)
class Callback:
    scope: str
    action: str
    entity: str | None = None
    value: str | None = None

    def pack(self) -> str:
        parts = [self.scope, self.action]

        if self.entity:
            parts.append(self.entity)

        if self.value:
            parts.append(self.value)

        data = ":".join(parts)

        if len(data) > MAX_CALLBACK_LENGTH:
            raise ValueError("callback too long")

        return data

    @staticmethod
    def parse(data: str) -> "Callback | None":
        parts = data.split(":")

        if len(parts) < 2:
            return None

        return Callback(
            scope=parts[0],
            action=parts[1],
            entity=parts[2] if len(parts) > 2 else None,
            value=parts[3] if len(parts) > 3 else None,
        )
