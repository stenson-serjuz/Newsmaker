from __future__ import annotations


class RoutingPolicy:
    def resolve_tariff(
        self,
        priority_score: int,
    ) -> str:
        if priority_score >= 80:
            return "premium"

        return "free"
