from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitRecord
from app.schemas.habit import HabitCreate, HabitUpdate, HabitOut, HabitRecordCreate, HabitRecordOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/habits", tags=["习惯追踪"])


@router.get("", response_model=list[HabitOut])
async def list_habits(
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Habit).where(Habit.user_id == current_user.id)
    if is_active is not None:
        query = query.where(Habit.is_active == is_active)
    result = await db.execute(query.order_by(Habit.created_at.desc()))
    return [HabitOut.model_validate(h) for h in result.scalars().all()]


@router.post("", response_model=HabitOut)
async def create_habit(
    data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    habit = Habit(user_id=current_user.id, **data.model_dump())
    db.add(habit)
    await db.flush()
    await db.refresh(habit)
    return HabitOut.model_validate(habit)


@router.put("/{habit_id}", response_model=HabitOut)
async def update_habit(
    habit_id: int,
    data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="习惯不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    await db.flush()
    await db.refresh(habit)
    return HabitOut.model_validate(habit)


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="习惯不存在")
    await db.delete(habit)
    return {"message": "删除成功"}


@router.get("/records", response_model=PageResult[HabitRecordOut])
async def list_habit_records(
    habit_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(HabitRecord).where(HabitRecord.user_id == current_user.id)
    count_query = select(func.count(HabitRecord.id)).where(HabitRecord.user_id == current_user.id)

    if habit_id:
        query = query.where(HabitRecord.habit_id == habit_id)
        count_query = count_query.where(HabitRecord.habit_id == habit_id)
    if start_date:
        query = query.where(HabitRecord.record_date >= start_date)
        count_query = count_query.where(HabitRecord.record_date >= start_date)
    if end_date:
        query = query.where(HabitRecord.record_date <= end_date)
        count_query = count_query.where(HabitRecord.record_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(HabitRecord.record_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [HabitRecordOut.model_validate(r) for r in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/records", response_model=HabitRecordOut)
async def create_habit_record(
    data: HabitRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = HabitRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return HabitRecordOut.model_validate(record)


@router.get("/checkin-calendar")
async def get_checkin_calendar(
    habit_id: int,
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    result = await db.execute(
        select(HabitRecord.record_date, HabitRecord.count)
        .where(
            HabitRecord.user_id == current_user.id,
            HabitRecord.habit_id == habit_id,
            HabitRecord.record_date >= start,
            HabitRecord.record_date < end,
        )
    )
    records = result.all()
    return [{"date": str(r.record_date), "count": r.count} for r in records]
