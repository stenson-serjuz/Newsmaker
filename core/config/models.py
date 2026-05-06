from pydantic import BaseModel, Field
from typing import Literal


class AppConfig(BaseModel):
    app_env: Literal["dev", "staging", "prod"] = Field(...)
    app_name: str = Field(default="news-bot")

    log_level: str = Field(default="INFO")

    db_dsn: str = Field(...)
    redis_url: str = Field(...)

    worker_concurrency: int = Field(default=10)

    class Config:
        frozen = True
