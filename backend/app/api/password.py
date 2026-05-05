from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.password import PasswordEntry, PasswordGroup
from app.schemas.password import (
    PasswordEntryCreate, PasswordEntryUpdate, PasswordEntryOut,
    PasswordGroupCreate, PasswordGroupOut,
)
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/passwords", tags=["密码管理"])


@router.get("/groups", response_model=list[PasswordGroupOut])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PasswordGroup).where(PasswordGroup.user_id == current_user.id).order_by(PasswordGroup.sort_order)
    )
    return [PasswordGroupOut.model_validate(g) for g in result.scalars().all()]


@router.post("/groups", response_model=PasswordGroupOut)
async def create_group(
    data: PasswordGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = PasswordGroup(user_id=current_user.id, **data.model_dump())
    db.add(group)
    await db.flush()
    await db.refresh(group)
    return PasswordGroupOut.model_validate(group)


@router.get("", response_model=PageResult[PasswordEntryOut])
async def list_passwords(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    group_id: Optional[int] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PasswordEntry).where(PasswordEntry.user_id == current_user.id)
    count_query = select(func.count(PasswordEntry.id)).where(PasswordEntry.user_id == current_user.id)

    if group_id:
        query = query.where(PasswordEntry.group_id == group_id)
        count_query = count_query.where(PasswordEntry.group_id == group_id)
    if keyword:
        query = query.where(PasswordEntry.title.contains(keyword))
        count_query = count_query.where(PasswordEntry.title.contains(keyword))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(PasswordEntry.title).offset((page - 1) * page_size).limit(page_size)
    )
    items = [PasswordEntryOut.model_validate(p) for p in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=PasswordEntryOut)
async def create_password(
    data: PasswordEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = PasswordEntry(user_id=current_user.id, **data.model_dump())
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return PasswordEntryOut.model_validate(entry)


@router.put("/{entry_id}", response_model=PasswordEntryOut)
async def update_password(
    entry_id: int,
    data: PasswordEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PasswordEntry).where(PasswordEntry.id == entry_id, PasswordEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="密码记录不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.flush()
    await db.refresh(entry)
    return PasswordEntryOut.model_validate(entry)


@router.delete("/{entry_id}")
async def delete_password(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PasswordEntry).where(PasswordEntry.id == entry_id, PasswordEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="密码记录不存在")
    await db.delete(entry)
    return {"message": "删除成功"}
