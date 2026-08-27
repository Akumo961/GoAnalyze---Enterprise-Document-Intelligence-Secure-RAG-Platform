"""Environmental decision-support rules.

Document profiles in this module describe workflow completeness only; they are
not statements of Québec law. Regulatory obligations come from an explicit,
versioned knowledge base and are surfaced only when their source is marked
``verified``. This prevents demo heuristics from being presented as legal
requirements.
"""
from uuid import UUID

from .models import AIFinding, EnvironmentalReviewRequest, EnvironmentalReviewResult, EvidenceCitation
from .regulatory import KnowledgeStatus, RegulatoryKnowledgeBase

# These are workflow profiles, not legal requirements. A government deployment
# should replace/extend them through governed configuration after validating
# the authoritative submission requirements for the relevant program.
DOCUMENT_PROFILES: dict[str, set[str]] = {
    "industrial_discharge": {"application_form", "site_plan", "technical_report"},
    "waste_management": {"application_form", "site_plan", "technical_report"},
    "water_taking": {"application_form", "technical_report"},
}


class EnvironmentalAuthorizationEngine:
    def __init__(self, knowledge_base: RegulatoryKnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base or RegulatoryKnowledgeBase()

    def review(
        self,
        request: EnvironmentalReviewRequest,
        available_document_types: set[str],
        citations: list[EvidenceCitation],
    ) -> EnvironmentalReviewResult:
        required = DOCUMENT_PROFILES.get(request.project_type, {"application_form"})
        missing = sorted(required - available_document_types)
        jurisdiction = str(request.attributes.get("jurisdiction", ""))
        obligations = self.knowledge_base.obligations_for(jurisdiction)

        mappings: list[AIFinding] = []
        for obligation in obligations:
            source = self.knowledge_base.source(obligation.source_id)
            if source is None or source.status is not KnowledgeStatus.verified:
                continue
            mappings.append(
                AIFinding(
                    finding_type="regulatory_obligation",
                    statement=obligation.title,
                    confidence=1.0,
                    citations=citations[:2],
                    grounded=bool(citations),
                    explanation=(
                        f"Authoritative knowledge item {obligation.obligation_id} from "
                        f"{source.publisher}; source status is verified."
                    ),
                )
            )

        if not mappings:
            mappings.append(
                AIFinding(
                    finding_type="regulatory_knowledge_unavailable",
                    statement="No verified regulatory knowledge pack is loaded for this jurisdiction.",
                    confidence=1.0,
                    citations=[],
                    grounded=False,
                    explanation=(
                        "GoAnalyze will not infer or invent legal requirements. "
                        "Load and govern an authoritative knowledge pack before regulatory mapping is used."
                    ),
                )
            )

        findings = self._compliance_findings(request.case_id, missing, citations)
        risk_score = self._risk_score(missing, findings, has_verified_knowledge=any(
            item.finding_type == "regulatory_obligation" for item in mappings
        ))
        recommendation = self._recommendation(missing, risk_score)
        justification = self._justification(missing, risk_score, mappings)
        return EnvironmentalReviewResult(
            case_id=request.case_id,
            admissible=len(missing) == 0,
            missing_documents=missing,
            regulation_mappings=mappings,
            compliance_findings=findings,
            risk_score=risk_score,
            recommendation=recommendation,
            justification=justification,
            requires_human_review=True,
        )

    def _compliance_findings(self, case_id: UUID, missing: list[str], citations: list[EvidenceCitation]) -> list[AIFinding]:
        if missing:
            return [
                AIFinding(
                    finding_type="missing_document",
                    statement=f"Configured workflow evidence is missing: {name}",
                    confidence=0.96,
                    citations=[],
                    grounded=True,
                    explanation=f"Case {case_id} is incomplete under its configured workflow profile.",
                )
                for name in missing
            ]
        return [
            AIFinding(
                finding_type="admissibility_screen",
                statement="Configured workflow evidence set is complete for this screening profile.",
                confidence=0.88,
                citations=citations[:3],
                grounded=bool(citations),
                explanation="The configured workflow profile contains no missing evidence types.",
            )
        ]

    def _risk_score(self, missing: list[str], findings: list[AIFinding], *, has_verified_knowledge: bool) -> float:
        base = 25.0
        missing_penalty = min(45.0, len(missing) * 9.0)
        confidence_penalty = sum(1.0 - finding.confidence for finding in findings) * 5.0
        knowledge_penalty = 0.0 if has_verified_knowledge else 15.0
        return round(min(100.0, base + missing_penalty + confidence_penalty + knowledge_penalty), 2)

    def _recommendation(self, missing: list[str], risk_score: float) -> str:
        if missing:
            return "request_additional_information"
        if risk_score >= 70:
            return "refer_to_senior_technical_review"
        return "proceed_to_technical_review"

    def _justification(self, missing: list[str], risk_score: float, mappings: list[AIFinding]) -> str:
        mapped = "; ".join(mapping.statement for mapping in mappings)
        prefix = f"{len(missing)} configured evidence item(s) are absent." if missing else "Configured evidence is complete."
        return f"{prefix} Regulatory knowledge state: {mapped}. Risk score: {risk_score}. Human review remains mandatory."


engine = EnvironmentalAuthorizationEngine()
