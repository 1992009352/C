from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.todo import Todo, TodoCategory
from app.schemas.todo import TodoCreate, TodoUpdate, TodoOut, TodoCategoryCreate, TodoCategoryOut
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/todos", tags=["待办管理"])


@router.get("/categories", response_model=list[TodoCategoryOut])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoCategory).where(TodoCategory.user_id == current_user.id).order_by(TodoCategory.sort_order)
    )
    return [TodoCategoryOut.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=TodoCategoryOut)
async def create_category(
    data: TodoCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = TodoCategory(user_id=current_user.id, **data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return TodoCategoryOut.model_validate(cat)


@router.get("", response_model=PageResult[TodoOut])
async def list_todos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Todo).where(Todo.user_id == current_user.id)
    count_query = select(func.count(Todo.id)).where(Todo.user_id == current_user.id)

    if status:
        query = query.where(Todo.status == status)
        count_query = count_query.where(Todo.status == status)
    if priority:
        query = query.where(Todo.priority == priority)
        count_query = count_query.where(Todo.priority == priority)
    if category_id:
        query = query.where(Todo.category_id == category_id)
        count_query = count_query.where(Todo.category_id == category_id)
    if keyword:
        query = query.where(Todo.title.contains(keyword))
        count_query = count_query.where(Todo.title.contains(keyword))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Todo.is_pinned.desc(), Todo.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    items = [TodoOut.model_validate(t) for t in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=TodoOut)
async def create_todo(
    data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = Todo(user_id=current_user.id, **data.model_dump())
    db.add(todo)
    await db.flush()
    await db.refresh(todo)
    return TodoOut.model_validate(todo)


@router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "completed":
        update_data["completed_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(todo, field, value)
    await db.flush()
    await db.refresh(todo)
    return TodoOut.model_validate(todo)


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")
    await db.delete(todo)
    return {"message": "删除成功"}
