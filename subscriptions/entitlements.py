from __future__ import annotations

from subscriptions.models import Tariff


class EntitlementPolicy:
    """
    Ownership:
    - pure domain policy
    - no IO
    """

    def can_access_source(
        self,
        tariff: Tariff,
        *,
        is_government: bool,
        has_city_scope: bool,
    ) -> bool:
        if tariff == Tariff.NEWS:
            return not is_government

        if tariff == Tariff.CITY:
            return has_city_scope

        if tariff == Tariff.DIASPORA:
            return True

        return False
