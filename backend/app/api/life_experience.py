from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.life_experience import LifeExperience
from app.schemas.life_experience import LifeExperienceCreate, LifeExperienceUpdate, LifeExperienceOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/experiences", tags=["人生经历"])


@router.get("", response_model=PageResult[LifeExperienceOut])
async def list_experiences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    experience_type: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LifeExperience).where(LifeExperience.user_id == current_user.id)
    count_query = select(func.count(LifeExperience.id)).where(LifeExperience.user_id == current_user.id)

    if experience_type:
        query = query.where(LifeExperience.experience_type == experience_type)
        count_query = count_query.where(LifeExperience.experience_type == experience_type)
    if keyword:
        query = query.where(LifeExperience.title.contains(keyword))
        count_query = count_query.where(LifeExperience.title.contains(keyword))
    if start_date:
        query = query.where(LifeExperience.experience_date >= start_date)
        count_query = count_query.where(LifeExperience.experience_date >= start_date)
    if end_date:
        query = query.where(LifeExperience.experience_date <= end_date)
        count_query = count_query.where(LifeExperience.experience_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(LifeExperience.experience_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [LifeExperienceOut.model_validate(e) for e in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=LifeExperienceOut)
async def create_experience(
    data: LifeExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exp = LifeExperience(user_id=current_user.id, **data.model_dump())
    db.add(exp)
    await db.flush()
    await db.refresh(exp)
    return LifeExperienceOut.model_validate(exp)


@router.put("/{exp_id}", response_model=LifeExperienceOut)
async def update_experience(
    exp_id: int,
    data: LifeExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LifeExperience).where(LifeExperience.id == exp_id, LifeExperience.user_id == current_user.id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="经历不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exp, field, value)
    await db.flush()
    await db.refresh(exp)
    return LifeExperienceOut.model_validate(exp)


@router.delete("/{exp_id}")
async def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LifeExperience).where(LifeExperience.id == exp_id, LifeExperience.user_id == current_user.id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="经历不存在")
    await db.delete(exp)
    return {"message": "删除成功"}
