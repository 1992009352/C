from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = ""
    color: Optional[str] = "#67C23A"
    frequency: Optional[str] = "daily"
    target_count: Optional[int] = 1
    unit: Optional[str] = "次"
    start_date: date
    end_date: Optional[date] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    frequency: Optional[str] = None
    target_count: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    end_date: Optional[date] = None


class HabitOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    color: str
    frequency: str
    target_count: int
    unit: str
    is_active: bool
    start_date: date
    end_date: Optional[date]
    created_at: datetime
    model_config = {"from_attributes": True}


class HabitRecordCreate(BaseModel):
    habit_id: int
    record_date: date
    count: Optional[int] = 1
    remark: Optional[str] = ""


class HabitRecordOut(BaseModel):
    id: int
    habit_id: int
    record_date: date
    count: int
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
