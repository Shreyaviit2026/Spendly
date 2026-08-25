# Spec: Profile Page

## Overview

The Profile Page allows logged-in users to view their basic account information, such as their full name and email address. This feature provides a dedicated space for user identity and serves as a foundation for future profile management features (e.g., updating details or changing passwords).

## Depends on

- Step 03: Login and Logout

## Routes

- `GET /profile` — Displays the current user's account details — logged-in

## Database changes

No new tables or columns. 
However, a helper function `get_user_by_id(user_id)` must be implemented in `database/db.py` to retrieve the user record using the session's `user_id`.

## Templates

- **Create:** `templates/profile.html` (extends `base.html`)

## Files to change

- `app.py`: Implement the `/profile` route logic to fetch user data and render the template.
- `database/db.py`: Add `get_user_by_id(user_id)` function.

## Files to create

- `templates/profile.html`

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done

- [ ] Logged-in users can access `/profile` and see their correct name and email.
- [ ] Unauthenticated users attempting to access `/profile` are redirected to the login page with a flash message.
- [ ] The profile page extends `base.html` and maintains consistent styling with the rest of the app.
- [ ] `get_user_by_id` is implemented in `database/db.py` and used by the `/profile` route.
