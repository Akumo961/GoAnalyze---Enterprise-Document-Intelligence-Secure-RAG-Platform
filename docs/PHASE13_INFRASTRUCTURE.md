# Phase 13 — Infrastructure Hardening and Validation

**Status:** implementation complete; CI verification required before release claims.

## Scope

Phase 13 hardens and validates the deployment substrate without claiming that any
specific government environment has been production-validated.

### Implemented

- Docker Compose topology now uses explicit local-only port bindings, service
  health checks, restart policies, persistent volumes, and an isolated
  application network.
- A dedicated `docker-compose.phase13.yml` provides a reproducible smoke
  topology for PostgreSQL, Redis, OpenSearch, MinIO/S3-compatible storage,
  Keycloak, and OpenTelemetry Collector.
- OpenTelemetry Collector has an explicit health endpoint and bounded memory/
  batching processors. The local exporter is intentionally `debug`; production
  telemetry destinations remain environment-specific.
- Helm now deploys both API and frontend workloads, with non-root execution,
  RuntimeDefault seccomp, dropped Linux capabilities, read-only root filesystems,
  disabled service-account token automounting, startup/readiness/liveness probes,
  rolling-update controls, PDB, HPA, TLS ingress, and a namespace-scoped network
  policy.
- Helm configuration references externally managed Kubernetes Secrets rather than
  embedding credentials in chart values.
- Terraform uses a dedicated namespace with Kubernetes Pod Security labels and
  an atomic, waited Helm release. Cluster credentials remain external to source
  control and Terraform configuration.
- Nginx remains the edge reverse-proxy configuration with TLS, security headers,
  upload-size control, and coarse edge rate limiting. CI validates its syntax
  against an ephemeral test certificate.
- CI now validates Compose configuration, starts the infrastructure smoke
  topology, verifies service health, renders/lints Helm, validates rendered
  Kubernetes manifests, runs Terraform formatting/validation, and validates
  Nginx syntax.

## Verification policy

A configuration file is not treated as operational evidence merely because it
exists. Phase 13 uses the following evidence levels:

- **GREEN:** an automated test or build actually executed and passed.
- **YELLOW:** implementation exists and has static validation, but the target
  deployment environment or real external service has not been exercised.
- **RED:** no sufficient implementation or execution evidence exists.

The smoke topology uses intentionally synthetic credentials and local-only
services. It proves container/service startup and endpoint reachability; it does
**not** prove production capacity, high availability, security authorization,
backup/restore, disaster recovery, or government accreditation.

## Deployment modes

| Mode | Phase 13 position |
|---|---|
| Local/demo Compose | Supported for reproducible infrastructure smoke testing. |
| Private cloud Kubernetes | Helm/Terraform artifacts prepared; target-cluster validation remains required. |
| Government-controlled cloud | Architecture is compatible in principle; identity, network, storage, key management, monitoring, and organizational controls require target-specific validation. |
| On-premises / isolated | Helm/Terraform can be adapted; image registry, DNS, PKI, identity, storage, observability and offline supply-chain processes require target-specific validation. |

## Explicit non-claims

Phase 13 does not claim:

- production validation of OpenSearch, MinIO, Keycloak, Kafka, Temporal or
  OpenTelemetry in a government environment;
- a completed Kubernetes deployment;
- disaster-recovery or backup/restore success;
- penetration-test results;
- Québec legal/privacy/security compliance;
- certification or government accreditation.

Those remain separate acceptance activities.
