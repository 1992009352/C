from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract

from app.core.database import get_db
from app.models.user import User
from app.models.finance import Transaction, TransactionType
from app.models.health import Exercise
from app.models.reading import Book
from app.models.todo import Todo
from app.models.habit import Habit, HabitRecord
from app.models.note import Note
from app.models.goal import Goal
from app.models.contact import Contact
from app.models.life_experience import LifeExperience
from app.schemas.dashboard import DashboardStats
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    month_start = date(now.year, now.month, 1)
    today = now.date()

    total_txn = (await db.execute(
        select(func.count(Transaction.id)).where(Transaction.user_id == current_user.id)
    )).scalar() or 0

    month_income = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.INCOME,
            Transaction.occur_date >= month_start,
        )
    )).scalar() or 0

    month_expense = (await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.occur_date >= month_start,
        )
    )).scalar() or 0

    total_exercises = (await db.execute(
        select(func.count(Exercise.id)).where(Exercise.user_id == current_user.id)
    )).scalar() or 0

    month_duration = (await db.execute(
        select(func.coalesce(func.sum(Exercise.duration), 0)).where(
            Exercise.user_id == current_user.id,
            Exercise.exercise_date >= month_start,
        )
    )).scalar() or 0

    total_books = (await db.execute(
        select(func.count(Book.id)).where(Book.user_id == current_user.id)
    )).scalar() or 0

    reading_books = (await db.execute(
        select(func.count(Book.id)).where(Book.user_id == current_user.id, Book.status == "reading")
    )).scalar() or 0

    total_todos = (await db.execute(
        select(func.count(Todo.id)).where(Todo.user_id == current_user.id)
    )).scalar() or 0

    pending_todos = (await db.execute(
        select(func.count(Todo.id)).where(Todo.user_id == current_user.id, Todo.status == "pending")
    )).scalar() or 0

    total_habits = (await db.execute(
        select(func.count(Habit.id)).where(Habit.user_id == current_user.id)
    )).scalar() or 0

    active_habits = (await db.execute(
        select(func.count(Habit.id)).where(Habit.user_id == current_user.id, Habit.is_active == True)
    )).scalar() or 0

    today_completed = (await db.execute(
        select(func.count(HabitRecord.id)).where(
            HabitRecord.user_id == current_user.id,
            HabitRecord.record_date == today,
        )
    )).scalar() or 0

    total_notes = (await db.execute(
        select(func.count(Note.id)).where(Note.user_id == current_user.id)
    )).scalar() or 0

    total_goals = (await db.execute(
        select(func.count(Goal.id)).where(Goal.user_id == current_user.id)
    )).scalar() or 0

    active_goals = (await db.execute(
        select(func.count(Goal.id)).where(Goal.user_id == current_user.id, Goal.status == "in_progress")
    )).scalar() or 0

    total_contacts = (await db.execute(
        select(func.count(Contact.id)).where(Contact.user_id == current_user.id)
    )).scalar() or 0

    total_experiences = (await db.execute(
        select(func.count(LifeExperience.id)).where(LifeExperience.user_id == current_user.id)
    )).scalar() or 0

    return DashboardStats(
        total_transactions=total_txn,
        month_income=float(month_income),
        month_expense=float(month_expense),
        total_exercises=total_exercises,
        month_exercise_duration=int(month_duration),
        total_books=total_books,
        reading_books=reading_books,
        total_todos=total_todos,
        pending_todos=pending_todos,
        total_habits=total_habits,
        active_habits=active_habits,
        today_habit_completed=today_completed,
        total_notes=total_notes,
        total_goals=total_goals,
        active_goals=active_goals,
        total_contacts=total_contacts,
        total_experiences=total_experiences,
    )


@router.get("/finance-trend")
async def get_finance_trend(
    year: int = 2026,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            extract("month", Transaction.occur_date).label("month"),
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .where(
            Transaction.user_id == current_user.id,
            extract("year", Transaction.occur_date) == year,
        )
        .group_by(extract("month", Transaction.occur_date), Transaction.type)
        .order_by(extract("month", Transaction.occur_date))
    )

    data = {}
    for row in result.all():
        m = int(row.month)
        if m not in data:
            data[m] = {"month": f"{m}月", "income": 0, "expense": 0}
        if row.type == TransactionType.INCOME or row.type == "income":
            data[m]["income"] = float(row.total)
        else:
            data[m]["expense"] = float(row.total)

    return [data.get(m, {"month": f"{m}月", "income": 0, "expense": 0}) for m in range(1, 13)]
