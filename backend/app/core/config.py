from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "LifeHub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://lifehub:lifehub123@postgres:5432/lifehub"
    DATABASE_URL_SYNC: str = "postgresql://lifehub:lifehub123@postgres:5432/lifehub"

    REDIS_URL: str = "redis://redis:6379/0"

    SECRET_KEY: str = "lifehub-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost"]

    UPLOAD_DIR: str = "/app/uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
