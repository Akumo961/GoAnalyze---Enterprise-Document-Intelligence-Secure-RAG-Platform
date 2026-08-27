# Phase 13 — Infrastructure Evidence

Status: **IMPLEMENTED; CI VERIFICATION REQUIRED**

## Scope

Phase 13 covers the infrastructure layer only. It does not constitute production certification or proof that every target environment has been deployed successfully.

### Implemented

- Docker Compose application configuration validation.
- Reproducible infrastructure smoke topology for PostgreSQL, Redis, OpenSearch, MinIO, Keycloak, and OpenTelemetry Collector.
- Docker health checks for infrastructure services.
- Helm linting and Kubernetes manifest rendering.
- Strict Kubernetes schema validation with kubeconform.
- Terraform formatting and validation.
- Terraform-managed Kubernetes namespace with Pod Security Admission `restricted` labels.
- Terraform Helm release configured for atomic deployment, rollback-on-failure semantics, waits, and a bounded timeout.
- Helm security controls including restricted pod security settings, non-root execution, seccomp, read-only filesystems, resource controls, probes, HPA/PDB, ingress TLS configuration, and NetworkPolicy where enabled by values.
- Nginx syntax validation using an ephemeral test certificate.
- Nginx TLS 1.2/1.3 configuration, security headers, upload-size limit, and coarse edge rate limiting.

## Verification policy

A capability is marked **verified** only when the corresponding GitHub Actions job completes successfully on the candidate commit. Static source inspection alone is not treated as runtime evidence.

### Current evidence states

- Docker Compose model: verified only by the `docker compose config` CI step.
- Infrastructure runtime: verified only when the Phase 13 smoke topology starts successfully and all health checks pass in CI.
- Helm: verified only by `helm lint` plus rendered-manifest validation.
- Terraform: verified only by `terraform fmt -check`, `terraform init -backend=false`, and `terraform validate`.
- Nginx: verified only by `nginx -t` in the CI container.
- Kubernetes deployment: **NOT VERIFIED IN CURRENT ENVIRONMENT** unless an actual cluster deployment job is present and passing.
- Managed-cloud networking/storage/identity: **NOT VERIFIED IN CURRENT ENVIRONMENT**.

## Important limitations

The smoke topology intentionally uses development/test settings (for example, disabled OpenSearch security and Keycloak `start-dev`). These settings are suitable for CI validation only and must not be interpreted as a production security configuration.

No claim is made here regarding government approval, Québec legal/privacy compliance, certification, penetration-test status, high-availability guarantees, disaster recovery objectives, or production operational readiness.
