from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ATA RAG"
    app_env: str = "development"
    debug: bool = True

    database_url: str | None = None

    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    chat_model: str | None = None

    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
