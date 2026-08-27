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
| Container scan | Trivy at HIGH/CRITICAL | Fails on a matching vulnerability with an available fix; unfixed findings remain reported release risks |
| SBOM | CycloneDX SBOMs for both images | Uploads artifacts only after generation succeeds |

The backend job provisions PostgreSQL and Redis service containers. The separate integration workflow also exercises migrations and health/readiness endpoints against PostgreSQL and Redis.

## Evidence rules

- Do not use a passing historical run to assert a later commit passes.
- A configured workflow is **YELLOW** until it has a successful run for the candidate commit.
- A failed, cancelled, skipped, or unavailable run is **RED** for release evidence.
- Coverage percentage is a regression floor, not a government-production coverage claim.
- Dependency and container scanners identify known issues; they do not replace threat modelling, code review, penetration testing, or supply-chain review.
- The container gate uses Trivy's ignore-unfixed option. This does not accept an unfixed vulnerability for production; it keeps non-remediable base-image findings visible while enforcing remediable findings.

## Current verified candidate

Candidate commit: `1df6e351e2efa801b437de0f6f3695dcbf3ebaa6` on `codex/phase12-quality-gate-hardening`.

GitHub Actions evidence for this candidate:

- **Quality Gates #38 — SUCCESS**: frontend quality gates, backend quality gates, security/SBOM/container gates.
- **CI #143 — SUCCESS**.
- **Phase 10 Acceptance #47 — SUCCESS**.

The successful Quality Gates run verified the configured pytest, Ruff, mypy, Bandit, API validation, dependency scanning, frontend lint/build, production image builds, CycloneDX SBOM generation, and Trivy HIGH/CRITICAL container gates. The security/container job completed successfully after the production images were hardened against the previously detected remediable base-image findings.

These results verify the candidate commit only. They do **not** establish production approval, regulatory compliance, penetration-test completion, or government accreditation.

## Current status

**GREEN — VERIFIED FOR PHASE 12 AUTOMATED QUALITY-GATE EXECUTION.**

Remaining release evidence is tracked separately in `PRODUCTION_READINESS.md`. Items requiring external assessment, operational exercises, authoritative regulatory data, privacy/legal review, or real-service deployment validation remain explicitly outside this Phase 12 green gate.
