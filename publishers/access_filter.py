from __future__ import annotations

from core.types.protocols import LoggerProtocol


class AccessFilter:
    """
    Enforces:
    - tariff rules
    - chat entitlement

    NOTE:
    - actual logic injected later (DB layer)
    """

    def __init__(self, logger: LoggerProtocol) -> None:
        self._logger = logger.bind(component="access_filter")

    async def is_allowed(self, chat_id: int) -> bool:
        # placeholder (no business logic here)
        return True
