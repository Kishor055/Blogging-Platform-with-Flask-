# BlogSphere Current Project Analysis

**Review date:** 2026-10-31  
**Scope:** Repository source, templates, migration, configuration, and pytest suite. This is a snapshot of the current implementation, not a feature-completion claim for the proposed expansion.

## Executive summary

BlogSphere is a working Flask modular monolith for multi-author article publishing. It provides account registration and login, author profiles, article CRUD and scheduling, rich-text editing, categories and tags, comments and reports, admin operations, search/filtering, an author dashboard, daily analytics, notifications, SEO distribution, image uploads, migrations, and a Docker/Gunicorn deployment path.

The implemented expansion includes revisions, scheduled publication, likes/bookmarks, nested comment replies and reports, pseudonymous daily view counts, in-app notifications, and SEO/RSS output. Follow relationships, richer analytics, editorial workflow, newsletters, advanced discovery, AI assistance, and a documented REST API remain future work.

## Current stack and entry points

| Area | Current implementation |
| --- | --- |
| Runtime | Python 3.10+ application; Docker image uses Python 3.13. |
| Web | Flask application factory in `app/__init__.py`; feature Blueprints. |
| Persistence | Flask-SQLAlchemy and SQLAlchemy models; SQLite by default, PostgreSQL URL supported. |
| Schema changes | Flask-Migrate/Alembic; one initial schema migration is present. |
| Authentication | Flask-Login; Werkzeug password hashing; Flask-WTF forms and global CSRF protection. |
| UI | Jinja templates, responsive CSS, Bootstrap CDN, Quill CDN editor, small vanilla JavaScript module. |
| Uploads | Pillow validation for PNG/JPEG/GIF/WebP; files stored in a configured local directory. |
| Deployment | `wsgi.py`, Gunicorn in the Docker command, Docker Compose with PostgreSQL and persistent volumes. |
| Tests | Pytest with a Flask test client and SQLite test database. |

`wsgi.py` exposes the app created by `run.py`. `create_app()` selects configuration, creates the instance/upload directories, initializes extensions, imports models, registers Blueprints and provides health/error handlers and a `create-admin` CLI command.

## Current feature inventory

### Accounts and authorization

- Registration validates username, email, and a minimum 10-character password; email is normalized on registration.
- Login uses email and password; a same-host `next` URL is accepted, and external redirects are rejected.
- Profiles are public; the profile owner can edit username, bio, and profile image.
- Flask-Login protects author and admin operations. Admin access is role-based.
- Logout is POST-only. State-changing forms use CSRF protection.

### Publishing and discovery

- Authors can create, edit, and delete their own articles; admins can manage any article.
- Article states are `draft`, `published`, and `scheduled`; scheduled local times are converted to UTC and remain private until the publisher command runs.
- Owners/admins can review and restore unlimited article content revisions.
- The Quill editor supports inline image uploads. Rich text is sanitized server-side with an allowlist.
- Articles have a title, unique slug, content, excerpt, optional featured image, author, optional category, tags, and timestamps.
- Public listing/detail views exclude drafts; an author or admin may access a non-published detail page.
- Listings support title/content `ILIKE` search, category and tag filtering, newest/oldest sort, and pagination.
- A reading-time property is calculated from stripped article markup.

### Community and administration

- Signed-in users can comment, reply up to two nested levels, report other users' comments, and delete their own comments. Admins can review reports and remove reported comments.
- Signed-in users can like articles and save published articles to a reading list.
- The author dashboard shows per-article daily unique view totals and recent reader comments.
- In-app notifications cover comments, replies, and scheduled publication.
- The admin page supports taxonomy management, user role changes, member deletion, article visibility toggling, comment moderation, and report review.
- Category/tag and article-management operations use POST routes.

### Operations and presentation

