import contextvars
from core.types.aliases import TraceId


_trace_id_ctx: contextvars.ContextVar[TraceId | None] = contextvars.ContextVar(
    "trace_id", default=None
)


def set_trace_id(trace_id: TraceId) -> None:
    _trace_id_ctx.set(trace_id)


def get_trace_id() -> TraceId | None:
    return _trace_id_ctx.get()
