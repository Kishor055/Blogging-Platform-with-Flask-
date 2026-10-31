# BlogSphere Advanced Feature Roadmap

**Status:** Mixed. The initial high-priority feature set below has shipped; remaining capabilities are still proposals. See the implementation and test docs for current behavior and validation.

## Shipped high-priority scope

- Post revision snapshots and restore (unlimited retention); scheduled publishing uses author-entered IANA timezones and UTC storage, with an idempotent `publish-scheduled` CLI command.
- Authenticated post likes and bookmarks; comment replies are limited to two nested levels, and users can report comments for admin review.
- Daily unique article views use a pseudonymous cookie identifier that is HMACed before storage; IP addresses are not recorded.
- In-app comment, reply, and scheduled-publishing notifications.
- Article SEO metadata, structured data, canonical links, sitemap, robots policy, and RSS.

These features do not imply that follow/unfollow, comment likes, rich analytics/trends, email notifications, autosave, soft-delete, or the other optional/production phases are implemented.

## Guiding approach

- Preserve current behavior and build on the existing Flask modular monolith.
- Deliver small, testable phases; do not begin with a rewrite.
- For each phase: define behavior and authorization, add migration(s), implement UI/API surface as applicable, add tests, run the focused suite, and update implementation/deployment documentation.
- Mark capabilities **done** only after source, tests, and docs agree. Do not report unrun test/build/deployment results.
- Optional capabilities (AI, public API, newsletter, external search) require a product decision before implementation.

## Phase plan

### Phase A — Repository baseline (complete for this analysis)

- Record current architecture, data model, routes, operational setup, and test status.
- Current verified baseline: `python -m pytest -q` → **25 passed in 22.65 seconds** on 2026-10-31.
- No claim is made here about PostgreSQL, browser, Docker build, or production verification.

### Phase B — Gap and architecture decisions (documents created)

- Maintain `IMPLEMENTATION_GAP_REPORT.md` and `PROPOSED_ARCHITECTURE.md`.
- Decide post lifecycle/roles, scheduling semantics, revision retention, analytics privacy, and optional modules before changing schema.

### Phase C — Data model and migration foundation

- Add only approved models/relations and constraints.
- Plan safe migrations against existing SQLite and PostgreSQL data.
- Add indexes according to query patterns and tests for uniqueness, cascade behavior, and migration reversibility.

**Exit checks:** Clean upgrade on a fresh DB; upgrade on representative existing data; documented downgrade limitations; model/permission tests pass.

### Phase D — Content management

**Shipped subset:** Revision history/restore and scheduled publishing. Revision retention is unlimited. Scheduled local times are converted to UTC; ambiguous DST times use fold 0 and nonexistent local times are rejected. The CLI publisher must be invoked by an external recurring scheduler.

- Define and enforce content state transitions.
- Implement preview and richer draft handling; add auto-save with explicit save/error/conflict state.
- Add revision history and restore; implement soft-delete/recovery and retention only after policy is agreed.
- Add scheduled publishing using durable, idempotent background work and explicit timezone semantics.
- Add featured content, reading time validation, and generated table of contents where appropriate.

**Exit checks:** Non-public content remains private; revision restoration and schedule retries are tested; author/admin transition rules are enforced.

### Phase E — User engagement

**Shipped subset:** Post likes/bookmarks, a reading list, up to two nested reply levels, comment reports, and admin report review.

- Implement likes, bookmarks, reading lists, and follow/unfollow with uniqueness constraints.
- Add bounded nested comments, comment likes, and content reporting/moderation.
- Add recent-viewed or recommendations only after defining privacy and ranking rules.

**Exit checks:** Duplicate operations are safe; authorization and deletion policies are covered; moderation actions are auditable.

### Phase F — Analytics and author dashboard

**Shipped subset:** One unique view per pseudonymous cookie, article, and UTC day, with author-scoped aggregate counts. No IP addresses are stored.

- Agree on view/unique-view definitions, bot treatment, retention, and privacy.
- Record and aggregate view events; add author-scoped time-range and article analytics.
- Extend the dashboard with engagement/trend data and export only if needed.

**Exit checks:** Tests prove counts and boundaries, and verify cross-author isolation. Include query/index performance checks for representative data.

### Phase G — Administration and editorial workflow

