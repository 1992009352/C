from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_dashboard_and_entry_creation(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    app = create_app(database_url=database_url, seed_demo=True)

    with TestClient(app) as client:
        dashboard_response = client.get('/api/dashboard')
        assert dashboard_response.status_code == 200
        dashboard_payload = dashboard_response.json()
        assert dashboard_payload['total_modules'] == 10
        assert dashboard_payload['total_entries'] >= 10
        assert len(dashboard_payload['score_breakdown']) == 5

        create_response = client.post(
            '/api/modules/workout/entries',
            json={
                'title': 'Tempo run',
                'status': 'done',
                'metric_value': 28,
                'amount': 320,
                'unit': 'minutes',
                'occurred_on': '2026-05-05',
                'tags': 'cardio,tempo',
                'notes': 'Steady pace throughout the run.',
                'payload': {},
            },
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created['module_key'] == 'workout'
        assert created['title'] == 'Tempo run'

        entries_response = client.get('/api/modules/workout/entries')
        assert entries_response.status_code == 200
        titles = [entry['title'] for entry in entries_response.json()]
        assert 'Tempo run' in titles


def test_homepage_renders(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'homepage.db').as_posix()}"
    app = create_app(database_url=database_url, seed_demo=True)

    with TestClient(app) as client:
        response = client.get('/')
        assert response.status_code == 200
        assert 'Life Weave OS' in response.text
        assert 'Life balance index' in response.text
