# Life Weave OS

Life Weave OS is a local-first personal life management system that blends the life analytics focus of Mulanbay with the unified personal data center idea of Personal Management System (PMS).

The implementation in this repository follows a clean, modular coding style:

- explicit domain registry for every life module
- unified storage model for cross-domain analytics
- separate config, database, service, route, and template layers
- Docker-first local deployment with sensible defaults

## Included modules

- Tasks
- Notes
- Contacts
- Expenses
- Subscriptions
- Workouts
- Meals
- Reading
- Health metrics
- Life events

## Core features

- unified dashboard across all life domains
- quick capture form and REST API
- life balance index derived from tracked habits
- module summaries with recent activity
- seeded demo data for first boot
- local SQLite persistence
- Docker and docker-compose deployment files

## Run locally with Python

```bash
python3 -m pip install --break-system-packages -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Test

```bash
pytest
```
