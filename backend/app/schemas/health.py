from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class HealthRecordCreate(BaseModel):
    record_date: date
    weight: Optional[float] = None
    height: Optional[float] = None
    blood_pressure_sys: Optional[int] = None
    blood_pressure_dia: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_sugar: Optional[float] = None
    body_fat: Optional[float] = None
    mood: Optional[int] = None
    remark: Optional[str] = ""


class HealthRecordOut(BaseModel):
    id: int
    record_date: date
    weight: Optional[float]
    height: Optional[float]
    blood_pressure_sys: Optional[int]
    blood_pressure_dia: Optional[int]
    heart_rate: Optional[int]
    blood_sugar: Optional[float]
    body_fat: Optional[float]
    mood: Optional[int]
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ExerciseCreate(BaseModel):
    exercise_type: str = "running"
    exercise_date: date
    duration: int = 0
    distance: Optional[float] = None
    calories: Optional[int] = None
    heart_rate_avg: Optional[int] = None
    location: Optional[str] = ""
    remark: Optional[str] = ""


class ExerciseOut(BaseModel):
    id: int
    exercise_type: str
    exercise_date: date
    duration: int
    distance: Optional[float]
    calories: Optional[int]
    heart_rate_avg: Optional[int]
    location: str
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}


class SleepRecordCreate(BaseModel):
    sleep_date: date
    bed_time: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    duration: int = 0
    quality: int = 3
    remark: Optional[str] = ""


class SleepRecordOut(BaseModel):
    id: int
    sleep_date: date
    bed_time: Optional[datetime]
    wake_time: Optional[datetime]
    duration: int
    quality: int
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
