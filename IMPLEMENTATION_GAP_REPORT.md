# BlogSphere Implementation Gap Report

**Review date:** 2026-10-31  
**Baseline:** Current repository source and local SQLite tests; see [TESTING_REPORT.md](./TESTING_REPORT.md) for the latest run.  
**Purpose:** Compare implemented behavior with the expansion proposal; gaps below are not claims of defects unless explicitly stated.

## Status definitions

- **Implemented:** Present in source and covered by the current product behavior.
- **Partial:** A related/basic capability exists, but not the proposed full capability.
- **Missing:** No corresponding implementation was found.
- **Proposed:** Recommended future work; not part of the current application.

## Feature gap matrix

| Capability | Status | Current evidence / gap |
| --- | --- | --- |
| Registration, login, profiles, roles | Implemented | User model, auth forms/routes, Flask-Login and admin decorator. No password reset, email verification, or OAuth. |
| Article editor and CRUD | Partial | Quill editor, sanitization, CRUD, unlimited text revisions/restore, and scheduled publishing. No auto-save, soft-delete, or full preview workflow. |
| Content status and editorial workflow | Partial | Draft/published/scheduled states exist. No pending review, approval/rejection, archive state, assignment, or audit trail. |
| Featured articles and reading tools | Partial | Reading-time property exists. No featured ranking/control, generated table of contents, or configurable publishing metadata. |
| Categories, tags, search, filters | Partial | Search, taxonomy filters, newest/oldest sort, and pagination exist. No relevance ranking, full-text index, saved searches, or recommendation logic. |
| Comments and moderation | Partial | Authenticated comments, two nested reply levels, reports, owner/admin deletion, and admin report review. No comment editing/likes or full audit trail. |
| Likes, bookmarks, follows, reading list | Partial | Post likes, bookmarks, and reading list implemented with uniqueness constraints. Author follows are not implemented. |
| Author analytics | Partial | Per-article daily unique view counts use a pseudonymous cookie identifier; no IP addresses are stored. No bot filtering, trends, retention controls, or export. |
| Admin studio | Partial | User, role, article visibility, comment, taxonomy, and report management. No editorial queue, audit history, bulk actions, or configurable system settings. |
| Notifications and email | Partial | In-app notifications for comments, replies, and scheduled publishing. No email delivery/preferences or generic event outbox. |
| AI writing assistant | Missing | No provider abstraction, prompt workflows, consent controls, or AI integration. |
| SEO and publication distribution | Partial | Per-article descriptions, canonical/structured metadata, sitemap, robots policy, and RSS are implemented. No newsletter. |
| REST API | Missing | `/health` is a basic operational JSON endpoint, not a content API. No API versioning, serializers, token auth, or API contract documentation. |
| Security controls | Partial | Password hashes, CSRF, route-level ownership/admin checks, rich-text allowlist, upload validation, production secret requirement and secure cookies exist. No formal threat model, rate limiting, security headers policy, audit logging, or security test suite was verified. |
| Deployment | Partial | Dockerfile, Compose PostgreSQL service, Gunicorn command, environment configuration and persistent named volumes exist. No verified CI/CD, object storage, worker, monitoring, backup/restore, or production run. |
| Automated tests | Partial | Core and selected new feature workflows are covered with SQLite tests. PostgreSQL, browser, recurring scheduler operations, API-contract, performance, and formal security testing remain unverified. |
| Documentation | Partial | README, structure, implementation, testing, and deployment documents exist. The requested analysis/gap/architecture/roadmap docs are new; future API/security/database/changelog docs will need to track real delivery. |

## Priority gaps and recommended completion criteria

### P0 — Preserve and strengthen the current baseline

