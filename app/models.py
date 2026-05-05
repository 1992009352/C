from __future__ import annotations

import json
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JournalEntry(Base):
    __tablename__ = 'journal_entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module_key: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64), default='active')
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occurred_on: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    tags: Mapped[str] = mapped_column(String(255), default='')
    notes: Mapped[str] = mapped_column(Text, default='')
    payload: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def payload_dict(self) -> dict[str, object]:
        try:
            return json.loads(self.payload or '{}')
        except json.JSONDecodeError:
            return {}
