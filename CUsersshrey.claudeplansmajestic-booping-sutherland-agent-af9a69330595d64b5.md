# Implementation Plan: Date Filter for Spendly Profile Page

This plan describes the implementation of a date range filter for the user profile dashboard, allowing users to view their spending summary, category breakdown, and recent transactions for specific time periods.

## 1. Database Layer Changes (`database/db.py`)

All three helper functions will be updated to accept optional `date_from` and `date_to` parameters.

### `get_spending_summary(user_id, date_from=None, date_to=None)`
- **Modification**: Update the SQL query to include a `BETWEEN` clause for the date if both parameters are provided.
- **SQL**: `SELECT SUM(amount) as total_all, SUM(CASE WHEN date >= date('now', 'start of month') THEN amount ELSE 0 END) as total_month FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?`
- **Note**: The `total_month` calculation remains relative to the current calendar month, but is further restricted by the filter range.

### `get_category_breakdown(user_id, date_from=None, date_to=None)`
- **Modification**: Add the date range filter to the `WHERE` clause before the `GROUP BY`.
- **SQL**: `SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? GROUP BY category ORDER BY total DESC`

### `get_expenses_by_user(user_id, date_from=None, date_to=None)`
- **Modification**: Add the date range filter to the `WHERE` clause.
- **SQL**: `SELECT * FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC`

---

## 2. Backend Logic Changes (`app.py`)

### Route: `/profile`
- **Query Parameter Handling**: Accept `date_from`, `date_to`, and `preset`.
- **Preset Calculation**:
    - **This Month**: `date_from` = first day of current month, `date_to` = today.
    - **Last 3 Months**: `date_from` = today - 90 days, `date_to` = today.
    - **Last 6 Months**: `date_from` = today - 180 days, `date_to` = today.
    - **All Time**: Redirect to `/profile` (clean URL).
- **Validation**:
    - Use `datetime.strptime(date_str, "%Y-%m-%d")` to verify ISO format.
    - Check if `date_from > date_to`.
    - If validation fails, use `flash()` to notify the user and fallback to `None` for dates.
- **Context**: Pass the final `date_from` and `date_to` to the `profile.html` template to allow the UI to highlight the active filter.

### Routes: `/analytics/summary`, `/analytics/recent`, `/analytics/categories`
- **Modification**: Update these JSON endpoints to accept `date_from` and `date_to` query parameters.
- **Integration**: Pass these parameters directly into the corresponding `database/db.py` helper functions.

---

## 3. Frontend Implementation (`templates/profile.html`)

### Filter Bar Structure
Add a new section above the `.stats-row` containing:
- **Preset Group**: A set of links/buttons for "All Time", "This Month", "Last 3 Months", and "Last 6 Months".
- **Custom Range Form**: A small form with:
    - `<input type="date" name="date_from">`
    - `<input type="date" name="date_to">`
    - `<button type="submit">Filter</button>`

### JavaScript Updates
- Modify the `DOMContentLoaded` script to read `date_from` and `date_to` from the current URL.
- Append these values as query strings to the `fetch` requests for `/analytics/summary`, `/analytics/recent`, and `/analytics/categories`.
- Example: `fetch(\`/analytics/summary?date_from=\${df}&date_to=\${dt}\`)`

---

## 4. Styling (`static/css/profile.css`)

Create a new stylesheet `profile.css` and link it in `profile.html`.

### Key Styles
- **Filter Bar Layout**: Use `display: flex`, `justify-content: space-between`, and `align-items: center` to position presets and the custom form.
- **Preset Buttons**: 
    - Base style: Ghost buttons with subtle borders.
    - Active state: Background color change using `--primary-color` and white text.
- **Custom Form**: Inline layout for date inputs and the filter button.
- **Responsiveness**: Stack the filter bar vertically on small screens using a media query.

## Implementation Sequence

1. **Database**: Update `db.py` helper functions.
2. **Backend API**: Update `/analytics` routes in `app.py` to support date params.
3. **Backend Page**: Implement `/profile` route logic (presets, validation).
4. **Frontend HTML**: Build the filter bar in `profile.html`.
5. **Frontend JS**: Connect the filter bar to the API calls.
6. **Frontend CSS**: Create and apply `profile.css` styles.
