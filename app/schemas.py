from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class EntryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    status: str = Field(default='active', max_length=64)
    metric_value: float | None = None
    amount: float | None = None
    unit: str | None = Field(default=None, max_length=64)
    occurred_on: date
    tags: str = Field(default='', max_length=255)
    notes: str = ''
    payload: dict[str, object] = Field(default_factory=dict)


class EntryRead(EntryCreate):
    id: int
    module_key: str
    created_at: datetime


class ModuleSummary(BaseModel):
    key: str
    label: str
    description: str
    category: str
    total_entries: int
    recent_titles: list[str]
    amount_total: float
    metric_total: float
    default_unit: str


class ScoreBreakdown(BaseModel):
    label: str
    score: int
    detail: str


class DashboardRead(BaseModel):
    title: str
    total_entries: int
    total_modules: int
    active_days: int
    balance_score: int
    insight_lines: list[str]
    module_summaries: list[ModuleSummary]
    score_breakdown: list[ScoreBreakdown]
    recent_entries: list[EntryRead]
