from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str
    app_name: str = "news-bot"

    log_level: str = "INFO"

    db_dsn: str
    redis_url: str

    worker_concurrency: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
    )


def load_settings() -> Settings:
    return Settings()
