# GoAnalyze — Demonstrable Differentiation

**Status:** Phase 17 product-positioning and evidence framework  
**Evidence rule:** This document distinguishes capabilities that are implemented in the repository from capabilities that require pilot or customer evidence. It does not claim market superiority, government approval, certification, customer adoption, or regulatory compliance.

## 1. Product thesis

GoAnalyze is positioned as a decision-support platform for sensitive environmental and regulatory document workflows. Its intended differentiation is not a generic chat interface or an LLM wrapper. The product architecture combines document processing, controlled retrieval, evidence-oriented AI, environmental workflow concepts, access control, auditability, observability, and deployment flexibility.

The human analyst remains accountable for consequential decisions. GoAnalyze must not autonomously issue legally binding environmental decisions.

## 2. Differentiation pillars

| Pillar | What is demonstrable in the repository | What still requires external evidence |
| --- | --- | --- |
| Environmental regulatory workflows | Environmental review/domain modules, evidence and completeness concepts, regulatory knowledge architecture | Validation against authoritative Québec workflows and real analyst requirements |
| Evidence traceability | RAG/retrieval architecture, citation-oriented response structures, audit/event records | Citation precision/recall and analyst acceptance measured on representative datasets |
| Government security architecture | Authentication/authorization, RBAC/ABAC concepts, tenant isolation, audit/security controls and hardened deployment artifacts | Independent security assessment, penetration testing, threat-led validation, organizational accreditation |
| Human-in-the-loop decisions | Review/assignment/decision workflow concepts and human decision telemetry | Validation that operational users can complete end-to-end review safely and efficiently |
| Auditability | Structured audit events and observable human actions | Tamper-resistance validation in the target infrastructure and formal records-management review |
| Regulatory knowledge | Extensible regulatory knowledge model and controlled loading architecture | Authoritative source onboarding, provenance governance, legal review and update operations |
| Deployment flexibility | Docker, Kubernetes/Helm, Terraform and configurable services are present | Customer-environment certification, HA/DR exercises and operational acceptance |
| Explainable AI | Evidence/inference/uncertainty-oriented response design and source references | Measured explanation quality and human-factors validation |
| Measurable workflow value | Phase 15 instrumentation for latency, throughput, review, queue and override signals | Baseline-vs-pilot results using real operational measurements |

## 3. Why this is different from generic RAG

A generic RAG application can retrieve passages and generate an answer. GoAnalyze's intended product boundary adds workflow and governance controls around that capability:

1. **Case/document context** — AI operates inside a document-review workflow rather than an isolated chat experience.
2. **Evidence traceability** — outputs are expected to point back to source material instead of presenting unsupported regulatory assertions as facts.
3. **Regulatory knowledge separation** — customer-authorized regulatory content is treated as managed knowledge with provenance, jurisdiction and lifecycle concerns.
4. **Human accountability** — review queues and recorded human decisions preserve an analyst decision point for consequential work.
5. **Security boundaries** — tenant, role and attribute controls are part of retrieval and workflow authorization, not only UI permissions.
6. **Auditability** — security, workflow and human actions are intended to produce an inspectable history.
7. **Operational measurement** — the platform instruments workflow and AI behavior so a pilot can measure real outcomes rather than relying on assumed ROI.
8. **Deployment control** — the architecture supports customer-controlled deployment patterns instead of requiring a public multi-tenant SaaS model.

These are architectural/product differentiators, not proof of superiority. Comparative claims require a documented benchmark against named alternatives.

## 4. Evidence hierarchy

Commercial claims should use the strongest available evidence:

- **Level A — Automated repository evidence:** CI tests, static analysis, acceptance checks and reproducible build artifacts.
- **Level B — Controlled technical evaluation:** security tests, retrieval/citation benchmarks, load tests and failure-recovery exercises using representative synthetic data.
- **Level C — Pilot evidence:** measured analyst workflow outcomes against a documented baseline.
- **Level D — Independent/customer evidence:** external security assessment, customer validation, procurement evaluation or third-party assurance.

GoAnalyze must not use Level A evidence to imply Level C or D outcomes.

## 5. Recommended proof package for a Québec buyer

A serious evaluation should demonstrate, using synthetic data first and authorized representative data later:

- end-to-end environmental application intake;
- document classification and completeness review;
- evidence retrieval with source references;
- regulatory obligation mapping using an explicitly versioned knowledge set;
- missing-evidence detection;
- analyst review and human decision capture;
- cross-tenant authorization tests;
- audit-history reconstruction;
- prompt-injection and malicious-document tests;
- measured latency and throughput;
- citation coverage and unsupported-claim rate;
- human override/acceptance rate;
- operational monitoring and incident evidence.

## 6. Claims we deliberately do not make

The repository does not establish that GoAnalyze:

- is superior to every competing RAG/document platform;
- has Québec government customers;
- has been approved by MELCCFP or another ministry;
- is certified under any security or privacy standard;
- satisfies a legal/regulatory obligation without legal review;
- has achieved a particular ROI or productivity improvement;
- is ready for unrestricted production use in a government environment;
- can autonomously make legally binding environmental decisions.

## 7. Product moat to build during a pilot

The most defensible long-term assets are expected to be operational rather than merely model-based:

- validated environmental workflow configurations;
- curated, provenance-controlled regulatory knowledge;
- evaluation datasets and citation benchmarks;
- integration adapters;
- security and audit controls validated in customer infrastructure;
- workflow telemetry and baseline history;
- analyst feedback loops;
- deployment automation and operational runbooks.

These assets should be developed from authorized customer requirements and data-governance processes, not fabricated for marketing.
