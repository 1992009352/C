from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class LifeExperienceCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    experience_type: Optional[str] = "event"
    experience_date: date
    location: Optional[str] = ""
    cost: Optional[float] = None
    rating: Optional[float] = None
    photos: Optional[str] = ""
    tags: Optional[str] = ""


class LifeExperienceUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    experience_type: Optional[str] = None
    experience_date: Optional[date] = None
    location: Optional[str] = None
    cost: Optional[float] = None
    rating: Optional[float] = None
    photos: Optional[str] = None
    tags: Optional[str] = None


class LifeExperienceOut(BaseModel):
    id: int
    title: str
    content: str
    experience_type: str
    experience_date: date
    location: str
    cost: Optional[float]
    rating: Optional[float]
    photos: str
    tags: str
    created_at: datetime
    model_config = {"from_attributes": True}
