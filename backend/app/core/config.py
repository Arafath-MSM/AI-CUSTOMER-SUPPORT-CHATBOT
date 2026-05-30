from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Customer Support Chatbot"
    app_env: str = "development"
    api_prefix: str = "/api"
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    )
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    openai_max_output_tokens: int = 500
    openai_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @cached_property
    def has_openai_api_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


settings = Settings()
