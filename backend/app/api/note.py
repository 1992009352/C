from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.note import Note, NoteCategory
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut, NoteCategoryCreate, NoteCategoryOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/notes", tags=["笔记管理"])


@router.get("/categories", response_model=list[NoteCategoryOut])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NoteCategory).where(NoteCategory.user_id == current_user.id).order_by(NoteCategory.sort_order)
    )
    return [NoteCategoryOut.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=NoteCategoryOut)
async def create_category(
    data: NoteCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = NoteCategory(user_id=current_user.id, **data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return NoteCategoryOut.model_validate(cat)


@router.get("", response_model=PageResult[NoteOut])
async def list_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    is_archived: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Note).where(Note.user_id == current_user.id)
    count_query = select(func.count(Note.id)).where(Note.user_id == current_user.id)

    if category_id:
        query = query.where(Note.category_id == category_id)
        count_query = count_query.where(Note.category_id == category_id)
    if keyword:
        query = query.where(Note.title.contains(keyword))
        count_query = count_query.where(Note.title.contains(keyword))
    if is_archived is not None:
        query = query.where(Note.is_archived == is_archived)
        count_query = count_query.where(Note.is_archived == is_archived)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    items = [NoteOut.model_validate(n) for n in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=NoteOut)
async def create_note(
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = Note(user_id=current_user.id, **data.model_dump())
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return NoteOut.model_validate(note)


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: int,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await db.flush()
    await db.refresh(note)
    return NoteOut.model_validate(note)


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    await db.delete(note)
    return {"message": "删除成功"}
