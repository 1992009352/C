from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.contact import Contact, ContactGroup
from app.schemas.contact import ContactCreate, ContactUpdate, ContactOut, ContactGroupCreate, ContactGroupOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/contacts", tags=["联系人管理"])


@router.get("/groups", response_model=list[ContactGroupOut])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ContactGroup).where(ContactGroup.user_id == current_user.id).order_by(ContactGroup.sort_order)
    )
    return [ContactGroupOut.model_validate(g) for g in result.scalars().all()]


@router.post("/groups", response_model=ContactGroupOut)
async def create_group(
    data: ContactGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = ContactGroup(user_id=current_user.id, **data.model_dump())
    db.add(group)
    await db.flush()
    await db.refresh(group)
    return ContactGroupOut.model_validate(group)


@router.get("", response_model=PageResult[ContactOut])
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    group_id: Optional[int] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contact).where(Contact.user_id == current_user.id)
    count_query = select(func.count(Contact.id)).where(Contact.user_id == current_user.id)

    if group_id:
        query = query.where(Contact.group_id == group_id)
        count_query = count_query.where(Contact.group_id == group_id)
    if keyword:
        query = query.where(Contact.name.contains(keyword))
        count_query = count_query.where(Contact.name.contains(keyword))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Contact.name).offset((page - 1) * page_size).limit(page_size)
    )
    items = [ContactOut.model_validate(c) for c in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ContactOut)
async def create_contact(
    data: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contact = Contact(user_id=current_user.id, **data.model_dump())
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return ContactOut.model_validate(contact)


@router.put("/{contact_id}", response_model=ContactOut)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    await db.flush()
    await db.refresh(contact)
    return ContactOut.model_validate(contact)


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    await db.delete(contact)
    return {"message": "删除成功"}