**Shipped subset:** Admins can view comment reports, mark them reviewed, or remove reported comments.

- Add editorial queue, assignments, review comments, approval/rejection, and audit history if separate review roles are approved.
- Add report queues, bulk operations, role-management guardrails, and operational summaries as justified.

**Exit checks:** Every state transition and moderation action has actor/permission coverage and admin auditability.

### Phase H — Search and discovery

- Measure expected content volume and select database full-text search or an external index only if justified.
- Add relevance, filters/facets, robust pagination, and related-content recommendations.

**Exit checks:** Search results respect published/visibility rules; indexing or query changes are migration-tested and bounded.

### Phase I — AI writing assistance (optional)

- Decide providers, permitted tasks, user consent, retention, and cost/rate limits.
- Add an optional provider interface for idea generation, outlines, rewrite, grammar, and metadata suggestions.
- Keep generated text opt-in and user-reviewed; never silently publish or overwrite content.

**Exit checks:** Provider keys are configuration-only; errors/timeouts are visible; provider-independent tests cover failure behavior; no sensitive content is sent without explicit policy and user action.

### Phase J — SEO, notifications, and newsletter

**Shipped subset:** Article metadata/structured data, canonical URLs, sitemap, robots policy, RSS, and in-app comment/reply/scheduled-publication notifications.

- Add article title/description/canonical metadata, sitemap, robots policy, structured data, and RSS.
- Add in-app notifications and preferences; use durable event delivery for email.
- Add newsletter subscriptions only with verification, consent tracking, unsubscribe, and delivery-failure handling.

**Exit checks:** Public outputs match published visibility; email preferences and unsubscribe paths work; retry behavior avoids duplicate messages.

### Phase K — Security, performance, and operations

- Review authorization, validation, CSRF, upload storage, rate limits, secrets, headers, and abuse cases for new features.
- Add measured caching/query optimization, structured logs, readiness/liveness checks, and monitoring.
- Validate PostgreSQL, backups/restores, task-worker reliability, and persistent upload storage.

**Exit checks:** Security and performance checks are tied to documented scope and reproducible evidence; no unverified production-readiness claims.

### Phase L — Automated test expansion

- Extend integration tests for new routes, states, authorization and migrations.
- Add PostgreSQL and browser/JavaScript tests where behavior requires them.
- Add focused coverage, API contract, task retry/idempotency, and performance tests as appropriate.

**Exit checks:** Full required test commands pass; record exact command, runtime/environment, results, and known gaps.

### Phase M — Deployment and documentation

- Update README, deployment, structure, implementation, testing, API, security, database, and changelog docs to match shipped code.
- Add CI/CD and monitoring/backups only where implemented and verified.
- Validate Docker build and Compose startup, database migrations, health/readiness, and an operational rollback/restore path.

**Exit checks:** A clean environment can follow the docs; all listed capabilities map to routes/models/tests; deployment statements have direct verification evidence.

## Priority grouping

### Core (preserve)

Authentication, article CRUD, comments, categories/tags, search, responsive UI, and deployment are already implemented at a baseline level.

### High priority (candidate next release)

Content preview/revisions/workflow, scheduled publishing, likes/bookmarks/follows, comment replies/reports, meaningful author analytics, notifications, and SEO fundamentals. Order must follow the Phase C decisions and dependencies.

### Advanced/optional

AI writing assistance, public REST API, newsletter, Redis caching/queues, external search, and sophisticated recommendations. These add operational/privacy/provider costs and should be approved based on actual user needs.

### Production engineering

PostgreSQL integration coverage, persistent media strategy, rate limiting, monitoring/logging, backup/restore, CI/CD, security validation, and verified Docker/Gunicorn deployment.

## Cross-phase acceptance checklist

- Existing behaviors and URLs remain compatible unless a migration or UX change is intentionally documented.
- Schema changes are migrated and do not silently discard existing user content.
- Every user action has server-side validation and access checks.
- Tests cover success, invalid input, unauthorized access, and failure/retry cases where relevant.
- UI shows meaningful saved, pending, empty, and error states and remains keyboard accessible.
- Documentation describes only behavior that exists and test results that were actually run.
- Deployment changes are reproducible and include environment variables, migrations, persistent data, and recovery guidance.
