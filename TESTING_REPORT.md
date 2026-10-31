# BlogSphere Testing Report

## Method

Pytest tests exercise Flask's test client against a per-test temporary SQLite database. CSRF is disabled only in the test configuration; production and development use Flask-WTF CSRF protection.

## Coverage

The suite includes checks for:

- Health check, homepage, and custom 404.
- Registration, normalized email, password hashing, duplicate accounts, login/logout, protected dashboard, and safe `next` redirects.
- Article create/edit/delete, author ownership, hidden drafts, search, category/tag combinations, pagination, and rich-text sanitization.
- Valid/invalid inline image uploads, safe embedded-image filtering, and dashboard reader activity.
- Comment creation/deletion and comment ownership.
- Admin-only pages, taxonomy creation/removal, and protected member deletion.
- Unlimited article revisions and restore authorization.
- Scheduled publishing with local timezones, invalid timezone rejection, idempotency, and publication notifications.
- Like/bookmark toggling, daily unique view deduplication, and reading-list visibility.
- Bounded comment replies, reports, in-app notifications, and admin report review.
- Sitemap, RSS, robots, and public/private content visibility.

## Execution and actual results

Run from the repository root:

```powershell
python -m pytest -q
```

**Latest execution:** 32 passed in 7.00 seconds (`python -m pytest -q`) on 2026-10-31. The run completed without warnings.

Both the initial and feature SQLite migrations applied to a fresh temporary database; `flask --app run.py db check` reported no new upgrade operations. `.gitignore` checks confirmed that local environment variants, secret directories, and common private-key files are ignored while `.env.example` remains trackable.

## Limitations

The tests use SQLite and do not replace a PostgreSQL integration test. Docker Compose validation/image build could not be run because the Docker CLI is unavailable in this environment. Uploaded-image handling, external CDN behavior, and a live production deployment require separate environment-level checks.
