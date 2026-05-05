from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, Numeric, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    calories_per_100g: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    protein: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    fat: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    carbs: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DietRecord(Base):
    __tablename__ = "diet_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    food_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("food_items.id"), nullable=True)
    meal_type: Mapped[str] = mapped_column(SAEnum(MealType), default=MealType.LUNCH)
    food_name: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    unit: Mapped[str] = mapped_column(String(20), default="g")
    calories: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    diet_date: Mapped[date] = mapped_column(Date, index=True)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
