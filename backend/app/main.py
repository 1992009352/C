from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, finance, health, todo, note, habit, diet, reading, life_experience, contact, password, goal, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LifeHub - 全方位个人生活管理系统",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(finance.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(todo.router, prefix="/api")
app.include_router(note.router, prefix="/api")
app.include_router(habit.router, prefix="/api")
app.include_router(diet.router, prefix="/api")
app.include_router(reading.router, prefix="/api")
app.include_router(life_experience.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(password.router, prefix="/api")
app.include_router(goal.router, prefix="/api")


@app.get("/api/health-check")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
