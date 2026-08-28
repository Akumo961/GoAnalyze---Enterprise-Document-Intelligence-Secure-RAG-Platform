# Phase 22 — Human Accountability and Decision Governance

## Status

**Implemented governance control.** This phase formalizes the operational boundary established in Phase 21: GoAnalyze Government is decision-support software, not an autonomous environmental decision-maker.

## Mandatory human accountability

GoAnalyze may prepare evidence, classify documents, identify potential gaps, retrieve source material, summarize records, map evidence to configured regulatory knowledge, and prioritize analyst review.

GoAnalyze must not autonomously issue, approve, deny, amend, suspend, revoke, or otherwise finalize a legally consequential environmental authorization or enforcement decision.

A consequential disposition requires an explicitly authorized human action. The system records that action separately from AI-generated analysis.

## Decision record model

A decision-support record should preserve, where implemented by the deployment:

- case/application identifier;
- human actor identifier;
- actor role/authorization context;
- timestamp;
- action/disposition;
- evidence references considered;
- relevant AI output presented to the actor;
- uncertainty/warnings presented;
- optional human rationale;
- audit-event identifier.

AI output is never itself treated as the human decision.

## Human override

Authorized analysts must be able to reject, correct, or override AI-generated classifications, evidence mappings, missing-evidence findings, summaries, and priority recommendations. Overrides should be auditable.

## Separation of authority

The AI layer must not receive credentials or tool permissions that allow it to directly perform legally consequential state transitions. Consequential workflow APIs must enforce authorization independently of model output.

## Regulatory interpretation

The platform must distinguish configured authoritative customer sources from demonstration/sample knowledge. If authoritative regulatory material is unavailable, the system must communicate that limitation rather than invent an obligation.

## Governance evidence

A deployment claiming this control should demonstrate it with automated tests and an end-to-end scenario showing:

1. AI analysis is generated.
2. Evidence and uncertainty are presented.
3. A human reviewer is required.
4. The human can accept, reject, or correct the recommendation.
5. The human action is independently authorized.
6. The resulting audit trail identifies the human actor and action.

## Verification boundary

This document and automated repository tests are engineering evidence only. They do not constitute legal advice, privacy-law compliance, security certification, government approval, or an external AI-risk assessment.
