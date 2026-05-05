from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NoteCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = ""
    color: Optional[str] = "#409EFF"
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0


class NoteCategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    parent_id: Optional[int]
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class NoteCreate(BaseModel):
    category_id: Optional[int] = None
    title: str
    content: Optional[str] = ""
    tags: Optional[str] = ""
    is_pinned: Optional[bool] = False


class NoteUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteOut(BaseModel):
    id: int
    category_id: Optional[int]
    title: str
    content: str
    tags: str
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
