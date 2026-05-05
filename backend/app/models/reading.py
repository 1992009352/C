from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, Integer, Text, ForeignKey, Enum as SAEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class BookStatus(str, enum.Enum):
    WISH = "wish"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100), default="")
    isbn: Mapped[str] = mapped_column(String(20), default="")
    cover_url: Mapped[str] = mapped_column(String(500), default="")
    category: Mapped[str] = mapped_column(String(50), default="")
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    current_page: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(SAEnum(BookStatus), default=BookStatus.WISH)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    review: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    finish_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ReadingRecord(Base):
    __tablename__ = "reading_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), index=True)
    read_date: Mapped[date] = mapped_column(Date, index=True)
    pages_read: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
