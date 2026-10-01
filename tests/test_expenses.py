import pytest
import sqlite3
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """A test client that is already logged in."""
    with app.app_context():
        from database.db import create_user, get_user_by_email
        email = 'test@example.com'
        user = get_user_by_email(email)

        if user:
            user_id = user['id']
        else:
            user_id = create_user('Test User', email, 'hashed_password')

        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    return client

class TestAddExpense:

    # --- Access Control ---

    def test_add_expense_page_redirects_to_login_when_unauthenticated(self, client):
        response = client.get('/expenses/add', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_add_expense_post_redirects_to_login_when_unauthenticated(self, client):
        response = client.post('/expenses/add', data={'amount': '10', 'category': 'Food', 'date': '2026-10-01'}, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    # --- Happy Path ---

    def test_add_expense_success(self, auth_client, app):
        payload = {
            'amount': '150.50',
            'category': 'Food',
            'date': '2026-10-01',
            'description': 'Lunch at cafe'
        }
        response = auth_client.post('/expenses/add', data=payload, follow_redirects=True)

        # Check redirection to expenses page and success message
        assert response.status_code == 200
        assert b'Expense added successfully!' in response.data

        # Verify DB persistence
        with app.app_context():
            db = get_db()
            row = db.execute(
                "SELECT * FROM expenses WHERE amount = ? AND category = ? AND date = ?",
                (150.50, 'Food', '2026-10-01')
            ).fetchone()
            assert row is not None
            assert row['description'] == 'Lunch at cafe'

    # --- Validation Errors ---

    @pytest.mark.parametrize("missing_field", [
        {'amount': ''},
        {'category': ''},
        {'date': ''},
    ])
    def test_add_expense_missing_fields(self, auth_client, missing_field):
        # Start with valid data and overwrite the missing field
        payload = {
            'amount': '100',
            'category': 'Travel',
            'date': '2026-10-01',
            'description': 'Bus'
        }
        payload.update(missing_field)

        response = auth_client.post('/expenses/add', data=payload)
        assert response.status_code == 200
        assert b'Amount, category, and date are required.' in response.data

    @pytest.mark.parametrize("invalid_amount", [
        '0',
        '-10',
        '-0.01'
    ])
    def test_add_expense_invalid_amount_value(self, auth_client, invalid_amount):
        payload = {
            'amount': invalid_amount,
            'category': 'Food',
            'date': '2026-10-01',
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload)
        assert response.status_code == 200
        assert b'Please enter a valid positive amount.' in response.data

    def test_add_expense_invalid_amount_format(self, auth_client):
        payload = {
            'amount': 'abc',
            'category': 'Food',
            'date': '2026-10-01',
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload)
        assert response.status_code == 200
        assert b'Please enter a valid positive amount.' in response.data

    # --- Edge Cases ---

    def test_add_expense_long_description(self, auth_client, app):
        long_desc = "A" * 1000
        payload = {
            'amount': '10',
            'category': 'Other',
            'date': '2026-10-01',
            'description': long_desc
        }
        auth_client.post('/expenses/add', data=payload, follow_redirects=True)

        with app.app_context():
            db = get_db()
            row = db.execute("SELECT description FROM expenses WHERE amount = 10").fetchone()
            assert row['description'] == long_desc
