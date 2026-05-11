from __future__ import annotations


class DeliveryRouter:
    def route(
        self,
        category: str,
        language: str,
    ) -> list[str]:
        return [
            "telegram",
        ]
