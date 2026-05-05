from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.health import HealthRecord, Exercise, SleepRecord
from app.schemas.health import (
    HealthRecordCreate, HealthRecordOut,
    ExerciseCreate, ExerciseOut,
    SleepRecordCreate, SleepRecordOut,
)
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/health", tags=["健康管理"])


@router.get("/records", response_model=PageResult[HealthRecordOut])
async def list_health_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(HealthRecord).where(HealthRecord.user_id == current_user.id)
    count_query = select(func.count(HealthRecord.id)).where(HealthRecord.user_id == current_user.id)

    if start_date:
        query = query.where(HealthRecord.record_date >= start_date)
        count_query = count_query.where(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.where(HealthRecord.record_date <= end_date)
        count_query = count_query.where(HealthRecord.record_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(HealthRecord.record_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [HealthRecordOut.model_validate(r) for r in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/records", response_model=HealthRecordOut)
async def create_health_record(
    data: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = HealthRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return HealthRecordOut.model_validate(record)


@router.delete("/records/{record_id}")
async def delete_health_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(HealthRecord).where(HealthRecord.id == record_id, HealthRecord.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(record)
    return {"message": "删除成功"}


@router.get("/exercises", response_model=PageResult[ExerciseOut])
async def list_exercises(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exercise_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Exercise).where(Exercise.user_id == current_user.id)
    count_query = select(func.count(Exercise.id)).where(Exercise.user_id == current_user.id)

    if exercise_type:
        query = query.where(Exercise.exercise_type == exercise_type)
        count_query = count_query.where(Exercise.exercise_type == exercise_type)
    if start_date:
        query = query.where(Exercise.exercise_date >= start_date)
        count_query = count_query.where(Exercise.exercise_date >= start_date)
    if end_date:
        query = query.where(Exercise.exercise_date <= end_date)
        count_query = count_query.where(Exercise.exercise_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Exercise.exercise_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [ExerciseOut.model_validate(e) for e in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/exercises", response_model=ExerciseOut)
async def create_exercise(
    data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exercise = Exercise(user_id=current_user.id, **data.model_dump())
    db.add(exercise)
    await db.flush()
    await db.refresh(exercise)
    return ExerciseOut.model_validate(exercise)


@router.delete("/exercises/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exercise).where(Exercise.id == exercise_id, Exercise.user_id == current_user.id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(exercise)
    return {"message": "删除成功"}


@router.get("/sleep", response_model=PageResult[SleepRecordOut])
async def list_sleep_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SleepRecord).where(SleepRecord.user_id == current_user.id)
    count_query = select(func.count(SleepRecord.id)).where(SleepRecord.user_id == current_user.id)

    if start_date:
        query = query.where(SleepRecord.sleep_date >= start_date)
        count_query = count_query.where(SleepRecord.sleep_date >= start_date)
    if end_date:
        query = query.where(SleepRecord.sleep_date <= end_date)
        count_query = count_query.where(SleepRecord.sleep_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(SleepRecord.sleep_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [SleepRecordOut.model_validate(r) for r in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/sleep", response_model=SleepRecordOut)
async def create_sleep_record(
    data: SleepRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = SleepRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return SleepRecordOut.model_validate(record)
