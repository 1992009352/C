from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TodoCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = ""
    color: Optional[str] = "#409EFF"
    sort_order: Optional[int] = 0


class TodoCategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class TodoCreate(BaseModel):
    category_id: Optional[int] = None
    title: str
    content: Optional[str] = ""
    priority: Optional[str] = "medium"
    status: Optional[str] = "pending"
    due_date: Optional[date] = None
    is_pinned: Optional[bool] = False
    tags: Optional[str] = ""


class TodoUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    is_pinned: Optional[bool] = None
    tags: Optional[str] = None


class TodoOut(BaseModel):
    id: int
    category_id: Optional[int]
    title: str
    content: str
    priority: str
    status: str
    due_date: Optional[date]
    completed_at: Optional[datetime]
    is_pinned: bool
    tags: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