1. Keep all existing tests passing and add tests with each schema or route change.
2. Use additive Alembic migrations; verify upgrade and downgrade behavior against populated data.
3. Specify authorization for each new action: actors, ownership, staff privileges, and visibility rules.
4. Verify PostgreSQL behavior and deployment settings rather than treating SQLite tests as production validation.
5. Define uploads' lifecycle and persistent storage/backup behavior before enabling deletion or revision restoration.

**Exit:** The original baseline and selected new-flow tests pass; the additive migration applies on a fresh SQLite database. Upgrade against representative populated production data and PostgreSQL remains unverified.

### P1 — Content workflow and writer experience

- Expand state transitions to include review/pending and archived states only after defining which roles may transition each state.
- **Implemented:** Unlimited text revision snapshots/restoration and scheduled publishing with UTC storage, author timezone, and a repeat-safe CLI publisher.
- **Remaining:** Soft-delete/recovery, featured selection, generated contents, a full preview flow, and operational deployment/monitoring of the recurring publisher.
- Implement auto-save as an explicit draft persistence flow; expose save state and conflict behavior to the editor.

**Exit:** State-transition tests, version restore tests, scheduler retry/idempotency tests, and draft isolation/authorization tests pass.

### P1 — Engagement and community

- **Implemented:** Unique like/bookmark relations, reading list, bounded comment replies, reports, and admin review.
- **Remaining:** Author-follow relations, comment likes, formal notification retry/outbox semantics, and report audit history.

**Exit:** Duplicate action protection, relationship integrity, nested-comment bounds, visibility rules, report/moderation tests, and notification preferences are covered.

### P1 — Analytics and dashboard

- **Implemented:** One pseudonymous visitor cookie per article per UTC day; only the HMACed identifier is stored, not raw IP.
- **Remaining:** Bot filtering, logged-in/repeat visitor policy beyond cookie deduplication, retention, time ranges, trend aggregation, and export.

**Exit:** Metric definitions are documented; event ingestion and aggregation tests match the displayed counts; the dashboard scopes data to the author.

### P2 — Search, SEO, API, and distribution

- Upgrade discovery based on expected dataset/database: indexes/full-text search, relevance, facets, and safe pagination.
- **Implemented:** Per-article metadata, canonical/structured data, sitemap/robots, RSS, and tests.
- Build an independently versioned `/api/v1` contract with serialization, authentication, rate limiting, and error formats if external consumers are in scope.
- Add email/newsletter subscription and delivery only after consent, unsubscribe, bounce/failure, and data-retention requirements are defined.

**Exit:** Metadata/API outputs are validated, permissions align with the web application, and email consent/unsubscribe behavior is covered.

### P2 — AI and operational maturity

- Treat AI as optional: provider boundary, secrets from environment, explicit user action/consent, bounded inputs, clear failure states, and no silent content changes.
- Add caching/background tasks only where measurements and workload justify them.
- Add structured logs, health/readiness checks, monitoring hooks, backup/restore runbooks, and CI validation.

**Exit:** Provider outages degrade safely; secrets/content handling are documented; deployment and backup/restore steps are exercised in an environment representative of production.

## Dependencies and sequencing risks

- Revisions, scheduled publication, and soft deletion all affect the Post lifecycle; scheduled/draft/published states and text revisions are implemented, while soft-delete remains open.
- Daily unique-view semantics and pseudonymous cookie privacy are implemented; bot filtering and retention remain open.
- Comment/reply/scheduled-publication notification triggers are implemented; durable outbox/retry behavior remains open.
- Search/index changes depend on the target database and dataset size; avoid committing to Redis or an external search engine before measurement.
- REST API and AI are separate product surfaces. Neither is required to deliver the core CMS/community roadmap.
- Database and upload persistence must be established before production scheduling, revisions, or deletion recovery can be considered reliable.

## Verification update

The expanded SQLite suite reports **32 passed in 7.00 seconds** on 2026-10-31. A fresh temporary SQLite database accepted both migrations and `flask db check` found no model drift. PostgreSQL, browser, Docker, and production scheduler operations remain unverified.
