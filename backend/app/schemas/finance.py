from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class BudgetCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = ""
    color: Optional[str] = "#409EFF"
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0


class BudgetCategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    parent_id: Optional[int]
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    category_id: Optional[int] = None
    type: str = "expense"
    amount: float
    description: Optional[str] = ""
    remark: Optional[str] = ""
    account: Optional[str] = ""
    tags: Optional[str] = ""
    occur_date: date


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    remark: Optional[str] = None
    account: Optional[str] = None
    tags: Optional[str] = None
    occur_date: Optional[date] = None


class TransactionOut(BaseModel):
    id: int
    category_id: Optional[int]
    type: str
    amount: float
    description: str
    remark: str
    account: str
    tags: str
    occur_date: date
    created_at: datetime
    model_config = {"from_attributes": True}


class BudgetCreate(BaseModel):
    category_id: int
    name: str
    amount: float
    period: Optional[str] = "monthly"
    start_date: date
    end_date: date


class BudgetOut(BaseModel):
    id: int
    category_id: int
    name: str
    amount: float
    period: str
    start_date: date
    end_date: date
    created_at: datetime
    model_config = {"from_attributes": True}
