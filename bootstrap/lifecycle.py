from bootstrap.container import Container


class LifecycleManager:
    def __init__(self, container: Container) -> None:
        self._container = container

    async def startup(self) -> None:
        self._container.init_config()
        self._container.init_logging()
        self._container.init_logger_factory()

    async def shutdown(self) -> None:
        # future: close pools
        pass
