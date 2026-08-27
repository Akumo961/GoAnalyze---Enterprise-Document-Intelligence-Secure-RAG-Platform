# GoAnalyze Government — Procurement Readiness & Commercial Packaging

**Status:** Proposed commercial strategy. This document is not a procurement commitment, legal opinion, pricing quote, or representation of government eligibility.

## 1. Product positioning

GoAnalyze Government is positioned as decision-support software for environmental document intelligence. The platform is designed to assist analysts with document ingestion, evidence retrieval, grounded AI assistance, regulatory-knowledge mapping, review workflows, and auditable human decisions.

It is not designed to autonomously make legally binding environmental decisions.

## 2. Separation of commercial scope

| Layer | Responsibility | Commercial treatment |
|---|---|---|
| Core Platform | Ingestion, document intelligence, retrieval, RAG, workflow, audit, security controls, observability | Product/software license or subscription |
| Government Configuration | Roles, queues, taxonomies, workflows, retention policies, UI configuration | Implementation/configuration services |
| Environment Integrations | IAM, SSO, object storage, search, workflow systems, data exchanges, monitoring | Integration/professional services |
| Customer Data | Customer documents, metadata, audit data, tenant content | Customer-controlled data; governed by contract and deployment architecture |
| Regulatory Knowledge | Customer-approved authoritative sources, versioning, applicability and provenance | Data onboarding/knowledge-management service; source authority remains with customer |
| Customer-specific extensions | Custom workflows, connectors, reports and policy configuration | Professional services / change orders |

## 3. Proposed commercial packages

### Tier 1 — Pilot

Purpose: establish evidence before a larger commitment.

Typical scope:
- one controlled environment
- synthetic data for demonstrations and/or a customer-approved limited dataset
- selected document classes
- limited analyst workflow
- baseline and post-pilot measurements
- security/privacy assessment appropriate to the pilot
- acceptance criteria agreed before execution

Commercial components:
- pilot license/subscription
- implementation
- configuration
- onboarding/training
- optional integration work

**Pricing:** to be determined through a real scope, procurement mechanism, deployment model, service levels, and customer requirements. No price is asserted here.

### Tier 2 — Department deployment

Purpose: operational deployment for one department or business unit.

Potential scope:
- production deployment in the customer's selected environment
- multiple workflows and document classes
- enterprise identity integration
- regulatory knowledge onboarding
- operational monitoring
- backup/recovery design
- analyst and administrator training
- support and maintenance
- measurable service levels agreed contractually

Commercial components:
- software subscription/license
- implementation and integration
- security hardening/assessment services
- training
- support and maintenance
- optional infrastructure services

### Tier 3 — Enterprise / multi-ministry program

Purpose: multi-year transformation across multiple organizations or ministries.

Potential scope:
- multiple isolated tenants or organizational domains
- shared platform governance with delegated administration
- multiple regulatory knowledge domains
- enterprise integrations
- high-availability/disaster-recovery architecture
- security operations and continuous assurance
- migration and change management
- training at scale
- service desk/support
- roadmap and product evolution

Commercial components can include:
- enterprise software rights/subscriptions
- implementation program
- integration program
- infrastructure/cloud services where contractually appropriate
- security and assurance services
- data/knowledge onboarding
- training/change management
- support and maintenance
- professional services and agreed enhancements

## 4. Deployment models

### Government-controlled cloud

The customer operates or controls the target cloud environment. GoAnalyze supplies application artifacts, configuration guidance, security requirements, and operational documentation. Exact cloud services and responsibilities must be agreed for the target environment.

### Private cloud

GoAnalyze can be packaged for an isolated private-cloud deployment subject to validation of the target Kubernetes/container/storage/identity stack.

### On-premises / isolated environment

The architecture can support an offline or restricted-network operating model, but every required dependency must be validated for the customer's exact environment. External services must not be assumed available.

### Vendor-operated SaaS/private cloud

A managed model may be offered where contractually and legally appropriate. Data residency, access, support, security operations, backup, incident response, and customer exit requirements must be explicitly contracted.

## 5. Contract/service building blocks

A future procurement response could separate:

1. software licensing/subscription
2. implementation
3. integration
4. deployment/infrastructure
5. data migration and knowledge onboarding
6. security/privacy assurance
7. training and change management
8. support and maintenance
9. optional professional services
10. roadmap/product enhancements

This structure makes a multi-year program economically understandable without claiming that any particular procurement will use it.

## 6. Potential multi-million-dollar program logic

A program approaching several million dollars would need to be justified by real scope and outcomes, not by repository size or feature count. A credible commercial structure could combine software, implementation, enterprise integrations, infrastructure, security/assurance, knowledge onboarding, training, support, and expansion over multiple years.

A ~$9M program should therefore be treated as a **hypothetical program-scale scenario**, not as a valuation of this repository.

For such a program to be credible, a buyer would reasonably need evidence such as:

- successful pilot with measured baseline-to-outcome improvement
- security and privacy assessments appropriate to the information handled
- authoritative regulatory-source governance and provenance
- validated integrations with target government systems
- demonstrated tenant isolation and authorization controls
- operational reliability and recovery evidence
- documented support and incident-management capability
- realistic implementation/migration plan
- adoption and training plan
- transparent total-cost model
- contractual acceptance criteria and measurable service levels
- supplier capacity and procurement eligibility established separately from the software

## 7. Procurement-readiness evidence checklist

| Evidence | Current position |
|---|---|
| Product architecture | Implemented/documented in repository |
| Synthetic stakeholder demo | Implemented and CI-tested |
| Business-value telemetry | Implemented and CI-tested |
| Government procurement strategy | This document; proposed |
| Government customer | Not claimed |
| Government deployment | Not claimed |
| Government approval/accreditation | Not claimed |
| Security certification | Not claimed |
| Legal/privacy compliance determination | Not claimed; requires assessment |
| Production SLA | Not claimed |
| Production-scale performance | Not verified |
| Reference customer outcomes | Not claimed |
| Supplier/procurement eligibility | Not established by repository |
| Authoritative Québec regulatory corpus | Not bundled; customer-authoritative onboarding required |

## 8. Buyer evaluation path

A credible sales path should be evidence-led:

**discovery → controlled demo → pilot → security/privacy assessment → integration validation → measured acceptance → production deployment → expansion**

The repository should never be presented as evidence of capabilities that have not been executed and independently evaluated.

## 9. Pricing principle

Pricing should be derived from scope, users/workload, deployment model, service levels, integration complexity, data/knowledge onboarding, support requirements, security requirements, and contract duration.

Any future prices published by the vendor should be explicitly labeled as commercial proposals or quotes rather than factual market values.
