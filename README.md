# 💰 Spendly - Personal Expense Tracker

**Live Demo:** [https://expense-tracker-production-7266.up.railway.app](https://expense-tracker-production-7266.up.railway.app)

Spendly is a lightweight, secure, and intuitive personal expense tracker designed to help users manage their finances with ease. Built using **Flask**, **SQLite**, and **Vanilla JavaScript**, it provides a seamless experience for logging expenses, tracking spending habits, and analyzing financial data through a clean, modern interface.

## 🚀 Features

- **User Authentication**: Secure registration and login system with password hashing.
- **Expense Management**: 
  - Log new expenses with category, amount, and date.
  - Edit and delete existing expenses with ownership enforcement.
- **Financial Analytics**:
  - **Profile Dashboard**: View total spending and monthly summaries.
  - **Category Breakdown**: Analyze spending patterns via categorical data.
  - **Date Filtering**: Filter expenses and analytics by custom date ranges or presets (This Month, Last 3 Months, Last 6 Months, All Time).
- **Responsive Design**: A fully responsive UI that works across desktop and mobile devices.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ / Flask
- **Database**: SQLite (Relational database for lightweight, local storage)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (No heavy frameworks)
- **Deployment**: Railway

## 📁 Project Structure

```text
spendly/
├── app.py              # Main application logic and route definitions
├── database/
│   └── db.py           # SQLite database helpers and connection logic
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Shared layout for all pages
│   └── *.html          # Page-specific templates
├── static/             # Static assets
│   ├── css/            # Global and page-specific styles
│   └── js/             # Vanilla JS for frontend interactivity
└── requirements.txt    # Project dependencies
```

## ⚙️ Local Setup

### Prerequisites
- Python 3.10 or higher installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/expense-tracker.git
   cd expense-tracker
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5001`.

## 🧪 Testing

The project uses `pytest` for ensuring reliability.

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_auth.py

# Run tests with output visible
pytest -s
```

## 🌐 Deployment

This project is optimized for deployment on **Railway**. 

1. Connect your GitHub repository to Railway.
2. Railway automatically detects the Flask app via `requirements.txt` and `app.py`.
3. Ensure the `PORT` environment variable is handled (the app defaults to `5001` locally but adapts to Railway's assigned port in production).

---
Developed with ❤️ for better financial clarity.
