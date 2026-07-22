from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ATA RAG"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    embedding_provider: str = "local"
    embedding_model: str = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )
    embedding_dimensions: int = 384

    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
