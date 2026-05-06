from core.config.models import AppConfig
from core.config.settings import load_settings


class RuntimeConfig:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def get(self) -> AppConfig:
        return self._config


def build_runtime_config() -> RuntimeConfig:
    settings = load_settings()

    config = AppConfig(
        app_env=settings.app_env,
        app_name=settings.app_name,
        log_level=settings.log_level,
        db_dsn=settings.db_dsn,
        redis_url=settings.redis_url,
        worker_concurrency=settings.worker_concurrency,
    )

    return RuntimeConfig(config)
