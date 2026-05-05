from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

Base = declarative_base()
engine = None
SessionLocal = None


def configure_database(database_url: str | None = None) -> None:
    global engine, SessionLocal
    url = database_url or settings.database_url
    connect_args = {'check_same_thread': False} if url.startswith('sqlite') else {}
    engine = create_engine(url, connect_args=connect_args, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    from app import models  # noqa: F401

    settings.ensure_paths()
    if engine is None:
        configure_database()
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        configure_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


configure_database()
