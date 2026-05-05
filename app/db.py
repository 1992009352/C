"""SQLite persistence layer for records, reminders, and local secrets."""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta
from typing import Any

from app.config import settings
from app.models import MODULES, SCORE_WEIGHTS, normalize_record_payload


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_iso() -> str:
    return date.today().isoformat()


def ensure_database() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                title TEXT NOT NULL,
                occurred_on TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                score REAL NOT NULL DEFAULT 0,
                tags TEXT NOT NULL DEFAULT '[]',
                details TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_records_module ON records(module);
            CREATE INDEX IF NOT EXISTS idx_records_occurred_on ON records(occurred_on);
            CREATE INDEX IF NOT EXISTS idx_records_status ON records(status);

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'local',
                due_at TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                is_done INTEGER NOT NULL DEFAULT 0,
                record_id INTEGER REFERENCES records(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        seed_demo_data(conn)


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def seed_demo_data(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS total FROM records").fetchone()["total"]
    if count:
        return

    samples = [
        ("expense", "午餐", {"amount": 38, "category": "餐饮", "merchant": "社区食堂"}, -2),
        ("exercise", "晨跑 5km", {"duration": 35, "distance": 5, "intensity": "medium"}, 9),
        ("reading", "读《原则》", {"book": "原则", "progress": 42, "unit": "pages"}, 7),
        ("health", "体重记录", {"metric": "weight", "value": 70.5, "unit": "kg"}, 5),
        ("diet", "高蛋白晚餐", {"calories": 620, "protein": 45, "carbs": 62}, 4),
        ("experience", "周末徒步", {"place": "西山", "mood": "energized"}, 8),
        ("todo", "整理五月目标", {"priority": "high"}, 4),
        ("note", "AI 行为分析想法", {"content": "把消费、运动和睡眠联动评分。"}, 3),
        (
            "contact",
            "家庭医生",
            {"name": "王医生", "phone": "13800000000", "relation": "health"},
            1,
        ),
        ("bill", "房租", {"amount": 3200, "due_date": today_iso(), "cycle": "monthly"}, -3),
    ]
    for offset, (module, title, details, score) in enumerate(samples):
        day = (date.today() - timedelta(days=offset)).isoformat()
        create_record(
            conn,
            module,
            {"title": title, "occurred_on": day, "details": details, "score": score},
        )


def list_records(
    conn: sqlite3.Connection,
    module: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM records"
    clauses: list[str] = []
    args: list[Any] = []
    if module:
        clauses.append("module = ?")
        args.append(module)
    if status:
        clauses.append("status = ?")
        args.append(status)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_on DESC, id DESC LIMIT ?"
    args.append(max(1, min(limit, 500)))
    return [row_to_record(row) for row in conn.execute(sql, args).fetchall()]


def search_records(conn: sqlite3.Connection, query: str, limit: int = 50) -> list[dict[str, Any]]:
    term = f"%{query.strip()}%"
    rows = conn.execute(
        """
        SELECT * FROM records
        WHERE title LIKE ? OR tags LIKE ? OR details LIKE ?
        ORDER BY occurred_on DESC, id DESC
        LIMIT ?
        """,
        (term, term, term, max(1, min(limit, 100))),
    ).fetchall()
    return [row_to_record(row) for row in rows]


def get_record(conn: sqlite3.Connection, record_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
    return row_to_record(row) if row else None


def create_record(conn: sqlite3.Connection, module: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_record_payload(module, payload)
    if module == "password" and normalized["details"].get("secret"):
        normalized["details"]["secret"] = protect_secret(str(normalized["details"]["secret"]))
    occurred_on = normalized["occurred_on"] or today_iso()
    score = normalized["score"]
    if score in (None, ""):
        score = calculate_score(module, normalized["details"])

    now = utc_now()
    cur = conn.execute(
        """
        INSERT INTO records
            (module, title, occurred_on, status, score, tags, details, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            module,
            normalized["title"],
            occurred_on,
            normalized["status"],
            float(score),
            json.dumps(normalized["tags"], ensure_ascii=False),
            json.dumps(normalized["details"], ensure_ascii=False),
            now,
            now,
        ),
    )
    return get_record(conn, cur.lastrowid) or {}


def update_record(
    conn: sqlite3.Connection, record_id: int, module: str, payload: dict[str, Any]
) -> dict[str, Any] | None:
    if not get_record(conn, record_id):
        return None
    normalized = normalize_record_payload(module, payload)
    if module == "password" and normalized["details"].get("secret"):
        normalized["details"]["secret"] = protect_secret(str(normalized["details"]["secret"]))
    occurred_on = normalized["occurred_on"] or today_iso()
    score = normalized["score"]
    if score in (None, ""):
        score = calculate_score(module, normalized["details"])
    conn.execute(
        """
        UPDATE records
        SET module = ?, title = ?, occurred_on = ?, status = ?, score = ?,
            tags = ?, details = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            module,
            normalized["title"],
            occurred_on,
            normalized["status"],
            float(score),
            json.dumps(normalized["tags"], ensure_ascii=False),
            json.dumps(normalized["details"], ensure_ascii=False),
            utc_now(),
            record_id,
        ),
    )
    return get_record(conn, record_id)


def delete_record(conn: sqlite3.Connection, record_id: int) -> bool:
    result = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    return result.rowcount > 0


def calculate_score(module: str, details: dict[str, Any]) -> float:
    base = SCORE_WEIGHTS.get(module, 0)
    if module in {"expense", "bill"}:
        amount = float(details.get("amount") or 0)
        return min(0, base - amount / 200)
    if module == "exercise":
        return base + min(float(details.get("duration") or 0) / 20, 5)
    if module == "reading":
        return base + min(float(details.get("progress") or 0) / 50, 3)
    if module == "diet":
        calories = float(details.get("calories") or 0)
        return base + (1 if 350 <= calories <= 750 else -1)
    return float(base)


def dashboard(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT module, COUNT(*) AS total, SUM(score) AS score
        FROM records
        GROUP BY module
        ORDER BY module
        """
    ).fetchall()
    today = today_iso()
    due_rows = conn.execute(
        """
        SELECT * FROM reminders
        WHERE is_done = 0 AND due_at <= ?
        ORDER BY due_at ASC
        LIMIT 20
        """,
        (today + "T23:59:59",),
    ).fetchall()
    recent = list_records(conn, limit=12)
    total_score = sum(float(row["score"] or 0) for row in rows)
    return {
        "modules": MODULES,
        "summary": [
            {
                "module": row["module"],
                "label": MODULES.get(row["module"], {}).get("label", row["module"]),
                "total": row["total"],
                "score": round(float(row["score"] or 0), 2),
            }
            for row in rows
        ],
        "life_score": round(total_score, 2),
        "recent": recent,
        "reminders_due": [row_to_reminder(row) for row in due_rows],
        "insights": build_insights(conn),
    }


def build_insights(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT module, COUNT(*) AS total, SUM(score) AS score
        FROM records
        WHERE occurred_on >= ?
        GROUP BY module
        """,
        ((date.today() - timedelta(days=30)).isoformat(),),
    ).fetchall()
    totals = {row["module"]: {"total": row["total"], "score": row["score"]} for row in rows}
    insights: list[str] = []
    if totals.get("expense", {}).get("total", 0) > totals.get("exercise", {}).get("total", 0) + 5:
        insights.append("近 30 天消费记录明显多于运动记录，建议设置每周运动提醒来平衡生活评分。")
    if "reading" not in totals:
        insights.append("近 30 天没有阅读记录，可以添加一本在读书籍并设置进度目标。")
    if totals.get("health", {}).get("total", 0) < 2:
        insights.append("健康数据较少，建议至少记录体重、睡眠或血压中的一项。")
    if not insights:
        insights.append("本月数据覆盖均衡，继续保持记录习惯即可提升预测和评分质量。")
    return insights


def forecast(conn: sqlite3.Connection) -> dict[str, Any]:
    since = (date.today() - timedelta(days=60)).isoformat()
    rows = conn.execute(
        """
        SELECT module, occurred_on, score
        FROM records
        WHERE occurred_on >= ?
        ORDER BY occurred_on ASC
        """,
        (since,),
    ).fetchall()
    by_module: dict[str, list[float]] = {}
    for row in rows:
        by_module.setdefault(row["module"], []).append(float(row["score"] or 0))
    predictions = {}
    for module, scores in by_module.items():
        window = scores[-7:]
        avg = sum(window) / len(window)
        trend = scores[-1] - scores[0] if len(scores) > 1 else 0
        predictions[module] = {
            "next_week_score": round(avg * 7, 2),
            "trend": "up" if trend > 1 else "down" if trend < -1 else "stable",
            "confidence": round(min(0.95, 0.35 + len(scores) / 80), 2),
        }
    return {"predictions": predictions, "method": "rolling-average-local"}


def list_reminders(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM reminders ORDER BY due_at ASC").fetchall()
    return [row_to_reminder(row) for row in rows]


def create_reminder(conn: sqlite3.Connection, payload: dict[str, Any]) -> dict[str, Any]:
    cur = conn.execute(
        """
        INSERT INTO reminders (title, channel, due_at, message, is_done, record_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(payload.get("title") or "提醒"),
            str(payload.get("channel") or "local"),
            str(payload.get("due_at") or today_iso()),
            str(payload.get("message") or ""),
            1 if payload.get("is_done") else 0,
            payload.get("record_id"),
            utc_now(),
        ),
    )
    return row_to_reminder(
        conn.execute("SELECT * FROM reminders WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def set_reminder_done(conn: sqlite3.Connection, reminder_id: int, done: bool) -> bool:
    result = conn.execute(
        "UPDATE reminders SET is_done = ? WHERE id = ?", (1 if done else 0, reminder_id)
    )
    return result.rowcount > 0


def protect_secret(secret: str) -> str:
    key = hashlib.sha256(settings.password_secret.encode("utf-8")).digest()
    data = secret.encode("utf-8")
    encoded = bytes(char ^ key[index % len(key)] for index, char in enumerate(data))
    return base64.urlsafe_b64encode(encoded).decode("ascii")


def reveal_secret(secret: str) -> str:
    key = hashlib.sha256(settings.password_secret.encode("utf-8")).digest()
    data = base64.urlsafe_b64decode(secret.encode("ascii"))
    decoded = bytes(char ^ key[index % len(key)] for index, char in enumerate(data))
    return decoded.decode("utf-8")


def reveal_record_secret(conn: sqlite3.Connection, record_id: int) -> str | None:
    row = conn.execute("SELECT module, details FROM records WHERE id = ?", (record_id,)).fetchone()
    if not row or row["module"] != "password":
        return None
    details = json.loads(row["details"] or "{}")
    encrypted = details.get("secret")
    return reveal_secret(str(encrypted)) if encrypted else None


def row_to_record(row: sqlite3.Row) -> dict[str, Any]:
    details = json.loads(row["details"] or "{}")
    if row["module"] == "password" and details.get("secret"):
        details = {**details, "secret": "********"}
    return {
        "id": row["id"],
        "module": row["module"],
        "title": row["title"],
        "occurred_on": row["occurred_on"],
        "status": row["status"],
        "score": row["score"],
        "tags": json.loads(row["tags"] or "[]"),
        "details": details,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_reminder(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "channel": row["channel"],
        "due_at": row["due_at"],
        "message": row["message"],
        "is_done": bool(row["is_done"]),
        "record_id": row["record_id"],
        "created_at": row["created_at"],
    }


def export_records(conn: sqlite3.Connection) -> dict[str, Any]:
    return {"records": list_records(conn, limit=500), "reminders": list_reminders(conn)}

