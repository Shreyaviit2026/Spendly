import pytest
from app import app
from database.db import init_db, create_user
from werkzeug.security import generate_password_hash
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        with app.app_context():
            # Completely reset the database for each test
            from database.db import get_db
            db = get_db()
            db.execute("DELETE FROM expenses")
            db.execute("DELETE FROM users")
            db.commit()
        yield client

def test_login_success(client):
    # Setup: create a user
    email = "test@example.com"
    password = "password123"
    hashed = generate_password_hash(password)
    create_user("Test User", email, hashed)

    # Act: login
    response = client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert b"Welcome back!" in response.data
    # Verify session
    with client.session_transaction() as sess:
        assert "user_id" in sess

def test_login_wrong_password(client):
    email = "test@example.com"
    password = "password123"
    hashed = generate_password_hash(password)
    create_user("Test User", email, hashed)

    response = client.post('/login', data={
        'email': email,
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b"Invalid email or password." in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess

def test_login_invalid_email(client):
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert b"Invalid email or password." in response.data

def test_logout(client):
    # Setup: login first
    email = "test@example.com"
    password = "password123"
    hashed = generate_password_hash(password)
    create_user("Test User", email, hashed)

    client.post('/login', data={'email': email, 'password': password})

    # Act: logout
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been signed out." in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess

def test_profile_protected(client):
    # Act: access profile without login
    response = client.get('/profile', follow_redirects=True)

    assert b"Please log in to access this page." in response.data
    assert b"Sign in" in response.data # Should be on login page

def test_login_redirect_if_authenticated(client):
    # Setup: login first
    email = "test@example.com"
    password = "password123"
    hashed = generate_password_hash(password)
    create_user("Test User", email, hashed)
    client.post('/login', data={'email': email, 'password': password})

    # Act: try to access login page
    response = client.get('/login', follow_redirects=True)

    # Assert: should be redirected to landing
    assert response.request.path == '/'
    # Or just check if we are on the landing page
    assert b"Know where your" in response.data # text from landing.html

def test_register_redirect_if_authenticated(client):
    # Setup: login first
    email = "test@example.com"
    password = "password123"
    hashed = generate_password_hash(password)
    create_user("Test User", email, hashed)
    client.post('/login', data={'email': email, 'password': password})

    # Act: try to access register page
    response = client.get('/register', follow_redirects=True)

    # Assert: should be redirected to landing
    assert response.request.path == '/'
    assert b"Know where your" in response.data

