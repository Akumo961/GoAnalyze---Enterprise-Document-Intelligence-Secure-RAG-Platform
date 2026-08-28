# Phase 19 — Execution Evidence

**Status:** Evidence framework implemented; results are produced by GitHub Actions and must not be inferred from static documentation.

## Purpose

Phase 19 establishes a reproducible evidence model for GoAnalyze. It distinguishes executed evidence from documentation, mocks, stand-ins, and unavailable infrastructure.

## Evidence states

- **GREEN — Verified:** the check executed successfully in the current CI run and its logs/artifacts are retained.
- **YELLOW — Partially verified:** a component or stand-in was executed, but the requested production dependency or deployment topology was not exercised end-to-end.
- **RED — Not verified:** the check was not executed or failed.

A skipped job is never treated as GREEN.

## Reproducible evidence gates

The Phase 19 workflow executes, where supported by the GitHub runner:

1. Python compilation
2. Full pytest suite
3. Ruff
4. mypy
5. Coverage threshold
6. Bandit
7. pip-audit
8. API/OpenAPI validation
9. Frontend dependency installation
10. Frontend lint
11. Frontend build
12. npm audit
13. Docker image build
14. SBOM generation
15. Container vulnerability scanning
16. Phase 14/15/16/17/18 acceptance scripts when present

The workflow records command output as CI evidence. It does not claim that local execution or a synthetic environment proves production readiness.

## Evidence interpretation

| Area | Required evidence | Status rule |
|---|---|---|
| Tests | Full test command completes successfully | GREEN only on successful execution |
| Static quality | Ruff and mypy execute successfully | GREEN only on successful execution |
| Security | Bandit, dependency audit, container scan execute | GREEN only on successful execution |
| Build | Frontend and backend/container builds execute | GREEN only on successful execution |
| API | OpenAPI/application validation executes | GREEN only on successful execution |
| Deployment | Real target infrastructure is exercised | YELLOW if only local/CI infrastructure is exercised |
| Disaster recovery | Backup/restore or recovery drill executes | YELLOW/RED unless current evidence exists |
| Performance | Measured benchmark/load test executes | YELLOW unless representative target infrastructure is used |
| Government environment | Customer-controlled environment validation | RED until actually performed |

## Non-fabrication rule

Phase 19 does not convert historical reports into current execution evidence. Historical evidence may be referenced with its date and scope, but it must not be represented as a fresh test run.

If a dependency cannot be run in the current environment, the result must explicitly state:

`NOT VERIFIED IN CURRENT ENVIRONMENT`

## Acceptance

Phase 19 is complete only when the Phase 19 GitHub workflow itself succeeds and its logs demonstrate that the declared checks actually executed. Any unavailable or environment-dependent capability remains explicitly marked YELLOW or RED.
