import pytest
from app import app
from database.db import get_db, init_db
import sqlite3

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    with app.test_client() as client:
        with app.app_context():
            # Use a separate test database if possible, but for now let's use the existing one
            # or create a temporary one.
            # For simplicity in this env, we'll use the default and just clean up.
            init_db()
            with get_db() as conn:
                conn.execute("DELETE FROM users")
                conn.commit()
        yield client

def test_register_success(client):
    # Use a unique email to avoid IntegrityError
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    # Verify in DB
    with app.app_context():
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", ("testuser@example.com",)).fetchone()
        assert user is not None
        assert user['name'] == "Test User"
        assert user['password'] != "password123" # Should be hashed

def test_register_password_mismatch(client):
    data = {
        "name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "password123",
        "confirm_password": "different_password"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_register_duplicate_email(client):
    # First registration
    data1 = {
        "name": "User 1",
        "email": "dup@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    client.post("/register", data=data1)

    # Second registration with same email
    data2 = {
        "name": "User 2",
        "email": "dup@example.com",
        "password": "password456",
        "confirm_password": "password456"
    }
    response = client.post("/register", data=data2)
    assert response.status_code == 200
    assert b"Email already registered" in response.data

def test_register_empty_fields(client):
    data = {
        "name": "",
        "email": "empty@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 200
    assert b"All fields are required" in response.data
