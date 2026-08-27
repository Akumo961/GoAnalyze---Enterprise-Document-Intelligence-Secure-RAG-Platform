"""Explainable document classification using transparent lexical rules.

Rules are configuration data rather than claims about Québec law. A customer
can replace them with an approved taxonomy and authoritative classifier later.
Every prediction carries the matched evidence and confidence ceiling.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationRule:
    label: str
    keywords: tuple[str, ...]
    minimum_matches: int = 1


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    confidence: float
    matched_terms: tuple[str, ...]
    method: str = "keyword-rule-v1"
    review_required: bool = True


DEFAULT_RULES = (
    ClassificationRule("environmental_application", ("application", "authorization", "project")),
    ClassificationRule("environmental_study", ("study", "assessment", "impact", "environmental"), 2),
    ClassificationRule("inspection_record", ("inspection", "inspector", "finding", "violation")),
    ClassificationRule("correspondence", ("letter", "correspondence", "subject", "recipient")),
    ClassificationRule("permit_or_authorization", ("permit", "authorization", "condition")),
)


def classify_document(text: str, rules: tuple[ClassificationRule, ...] = DEFAULT_RULES) -> ClassificationResult:
    normalized = text.casefold()
    candidates: list[tuple[ClassificationRule, tuple[str, ...]]] = []
    for rule in rules:
        matches = tuple(keyword for keyword in rule.keywords if keyword.casefold() in normalized)
        if len(matches) >= rule.minimum_matches:
            candidates.append((rule, matches))
    if not candidates:
        return ClassificationResult("unclassified", 0.0, ())
    rule, matches = max(candidates, key=lambda item: (len(item[1]), item[0].label))
    confidence = min(0.95, 0.5 + 0.15 * len(matches))
    return ClassificationResult(rule.label, confidence, matches)
