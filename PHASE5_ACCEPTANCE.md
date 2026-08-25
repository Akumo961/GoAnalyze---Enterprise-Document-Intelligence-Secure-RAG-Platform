# Phase 5 — Durable government workflow and analyst queues

## Scope

Phase 5 extends the Phase 4 persistence foundation into the government case-review workflow:

- durable tenant-scoped case records;
- explicit analyst workflow states;
- server-side tenant isolation on case reads and queue listings;
- persistent analyst queue assignment;
- human decision-officer identity and decision reason for approval/rejection;
- explicit transition validation preventing direct autonomous approval from intake;
- Alembic migration and SQLite integration tests.

## Evidence gates

The Phase 5 acceptance workflow must execute:

1. Phase 5 persistence/workflow tests.
2. Full Python test suite.
3. Ruff.
4. mypy.

A green workflow is evidence for the tested commit only.

## Deliberate boundaries

- Case records are decision-support workflow data, not legally binding decisions.
- Approval/rejection requires an identified human actor and non-empty reason.
- No authoritative Québec regulatory content is introduced.
- No production PostgreSQL deployment is claimed from SQLite tests.
- API endpoint integration and deployed-service integration remain separate evidence gates until implemented and exercised.
