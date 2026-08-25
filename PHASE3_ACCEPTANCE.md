# Phase 3 — Government workflow and governance foundation

## Scope

Phase 3 turns the Phase 1/2 evidence pipeline into reusable government workflow primitives without claiming production legal compliance or authoritative Québec regulatory content.

### Implemented
- Versioned regulatory knowledge schema for laws, regulations, policies, directives, permit conditions, and guidance.
- Jurisdiction/date filtering for active obligations.
- Human-controlled case state machine with explicit approval/rejection transitions.
- Tamper-evident SHA-256 audit event chaining and verification.
- Retention-policy and deletion-due primitives with timezone validation.
- Automated Phase 3 unit tests.

### Deliberate boundaries
- Regulatory records are customer-loaded data; the repository does not assert that demo content is authoritative Québec law.
- Retention primitives do not by themselves constitute legal retention compliance; policy enforcement, legal hold storage, and deletion execution remain deployment responsibilities.
- Audit hashes provide tamper evidence, not an independent immutable ledger or external audit certification.
- Workflow approval remains a human action; no legally binding environmental decision is automated.

## Acceptance criteria

A Phase 3 acceptance run must execute the Phase 3 tests, the full Python test suite, Ruff, and mypy. A green result is evidence for the tested commit only.

## Next phase boundary

Production Phase 4 work should connect these primitives to persistent PostgreSQL models, API authorization, customer-configurable regulatory ingestion, real analyst queues, retention execution, and integration tests against deployed services.
