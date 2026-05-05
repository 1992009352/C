from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, Numeric, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ExerciseType(str, enum.Enum):
    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    GYM = "gym"
    YOGA = "yoga"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HIKING = "hiking"
    OTHER = "other"


class HealthRecord(Base):
    __tablename__ = "health_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    record_date: Mapped[date] = mapped_column(Date, index=True)
    weight: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    height: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    blood_pressure_sys: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blood_pressure_dia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blood_sugar: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    body_fat: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    mood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    exercise_type: Mapped[str] = mapped_column(SAEnum(ExerciseType), default=ExerciseType.RUNNING)
    exercise_date: Mapped[date] = mapped_column(Date, index=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    distance: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_rate_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(String(100), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SleepRecord(Base):
    __tablename__ = "sleep_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    sleep_date: Mapped[date] = mapped_column(Date, index=True)
    bed_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    wake_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    quality: Mapped[int] = mapped_column(Integer, default=3)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    metric_date: Mapped[date] = mapped_column(Date, index=True)
    metric_name: Mapped[str] = mapped_column(String(50))
    metric_value: Mapped[float] = mapped_column(Numeric(10, 2))
    unit: Mapped[str] = mapped_column(String(20), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
