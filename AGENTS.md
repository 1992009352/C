# AGENTS.md

## Cursor Cloud specific instructions

### Overview

LifeHub is a personal life management system with a **FastAPI backend** (Python 3.12) and a **Vue 3 frontend** (Vite + Element Plus). The codebase lives on the `cursor/life-management-system-ee9a` branch (the `master` branch is empty).

### Required Infrastructure

- **PostgreSQL 16**: Primary database (`lifehub` / `lifehub` / `lifehub123` on port 5432)
- **Redis 7**: Cache on port 6379

Both can be started as Docker containers:
```
docker run -d --name lifehub-postgres -e POSTGRES_DB=lifehub -e POSTGRES_USER=lifehub -e POSTGRES_PASSWORD=lifehub123 -p 5432:5432 postgres:16-alpine
docker run -d --name lifehub-redis -p 6379:6379 redis:7-alpine
```

### Running Services

**Backend** (port 8000):
```
cd backend
DATABASE_URL="postgresql+asyncpg://lifehub:lifehub123@localhost:5432/lifehub" \
DATABASE_URL_SYNC="postgresql://lifehub:lifehub123@localhost:5432/lifehub" \
REDIS_URL="redis://localhost:6379/0" \
SECRET_KEY="lifehub-secret-key-change-in-production-2026" \
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (port 3000):
```
cd frontend
npm run dev
```

The Vite dev config proxies `/api` to `http://backend:8000`. For local dev without Docker Compose networking, add `127.0.0.1 backend` to `/etc/hosts`.

### Gotchas

- **bcrypt compatibility**: `passlib` (used for password hashing) is incompatible with `bcrypt>=4.1`. Pin `bcrypt==4.0.1` after installing `requirements.txt` to avoid `ValueError: password cannot be longer than 72 bytes`.
- **Tables auto-created**: SQLAlchemy `Base.metadata.create_all` runs in the FastAPI lifespan hook on startup — no manual migration step needed.
- **No lint/test config**: The repository does not include ESLint, Prettier, pytest config, or any CI pipeline. There are no automated tests to run.
- **API docs**: Available at `http://localhost:8000/docs` (Swagger UI) when the backend is running.
- **Frontend build**: `npm run build` in `frontend/` produces output in `frontend/dist/`.

### Standard Commands

See `README.md` for Docker Compose commands and `Makefile` for shortcuts (`make up`, `make down`, `make logs`, etc.).
