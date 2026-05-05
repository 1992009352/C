from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class BookCreate(BaseModel):
    title: str
    author: Optional[str] = ""
    isbn: Optional[str] = ""
    cover_url: Optional[str] = ""
    category: Optional[str] = ""
    total_pages: Optional[int] = 0
    status: Optional[str] = "wish"
    start_date: Optional[date] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    category: Optional[str] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    review: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    cover_url: str
    category: str
    total_pages: int
    current_page: int
    status: str
    rating: Optional[float]
    review: str
    start_date: Optional[date]
    finish_date: Optional[date]
    created_at: datetime
    model_config = {"from_attributes": True}


class ReadingRecordCreate(BaseModel):
    book_id: int
    read_date: date
    pages_read: int = 0
    duration: int = 0
    note: Optional[str] = ""


class ReadingRecordOut(BaseModel):
    id: int
    book_id: int
    read_date: date
    pages_read: int
    duration: int
    note: str
    created_at: datetime
    model_config = {"from_attributes": True}
