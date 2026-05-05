"""Runtime configuration for Superpower Life OS."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings with safe local defaults."""

    app_name: str = "Superpower Life OS"
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    data_dir: Path = Path(os.getenv("DATA_DIR", "/app/data"))
    database_path: Path = Path(os.getenv("DATABASE_PATH", "/app/data/life_os.sqlite3"))
    timezone: str = os.getenv("TZ", "Asia/Shanghai")
    password_secret: str = os.getenv("PASSWORD_SECRET", "change-me-local-secret")


settings = Settings()
