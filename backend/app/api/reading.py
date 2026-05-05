from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.reading import Book, ReadingRecord
from app.schemas.reading import BookCreate, BookUpdate, BookOut, ReadingRecordCreate, ReadingRecordOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/reading", tags=["阅读管理"])


@router.get("/books", response_model=PageResult[BookOut])
async def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Book).where(Book.user_id == current_user.id)
    count_query = select(func.count(Book.id)).where(Book.user_id == current_user.id)

    if status:
        query = query.where(Book.status == status)
        count_query = count_query.where(Book.status == status)
    if keyword:
        query = query.where(Book.title.contains(keyword))
        count_query = count_query.where(Book.title.contains(keyword))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Book.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [BookOut.model_validate(b) for b in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/books", response_model=BookOut)
async def create_book(
    data: BookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    book = Book(user_id=current_user.id, **data.model_dump())
    db.add(book)
    await db.flush()
    await db.refresh(book)
    return BookOut.model_validate(book)


@router.put("/books/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int,
    data: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    await db.flush()
    await db.refresh(book)
    return BookOut.model_validate(book)


@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    await db.delete(book)
    return {"message": "删除成功"}


@router.get("/records", response_model=PageResult[ReadingRecordOut])
async def list_reading_records(
    book_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ReadingRecord).where(ReadingRecord.user_id == current_user.id)
    count_query = select(func.count(ReadingRecord.id)).where(ReadingRecord.user_id == current_user.id)

    if book_id:
        query = query.where(ReadingRecord.book_id == book_id)
        count_query = count_query.where(ReadingRecord.book_id == book_id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(ReadingRecord.read_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [ReadingRecordOut.model_validate(r) for r in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/records", response_model=ReadingRecordOut)
async def create_reading_record(
    data: ReadingRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = ReadingRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return ReadingRecordOut.model_validate(record)
