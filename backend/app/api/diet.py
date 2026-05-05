from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.diet import DietRecord, FoodItem
from app.schemas.diet import DietRecordCreate, DietRecordOut, FoodItemCreate, FoodItemOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/diet", tags=["饮食管理"])


@router.get("/foods", response_model=list[FoodItemOut])
async def list_foods(
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(FoodItem).where(FoodItem.user_id == current_user.id)
    if keyword:
        query = query.where(FoodItem.name.contains(keyword))
    result = await db.execute(query.order_by(FoodItem.name))
    return [FoodItemOut.model_validate(f) for f in result.scalars().all()]


@router.post("/foods", response_model=FoodItemOut)
async def create_food(
    data: FoodItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    food = FoodItem(user_id=current_user.id, **data.model_dump())
    db.add(food)
    await db.flush()
    await db.refresh(food)
    return FoodItemOut.model_validate(food)


@router.get("/records", response_model=PageResult[DietRecordOut])
async def list_diet_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    meal_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(DietRecord).where(DietRecord.user_id == current_user.id)
    count_query = select(func.count(DietRecord.id)).where(DietRecord.user_id == current_user.id)

    if meal_type:
        query = query.where(DietRecord.meal_type == meal_type)
        count_query = count_query.where(DietRecord.meal_type == meal_type)
    if start_date:
        query = query.where(DietRecord.diet_date >= start_date)
        count_query = count_query.where(DietRecord.diet_date >= start_date)
    if end_date:
        query = query.where(DietRecord.diet_date <= end_date)
        count_query = count_query.where(DietRecord.diet_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(DietRecord.diet_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [DietRecordOut.model_validate(r) for r in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/records", response_model=DietRecordOut)
async def create_diet_record(
    data: DietRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = DietRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return DietRecordOut.model_validate(record)


@router.delete("/records/{record_id}")
async def delete_diet_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DietRecord).where(DietRecord.id == record_id, DietRecord.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(record)
    return {"message": "删除成功"}


@router.get("/daily-summary")
async def daily_diet_summary(
    diet_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            DietRecord.meal_type,
            func.count(DietRecord.id).label("count"),
            func.coalesce(func.sum(DietRecord.calories), 0).label("total_calories"),
        )
        .where(DietRecord.user_id == current_user.id, DietRecord.diet_date == diet_date)
        .group_by(DietRecord.meal_type)
    )
    rows = result.all()
    return [{"meal_type": r.meal_type, "count": r.count, "total_calories": float(r.total_calories)} for r in rows]
