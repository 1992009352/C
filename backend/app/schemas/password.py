from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PasswordGroupCreate(BaseModel):
    name: str
    icon: Optional[str] = ""
    sort_order: Optional[int] = 0


class PasswordGroupOut(BaseModel):
    id: int
    name: str
    icon: str
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class PasswordEntryCreate(BaseModel):
    group_id: Optional[int] = None
    title: str
    url: Optional[str] = ""
    username: Optional[str] = ""
    password: Optional[str] = ""
    remark: Optional[str] = ""


class PasswordEntryUpdate(BaseModel):
    group_id: Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    remark: Optional[str] = None


class PasswordEntryOut(BaseModel):
    id: int
    group_id: Optional[int]
    title: str
    url: str
    username: str
    password: str
    remark: str
    created_at: datetime
    model_config = {"from_attributes": True}
