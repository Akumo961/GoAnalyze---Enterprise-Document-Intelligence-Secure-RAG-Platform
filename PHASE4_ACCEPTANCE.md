# Phase 4 — Persistent government data foundation

## Implemented scope

Phase 4 connects the Phase 3 governance primitives to durable data structures:

- PostgreSQL-compatible SQLAlchemy persistence for versioned regulatory sources and obligations.
- Alembic migration for regulatory knowledge tables.
- Version key `(source_id, version)` so multiple source versions can coexist.
- Customer/source authority labels remain explicit; the platform does not certify legal authority.
- Tenant-safe persistence remains the responsibility of the calling service; the existing authenticated context and tenant-scoped repositories remain the enforcement boundary.
- Retention execution planning separates `legal_hold`, `retain`, and `delete_eligible` states.
- Destructive deletion requires an explicit executor callback; age alone never silently deletes data.
- SQLite integration tests exercise the ORM/repository behavior without claiming PostgreSQL production validation.

## Acceptance gates

The Phase 4 workflow must run:

1. Phase 4 persistence tests.
2. Full Python test suite.
3. Ruff.
4. mypy.

The results prove only the tested commit. PostgreSQL, deployed-service integration, and production retention execution remain unverified until those environments are exercised.

## Not claimed

- No Québec regulatory source is included as authoritative data.
- No legal/privacy compliance certification is claimed.
- No live PostgreSQL deployment is claimed from SQLite tests.
- No automatic legal decision is made.
