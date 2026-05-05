from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app import database
from app.routes import api_router, web_router
from app.seed import seed_demo_data


def create_app(database_url: str | None = None, seed_demo: bool = True) -> FastAPI:
    if database_url:
        database.configure_database(database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database.init_db()
        if seed_demo and database.SessionLocal is not None:
            db = database.SessionLocal()
            try:
                seed_demo_data(db)
            finally:
                db.close()
        yield

    app = FastAPI(title=settings.app_name, description=settings.app_tagline, lifespan=lifespan)
    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(web_router)
    app.include_router(api_router)

    @app.get('/healthz', tags=['system'])
    def healthcheck() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()
