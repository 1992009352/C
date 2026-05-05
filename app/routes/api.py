from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain import MODULES
from app.schemas import DashboardRead, EntryCreate, EntryRead
from app.services import build_dashboard, create_entry, list_entries

router = APIRouter(prefix='/api', tags=['api'])


@router.get('/modules')
def get_modules() -> list[dict[str, str]]:
    return [module.to_dict() for module in MODULES]


@router.get('/dashboard', response_model=DashboardRead)
def dashboard(db: Session = Depends(get_db)) -> DashboardRead:
    return build_dashboard(db)


@router.get('/modules/{module_key}/entries', response_model=list[EntryRead])
def module_entries(module_key: str, db: Session = Depends(get_db)) -> list[EntryRead]:
    try:
        return list_entries(db, module_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post('/modules/{module_key}/entries', response_model=EntryRead, status_code=201)
def create_module_entry(module_key: str, payload: EntryCreate, db: Session = Depends(get_db)) -> EntryRead:
    try:
        return create_entry(db, module_key, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