- `/health` returns a basic JSON status response.
- `/sitemap.xml`, `/robots.txt`, and `/feed.xml` provide search discovery and RSS.
- Article details include canonical, Open Graph, and structured article metadata.
- View analytics store one HMACed cookie identifier per article per UTC day; raw IP addresses are not collected.
- Production configuration requires an explicit `SECRET_KEY` and enables secure session/remember cookies.
- Compose configures PostgreSQL, a health check, and named database/upload/instance volumes.
- The container applies database migrations before starting two Gunicorn workers.
- The base layout includes a theme preference toggle, responsive navigation and CDN-loaded Bootstrap, fonts, and Quill assets.

## Data model

The current ORM schema contains:

- `User`: username, email, password hash, optional profile image, bio, role, creation time.
- `Post`: title, slug, content, excerpt, optional featured image, status, timestamps, author and optional category.
- `PostRevision`, `PostLike`, `Bookmark`, and `ArticleView`: content snapshots, unique engagement relations, and daily unique-view records.
- `Category`: name, slug, description.
- `Tag`: name and slug.
- `Comment`: content, timestamps, author, post, optional parent, and associated reports.
- `CommentReport` and `Notification`: moderation reports and in-app recipient/read state.
- `post_tags`: many-to-many association table with a composite primary key.

Foreign keys define cascade deletion for a user's posts/comments and a post's comments; deleting a category sets the post category to null. The migration defines unique usernames, emails, category/tag names, and slugs (slug uniqueness is represented by unique indexes). Common author, category, status, comment, and slug lookups have indexes.

## Request and content flow

1. Flask dispatches to a registered feature Blueprint.
2. WTForms validates submitted form fields and CSRF tokens.
3. Route-level checks enforce login, admin role, and article/comment ownership.
4. SQLAlchemy persists changes; Jinja renders the response.
5. Rich article content is sanitized before storage. Uploads are checked against the allowed extension, decoded image format, and maximum pixel count before saving.

## Repository layout

```text
app/
  admin/       Admin dashboard and moderation routes
  auth/        Registration, login, and profile routes/forms
  blog/        Public discovery, article editor, detail, and CRUD routes/forms
  comments/    Comment replies, reports, and deletion
  dashboard/   Author dashboard and analytics
  notifications/ In-app notification inbox
  models/      Content, engagement, analytics, notification, and moderation models
  static/      CSS, JavaScript, and uploads
  templates/   Shared layout and feature/error pages
  utils/       Authorization, text, and upload helpers
migrations/    Alembic environment and schema revisions
tests/         Flask integration tests
```

## Verification performed for this analysis

- `python -m pytest -q`: **32 passed in 7.00 seconds** on 2026-10-31.
- Fresh SQLite migration upgrade and `flask db check` were validated after adding the feature migration.
- New tests cover revisions/restoration, scheduled publishing/idempotency, likes/bookmarks, daily analytics, comment replies/reports/notifications, and SEO output.
- This run verifies the test configuration and SQLite behavior only. It does not constitute a PostgreSQL integration test, browser test, Docker build, production deployment, or coverage measurement.

## Constraints and known scope limits

- No auto-save, soft deletion, featured ranking controls, or table of contents.
- No author follows, comment likes, rich analytics/trends, or recommendation system.
- Analytics are aggregate daily unique counts, not a configurable reporting system; user-agent bot filtering and retention policies are not implemented.
- Search is database `ILIKE` and has no relevance ranking, facets beyond category/tag, or dedicated full-text index.
- No editorial submission/review/approval workflow or differentiated editor role is implemented.
- No versioned REST API, AI provider integration, email/newsletter delivery, or public subscription management is present.
- Upload storage is local filesystem storage. Compose supplies a named volume, but no object-storage/CDN adapter or cleanup process is implemented.
- Compose and production startup wiring exist, but this analysis did not verify an image build, live PostgreSQL operation, deployment, backup/restore, monitoring, or CI pipeline.

## Repository state note

At analysis time, the tracked/untracked status reported the existing project files as untracked. No attempt was made to stage, discard, or otherwise alter those pre-existing files.
