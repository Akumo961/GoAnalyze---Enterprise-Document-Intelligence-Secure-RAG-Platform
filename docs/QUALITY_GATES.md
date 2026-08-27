# Quality Gates

This document describes the automated Phase 12 gates. A gate is **configured**, not verified, until a GitHub Actions run for the relevant commit succeeds. Artifacts are retained by GitHub Actions according to repository policy.

## Required pull-request gates

| Gate | Workflow job / command | Failure behavior |
|---|---|---|
| Python tests and coverage | `pytest --cov=gov_platform --cov-fail-under=70` | Fails below 70% or on test failure |
| Python lint | `ruff check gov_platform tests migrations scripts` | Fails on lint finding |
| Static typing | `mypy gov_platform --ignore-missing-imports` | Fails on type finding |
| Source security scan | `bandit -r gov_platform -q` | Fails on a Bandit finding |
| Dependency scan | `pip-audit`; `npm audit --audit-level=high` | Fails for reported dependency vulnerability at the configured threshold |
| API validation | FastAPI OpenAPI generation assertion | Fails when OpenAPI cannot be produced |
| Frontend lint/build | `npm run lint`; `npm run build` | Fails on either command |
| Container build | Production API and frontend images | Fails on Docker build error |
| Container scan | Trivy at HIGH/CRITICAL | Fails on matching known vulnerability |
| SBOM | CycloneDX SBOMs for both images | Uploads artifacts only after generation succeeds |

The backend job provisions PostgreSQL and Redis service containers. The separate integration workflow also exercises migrations and health/readiness endpoints against PostgreSQL and Redis.

## Evidence rules

- Do not use a passing historical run to assert a later commit passes.
- A configured workflow is **YELLOW** until it has a successful run for the candidate commit.
- A failed, cancelled, skipped, or unavailable run is **RED** for release evidence.
- Coverage percentage is a regression floor, not a government-production coverage claim.
- Dependency and container scanners identify known issues; they do not replace threat modelling, code review, penetration testing, or supply-chain review.

## Current status

**NOT VERIFIED IN CURRENT ENVIRONMENT:** This Phase 12 change has not been executed by GitHub Actions from this environment. Review the workflow run and its artifacts before treating any gate as passing.
