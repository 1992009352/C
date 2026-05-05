from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ContactGroupCreate(BaseModel):
    name: str
    icon: Optional[str] = ""
    sort_order: Optional[int] = 0


class ContactGroupOut(BaseModel):
    id: int
    name: str
    icon: str
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    group_id: Optional[int] = None
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    company: Optional[str] = ""
    position: Optional[str] = ""
    address: Optional[str] = ""
    birthday: Optional[date] = None
    remark: Optional[str] = ""


class ContactUpdate(BaseModel):
    group_id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None
    remark: Optional[str] = None


class ContactOut(BaseModel):
    id: int
    group_id: Optional[int]
    name: str
    phone: str
    email: str
    company: str
    position: str
    address: str
    birthday: Optional[date]
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
