from flask import Flask, render_template, g, request, redirect, url_for, flash, session, jsonify
from database.db import get_db, create_user, get_user_by_email, get_user_by_id, get_spending_summary, get_expenses_by_user, get_category_breakdown
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "dev-secret-key-spendly-2026"


def get_db_conn():
    if 'db' not in g:
        g.db = get_db()
    return g.db


@app.teardown_appcontext
def teardown_db(_exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation
        if not all([name, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "error")
            return render_template("register.html")

        try:
            hashed_password = generate_password_hash(password)
            create_user(name, email, hashed_password)
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")

        user = get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            session["user_id"] = user['id']
            flash("Welcome back!", "success")
            return redirect(url_for("landing"))

        flash("Invalid email or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/expenses")
@login_required
def expenses():
    user_id = session.get("user_id")
    expenses = get_expenses_by_user(user_id)
    return render_template("expenses.html", expenses=expenses)

@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")

@app.route("/analytics/recent")
@login_required
def analytics_recent():
    user_id = session.get("user_id")
    expenses = get_expenses_by_user(user_id)
    # Limit to top 5 for the "Recent Transactions" view
    return jsonify([dict(row) for row in expenses[:5]])

@app.route("/analytics/summary")
@login_required
def analytics_summary():
    user_id = session.get("user_id")
    summary = get_spending_summary(user_id)
    return jsonify({
        "total_all": summary['total_all'] if summary and summary['total_all'] else 0.0,
        "total_month": summary['total_month'] if summary and summary['total_month'] else 0.0
    })

@app.route("/analytics/categories")
@login_required
def analytics_categories():
    user_id = session.get("user_id")
    breakdown = get_category_breakdown(user_id)
    return jsonify([dict(row) for row in breakdown])


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)

    if not user:
        flash("User profile not found.", "error")
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(_id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(_id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
