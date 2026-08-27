# Testing and Verification Strategy

## Phase 11 scope

Phase 11 expands automated evidence without treating tests as proof of production readiness. A green CI run proves only the checks that actually execute in that run.

| Area | Automated evidence | Current status |
|---|---|---|
| Authentication | JWT/authentication tests and production dev-auth guard | GREEN in CI when executed |
| Authorization | ABAC role, purpose, classification and tenant tests | GREEN in CI when executed |
| Tenant isolation | Cross-tenant denial tests | GREEN in CI when executed |
| Audit integrity | Audit hashing and existing audit-chain tests | PARTIALLY VERIFIED; high-concurrency PostgreSQL evidence remains integration-specific |
| RAG retrieval/grounding | Grounded vs unsupported-answer tests | GREEN; retrieval backend integration remains separate |
| Citation accuracy/integrity | Citation schema and bounded citation tests | GREEN for schema/grounding behavior; factual accuracy requires evaluation corpus |
| Prompt injection | Existing security controls are regression-tested where exposed by the application | PARTIALLY VERIFIED; adversarial corpus coverage remains required |
| Document poisoning | Ingestion/validation regression coverage | PARTIALLY VERIFIED; real malicious-document scanning requires an actual scanner/service |
| Malicious uploads | Document input validation tests | PARTIALLY VERIFIED; malware scanning requires deployment integration |
| API security | Authentication, ABAC and rate-limit tests | GREEN for implemented controls |
| Concurrency | Existing database/audit concurrency coverage plus PostgreSQL CI smoke infrastructure | PARTIALLY VERIFIED in CI; stress levels are environment-dependent |
| Database integrity | SQLite regression suite plus real PostgreSQL migration smoke test in CI | GREEN for migration smoke; full production topology is not claimed |
| Failure recovery | Existing service/error-path tests | PARTIALLY VERIFIED; disaster/failover testing requires deployed dependencies |
| Rate limiting | Dedicated rate-limit tests with fakeredis | GREEN when executed |
| Access-control bypasses | Negative ABAC tests | GREEN for implemented ABAC policy |
| Data leakage | Cross-tenant and authorization regression tests | GREEN for tested policy paths; broader adversarial DLP testing remains required |
| Regression testing | Full `pytest tests/` suite on GitHub Actions | GREEN only when the corresponding CI run is green |

## Real services in CI

The Phase 11 acceptance workflow provisions PostgreSQL 16 and Redis 7 as GitHub Actions service containers. It runs Alembic migrations against the real PostgreSQL service after the Python test suite, rather than treating the database as a mock.

The repository's general CI also builds containers, generates a backend SBOM, performs image vulnerability scanning, and runs frontend/backend quality gates. These are evidence-producing checks, not certification claims.

## What is deliberately not claimed

A passing test suite does **not** establish legal/privacy compliance, malware-scanning effectiveness, production disaster recovery, penetration-test status, citation factual accuracy across a regulatory corpus, or operational readiness at government scale. Those require the corresponding real environment, test corpus, external services, audits, or organizational controls.

## Commands

```bash
python -m pytest tests/ -v
ruff check gov_platform tests migrations
mypy gov_platform --ignore-missing-imports
```
