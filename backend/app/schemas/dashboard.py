from pydantic import BaseModel
from typing import Optional


class DashboardStats(BaseModel):
    total_transactions: int = 0
    month_income: float = 0
    month_expense: float = 0
    total_exercises: int = 0
    month_exercise_duration: int = 0
    total_books: int = 0
    reading_books: int = 0
    total_todos: int = 0
    pending_todos: int = 0
    total_habits: int = 0
    active_habits: int = 0
    today_habit_completed: int = 0
    total_notes: int = 0
    total_goals: int = 0
    active_goals: int = 0
    total_contacts: int = 0
    total_experiences: int = 0


class MonthTrend(BaseModel):
    month: str
    income: float = 0
    expense: float = 0


class ExerciseTrend(BaseModel):
    date: str
    duration: int = 0
    calories: int = 0
