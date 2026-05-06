from __future__ import annotations

from datetime import datetime, timezone

from sources.models.health import SourceHealth


class SourceLifecycle:
    """
    Source health + lifecycle transitions.
    """

    FAILURE_THRESHOLD = 5

    def on_success(self, health: SourceHealth) -> SourceHealth:
        return SourceHealth(
            last_success_at=datetime.now(timezone.utc),
            last_error_at=health.last_error_at,
            failure_count=0,
            is_degraded=False,
        )

    def on_failure(self, health: SourceHealth) -> SourceHealth:
        failures = health.failure_count + 1

        return SourceHealth(
            last_success_at=health.last_success_at,
            last_error_at=datetime.now(timezone.utc),
            failure_count=failures,
            is_degraded=failures >= self.FAILURE_THRESHOLD,
        )

    def should_disable(self, health: SourceHealth) -> bool:
        return health.failure_count >= self.FAILURE_THRESHOLD
