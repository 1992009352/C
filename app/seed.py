from __future__ import annotations

import json
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JournalEntry


def seed_demo_data(db: Session) -> None:
    existing = db.scalar(select(JournalEntry.id).limit(1))
    if existing is not None:
        return

    today = date.today()
    demo_entries = [
        JournalEntry(module_key='task', title='Plan weekly priorities', status='done', metric_value=90, unit='points', occurred_on=today - timedelta(days=1), tags='planning,focus', notes='Closed all top priorities before evening.'),
        JournalEntry(module_key='task', title='Call family', status='planned', metric_value=40, unit='points', occurred_on=today, tags='family', notes='Schedule after dinner.'),
        JournalEntry(module_key='note', title='Idea: simplify morning routine', status='active', metric_value=75, unit='points', occurred_on=today - timedelta(days=3), tags='reflection', notes='Move charging station away from the bed.'),
        JournalEntry(module_key='contact', title='Alex Chen', status='active', metric_value=88, unit='points', occurred_on=today - timedelta(days=6), tags='friend,mentor', notes='Discussed career direction.', payload=json.dumps({'email': 'alex@example.com', 'phone': '+1-555-0100'})),
        JournalEntry(module_key='expense', title='Groceries', status='logged', metric_value=12, unit='items', amount=64.5, occurred_on=today - timedelta(days=2), tags='food,home', notes='Stocked vegetables and protein.'),
        JournalEntry(module_key='subscription', title='Gym membership', status='active', metric_value=30, unit='days', amount=49.0, occurred_on=today - timedelta(days=12), tags='fitness', notes='Monthly renewal.', payload=json.dumps({'renewal_day': 15})),
        JournalEntry(module_key='workout', title='Strength session', status='done', metric_value=50, unit='minutes', amount=420, occurred_on=today - timedelta(days=1), tags='legs,push', notes='Good energy throughout session.'),
        JournalEntry(module_key='workout', title='Morning walk', status='done', metric_value=35, unit='minutes', amount=180, occurred_on=today - timedelta(days=4), tags='recovery', notes='Light pace.'),
        JournalEntry(module_key='meal', title='Homemade lunch bowl', status='logged', metric_value=82, unit='points', amount=11.8, occurred_on=today - timedelta(days=1), tags='protein,fiber', notes='Balanced meal with grains and greens.'),
        JournalEntry(module_key='reading', title='Systems thinking chapter', status='done', metric_value=42, unit='pages', amount=0, occurred_on=today - timedelta(days=5), tags='learning,book', notes='Highlighted three passages.'),
        JournalEntry(module_key='health', title='Sleep quality', status='logged', metric_value=84, unit='points', amount=0, occurred_on=today - timedelta(days=1), tags='sleep,recovery', notes='7.5 hours, stable wake-up time.'),
        JournalEntry(module_key='life_event', title='Weekend mountain trip', status='recorded', metric_value=93, unit='points', amount=120.0, occurred_on=today - timedelta(days=14), tags='travel,memory', notes='Excellent reset before the new month.'),
    ]
    db.add_all(demo_entries)
    db.commit()
