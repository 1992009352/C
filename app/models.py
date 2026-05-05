from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal


ModuleName = Literal[
    "expense",
    "exercise",
    "reading",
    "health",
    "diet",
    "experience",
    "todo",
    "note",
    "password",
    "contact",
    "bill",
]


MODULES: dict[str, dict[str, str]] = {
    "expense": {"label": "消费", "icon": "wallet", "accent": "#2563eb"},
    "exercise": {"label": "锻炼", "icon": "activity", "accent": "#16a34a"},
    "reading": {"label": "阅读", "icon": "book", "accent": "#7c3aed"},
    "health": {"label": "健康", "icon": "heart", "accent": "#dc2626"},
    "diet": {"label": "饮食", "icon": "utensils", "accent": "#ea580c"},
    "experience": {"label": "人生经历", "icon": "map", "accent": "#0891b2"},
    "todo": {"label": "待办", "icon": "check", "accent": "#4f46e5"},
    "note": {"label": "笔记", "icon": "note", "accent": "#9333ea"},
    "password": {"label": "密码", "icon": "lock", "accent": "#475569"},
    "contact": {"label": "联系人", "icon": "users", "accent": "#0d9488"},
    "bill": {"label": "账单", "icon": "receipt", "accent": "#ca8a04"},
}


SCORE_WEIGHTS: dict[str, int] = {
    "exercise": 9,
    "reading": 7,
    "health": 6,
    "diet": 5,
    "experience": 8,
    "todo": 4,
    "note": 3,
    "expense": -1,
    "bill": -1,
    "password": 1,
    "contact": 1,
}


REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "expense": ("amount",),
    "exercise": ("duration",),
    "reading": ("progress",),
    "health": ("value",),
    "diet": ("calories",),
    "bill": ("amount", "due_date"),
    "password": ("secret",),
}


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate_module(module: str) -> ValidationResult:
    if module in MODULES:
        return ValidationResult(True, [])
    return ValidationResult(False, [f"Unknown module '{module}'."])


def normalize_record_payload(module: str, payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title") or "").strip()
    if not title:
        title = MODULES.get(module, {}).get("label", module)

    status = str(payload.get("status") or "active").strip().lower()
    tags = payload.get("tags")
    if isinstance(tags, str):
        tags = [item.strip() for item in tags.split(",") if item.strip()]
    elif not isinstance(tags, list):
        tags = []

    entry: dict[str, Any] = {
        "module": module,
        "title": title,
        "occurred_on": str(payload.get("occurred_on") or "").strip() or date.today().isoformat(),
        "status": status,
        "score": payload.get("score"),
        "tags": tags,
        "details": payload.get("details") if isinstance(payload.get("details"), dict) else {},
    }

    for key, value in payload.items():
        if key not in entry and key not in {"details", "tags"}:
            entry["details"][key] = value
    return entry


def validate_record(module: str, payload: dict[str, Any]) -> ValidationResult:
    module_check = validate_module(module)
    if not module_check.is_valid:
        return module_check

    errors: list[str] = []
    normalized = normalize_record_payload(module, payload)
    details = normalized["details"]
    for field in REQUIRED_FIELDS.get(module, ()):
        if normalized.get(field) in (None, "") and details.get(field) in (None, ""):
            errors.append(f"Field '{field}' is required for module '{module}'.")

    if normalized["status"] not in {"active", "done", "archived", "pending", "paid", "unpaid"}:
        errors.append("Status must be active, done, archived, pending, paid, or unpaid.")

    return ValidationResult(not errors, errors)
