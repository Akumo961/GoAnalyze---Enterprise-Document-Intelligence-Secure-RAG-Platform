# Enterprise Deployment — Phase 10

## Status

This document describes the deployment architecture and the controls that are implemented in the repository. Infrastructure reachability, customer networking, identity federation, managed-service configuration, disaster recovery, and security accreditation remain environment-specific validation activities.

## Supported deployment models

### Government-controlled cloud

**Architecture:** containerized API/frontend services behind an approved ingress or reverse proxy, PostgreSQL, Redis, object storage, search, identity provider, and telemetry collector managed by the government or an approved provider.

**Dependencies:** Kubernetes or an equivalent container platform; PostgreSQL; Redis; S3-compatible object storage; OpenSearch-compatible search; OIDC identity provider; secrets manager; TLS certificates; centralized logs/metrics/traces.

**Assumptions:** the government controls network policy, DNS, certificates, identity federation, backup policy, and data residency decisions. Connectivity to external AI providers is optional and must be explicitly approved if used.

**Not verified:** deployment in any Québec government cloud, government security accreditation, data residency, or production service-level objectives.

### Private cloud

**Architecture:** the same containerized platform deployed into a customer-controlled Kubernetes/private-cloud environment. Stateful services may be managed by the customer or supplied as dedicated platform dependencies.

**Dependencies:** Kubernetes, ingress/load balancer, persistent storage, PostgreSQL, Redis, object storage, search, OIDC, secrets management, and observability.

**Assumptions:** the operator supplies resilient storage, backups, certificate management, network segmentation, and identity integration.

**Not verified:** a specific private-cloud distribution or provider.

### On-premises

**Architecture:** application containers and stateful dependencies run inside customer-controlled infrastructure with no required public inbound connectivity.

**Dependencies:** Linux container runtime, Kubernetes or equivalent orchestrator, internal DNS, TLS, persistent storage, PostgreSQL, Redis, S3-compatible object storage, search, and internal OIDC.

**Assumptions:** the customer provides compute capacity, storage, backup/restore, patching, network security, and identity services.

**Not verified:** installation on a specific customer hardware stack.

### Isolated / disconnected environment

**Architecture:** all required runtime images, Python dependencies, frontend assets, model/runtime dependencies, configuration, and deployment charts are staged into an approved internal artifact repository before installation. External network access is not assumed at runtime.

**Dependencies:** internal container registry, package/artifact mirror, internal identity provider, internal object storage/search/database services, and internally reachable telemetry.

**Assumptions:** an offline artifact promotion process exists and all required software licenses permit the deployment model.

**Not verified:** a complete air-gapped installation, offline LLM inference, or offline vulnerability-feed synchronization.

## Production configuration validation

GoAnalyze now provides a fail-closed validator at `scripts/validate_production_config.py` and `gov_platform.production_config`.

Run before deployment:

```bash
python scripts/validate_production_config.py
```

Production validation rejects unsafe configuration including insecure development authentication, disabled rate limiting, disabled tracing, short audit secrets, non-PostgreSQL databases, localhost database targets, insecure object storage transport, and invalid Redis/OpenSearch endpoints.

This validation is configuration validation only. It does **not** prove that external services are reachable, correctly secured, highly available, backed up, or approved for government use.

## Deployment separation

- **Core platform:** application code, APIs, authorization, document processing, retrieval, audit, workflows.
- **Government configuration:** identity, network, retention policy, approved AI providers, telemetry, operational controls.
- **Environment integrations:** customer storage, OCR, malware scanner, search, email, enterprise identity, SIEM.
- **Customer data:** never bundled with the product source repository.
- **Customer regulatory knowledge:** loaded and governed by authorized customer processes.

## Release gate

A production release should require, at minimum: configuration validation, unit/integration tests, security/dependency scans, image scanning, infrastructure review, backup/restore evidence, identity integration validation, and customer-specific privacy/security approval. The repository must not label any of those external activities as completed without evidence.
