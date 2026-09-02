import sqlite3

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

def create_user(name, email, password):
    """
    Creates a new user in the database.
    Password should be hashed before being passed to this function.
    Returns the ID of the created user.
    """
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        return cursor.lastrowid

def get_user_by_email(email):
    """
    Retrieves a user record by their email address.
    Returns a sqlite3.Row object if found, otherwise None.
    """
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

def get_user_by_id(user_id):
    """
    Retrieves a user record by their user ID.
    Returns a sqlite3.Row object if found, otherwise None.
    """
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

def get_category_breakdown(user_id, date_from=None, date_to=None):
    """
    Retrieves the total spending per category for a given user, optionally filtered by date.
    Returns a list of sqlite3.Row objects.
    """
    with get_db() as conn:
        sql = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
        params = [user_id]
        if date_from and date_to:
            sql += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])
        sql += " GROUP BY category ORDER BY total DESC"
        return conn.execute(sql, params).fetchall()


def get_total_spending(user_id):
    """
    Retrieves the total spending for a given user.
    Returns the total amount as a float.
    """
    with get_db() as conn:
        result = conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return result['total'] if result and result['total'] else 0.0

def get_spending_summary(user_id, date_from=None, date_to=None):
    """
    Retrieves the total spending and spending for the current month for a user, optionally filtered by date.
    Returns a sqlite3.Row object.
    """
    with get_db() as conn:
        sql = "SELECT SUM(amount) as total_all, SUM(CASE WHEN date >= date('now', 'start of month') THEN amount ELSE 0 END) as total_month FROM expenses WHERE user_id = ?"
        params = [user_id]
        if date_from and date_to:
            sql += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])
        return conn.execute(sql, params).fetchone()


def get_expenses_by_user(user_id, date_from=None, date_to=None):
    """
    Retrieves all expenses for a given user, optionally filtered by date, ordered by date descending.
    Returns a list of sqlite3.Row objects.
    """
    with get_db() as conn:
        sql = "SELECT * FROM expenses WHERE user_id = ? "
        params = [user_id]
        if date_from and date_to:
            sql += "AND date BETWEEN ? AND ? "
            params.extend([date_from, date_to])
        sql += "ORDER BY date DESC"
        return conn.execute(sql, params).fetchall()

