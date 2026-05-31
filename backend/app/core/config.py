from functools import cached_property
import secrets
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "AI Customer Support Chatbot"
    app_env: str = "development"
    api_prefix: str = "/api"
    admin_api_token: str = "dev-admin-token"
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    )
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_output_tokens: int = 500
    openai_timeout_seconds: float = 30.0
    rag_top_k: int = 4
    rag_chunk_size: int = 900
    rag_chunk_overlap: int = 150
    knowledge_store_path: Path = BACKEND_DIR / "storage" / "knowledge_base.json"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
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

    def verify_admin_token(self, token: str | None) -> bool:
        expected_token = self.admin_api_token.strip()
        provided_token = (token or "").strip()
        return bool(expected_token) and secrets.compare_digest(
            provided_token,
            expected_token,
        )


settings = Settings()
