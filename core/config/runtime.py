from core.config.models import AppConfig
from core.config.settings import load_settings


class RuntimeConfig:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    @property
    def app_env(self) -> str:
        return self._config.app_env

    @property
    def log_level(self) -> str:
        return self._config.log_level

    @property
    def db_dsn(self) -> str:
        return self._config.db_dsn

    @property
    def redis_url(self) -> str:
        return self._config.redis_url

    @property
    def worker_concurrency(self) -> int:
        return self._config.worker_concurrency


def build_runtime_config() -> RuntimeConfig:
    settings = load_settings()

    return RuntimeConfig(
        AppConfig(
            app_env=settings.app_env,
            app_name=settings.app_name,
            log_level=settings.log_level,
            db_dsn=settings.db_dsn,
            redis_url=settings.redis_url,
            worker_concurrency=settings.worker_concurrency,
        )
    )
