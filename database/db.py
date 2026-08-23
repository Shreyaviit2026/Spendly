import sqlite3
import os

DATABASE = "spendly.db"

def get_db():
    """
    Establishes a connection to the SQLite database.
    Enforces foreign keys and sets the row factory to sqlite3.Row.
    """
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating the users and expenses tables.
    Sets journal_mode to WAL for better concurrency.
    """
    with get_db() as conn:
        conn.execute("PRAGMA journal_mode=WAL")

        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def seed_db():
    """
    Seeds the database with sample data for development and testing.
    """
    with get_db() as conn:
        # Seed users - Using INSERT OR IGNORE to avoid duplicates on email
        users = [
            ("Nitish Kumar", "nitish@example.com", "hashed_password_123"),
            ("Jane Doe", "jane@example.com", "hashed_password_456"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)",
            users
        )

        # Get user IDs for seeding expenses
        user_ids = [row['id'] for row in conn.execute("SELECT id FROM users").fetchall()]

        if not user_ids:
            return

        # Seed expenses for the first user
        expenses = [
            (user_ids[0], 450.0, "Food", "Grocery shopping", "2026-08-20"),
            (user_ids[0], 1200.0, "Travel", "Fuel for car", "2026-08-21"),
            (user_ids[0], 3000.0, "Bills", "Electricity bill", "2026-08-22"),
            (user_ids[0], 150.0, "Food", "Dinner out", "2026-08-23"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
