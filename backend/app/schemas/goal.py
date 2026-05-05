from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    target_value: float = 100
    current_value: float = 0
    unit: Optional[str] = "%"
    start_date: date
    end_date: Optional[date] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    end_date: Optional[date] = None


class GoalOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    target_value: float
    current_value: float
    unit: str
    start_date: date
    end_date: Optional[date]
    completed_at: Optional[datetime]
    created_at: datetime
    model_config = {"from_attributes": True}


class GoalProgressCreate(BaseModel):
    goal_id: int
    record_date: date
    value: float
    remark: Optional[str] = ""


class GoalProgressOut(BaseModel):
    id: int
    goal_id: int
    record_date: date
    value: float
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
