from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "URL Shortener API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/urlshortener"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 3600  # 1 hour

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Short URL
    SHORT_CODE_LENGTH: int = 6
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
