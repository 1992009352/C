FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    DATA_DIR=/app/data \
    DATABASE_PATH=/app/data/life_os.sqlite3

WORKDIR /app

COPY app ./app

RUN mkdir -p /app/data \
    && useradd --create-home --shell /bin/bash lifeos \
    && chown -R lifeos:lifeos /app/data
USER lifeos

EXPOSE 8000

CMD ["python", "-m", "app.server"]
