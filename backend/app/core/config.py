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

    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
