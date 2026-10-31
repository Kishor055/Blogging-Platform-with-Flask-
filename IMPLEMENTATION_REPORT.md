# BlogSphere Implementation Report

## Overview

BlogSphere is implemented as a modular Flask application with SQLAlchemy models, Flask-Migrate, Flask-Login, Flask-WTF, Jinja templates, and responsive static assets. It is built as one application spanning the seven roadmap milestones, not as separate weekly projects.

## Milestone coverage

| Milestone | Implemented scope |
| --- | --- |
| Week 1 — Foundation | Application factory, configuration profiles, Blueprints, SQLAlchemy, migration extension, environment configuration. |
| Week 2 — Authentication | Registration, login/logout, Werkzeug password hashes, Flask-Login sessions, profile editing, admin role checks, CSRF forms. |
| Week 3 — Publishing | Post/category/tag models, draft/published/scheduled CRUD, unique slugs, unlimited content revisions with restore, author-timezone scheduling, Quill editor, constrained uploads, Bleach sanitization. |
| Week 4 — Frontend | Responsive homepage/listing/detail, navigation, author profiles, pagination, error pages, empty states, author dashboard. |
| Week 5 — Community | Authenticated comments with bounded replies, reports, owner deletion, admin moderation, in-app comment/reply notifications, likes, and bookmarks. |
| Week 6 — Discovery and analytics | Case-insensitive title/body search, combined category/tag filters, sorting, pagination, daily pseudonymous unique article views, author-scoped counts, canonical/structured metadata, sitemap, robots, and RSS. |
| Week 7 — Delivery | Pytest suite, Gunicorn WSGI module, Dockerfile, PostgreSQL Compose stack, migrations, deployment instructions. |

## Implemented security controls

- Passwords are stored as Werkzeug password hashes.
- Global CSRF protection applies to state-changing web forms.
- Owner/admin checks protect article and comment operations.
- Public queries exclude drafts; non-owners cannot view draft detail pages.
- Rich text is sanitized server-side using allowlisted tags, attributes, and URL schemes.
- Scheduled publishing is an explicit CLI operation and uses an atomic status transition; run it periodically with an external scheduler.
- Analytics store HMACed daily cookie identifiers without collecting IP addresses.
- `.gitignore` excludes local environment variants, secret directories, private-key files, local databases, and uploads while retaining `.env.example`.
- Upload extensions and total request size are constrained.
- Uploaded article images are decoded and checked against the declared format, capped by pixel count, and rich-text embeds can reference only locally stored uploads.
- Production refuses to start without an explicit `SECRET_KEY`; production cookies are marked secure.
- Postgres credentials and session secrets are supplied via environment variables.

## Architecture and data

Feature Blueprints separate request handlers; models define the user/post/comment/category/tag, engagement, revision, view, report, and notification relationships; reusable templates share the site shell. See [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md) for the project tree, request flows, and Mermaid ER diagram.

## Verification status

The latest test and migration results are recorded in [TESTING_REPORT.md](./TESTING_REPORT.md). Browser-only interaction, PostgreSQL integration, and Docker Compose validation/image build are not covered by the SQLite pytest result.

## Known scope limits

- No email verification, password reset, external OAuth, or newsletter delivery.
- No image cropping/optimization or external object storage integration.
- Search uses database `ILIKE` and is suitable for the included application scale; large production datasets may need full-text indexing.
- CDN assets need self-hosting for deployments requiring offline operation.
- Inline uploaded images are stored as files and may need cleanup when authors discard an unsaved draft.
