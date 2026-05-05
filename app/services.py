from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.domain import MODULES, get_module
from app.models import JournalEntry
from app.schemas import DashboardRead, EntryCreate, EntryRead, ModuleSummary, ScoreBreakdown


def serialize_entry(entry: JournalEntry) -> EntryRead:
    return EntryRead(
        id=entry.id,
        module_key=entry.module_key,
        title=entry.title,
        status=entry.status,
        metric_value=entry.metric_value,
        amount=entry.amount,
        unit=entry.unit,
        occurred_on=entry.occurred_on,
        tags=entry.tags,
        notes=entry.notes,
        payload=entry.payload_dict(),
        created_at=entry.created_at,
    )


def list_entries(db: Session, module_key: str, limit: int | None = None) -> list[EntryRead]:
    get_module(module_key)
    statement = select(JournalEntry).where(JournalEntry.module_key == module_key).order_by(desc(JournalEntry.occurred_on), desc(JournalEntry.created_at))
    if limit is not None:
        statement = statement.limit(limit)
    return [serialize_entry(entry) for entry in db.scalars(statement).all()]


def create_entry(db: Session, module_key: str, payload: EntryCreate) -> EntryRead:
    module = get_module(module_key)
    entry = JournalEntry(
        module_key=module_key,
        title=payload.title,
        status=payload.status or module.default_status,
        metric_value=payload.metric_value,
        amount=payload.amount,
        unit=payload.unit or module.default_unit,
        occurred_on=payload.occurred_on,
        tags=payload.tags,
        notes=payload.notes,
        payload=json.dumps(payload.payload),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return serialize_entry(entry)


def _recent_entries(db: Session) -> list[JournalEntry]:
    statement = select(JournalEntry).order_by(desc(JournalEntry.occurred_on), desc(JournalEntry.created_at)).limit(12)
    return db.scalars(statement).all()


def _module_summary(db: Session, module_key: str) -> ModuleSummary:
    module = get_module(module_key)
    entries = db.scalars(
        select(JournalEntry).where(JournalEntry.module_key == module_key).order_by(desc(JournalEntry.occurred_on), desc(JournalEntry.created_at)).limit(settings.page_size)
    ).all()
    return ModuleSummary(
        key=module.key,
        label=module.label,
        description=module.description,
        category=module.category,
        total_entries=len(entries),
        recent_titles=[entry.title for entry in entries[:3]],
        amount_total=round(sum(entry.amount or 0 for entry in entries), 2),
        metric_total=round(sum(entry.metric_value or 0 for entry in entries), 2),
        default_unit=module.default_unit,
    )


def _score(value: float, target: float) -> int:
    if target <= 0:
        return 0
    return max(0, min(int((value / target) * 100), 100))


def _build_breakdown(db: Session) -> list[ScoreBreakdown]:
    today = date.today()
    window_start = today - timedelta(days=30)
    entries = db.scalars(select(JournalEntry).where(JournalEntry.occurred_on >= window_start)).all()
    grouped = Counter(entry.module_key for entry in entries)
    task_done = sum(1 for entry in entries if entry.module_key == 'task' and entry.status == 'done')
    workout_minutes = sum(entry.metric_value or 0 for entry in entries if entry.module_key == 'workout')
    reading_pages = sum(entry.metric_value or 0 for entry in entries if entry.module_key == 'reading')
    meal_logs = grouped.get('meal', 0)
    health_scores = [entry.metric_value for entry in entries if entry.module_key == 'health' and entry.metric_value is not None]
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 75
    return [
        ScoreBreakdown(label='Execution', score=_score(task_done, 5), detail=f'Completed {task_done} task entries in 30 days.'),
        ScoreBreakdown(label='Movement', score=_score(workout_minutes, 150), detail=f'Logged {int(workout_minutes)} workout minutes.'),
        ScoreBreakdown(label='Nutrition', score=_score(meal_logs, 21), detail=f'Tracked {meal_logs} meals this month.'),
        ScoreBreakdown(label='Learning', score=_score(reading_pages, 300), detail=f'Read {int(reading_pages)} pages this month.'),
        ScoreBreakdown(label='Wellbeing', score=max(0, min(int(avg_health), 100)), detail=f'Average health score is {avg_health:.0f}.'),
    ]


def build_dashboard(db: Session) -> DashboardRead:
    total_entries = db.scalar(select(func.count(JournalEntry.id))) or 0
    unique_days = db.scalar(select(func.count(func.distinct(JournalEntry.occurred_on)))) or 0
    module_summaries = [_module_summary(db, module.key) for module in MODULES]
    breakdown = _build_breakdown(db)
    balance_score = round(sum(item.score for item in breakdown) / len(breakdown)) if breakdown else 0
    recent = [serialize_entry(entry) for entry in _recent_entries(db)]
    spending = sum(entry.amount or 0 for entry in recent if entry.module_key in {'expense', 'subscription', 'meal'})
    workouts = sum(1 for entry in recent if entry.module_key == 'workout')
    categories = Counter(entry.module_key for entry in recent)
    most_active_key = categories.most_common(1)[0][0] if categories else 'task'
    most_active_label = get_module(most_active_key).label
    insight_lines = [
        f'Balance score is {balance_score}/100 based on recent execution, movement, nutrition, learning, and wellbeing signals.',
        f'Recent logged spending across expenses, meals, and subscriptions is {spending:.2f}.',
        f'Most active module right now is {most_active_label}.',
        f'You logged {workouts} workout entries in the latest activity stream.',
    ]
    return DashboardRead(
        title='All-around life management dashboard',
        total_entries=total_entries,
        total_modules=len(MODULES),
        active_days=unique_days,
        balance_score=balance_score,
        insight_lines=insight_lines,
        module_summaries=module_summaries,
        score_breakdown=breakdown,
        recent_entries=recent,
    )
