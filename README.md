# BlogSphere — Modern Flask Blogging Platform

**Write. Publish. Connect. Share your stories with the world.**

BlogSphere is a modular, full-stack blogging platform built with **Python and Flask**. It provides writers with the tools to create and manage articles, build author profiles, engage with readers, and organize content through categories and tags.

Designed with maintainability, security, and extensibility in mind, BlogSphere includes rich-text publishing, scheduled articles, revision history, community interactions, administrative controls, SEO features, and Docker-based deployment support.

Run it locally with SQLite or deploy it with PostgreSQL and Docker Compose.

<!-- Replace these links if your repository paths change. -->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Flask-Modular-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-red" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="Database support">
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Creating an Administrator](#creating-an-administrator)
- [Application Routes](#application-routes)
- [Scheduled Publishing](#scheduled-publishing)
- [Rich Text and Media Uploads](#rich-text-and-media-uploads)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Security and Privacy](#security-and-privacy)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

BlogSphere provides a complete blogging workflow, from drafting and editing articles to publishing, discovering, and engaging with content.

The application follows a modular Flask architecture using an application factory, Blueprints, SQLAlchemy models, and Flask-Migrate for database schema management.

### Key capabilities

- **Content management:** Create, edit, delete, schedule, and restore articles.
- **Writer profiles:** Manage author information, avatars, and published work.
- **Community engagement:** Support comments, nested replies, likes, bookmarks, reports, and notifications.
- **Administration:** Manage users, roles, categories, tags, article visibility, and reported content.
- **Content discovery:** Search articles, filter by category and tag, and browse paginated results.
- **Publishing automation:** Publish scheduled articles using a repeatable CLI command.
- **SEO and discoverability:** Generate canonical URLs, structured metadata, sitemaps, robots directives, and RSS feeds.
- **Deployment flexibility:** Run locally with SQLite or deploy using PostgreSQL, Docker, and Gunicorn.

## Features

### 1. Authentication and user management

- User registration, login, and logout.
- Secure password hashing.
- Public author profiles and avatar uploads.
- Role-based access for administrators.
- Ownership checks for article editing and deletion.
- Dedicated author dashboard for content management and activity.

### 2. Article creation and publishing

- Full article CRUD functionality.
- Rich-text editing powered by Quill 2.
- Featured images and inline article images.
- Draft, published, and scheduled publication states.
- Categories, tags, and combined content filters.
- Search, pagination, and reading-time metadata.
- Article revision history with restoration.
- Author-timezone-aware scheduling.

### 3. Reader engagement

- Authenticated article likes.
- Personal reading lists and bookmarks.
- Authenticated comments and bounded nested replies.
- Comment reporting and administrator review.
- In-app comment, reply, and scheduled-publication notifications.
- Recent reader activity and publishing statistics in the author dashboard.

### 4. Administration

- Manage users, accounts, and roles.
- Moderate comments and review reports.
- Manage categories and tags.
- Control article visibility.
- Access administrative content-management tools.

### 5. SEO and content discovery

- Canonical article URLs.
- Structured metadata.
- XML sitemap.
- Robots policy.
- RSS feed.
- Searchable, filterable, paginated article listings.

### 6. Analytics and personalization

- Author-scoped daily unique-view counts.
- Pseudonymous, cookie-based article-view tracking.
- No retention of visitor IP addresses for article analytics.
- Persistent light and dark theme preference.

### 7. Security and reliability

- CSRF protection.
- Server-side rich-text sanitization.
- Authenticated upload handling and image verification.
- Secure session-cookie configuration.
- Production requirement for an explicitly configured secret key.
- Automated tests for major application workflows.
- Database migrations and repeatable scheduled publishing.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Web framework | Flask |
| Application architecture | Application factory and Blueprints |
| ORM | Flask-SQLAlchemy / SQLAlchemy |
| Database migrations | Flask-Migrate / Alembic |
| Local database | SQLite |
| Production database option | PostgreSQL |
| Template engine | Jinja2 |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 |
| Rich-text editor | Quill 2 |
| Authentication security | Werkzeug password hashing |
| Testing | pytest |
| Production server | Gunicorn |
| Containerization | Docker and Docker Compose |

## Architecture

BlogSphere separates application responsibilities into focused modules.

- **Authentication:** Registration, sessions, and author profiles.
- **Blog:** Article lifecycle, search, filtering, and publishing.
- **Comments:** Replies, moderation, and reports.
- **Dashboard:** Author statistics and content management.
- **Admin:** Administrative workflows and taxonomy management.
- **Models:** Persistent entities and relationships.
- **Utilities:** Shared helpers, validation, and supporting logic.
- **Migrations:** Version-controlled database schema changes.
- **Tests:** Automated application and security checks.

For the complete entity-relationship diagram and request flows, see [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md).

## Contents

- [Requirements](#requirements)
- [Local setup](#local-setup)
- [Administrator account](#administrator-account)
- [Environment variables](#environment-variables)
- [Features and routes](#features-and-routes)
- [Database design](#database-design)
- [Rich text and uploads](#rich-text-and-uploads)
- [Tests](#tests)
- [Docker and production](#docker-and-production)
- [Project layout](#project-layout)
- [Accessibility and external assets](#accessibility-and-external-assets)
- [License](#license)

## Requirements

Before installing BlogSphere, ensure you have:

- Python 3.10 or newer.
- pip.
- A virtual-environment tool.
- Git.
- Docker Compose v2 if using the containerized deployment.

The Docker image uses Python 3.13.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/Kishor055/Blogging-Platform-with-Flask-.git
cd Blogging-Platform-with-Flask-
```

### 2. Create and activate a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the appropriate Python executable from `.venv\Scripts\python.exe` or follow your organization's approved PowerShell policy.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure a unique secret key before using the application beyond local development.

Generate a cryptographically random key with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

If `SECRET_KEY` is not set, development uses a temporary key and sessions will not survive an application restart. Never commit `.env` or production credentials.

### 5. Initialize the database

The repository includes its Alembic migrations. On a fresh checkout, apply the committed migrations to create the schema and starter categories and tags:

```powershell
flask --app run.py db upgrade
```

Administrators can add or remove taxonomy in the Admin studio.

### 6. Start the development server

```powershell
flask --app run.py run
```

Open the application:

**http://127.0.0.1:5000**

The `/health` endpoint provides a basic application health response.

> **Note:** Use `flask db init` only if the repository does not already contain a migrations directory. Create new migrations with `flask db migrate` and apply them with `flask db upgrade`.

## Configuration

BlogSphere uses environment variables to configure the application.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Secret used for session and CSRF signing; must be configured in production. |
| `DATABASE_URL` | SQLAlchemy database connection URL. Defaults to local SQLite. |
| `APP_ENV` | Configuration profile: `development`, `testing`, or `production`. |
| `UPLOAD_FOLDER` | Directory used for uploaded article images. |
| `POSTGRES_PASSWORD` | PostgreSQL password used by the Docker Compose configuration. |

### PostgreSQL configuration

Example SQLAlchemy URL:

```text
postgresql+psycopg://<user>:<password>@localhost:5432/blogsphere
```

URL-encode special characters in database credentials. In Docker Compose, the database hostname is `db`, and Compose builds the URL from `POSTGRES_PASSWORD`.

## Database Setup

The default database is SQLite, stored at:

```text
instance/blogsphere.db
```

BlogSphere's data model includes:

- `User`: Account information, roles, and author identity.
- `Post`: Article content, publication state, and ownership.
- `Category`: Article classification.
- `Tag`: Reusable topic labels.
- `Comment`: Reader feedback and nested replies.
- `Bookmark`: Saved articles.
- `Like`: Article engagement records.
- `Notification`: In-app activity notifications.
- `PostRevision`: Article version history.
- `Report`: Submitted content reports.
- Daily view events: Article analytics.

Posts can belong to a category and can be associated with multiple tags through the `post_tags` many-to-many relationship.

Uniqueness constraints prevent duplicate supported engagement actions and daily view records.

For the definitive model relationships, consult the application's model definitions and [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md).

## Creating an Administrator

Create an administrator using the interactive CLI:

```powershell
flask --app run.py create-admin
```

Follow the prompts to enter a username, email address, and password.

The command stores a password hash rather than the plaintext password.

**Security recommendation:** Do not grant administrator privileges through public registration. Create and manage administrator accounts through trusted administrative procedures.

## Application Routes

The following table summarizes the main application endpoints.

| Route | Purpose | Access |
|---|---|---|
| `/` | Homepage | Public |
| `/articles` | Browse, search, and filter articles | Public |
| `/article/<slug>` | View an article and its comments | Public for published articles |
| `/article/new` | Create an article | Authenticated |
| `/article/<slug>/edit` | Edit or schedule an article | Owner or admin |
| `/article/<slug>/delete` | Delete an article | Owner or admin; POST |
| `/article/<slug>/revisions` | Review and restore revisions | Owner or admin |
| `/article/<slug>/like` | Toggle an article like | Authenticated; POST |
| `/article/<slug>/bookmark` | Toggle a bookmark | Authenticated; POST |
| `/bookmarks` | View saved articles | Authenticated |
| `/comments/<id>/reply` | Reply to a comment | Authenticated; POST |
| `/comments/<id>/report` | Report a comment | Authenticated; POST |
| `/notifications/` | View notifications | Authenticated |
| `/category/<slug>` | Browse a category | Public |
| `/tag/<slug>` | Browse a tag | Public |
| `/auth/register` | Register an account | Public |
| `/auth/login` | Sign in | Public |
| `/auth/logout` | Sign out | Authenticated |
| `/auth/profile/<username>` | View an author profile | Public |
| `/dashboard/` | Author dashboard | Authenticated |
| `/admin/` | Administrative management | Admin |
| `/sitemap.xml` | Sitemap | Public |
| `/robots.txt` | Crawler directives | Public |
| `/feed.xml` | RSS feed | Public |
| `/health` | Application health response | Public |

Destructive and state-changing operations should use the HTTP methods and authorization rules enforced by the actual application routes.

## Scheduled Publishing

BlogSphere supports scheduled publication using a CLI command:

```powershell
flask --app run.py publish-scheduled
```

Run this command periodically using cron, a task scheduler, or your deployment platform's scheduled-job facility.

For example, invoke it once per minute if your publishing requirements need that level of granularity.

Scheduling behavior includes:

- Storing publication instants in UTC.
- Retaining the IANA timezone used to enter the local publication time.
- Rejecting nonexistent local times during daylight-saving transitions.
- Selecting the first occurrence for ambiguous local times.
- Avoiding duplicate publication of already-published articles.

The command is designed to be idempotent.

## Rich Text and Media Uploads

The article editor uses Quill 2 and supports inline image uploads.

The application performs server-side sanitization using an explicit HTML, attribute, and protocol allowlist. Embedded article images are restricted to locally uploaded image paths.

Uploaded images are decoded and verified as PNG, JPEG, GIF, or WebP, with a 20-million-pixel limit and a 3 MB request limit.

For production deployments:

- Store uploaded media on persistent storage.
- Back up uploaded content alongside the database.
- Consider external object storage or a media CDN as the project scales.
- Review upload permissions, serving rules, and reverse-proxy request limits.

## Testing

Run the automated test suite:

```powershell
python -m pytest
```

Tests use a temporary SQLite database and cover major application workflows, including:

- Application responses and authentication.
- Authorization and role checks.
- Article CRUD and revision restoration.
- Scheduled publication.
- Likes, bookmarks, and daily analytics.
- Nested comments, reports, and notifications.
- SEO output and rich-text sanitization.
- Search, filters, and pagination.
- Administrative access.

Consult [TESTING_REPORT.md](./TESTING_REPORT.md) for the recorded test outcome.

## Docker Deployment

BlogSphere includes a Dockerfile and PostgreSQL Compose configuration.

### 1. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Set a strong, randomly generated `SECRET_KEY` and a strong `POSTGRES_PASSWORD`.

### 2. Build and start the services

```powershell
docker compose up --build
```

The app container selects the production configuration, applies committed Alembic migrations, and starts Gunicorn on port 8000. Persistent Docker volumes hold PostgreSQL data and uploaded images. Check `http://localhost:8000/health` after startup. For deployment, use HTTPS behind a trusted reverse proxy, protect environment variables, configure backups and monitoring, and review worker/resource sizing. See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

Docker volumes persist PostgreSQL data and uploaded images.

### Production checklist

- Configure HTTPS behind a trusted reverse proxy.
- Store secrets in the hosting platform's environment configuration.
- Use persistent storage for uploads and database data.
- Configure database backups and recovery procedures.
- Monitor application errors and resource utilization.
- Configure scheduled publishing as a separate recurring task.
- Review worker counts, timeouts, and resource limits.
- Test migrations and restore procedures before production upgrades.

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for additional deployment information.

## Security and Privacy

BlogSphere includes several security and privacy safeguards:

- Password hashing rather than plaintext password storage.
- CSRF protection for supported state-changing requests.
- Authorization and ownership checks for protected operations.
- Server-side rich-text sanitization.
- Verified image formats and upload limits.
- Secure session-cookie configuration.
- An explicit production `SECRET_KEY` requirement.
- Pseudonymous, cookie-based article-view analytics without IP-address retention.

The analytics implementation uses an HMAC derived from the cookie identifier and `SECRET_KEY`. Visitor identifiers and IP addresses are not retained by the described analytics mechanism.

Operational logs, reverse proxies, hosting providers, and other infrastructure may have separate logging behavior. Review those systems independently when establishing a complete privacy policy.

Never commit API keys, passwords, production secrets, or private environment files to Git.

## Project Structure

```text
Blogging-Platform-with-Flask-/
├── app/
│   ├── admin/
│   ├── auth/
│   ├── blog/
│   ├── comments/
│   ├── dashboard/
│   ├── models/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/
│   └── utils/
├── migrations/
├── tests/
├── instance/
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── STRUCTURE_REPORT.md
├── IMPLEMENTATION_REPORT.md
├── TESTING_REPORT.md
├── DEPLOYMENT_GUIDE.md
└── README.md
```

The full directory explanations, request flows, and model diagram are in [STRUCTURE_REPORT.md](./STRUCTURE_REPORT.md). Milestone coverage is summarized in [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md), and the current test record is in [TESTING_REPORT.md](./TESTING_REPORT.md).

## Documentation

Additional project documentation:

- [Architecture and database structure](./STRUCTURE_REPORT.md)
- [Implementation and milestone report](./IMPLEMENTATION_REPORT.md)
- [Automated testing report](./TESTING_REPORT.md)
- [Deployment guide](./DEPLOYMENT_GUIDE.md)

## Troubleshooting

### Database tables are missing

Apply the committed migrations:

```powershell
flask --app run.py db upgrade
```

### The application secret changes after restarting

Configure a stable, random `SECRET_KEY` in your environment. An ephemeral development key invalidates existing sessions when the process restarts.

### Scheduled articles are not publishing

Verify that the scheduled-publication CLI command is being invoked regularly and inspect the application logs and configured timezone.

### Uploaded images disappear after redeployment

Use persistent storage for uploaded files and confirm that the deployment mounts the upload directory correctly.

### PostgreSQL connection fails

Check the database URL, credentials, network access, database readiness, and installed PostgreSQL driver.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes with appropriate tests.
4. Run the test suite.
5. Submit a pull request describing the change.

For significant changes, open an issue first to discuss the proposed design.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

<p align="center">
  <strong>BlogSphere</strong><br>
  Built with Python, Flask, and a passion for sharing ideas.
</p>
