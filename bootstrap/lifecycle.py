from enum import Enum, auto

from bootstrap.container import Container


class LifecycleState(Enum):
    INITIAL = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


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

        self._container.init_config()
        self._container.init_logging()
        self._container.init_logger_factory()

        self._state = LifecycleState.RUNNING

    async def shutdown(self) -> None:
        if self._state is not LifecycleState.RUNNING:
            raise RuntimeError("Invalid lifecycle transition to shutdown")

        self._state = LifecycleState.STOPPING

        # future: close pools

        self._state = LifecycleState.STOPPED
