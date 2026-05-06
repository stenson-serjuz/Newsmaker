import logging
import structlog
from structlog.typing import FilteringBoundLogger

from core.logging.context import get_trace_id


def add_trace_id(_, __, event_dict):
    trace_id = get_trace_id()
    if trace_id:
        event_dict["trace_id"] = trace_id
    return event_dict


def configure_logging(level: str) -> None:
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_trace_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger() -> FilteringBoundLogger:
    return structlog.get_logger()
