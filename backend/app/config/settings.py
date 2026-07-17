from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "dev-secret"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./finai.db"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "/data/uploads"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-large"

    vector_store: str = "faiss"  # azure_search | faiss
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index: str = "financial-chunks"

    ocr_provider: str = "tesseract"  # azure_di | tesseract
    azure_di_endpoint: str = ""
    azure_di_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
