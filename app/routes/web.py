from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain import MODULES, get_module
from app.schemas import EntryCreate
from app.services import build_dashboard, create_entry, list_entries

templates = Jinja2Templates(directory='app/templates')
router = APIRouter(tags=['web'])


@router.get('/', response_class=HTMLResponse)
def home(request: Request, selected_module: str = 'task', db: Session = Depends(get_db)) -> HTMLResponse:
    dashboard = build_dashboard(db)
    module_entries = list_entries(db, selected_module, limit=8)
    return templates.TemplateResponse(
        request,
        'dashboard.html',
        {
            'dashboard': dashboard,
            'modules': [module.to_dict() for module in MODULES],
            'module_entries': module_entries,
            'selected_module': selected_module,
            'selected_module_meta': get_module(selected_module).to_dict(),
            'today': date.today().isoformat(),
        },
    )


@router.post('/entries')
def create_entry_from_form(
    module_key: str = Form(...),
    title: str = Form(...),
    status: str = Form('active'),
    metric_value: str = Form(''),
    amount: str = Form(''),
    unit: str = Form(''),
    occurred_on: date = Form(...),
    tags: str = Form(''),
    notes: str = Form(''),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    module = get_module(module_key)
    payload = EntryCreate(
        title=title,
        status=status or module.default_status,
        metric_value=float(metric_value) if metric_value else None,
        amount=float(amount) if amount else None,
        unit=unit or module.default_unit,
        occurred_on=occurred_on,
        tags=tags,
        notes=notes,
        payload={},
    )
    create_entry(db, module_key, payload)
    return RedirectResponse(url=f'/?selected_module={module_key}', status_code=303)
