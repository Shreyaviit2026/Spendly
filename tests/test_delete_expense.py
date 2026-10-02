import pytest
from app import app
from database.db import get_db, delete_expense, get_expense_by_id
import sqlite3
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_conn():
    conn = get_db()
    yield conn
    conn.close()

@pytest.fixture
def setup_data(db_conn):
    # Clear tables to ensure a clean state for each test
    db_conn.execute("DELETE FROM expenses")
    db_conn.execute("DELETE FROM users")
    db_conn.commit()

    # Create users
    cursor = db_conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ("User One", "user1@example.com", "hash1"))
    u1_id = cursor.lastrowid
    cursor = db_conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ("User Two", "user2@example.com", "hash2"))
    u2_id = cursor.lastrowid

    # Create expenses
    cursor = db_conn.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                           (u1_id, 100.0, "Food", "Lunch", "2026-10-01"))
    e1_id = cursor.lastrowid
    cursor = db_conn.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                           (u2_id, 200.0, "Travel", "Bus", "2026-10-01"))
    e2_id = cursor.lastrowid

    db_conn.commit()
    return {"u1_id": u1_id, "u2_id": u2_id, "e1_id": e1_id, "e2_id": e2_id}

# --- Unit Tests ---

def test_delete_expense_success(db_conn, setup_data):
    # Delete own expense
    delete_expense(setup_data["e1_id"], setup_data["u1_id"])

    row = db_conn.execute("SELECT * FROM expenses WHERE id = ?", (setup_data["e1_id"],)).fetchone()
    assert row is None

def test_delete_expense_wrong_user(db_conn, setup_data):
    # Try to delete another user's expense
    delete_expense(setup_data["e1_id"], setup_data["u2_id"])

    row = db_conn.execute("SELECT * FROM expenses WHERE id = ?", (setup_data["e1_id"],)).fetchone()
    assert row is not None

def test_delete_expense_non_existent(db_conn):
    # Delete non-existent expense
    delete_expense(9999, 1)
    # Should not raise error

# --- Route Tests ---

def test_delete_route_unauthenticated(client, setup_data):
    # POST /expenses/<id>/delete without login
    response = client.post(f"/expenses/{setup_data['e1_id']}/delete")
    assert response.status_code == 302
    assert "/login" in response.location

def test_delete_route_authenticated_own(client, setup_data):
    # Login as User One
    with client.session_transaction() as sess:
        sess["user_id"] = setup_data["u1_id"]

    response = client.post(f"/expenses/{setup_data['e1_id']}/delete")
    assert response.status_code == 302
    assert "/profile" in response.location

    # Verify deletion in DB
    conn = get_db()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (setup_data["e1_id"],)).fetchone()
    conn.close()
    assert row is None

def test_delete_route_authenticated_other(client, setup_data):
    # Login as User Two
    with client.session_transaction() as sess:
        sess["user_id"] = setup_data["u2_id"]

    # Try to delete User One's expense
    response = client.post(f"/expenses/{setup_data['e1_id']}/delete")
    assert response.status_code == 404

    # Verify expense still exists
    conn = get_db()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (setup_data["e1_id"],)).fetchone()
    conn.close()
    assert row is not None

def test_delete_route_non_existent(client, setup_data):
    # Login as User One
    with client.session_transaction() as sess:
        sess["user_id"] = setup_data["u1_id"]

    response = client.post(f"/expenses/9999/delete")
    assert response.status_code == 404

def test_delete_route_method_not_allowed(client, setup_data):
    # GET /expenses/<id>/delete should return 405
    response = client.get(f"/expenses/{setup_data['e1_id']}/delete")
    assert response.status_code == 405
