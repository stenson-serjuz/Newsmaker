from enum import Enum, auto

from bootstrap.container import Container


class LifecycleState(Enum):
    INITIAL = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


class LifecycleManager:
    def __init__(self, container: Container) -> None:
        self._container = container
        self._state = LifecycleState.INITIAL

    @property
    def state(self) -> LifecycleState:
        return self._state

    async def startup(self) -> None:
        if self._state is not LifecycleState.INITIAL:
            raise RuntimeError("Invalid lifecycle transition to startup")

        self._state = LifecycleState.STARTING

        try:
            self._container.init_config()
            self._container.init_logging()
            self._container.init_logger_factory()

            self._state = LifecycleState.RUNNING
        except Exception:
            self._state = LifecycleState.FAILED
            raise

    async def shutdown(self) -> None:
        if self._state not in (LifecycleState.RUNNING, LifecycleState.FAILED):
            raise RuntimeError("Invalid lifecycle transition to shutdown")

        self._state = LifecycleState.STOPPING

        # future: close pools safely

        self._state = LifecycleState.STOPPED
