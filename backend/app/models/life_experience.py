from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, Integer, Text, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ExperienceType(str, enum.Enum):
    TRAVEL = "travel"
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    MEMORY = "memory"
    EVENT = "event"
    OTHER = "other"


class LifeExperience(Base):
    __tablename__ = "life_experiences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    experience_type: Mapped[str] = mapped_column(SAEnum(ExperienceType), default=ExperienceType.EVENT)
    experience_date: Mapped[date] = mapped_column(Date, index=True)
    location: Mapped[str] = mapped_column(String(200), default="")
    cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    photos: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
