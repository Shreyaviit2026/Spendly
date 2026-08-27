# Spec: Backend Routes for Profile Page

## Overview

While the basic profile view is implemented, users currently have no way to manage their account details. This feature implements the backend routes and database logic required to allow users to update their profile information (name and email) and securely change their account password.

## Depends on

- Step 04: Profile Page

## Routes

- `POST /profile/update` — Updates the user's name and email — logged-in
- `POST /profile/password` — Updates the user's password — logged-in

## Database changes

No new tables or columns. The following helper functions must be implemented in `database/db.py`:

- `update_user(user_id, name, email)`: Updates the user's name and email in the `users` table.
- `update_user_password(user_id, password)`: Updates the user's hashed password in the `users` table.

## Templates

- **Modify:** `templates/profile.html` — Add forms for updating user details and changing the password.

## Files to change

- `app.py`: Implement the `/profile/update` and `/profile/password` routes.
- `database/db.py`: Add `update_user` and `update_user_password` helper functions.
- `templates/profile.html`: Add the necessary HTML forms and flash message integration.

## Files to create

No new files.

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done

- [ ] Logged-in users can update their name and email via the profile page, and the changes are persisted in the database.
- [ ] Logged-in users can change their password; the new password must be hashed and stored correctly.
- [ ] Validation is implemented for email format and password matching (confirm password).
- [ ] Appropriate flash messages (success/error) are displayed after update attempts.
- [ ] Authenticated session is maintained after updates, and unauthorized access to these routes is blocked by `@login_required`.
