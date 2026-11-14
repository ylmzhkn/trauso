"""Runtime configuration. Secrets must be supplied through environment variables or a secret store."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8787
    workspace_root: str = "./workspace"
    database_url: str | None = None
    nats_url: str | None = None
    heartbeat_interval_seconds: int = Field(default=5, ge=1)
    heartbeat_timeout_seconds: int = Field(default=20, ge=2)
    default_task_timeout_seconds: int = Field(default=900, ge=1)
    max_retries: int = Field(default=2, ge=0)
    max_identical_actions: int = Field(default=3, ge=1)
    test_execution_enabled: bool = False


settings = Settings()
