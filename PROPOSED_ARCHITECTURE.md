# BlogSphere Proposed Architecture

**Status:** Proposal for incremental evolution of the existing Flask application. Nothing in this document implies that the proposed modules have been implemented.

## Architectural direction

Keep BlogSphere as a **modular monolith**. The current Flask factory, Blueprints, SQLAlchemy models, Jinja UI, and PostgreSQL-capable deployment provide a suitable base. Add domain modules within the existing application and extract worker or API processes only when operational needs justify them. Do not rewrite the app or introduce microservices as a prerequisite.

### Core principles

- One canonical Post aggregate and a single authorization policy for web and API operations.
- Additive, reviewed schema migrations; retain existing records and URLs.
- Keep HTTP parsing/rendering in routes, business transitions in small service functions, and persistence in existing SQLAlchemy models.
- Separate optional external integrations (email, AI, object storage) behind narrow interfaces with explicit configuration and failure handling.
- Make background work durable, retryable, idempotent, observable, and safe to run more than once.
- Build accessibility, responsive behavior, CSRF, ownership checks, validation, and automated tests into each feature.

## Application module layout

```text
app/
  __init__.py              Factory, extensions, error handlers, CLI
  auth/                    Accounts, sessions, profiles
  blog/                    Public content, editor, discovery
  comments/                Comment routes and moderation
  dashboard/               Author dashboard and analytics views
  admin/                   Administration and editorial queues
  engagement/              Likes, bookmarks, follows, reports
  notifications/           In-app notification preferences and inbox
  api/v1/                  Optional versioned API and serializers
  models/                  Shared SQLAlchemy models and relationships
  services/                Publishing, revisions, analytics, notifications
  tasks/                   Scheduled publishing and async delivery tasks
  utils/                   Cross-cutting helpers (uploads, text, access)
```

Add a module when there is a concrete feature and test boundary; do not split the current CRUD implementation into layers that only forward calls.

## Proposed content lifecycle

Retain the existing `Post` record and slug/URL behavior. Extend its lifecycle with a defined set of states, for example:

```text
draft -> pending_review -> published -> archived
          |                 |
          +-> draft         +-> draft (authorized edit/unpublish)
```

The exact allowed transitions and role permissions must be agreed before implementation. A scheduled post should remain distinguishable from a published article and must not become publicly visible until its scheduled time and a successful, idempotent publish transition.

Suggested content-related columns or relations:

- `scheduled_at` in UTC, optional.
- Explicit publication timestamp `published_at`, separate from `created_at`/`updated_at`.
- `is_featured` or a curated feature relation, with a defined admin/editor permission.
- SEO title/description and canonical URL only if product requirements call for per-article overrides.
- `deleted_at` for recoverable deletion, with a retention/purge policy.
- Revision snapshots in a separate `PostRevision` table rather than overwriting the only copy.

Use database constraints/indexes for valid state and common lookups where supported, while keeping Python validation and migration behavior consistent across SQLite and PostgreSQL.

## Proposed model additions

| Model/relation | Responsibility | Design considerations |
| --- | --- | --- |
| `PostRevision` | Immutable content/title/metadata snapshots and restoration provenance. | Include post, revision number, actor, timestamp, and snapshot fields; decide retention and deletion interaction. |
| `PostLike` | Unique user-to-post like relation. | Unique `(user_id, post_id)`; only visible posts are eligible. |
| `Bookmark` | User's saved articles/reading list. | Unique `(user_id, post_id)`; removal does not alter the article. |
| `Follow` | Reader follows an author. | Unique follower/author pair; reject self-follow; define behavior if an account is removed. |
| `Comment.parent_id` | Nested reply relationship. | Enforce same-post parent and decide maximum depth/flattening policy. |
| `CommentLike` / `ContentReport` | Comment reaction and abuse report. | Unique reaction; report reason/status, reporter, timestamps, and moderation audit. |
| `Notification` | In-app recipient/event/read state. | Store event reference and deduplication key; avoid duplicating sensitive content. |
| `PostView` or `PostViewAggregate` | Analytics events or bounded aggregates. | Define privacy, bot filtering, retention, uniqueness, and aggregation before schema choice. |
| `NewsletterSubscription` | Consent and delivery lifecycle. | Store verification/unsubscribe tokens safely; record consent and unsubscribe timestamps. |
| Editorial assignment/audit model | Review assignments and auditable state transitions. | Add only if distinct editor/reviewer roles are adopted. |

