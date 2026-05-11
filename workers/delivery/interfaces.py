from __future__ import annotations

from typing import Protocol


class DeliveryAdapter(Protocol):
    async def send(
        self,
        target: str,
        text: str,
    ) -> None:
        ...
