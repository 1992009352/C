from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / 'data'


@dataclass(frozen=True)
class Settings:
    app_name: str = 'Life Weave OS'
    app_tagline: str = 'Personal life operations system'
    data_dir: Path = Path(os.getenv('LIFE_OS_DATA_DIR', DEFAULT_DATA_DIR))
    database_url: str = os.getenv(
        'LIFE_OS_DATABASE_URL',
        f"sqlite:///{(Path(os.getenv('LIFE_OS_DATA_DIR', DEFAULT_DATA_DIR)) / 'life_os.db').resolve().as_posix()}",
    )
    page_size: int = int(os.getenv('LIFE_OS_PAGE_SIZE', '8'))

    def ensure_paths(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
