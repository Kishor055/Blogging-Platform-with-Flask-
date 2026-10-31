# BlogSphere

A modular Flask blogging platform for publishing articles, building a writer profile, and discovering stories by topic, tag, or search.

## What it includes

- Flask application factory, Blueprints, SQLAlchemy, and Flask-Migrate.
- User registration, password hashing, login/logout, profiles, avatar uploads, and administrator roles.
- Draft/published/scheduled article CRUD with ownership checks, a Quill editor, featured image uploads, categories, and tags.
- Responsive editorial-style Jinja templates, article pagination, search, combined category/tag filters, and reading-time metadata.
- Authenticated comments with owner/admin moderation and an author dashboard.
- Dashboard activity showing recent reader comments alongside post statistics and drafts.
- Admin tools for managing taxonomy, member roles/accounts, article visibility, and comment moderation.
- Unlimited article revisions with restore, author-timezone scheduling, and a CLI publisher for periodic jobs.
- Authenticated likes and reading-list bookmarks, bounded comment replies, report submission, and admin report review.
- In-app comment/reply/scheduled-publication notifications and author-scoped daily unique-view counts that do not retain IP addresses.
- Article metadata and structured data, canonical links, sitemap, robots policy, and RSS feed.
- Persistent light/dark theme preference and inline article images uploaded through the authenticated editor.
- Rich-text sanitization, CSRF protection, secure session-cookie settings, and a production `SECRET_KEY` requirement.
- Pytest suite, Gunicorn entry point, Dockerfile, and PostgreSQL Compose configuration.

## Requirements

- Python 3.10 or newer (the Docker image uses Python 3.13).
- pip and a virtual-environment tool.
- Docker and Docker Compose for the container setup.

## Local setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `SECRET_KEY` in `.env` to a unique random value before using the app beyond local development. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`. The development app generates an ephemeral key if none is set; sessions will not survive a restart until a stable value is configured.

The default database is SQLite under `instance/blogsphere.db`. Initialize migrations and apply them:

```powershell
$env:FLASK_APP = "run.py"
flask db init       # only once, if migrations/ does not exist
flask db migrate -m "Initial schema"
flask db upgrade
flask run
```

The repository includes its initial migration. On a fresh checkout, run `flask db upgrade` and then `flask run`.

Visit `http://127.0.0.1:5000`. The `/health` endpoint returns a simple application health response.

## Administrator account

Create an admin using the interactive CLI after the database migration:

```powershell
flask --app run.py create-admin
```

The command prompts for a username, email, and password and stores only a password hash. Do not assign the admin role through public registration.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Session and CSRF signing key; required in production. |
| `DATABASE_URL` | SQLAlchemy URL; defaults to a local SQLite database. |
| `APP_ENV` | Configuration profile: `development`, `testing`, or `production`. |
| `UPLOAD_FOLDER` | Directory for article image uploads. |
| `POSTGRES_PASSWORD` | PostgreSQL password used by Docker Compose. |

For PostgreSQL, use `postgresql+psycopg://user:password@host:5432/blogsphere`. URL-encode special characters in credentials.

## Features and routes

| Path | Purpose | Access |
| --- | --- | --- |
| `/` and `/articles` | Published stories, search, filters, and pagination | Public |
| `/article/<slug>` | Article and comments | Published articles are public |
| `/article/new` | Create article | Signed-in user |
| `/article/<slug>/edit` | Edit or schedule an article | Owner or admin |
| `/article/<slug>/delete` | Delete article | Owner or admin; POST |
| `/article/<slug>/revisions` | Review and restore article revisions | Owner or admin |
| `/article/<slug>/like`, `/article/<slug>/bookmark` | Toggle article engagement | Signed-in user; POST |
| `/bookmarks` | Saved published stories | Signed-in user |
| `/comments/<id>/reply`, `/comments/<id>/report` | Reply to or report a comment | Signed-in user; POST |
| `/notifications/` | In-app notifications | Signed-in user |
| `/category/<slug>`, `/tag/<slug>` | Browse by topic | Public |
| `/auth/register`, `/auth/login`, `/auth/logout` | Account/session management | Public / signed-in |
| `/auth/profile/<username>` | Writer profile and published work | Public |
| `/dashboard/` | Author stats and article management | Signed-in user |
| `/admin/` | User, content, and taxonomy management | Admin |
| `/sitemap.xml`, `/robots.txt`, `/feed.xml` | Search discovery and RSS | Public |
| `/health` | Health-check JSON | Public |

## Database design

`User` owns many `Post`, `Comment`, `Bookmark`, and notification records. Posts own revisions, likes, and daily view events; comments can have nested replies and reports. Like, bookmark, report, and view uniqueness constraints prevent duplicate actions. A post optionally belongs to one `Category`; posts and `Tag` records have a many-to-many association (`post_tags`). See [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md) for the ER diagram and architecture notes.

Scheduled posts store their publish instant in UTC and retain the IANA timezone used to enter the local time. Schedule publishing by invoking this command once per minute (for example with cron or a platform scheduler):

```powershell
flask --app run.py publish-scheduled
```

The command is idempotent: already-published articles are not sent twice. Daylight-saving ambiguous local times use the first occurrence; nonexistent local times are rejected. Article analytics count one pseudonymous cookie per article per UTC day. The cookie identifier is HMACed with `SECRET_KEY`; raw visitor IDs and IP addresses are not stored.

## Rich text and uploads

The editor uses Quill 2 from a CDN and supports inline uploaded images. Article markup is cleaned server-side with an explicit HTML/tag/attribute/protocol allowlist; embedded images are restricted to locally uploaded image paths. Uploaded images are decoded and verified as PNG, JPEG, GIF, or WebP, capped at 20 million pixels and a 3 MB request limit. Store uploads on persistent storage in production and configure an external media service/CDN if needed.

## Tests

```powershell
python -m pytest
```

Tests use a temporary SQLite database and cover application responses, authentication, authorization, article CRUD and revisions, scheduled publishing, engagement, daily analytics, nested comments/reports/notifications, SEO output, sanitization, search/filter combinations, pagination, and admin access. The actual current test outcome is recorded in [TESTING_REPORT.md](./TESTING_REPORT.md).

## Docker and production

For Docker Compose, copy `.env.example` to `.env`, set a long random `SECRET_KEY` and a strong URL-safe `POSTGRES_PASSWORD` (for example, 32 random bytes encoded as hex), then start the services:

```powershell
docker compose up --build
```

The app container selects the production configuration, applies committed Alembic migrations, and starts Gunicorn on port 8000. Persistent Docker volumes hold PostgreSQL data and uploaded images. For deployment, use HTTPS behind a trusted reverse proxy, protect environment variables, configure backups and monitoring, and review worker/resource sizing. See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

## Project layout

```text
app/
  admin/ auth/ blog/ comments/ dashboard/
  models/
  static/css/ static/js/ static/uploads/
  templates/
  utils/
migrations/
tests/
config.py
run.py
wsgi.py
```

The full directory explanations, request flows, and model diagram are in [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md). Milestone coverage is summarized in [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md).

## Accessibility and external assets

Templates use semantic landmarks, form labels, responsive Bootstrap 5 layouts, and accessible text alternatives for uploaded article images. Google Fonts, Bootstrap, and Quill assets are loaded from CDNs; deployments that require offline/self-hosted assets should vendor those files and adjust CDN policy accordingly.

## License

MIT; see [LICENSE](./LICENSE).
