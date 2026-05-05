"""Small local natural-language parser for quick life records."""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any


MODULE_KEYWORDS = {
    "expense": ("花", "消费", "买", "支出", "付款", "午餐", "晚餐", "早餐"),
    "exercise": ("跑步", "健身", "运动", "骑行", "游泳", "瑜伽", "锻炼"),
    "reading": ("读", "阅读", "看书", "书"),
    "health": ("体重", "血压", "睡眠", "健康", "心率"),
    "diet": ("饮食", "热量", "蛋白", "早餐", "午餐", "晚餐"),
    "experience": ("旅行", "徒步", "经历", "参观", "看展", "电影"),
    "todo": ("待办", "要做", "todo", "任务"),
    "note": ("笔记", "记录", "想法", "灵感"),
    "bill": ("账单", "房租", "水电", "还款", "缴费"),
    "contact": ("联系人", "电话", "认识"),
    "password": ("密码", "账号", "登录"),
}


def parse_quick_entry(text: str) -> dict[str, Any]:
    """Convert a short sentence into a record payload.

    This is intentionally deterministic and offline: it gives the application a
    Mulanbay-like quick entry experience without sending private data to a model.
    """

    value = text.strip()
    module = detect_module(value)
    payload: dict[str, Any] = {
        "module": module,
        "title": compact_title(value),
        "occurred_on": detect_date(value),
        "details": {"raw": value},
        "tags": detect_tags(value),
    }
    enrich_details(module, value, payload["details"])
    return payload


def detect_module(text: str) -> str:
    scores = {
        module: sum(1 for keyword in keywords if keyword.lower() in text.lower())
        for module, keywords in MODULE_KEYWORDS.items()
    }
    winner = max(scores, key=scores.get)
    return winner if scores[winner] else "note"


def compact_title(text: str) -> str:
    title = re.sub(r"#\S+", "", text).strip(" ，,。")
    return title[:40] or "快速记录"


def detect_tags(text: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"#([\w\u4e00-\u9fff-]+)", text)]


def detect_date(text: str) -> str:
    today = date.today()
    if "前天" in text:
        return (today - timedelta(days=2)).isoformat()
    if "昨天" in text:
        return (today - timedelta(days=1)).isoformat()
    if "明天" in text:
        return (today + timedelta(days=1)).isoformat()
    match = re.search(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", text)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
    return today.isoformat()


def enrich_details(module: str, text: str, details: dict[str, Any]) -> None:
    number = first_number(text)
    money = re.search(r"(\d+(?:\.\d+)?)\s*(元|块|rmb|¥)", text, flags=re.IGNORECASE)
    minutes = re.search(r"(\d+(?:\.\d+)?)\s*(分钟|min|小时)", text, flags=re.IGNORECASE)
    km = re.search(r"(\d+(?:\.\d+)?)\s*(km|公里)", text, flags=re.IGNORECASE)

    if module in {"expense", "bill"}:
        details["amount"] = float(money.group(1)) if money else number
    elif module == "exercise":
        details["duration"] = float(minutes.group(1)) if minutes else number
        if km:
            details["distance"] = float(km.group(1))
    elif module == "reading":
        details["progress"] = number or 1
    elif module == "health":
        details["value"] = number or 0
    elif module == "diet":
        details["calories"] = number or 0
    elif module == "password":
        secret = re.search(r"(密码|password)[:： ]+(\S+)", text, flags=re.IGNORECASE)
        if secret:
            details["secret"] = secret.group(2)


def first_number(text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else 0
