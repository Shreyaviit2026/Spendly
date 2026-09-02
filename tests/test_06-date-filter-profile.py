import pytest
import os
from datetime import datetime, timedelta, date
from app import app as flask_app
import database.db

@pytest.fixture
def app(tmp_path):
    """
    Configure the app for testing.
    Uses a temporary file-based SQLite DB because :memory:
    would create a new empty DB on every get_db() call.
    """
    db_file = tmp_path / "test_spendly.db"
    database.db.DATABASE = str(db_file)

    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    with flask_app.app_context():
        database.db.init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    # Use register since we are in a fresh DB
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seed_expenses(auth_client):
    """
    Seeds specific expenses for testing date filters.
    Dates are relative to today to ensure preset tests are deterministic.
    """
    with flask_app.app_context():
        # Get the first user created in auth_client
        conn = database.db.get_db()
        user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        user_id = user['id']

        today = datetime.now().date()

        expenses = [
            # Today
            (user_id, 100.0, "Food", "Today Lunch", today.strftime("%Y-%m-%d")),
            # 15 days ago (Same month)
            (user_id, 200.0, "Travel", "Taxi", (today - timedelta(days=15)).strftime("%Y-%m-%d")),
            # 45 days ago (Last 3 months, not this month)
            (user_id, 300.0, "Bills", "Internet", (today - timedelta(days=45)).strftime("%Y-%m-%d")),
            # 120 days ago (Last 6 months, not last 3)
            (user_id, 400.0, "Food", "Old Grocery", (today - timedelta(days=120)).strftime("%Y-%m-%d")),
            # 200 days ago (All time, not last 6)
            (user_id, 500.0, "Shopping", "Old Shoes", (today - timedelta(days=200)).strftime("%Y-%m-%d")),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Verify that unauthenticated requests to /profile are redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_no_filter(self, auth_client, seed_expenses):
        """Verify that /profile without params shows all expenses."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Check that summary reflects all data (100+200+300+400+500 = 1500)
        assert b'1,500.00' in response.data or b'1500.00' in response.data

    def test_analytics_custom_range_valid(self, auth_client, seed_expenses):
        """Verify a valid custom date range filters all analytics endpoints."""
        today = datetime.now().date()
        date_from = (today - timedelta(days=20)).strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")

        # 1. Summary
        resp_summary = auth_client.get(f'/analytics/summary?date_from={date_from}&date_to={date_to}')
        import json
        data = json.loads(resp_summary.data)
        assert data['total_all'] == 300.0

        # 2. Recent
        resp_recent = auth_client.get(f'/analytics/recent?date_from={date_from}&date_to={date_to}')
        recent = json.loads(resp_recent.data)
        assert len(recent) == 2

        # 3. Categories
        resp_cats = auth_client.get(f'/analytics/categories?date_from={date_from}&date_to={date_to}')
        cats = json.loads(resp_cats.data)
        categories = [row['category'] for row in cats]
        assert "Food" in categories
        assert "Travel" in categories
        assert "Bills" not in categories

    def test_profile_preset_this_month(self, auth_client, seed_expenses):
        """Verify 'this-month' preset filters correctly."""
        today = datetime.now().date()
        date_from = today.replace(day=1).strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")

        resp_summary = auth_client.get(f'/analytics/summary?date_from={date_from}&date_to={date_to}')
        import json
        assert json.loads(resp_summary.data)['total_all'] == 300.0

    def test_profile_preset_last_3_months(self, auth_client, seed_expenses):
        """Verify 'last-3-months' preset filters correctly (90 days)."""
        today = datetime.now().date()
        date_from = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")
        resp_summary = auth_client.get(f'/analytics/summary?date_from={date_from}&date_to={date_to}')
        import json
        assert json.loads(resp_summary.data)['total_all'] == 600.0

    def test_profile_preset_last_6_months(self, auth_client, seed_expenses):
        """Verify 'last-6-months' preset filters correctly (180 days)."""
        today = datetime.now().date()
        date_from = (today - timedelta(days=180)).strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")
        resp_summary = auth_client.get(f'/analytics/summary?date_from={date_from}&date_to={date_to}')
        import json
        assert json.loads(resp_summary.data)['total_all'] == 1000.0

    def test_profile_preset_all_time(self, auth_client, seed_expenses):
        """Verify 'all-time' preset redirects to clean profile URL."""
        response = auth_client.get('/profile?preset=all-time')
        assert response.status_code == 302
        assert response.location == '/profile'

    def test_profile_date_validation_start_after_end(self, auth_client, seed_expenses):
        """Verify date_from > date_to flashes error and falls back to unfiltered."""
        response = auth_client.get('/profile?date_from=2026-12-01&date_to=2026-01-01')
        assert response.status_code == 200
        assert b"Start date must be before end date." in response.data

    def test_profile_date_validation_malformed(self, auth_client, seed_expenses):
        """Verify malformed date strings fallback silently to unfiltered."""
        response = auth_client.get('/profile?date_from=invalid-date&date_to=2026-01-01')
        assert response.status_code == 200
        assert b"Start date must be before end date." not in response.data

    def test_profile_no_transactions_in_range(self, auth_client, seed_expenses):
        """Verify valid range with no data returns 0 and empty results."""
        resp_summary = auth_client.get('/analytics/summary?date_from=2020-01-01&date_to=2020-01-31')
        import json
        data = json.loads(resp_summary.data)
        assert data['total_all'] == 0.0

        resp_cats = auth_client.get('/analytics/categories?date_from=2020-01-01&date_to=2020-01-31')
        assert json.loads(resp_cats.data) == []

    def test_analytics_auth_guards(self, client):
        """Verify all analytics endpoints are protected."""
        endpoints = ['/analytics/summary', '/analytics/recent', '/analytics/categories']
        for ep in endpoints:
            response = client.get(ep)
            assert response.status_code == 302
            assert '/login' in response.location
