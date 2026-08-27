# Phase 13 — Infrastructure Evidence

Status: **IMPLEMENTED; CI VERIFICATION REQUIRED**

Phase 13 covers Docker/Compose, Kubernetes/Helm, Terraform, Nginx, and the supporting infrastructure topology. It does not constitute production certification or prove deployment in a government environment.

## Implemented

- Docker Compose configuration validation.
- Reproducible smoke topology for PostgreSQL, Redis, OpenSearch, MinIO, Keycloak, and OpenTelemetry Collector.
- Docker health checks for infrastructure services.
- Helm linting and Kubernetes rendering.
- Strict Kubernetes schema validation with kubeconform.
- Terraform formatting and validation.
- Terraform-managed namespace with Pod Security Admission `restricted` labels.
- Atomic Terraform Helm deployment with waits and bounded timeout.
- Kubernetes security hardening including non-root execution, seccomp, read-only filesystems, resources, probes, HPA/PDB, TLS ingress configuration, and NetworkPolicy where enabled.
- Nginx syntax validation using an ephemeral test certificate.
- Nginx TLS 1.2/1.3, security headers, upload-size limit, and coarse edge rate limiting.

## Verification policy

A capability is **verified** only when its GitHub Actions job completes successfully on the candidate commit. Static source inspection is not runtime evidence.

- Docker Compose: verified by `docker compose config` and smoke-topology CI steps.
- Infrastructure runtime: verified only when the smoke topology starts successfully and all service health checks pass.
- Helm/Kubernetes manifests: verified by Helm lint/render plus kubeconform.
- Terraform: verified by `terraform fmt -check`, `terraform init -backend=false`, and `terraform validate`.
- Nginx: verified by `nginx -t` in CI.
- Actual Kubernetes deployment: **NOT VERIFIED IN CURRENT ENVIRONMENT** unless a real cluster deployment job is present and passing.
- Managed-cloud networking/storage/identity: **NOT VERIFIED IN CURRENT ENVIRONMENT**.

## Important limitations

The smoke topology uses CI-only development settings (including disabled OpenSearch security and Keycloak `start-dev`). These settings must not be used as a production security configuration.

No claim is made here regarding government approval, Québec legal/privacy compliance, certification, penetration-test status, high-availability guarantees, disaster-recovery objectives, or production operational readiness.