All additions require forward and downgrade migration review, foreign-key deletion rules, indexes, and tests for data integrity. Avoid storing derived counts as authoritative values until consistency/reconciliation is specified.

## Request and background-work flow

### Synchronous web request

1. Blueprint validates request/form and CSRF token.
2. Shared policy/service verifies actor permissions and allowed state transition.
3. SQLAlchemy commits the canonical content/engagement change.
4. An event/outbox record is committed in the same transaction when a durable notification or task is required.
5. The response is rendered or returned by a serializer; no success response should be sent if persistence fails.

### Scheduled publishing and delivery

Introduce a database-backed task/outbox pattern before enabling reliable scheduling. A worker claims due tasks, performs an idempotent state transition, and records success/failure/next retry. A periodic scheduler may enqueue due work; the database remains the source of truth. Redis may be added as a queue/cache if selected infrastructure and load justify it, but queue state should not be the only copy of a scheduled publication.

Use the same principle for email and notification delivery: persist intent, retry transient failures, expose permanent failures, and make duplicate delivery detectable.

## Analytics design

Treat analytics as a product/data design decision, not a template counter:

- Define view and unique-view rules, bot treatment, deduplication window, author access, retention, and privacy disclosures.
- Capture only the minimum event data needed; avoid storing raw IP addresses unless justified and protected.
- Aggregate by time range and article, with indexes based on actual queries.
- Separate raw-event retention from dashboard aggregates where volume requires it.
- Test that an author cannot see another author's private analytics and that public content visibility is respected.

## API design (optional module)

If external API use is approved:

- Mount a distinct `/api/v1` Blueprint.
- Reuse service-level authorization and publishing rules; do not duplicate them in API handlers.
- Define stable request/response schemas, pagination, validation errors, authentication, rate limits, and deprecation policy.
- Keep browser session/CSRF behavior distinct from token-based clients; do not expose admin-only or private fields by default.
- Maintain API tests and generated/maintained endpoint documentation with actual implementations only.

## UI and templates

Continue using the shared Jinja layout and established CSS/JavaScript conventions for the web product. Add dedicated editor workflow, reading list, author analytics, notification, and admin moderation views as needed. Keep user actions keyboard-accessible and provide explicit pending/saved/error states for auto-save, uploads, scheduled actions, and asynchronous operations. CDN assets should be self-hosted or pinned/managed according to the deployment's offline and supply-chain requirements.

## Security and reliability boundaries

- Preserve password hashing, global CSRF protection, safe redirect handling, ownership checks, admin checks, and rich-text sanitization.
- Apply authorization to every new route and object lookup; test both permitted and denied actors.
- Add request limits and abuse controls appropriate to new endpoints; avoid treating a hidden UI control as authorization.
- Keep secrets out of source, logs, API responses, prompts, and exception messages.
- Validate file content and size; use persistent/object storage and cleanup policies rather than relying on local container filesystems.
- Add structured application logs, readiness checks, migration/deployment observability, and backup/restore validation.

## Deployment and configuration evolution

The existing Docker Compose Postgres configuration is the baseline. If adding async tasks, define explicit worker and scheduler services, shared database configuration, health checks, bounded retries, and shutdown behavior. Use environment-based configuration for optional services. Keep local SQLite development convenient while testing migrations and database-specific behavior against PostgreSQL in CI or an integration environment.

## Architecture decision checkpoints

Before feature implementation, resolve:

1. Whether editorial review requires a separate editor role or only author/admin.
2. Exact post state transitions and time zone/schedule semantics.
3. Revision and deleted-content retention/recovery expectations.
4. Analytics privacy, view definition, and retention.
5. Whether the API, AI, newsletter, and external storage are in scope for the first release.
6. Expected deployment scale before selecting Redis, a search engine, or more complex worker infrastructure.
