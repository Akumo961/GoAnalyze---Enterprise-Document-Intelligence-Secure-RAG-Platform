# Production Readiness — Authoritative Status

**Assessment date:** 2026-08-27  
**Scope:** repository inspection and existing recorded evidence. This document supersedes readiness claims in other repository reports; older reports are historical context only.

## Rating definitions

- **GREEN — verified:** evidence identifies an executed test, build, scan, or environment verification and its scope.
- **YELLOW — partially verified:** code/configuration and/or limited automated tests exist, but the production-like claim has not been independently verified.
- **RED — not implemented or not verified:** no sufficient implementation or evidence was located.

## Evidence-backed status

| Area | Status | Evidence and limit |
|---|---|---|
| API authentication, RBAC/ABAC and tenant checks | YELLOW | Implementation and dedicated tests are present; a current independent end-to-end IdP test is not evidenced here. |
| Tamper-evident audit trail | YELLOW | Hash-chain implementation and historical concurrency evidence are documented; current-environment verification was not performed. |
| Secure upload/download controls | YELLOW | Size cap, SHA-256 check, tenant-derived storage keys and safe Content-Disposition code are present; malware scanning is not implemented. |
| RAG evidence/citation checks | YELLOW | Citation document ownership and classification checks are implemented and tests exist; citation factual accuracy against a real model/corpus is not verified. |
| Environmental review | YELLOW | Environmental-review endpoints and tests exist; authoritative Québec regulatory knowledge and legal validation are not evidenced. |
| Backend automated tests | YELLOW | Tests and a coverage-enforcing workflow are present. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| Lint, type checking, API validation | YELLOW | Ruff, mypy and OpenAPI gates are configured. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| Frontend lint/build | YELLOW | npm lint/build gates are configured. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| Dependency, source, and container scanning | YELLOW | pip-audit, npm audit, Bandit and Trivy gates are configured. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| SBOM | YELLOW | SBOM generation is configured for API and frontend images. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| PostgreSQL/Redis CI integration | YELLOW | CI provisions those services and runs migrations/readiness checks. **NOT VERIFIED IN CURRENT ENVIRONMENT** for the candidate commit. |
| OpenSearch, MinIO, Keycloak, malware scanning | RED | No current real-service integration evidence located; malware scanner integration point is not implemented. |
| Kubernetes, Helm and Terraform deployment | YELLOW | Artifacts exist; a government-like deployment/restore exercise is not verified. |
| Québec privacy, security or procurement compliance | RED | Requires formal legal/privacy assessment, security authorization and procurement process; code alone cannot establish it. |
| Disaster recovery, business continuity and penetration testing | RED | No sufficient current evidence located. |

## Release decision

GoAnalyze is **not production approved** by this assessment. It is a security-oriented government-platform candidate with meaningful implemented controls and automated-gate configuration, but it requires successful CI evidence, real dependent-service integration, threat-model/penetration testing, operational exercises, privacy/legal review, and customer-specific regulatory validation before a government production evaluation.

## Scoring method

Scores must be based on evidence, not feature count or market ambition. The present repository evidence supports a provisional **production-readiness score of 42/100**. That score must not be interpreted as certification, compliance confirmation, or authorization to operate.

See [Quality Gates](docs/QUALITY_GATES.md) for the gate definition and evidence rule.
