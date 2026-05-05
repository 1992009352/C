.PHONY: up down build restart logs backend-logs frontend-logs db-logs clean

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build --no-cache

restart:
	docker compose restart

logs:
	docker compose logs -f

backend-logs:
	docker compose logs -f backend

frontend-logs:
	docker compose logs -f frontend

db-logs:
	docker compose logs -f postgres

clean:
	docker compose down -v --rmi all
