from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class FoodItemCreate(BaseModel):
    name: str
    calories_per_100g: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None


class FoodItemOut(BaseModel):
    id: int
    name: str
    calories_per_100g: Optional[float]
    protein: Optional[float]
    fat: Optional[float]
    carbs: Optional[float]
    created_at: datetime
    model_config = {"from_attributes": True}


class DietRecordCreate(BaseModel):
    food_id: Optional[int] = None
    meal_type: str = "lunch"
    food_name: str
    amount: float = 0
    unit: Optional[str] = "g"
    calories: Optional[float] = None
    diet_date: date
    remark: Optional[str] = ""


class DietRecordOut(BaseModel):
    id: int
    food_id: Optional[int]
    meal_type: str
    food_name: str
    amount: float
    unit: str
    calories: Optional[float]
    diet_date: date
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
