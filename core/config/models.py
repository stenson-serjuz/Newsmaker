from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_env: Literal["dev", "staging", "prod"]
    app_name: str = Field(default="news-bot")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    db_dsn: str
    redis_url: str

    worker_concurrency: int = Field(gt=0, default=10)
