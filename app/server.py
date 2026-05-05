"""HTTP API and static web server for Superpower Life OS."""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.config import Settings, settings
from app.db import (
    connect,
    create_record,
    create_reminder,
    dashboard,
    delete_record,
    ensure_database,
    export_records,
    forecast,
    get_record,
    list_records,
    list_reminders,
    reveal_record_secret,
    set_reminder_done,
    update_record,
)
from app.models import MODULES, validate_record
from app.nlp import parse_quick_entry


STATIC_DIR = Path(__file__).parent / "static"


class LifeOSHandler(BaseHTTPRequestHandler):
    server_version = "SuperpowerLifeOS/0.1"

    def do_GET(self) -> None:  # noqa: N802
        route = urlparse(self.path)
        if route.path == "/api/health":
            self.send_json({"status": "ok", "app": settings.app_name})
            return
        if route.path == "/api/modules":
            self.send_json({"modules": MODULES})
            return
        if route.path == "/api/dashboard":
            with connect() as conn:
                self.send_json(dashboard(conn))
            return
        if route.path == "/api/records":
            params = parse_qs(route.query)
            with connect() as conn:
                self.send_json(
                    {
                        "records": list_records(
                            conn,
                            module=first(params, "module"),
                            status=first(params, "status"),
                            limit=int(first(params, "limit") or 100),
                        )
                    }
                )
            return
        if route.path.startswith("/api/records/"):
            record_id = parse_int(route.path.rsplit("/", 1)[-1])
            if record_id is None:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid record id.")
                return
            with connect() as conn:
                record = get_record(conn, record_id)
            if record:
                self.send_json({"record": record})
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Record not found.")
            return
        if route.path == "/api/reminders":
            with connect() as conn:
                self.send_json({"reminders": list_reminders(conn)})
            return
        if route.path == "/api/forecast":
            with connect() as conn:
                self.send_json(forecast(conn))
            return
        if route.path == "/api/export":
            with connect() as conn:
                self.send_json(export_records(conn))
            return
        self.serve_static(route.path)

    def do_POST(self) -> None:  # noqa: N802
        route = urlparse(self.path)
        payload = self.read_json()
        if payload is None:
            return
        if route.path == "/api/records":
            module = str(payload.get("module") or "").strip()
            validation = validate_record(module, payload)
            if not validation.is_valid:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "; ".join(validation.errors))
                return
            with connect() as conn:
                record = create_record(conn, module, payload)
            self.send_json({"record": record}, HTTPStatus.CREATED)
            return
        if route.path == "/api/quick-entry":
            text = str(payload.get("text") or "").strip()
            if not text:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Field 'text' is required.")
                return
            parsed = parse_quick_entry(text)
            validation = validate_record(parsed["module"], parsed)
            if not validation.is_valid:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "; ".join(validation.errors))
                return
            with connect() as conn:
                record = create_record(conn, parsed["module"], parsed)
            self.send_json({"record": record, "parsed": parsed}, HTTPStatus.CREATED)
            return
        if route.path == "/api/reminders":
            if not payload.get("title") or not payload.get("due_at"):
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Fields 'title' and 'due_at' are required.")
                return
            with connect() as conn:
                reminder = create_reminder(conn, payload)
            self.send_json({"reminder": reminder}, HTTPStatus.CREATED)
            return
        if route.path.startswith("/api/passwords/") and route.path.endswith("/reveal"):
            record_id = parse_int(route.path.split("/")[-2])
            if record_id is None:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid record id.")
                return
            with connect() as conn:
                secret = reveal_record_secret(conn, record_id)
            if secret is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Password record not found.")
            else:
                self.send_json({"secret": secret})
            return
        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found.")

    def do_PUT(self) -> None:  # noqa: N802
        route = urlparse(self.path)
        payload = self.read_json()
        if payload is None:
            return
        if route.path.startswith("/api/records/"):
            record_id = parse_int(route.path.rsplit("/", 1)[-1])
            module = str(payload.get("module") or "").strip()
            if record_id is None:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid record id.")
                return
            validation = validate_record(module, payload)
            if not validation.is_valid:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "; ".join(validation.errors))
                return
            with connect() as conn:
                record = update_record(conn, record_id, module, payload)
            if record:
                self.send_json({"record": record})
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Record not found.")
            return
        if route.path.startswith("/api/reminders/"):
            record_id = parse_int(route.path.rsplit("/", 1)[-1])
            if record_id is None:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid reminder id.")
                return
            with connect() as conn:
                ok = set_reminder_done(conn, record_id, bool(payload.get("is_done")))
            if ok:
                self.send_json({"ok": True})
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Reminder not found.")
            return
        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found.")

    def do_DELETE(self) -> None:  # noqa: N802
        route = urlparse(self.path)
        if route.path.startswith("/api/records/"):
            record_id = parse_int(route.path.rsplit("/", 1)[-1])
            if record_id is None:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid record id.")
                return
            with connect() as conn:
                ok = delete_record(conn, record_id)
            if ok:
                self.send_json({"ok": True})
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Record not found.")
            return
        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found.")

    def read_json(self) -> dict[str, object] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b"{}"
            data = json.loads(body.decode("utf-8") or "{}")
        except (ValueError, json.JSONDecodeError):
            self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body.")
            return None
        if not isinstance(data, dict):
            self.send_error_json(HTTPStatus.BAD_REQUEST, "JSON body must be an object.")
            return None
        return data

    def serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        target = (STATIC_DIR / relative).resolve()
        if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
            self.send_error_json(HTTPStatus.FORBIDDEN, "Forbidden path.")
            return
        if not target.exists() or not target.is_file():
            target = STATIC_DIR / "index.html"
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"error": message}, status)

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))


def first(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    return values[0] if values else None


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def run() -> None:
    ensure_database()
    httpd = ThreadingHTTPServer((settings.host, settings.port), LifeOSHandler)
    print(f"{settings.app_name} listening on http://{settings.host}:{settings.port}")
    httpd.serve_forever()


def create_handler(test_settings: Settings | None = None) -> type[LifeOSHandler]:
    """Return the handler class; kept small for tests that spin up a server."""

    _ = test_settings
    return LifeOSHandler


if __name__ == "__main__":
    run()
