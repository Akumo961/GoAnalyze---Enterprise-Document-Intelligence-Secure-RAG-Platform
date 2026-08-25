# AI Security and Governance

## Threats

GoAnalyze Government treats uploaded documents as untrusted content. Threats include direct prompt injection, indirect prompt injection, malicious instructions in documents, retrieval manipulation, cross-tenant leakage, unauthorized tool access, unsupported regulatory assertions, hallucinated citations and data exfiltration.

## Required control pattern

1. Authenticate and authorize before retrieval.
2. Apply tenant and attribute filters server-side; never trust model-generated filters.
3. Treat retrieved text as evidence, never as executable instructions.
4. Give models the minimum permissions required for the task.
5. Do not permit the model to directly approve, reject or issue a legally binding environmental decision.
6. Require citations for factual claims where source evidence exists.
7. Refuse or qualify claims when authoritative evidence is unavailable.
8. Log model requests, retrieval identifiers, model/version metadata and analyst overrides subject to customer privacy policy.
9. Evaluate citation correctness, retrieval leakage, refusal behavior and prompt-injection resistance with a versioned test set.

## Evidence taxonomy

- **FACTUAL EVIDENCE:** directly supported by an identified source excerpt.
- **INFERENCE:** a reasoned interpretation derived from evidence.
- **MODEL SUMMARY:** generated synthesis that must remain traceable to evidence.
- **UNCERTAINTY:** explicit indication that evidence is incomplete, conflicting or unavailable.

## Regulatory-source rule

The model must not silently invent regulatory requirements. Regulatory assertions must resolve to a versioned, provenance-bearing source that has been marked authoritative or customer-approved. Unverified/demo sources cannot be represented as authoritative law.

## Governance boundary

The system is decision support. Government personnel retain responsibility for legal and administrative decisions. Security testing, privacy review, legal review and customer-specific governance remain external gates and are not represented as completed by this repository.
