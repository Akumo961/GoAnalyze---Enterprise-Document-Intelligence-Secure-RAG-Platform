# GoAnalyze Government — Production Readiness Register

**Status date:** 2026-08-25  
**Rule:** GREEN requires reproducible evidence. YELLOW means partially implemented or verified only in a limited environment. RED means not implemented or not verified.

## Current evidence

| Area | Status | Evidence / limitation |
|---|---|---|
| Authentication | GREEN | Real Keycloak-issued JWTs were exercised; signature, issuer, audience and expiry checks are documented. |
| RBAC/ABAC | GREEN | Tenant, role, classification and purpose checks have regression/live evidence. |
| Tenant isolation | GREEN | Cross-tenant access tests are documented as blocked. |
| Audit integrity | GREEN | Hash-chain concurrency defect was found and fixed; the fix was verified with real PostgreSQL up to 500 concurrent writers. |
| Upload security | GREEN | Size cap, safe Content-Disposition, server-derived storage keys and SHA-256 integrity checks are implemented/tested. |
| Rate limiting | YELLOW | Real Redis behavior was verified for correctness, but production-scale capacity remains unverified. |
| PostgreSQL | YELLOW | Real PostgreSQL integration, backup/restore and concurrency evidence exist; complete production DR/PITR exercise remains open. |
| OpenSearch | YELLOW | Real HTTP integration exists, but a real cluster has not been exercised in this environment. |
| MinIO/S3 | YELLOW | Real SDK integration exists, but real object-storage deployment/load validation remains open. |
| Frontend | YELLOW | Build/lint and dashboard/search/upload routes exist, but the full government analyst workflow is not yet implemented. |
| RAG | RED/YELLOW | Citation-grounded service exists, but the current `rag.py` is not an LLM-backed production RAG pipeline. Retrieval/model evaluation is not established. |
| Regulatory knowledge | YELLOW | Architecture is now explicit; authoritative Québec content is intentionally not bundled or invented. |
| CI | YELLOW | A GitHub Actions workflow exists with pytest, ruff, mypy, frontend checks, image build, SBOM and Trivy steps; successful execution on GitHub must be demonstrated before GREEN. |
| SBOM | GREEN | Backend and frontend CycloneDX SBOM generation was executed with real tooling. |
| Image scanning | RED | Trivy was obtained, but vulnerability-database access was blocked in the recorded environment. |
| Penetration testing | RED | No independent human penetration test has been completed. |
| Privacy/legal assessment | RED | No legal/privacy assessment is claimed by this repository. |
| DR/BCP | RED | Backup evidence exists, but a complete documented recovery exercise, RTO/RPO validation and operational runbook are not yet established. |
| Government production deployment | RED | No government deployment, accreditation, approval or customer production operation is claimed. |

## Important corrections to older reports

Older documents contain both verified evidence and planned/target architecture. In particular, `ARCHITECTURE.md` describes Kafka, Temporal, HA infrastructure and other target components; their presence in an architecture diagram must not be interpreted as proof that those components are fully integrated and production-validated.

`FINAL_PRODUCTION_READINESS.md` itself records a 75/100 score while also recording substantial unverified infrastructure. That score is historical, not a government production approval. This register supersedes it as the authoritative evidence classification.

## Required gates before production claim

1. Run the complete stack from a clean checkout with PostgreSQL, Redis, OpenSearch, object storage and identity provider.
2. Exercise the complete analyst workflow end to end with synthetic data.
3. Establish automated RAG/citation evaluation with a versioned benchmark dataset.
4. Complete threat-model review, penetration testing and remediation.
5. Establish privacy, retention, deletion, access-review and incident-response processes with the customer/legal team.
6. Validate backup, restore, disaster recovery, RTO/RPO and operational runbooks.
7. Execute CI on GitHub and retain build, test, SBOM and vulnerability-scan artifacts.
8. Validate production Kubernetes/Helm/Terraform configuration in a controlled environment.
9. Establish authoritative regulatory-source ingestion and provenance controls.
10. Obtain customer-specific security, privacy, architecture and procurement approvals.

## Decision-support boundary

GoAnalyze Government is decision-support software. It must not autonomously make legally binding environmental decisions. Regulatory mappings, risk scores and recommendations require evidence and human review.
