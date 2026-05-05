from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.goal import Goal, GoalProgress
from app.schemas.goal import GoalCreate, GoalUpdate, GoalOut, GoalProgressCreate, GoalProgressOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/goals", tags=["目标管理"])


@router.get("", response_model=list[GoalOut])
async def list_goals(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Goal).where(Goal.user_id == current_user.id)
    if status:
        query = query.where(Goal.status == status)
    result = await db.execute(query.order_by(Goal.created_at.desc()))
    return [GoalOut.model_validate(g) for g in result.scalars().all()]


@router.post("", response_model=GoalOut)
async def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = Goal(user_id=current_user.id, **data.model_dump())
    db.add(goal)
    await db.flush()
    await db.refresh(goal)
    return GoalOut.model_validate(goal)


@router.put("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    await db.flush()
    await db.refresh(goal)
    return GoalOut.model_validate(goal)


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    await db.delete(goal)
    return {"message": "删除成功"}


@router.get("/progress", response_model=PageResult[GoalProgressOut])
async def list_goal_progress(
    goal_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(GoalProgress).where(
        GoalProgress.user_id == current_user.id, GoalProgress.goal_id == goal_id
    )
    count_query = select(func.count(GoalProgress.id)).where(
        GoalProgress.user_id == current_user.id, GoalProgress.goal_id == goal_id
    )

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(GoalProgress.record_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [GoalProgressOut.model_validate(p) for p in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/progress", response_model=GoalProgressOut)
async def create_goal_progress(
    data: GoalProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    progress = GoalProgress(user_id=current_user.id, **data.model_dump())
    db.add(progress)
    await db.flush()
    await db.refresh(progress)
    return GoalProgressOut.model_validate(progress)
