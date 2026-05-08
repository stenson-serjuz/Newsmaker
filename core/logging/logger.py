from __future__ import annotations

import logging
import sys

from typing import Any


class BoundLogger:
    def __init__(
        self,
        logger: logging.Logger,
        context: dict[str, Any] | None = None,
    ) -> None:
        self._logger = logger
        self._context = context or {}

    def bind(self, **kwargs: Any) -> "BoundLogger":
        merged = dict(self._context)
        merged.update(kwargs)

        return BoundLogger(
            logger=self._logger,
            context=merged,
        )

    def _format(self, event: str, **kwargs: Any) -> str:
        payload = dict(self._context)

        if kwargs:
            payload.update(kwargs)

        if not payload:
            return event

        return f"{event} | {payload}"

    def debug(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(self._format(event, **kwargs))

    def info(self, event: str, **kwargs: Any) -> None:
        self._logger.info(self._format(event, **kwargs))

    def warning(self, event: str, **kwargs: Any) -> None:
        self._logger.warning(self._format(event, **kwargs))

    def error(self, event: str, **kwargs: Any) -> None:
        self._logger.error(self._format(event, **kwargs))

    def exception(self, event: str, **kwargs: Any) -> None:
        self._logger.exception(self._format(event, **kwargs))


def get_logger() -> BoundLogger:
    logger = logging.getLogger("newsmaker")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

        logger.propagate = False

    return BoundLogger(logger)
