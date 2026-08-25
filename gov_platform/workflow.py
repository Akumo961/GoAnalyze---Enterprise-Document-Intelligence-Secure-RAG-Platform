"""Human-controlled environmental review workflow state machine."""
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum


class CaseState(StrEnum):
    intake = "intake"
    admissibility = "admissibility"
    technical_review = "technical_review"
    legal_review = "legal_review"
    awaiting_information = "awaiting_information"
    recommendation = "recommendation"
    approved = "approved"
    rejected = "rejected"


class WorkflowRole(StrEnum):
    analyst = "analyst"
    decision_officer = "decision_officer"


@dataclass(frozen=True)
class Transition:
    actor: str
    role: WorkflowRole
    from_state: CaseState
    to_state: CaseState
    reason: str


_ALLOWED: dict[CaseState, frozenset[CaseState]] = {
    CaseState.intake: frozenset({CaseState.admissibility}),
    CaseState.admissibility: frozenset({CaseState.technical_review, CaseState.awaiting_information}),
    CaseState.technical_review: frozenset({CaseState.legal_review, CaseState.awaiting_information}),
    CaseState.legal_review: frozenset({CaseState.recommendation, CaseState.awaiting_information}),
    CaseState.awaiting_information: frozenset({CaseState.admissibility, CaseState.technical_review}),
    CaseState.recommendation: frozenset({CaseState.approved, CaseState.rejected}),
    CaseState.approved: frozenset(),
    CaseState.rejected: frozenset(),
}


@dataclass
class ReviewCase:
    case_id: str
    tenant_id: str
    state: CaseState = CaseState.intake
    transitions: list[Transition] = field(default_factory=list)

    def transition(
        self,
        actor: str,
        target: CaseState,
        reason: str,
        role: WorkflowRole = WorkflowRole.analyst,
    ) -> Transition:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor_and_reason_required")
        if target in {CaseState.approved, CaseState.rejected} and role is not WorkflowRole.decision_officer:
            raise ValueError("decision_officer_role_required")
        if target not in _ALLOWED[self.state]:
            raise ValueError(f"invalid_transition:{self.state}->{target}")
        event = Transition(actor, role, self.state, target, reason)
        self.transitions.append(event)
        self.state = target
        return event


def allowed_next_states(state: CaseState) -> tuple[CaseState, ...]:
    return tuple(sorted(_ALLOWED[state], key=str))


def validate_transition_history(transitions: Iterable[Transition]) -> bool:
    previous: CaseState | None = None
    for transition in transitions:
        if previous is not None and transition.from_state != previous:
            return False
        if transition.to_state in {CaseState.approved, CaseState.rejected} and transition.role is not WorkflowRole.decision_officer:
            return False
        if transition.to_state not in _ALLOWED[transition.from_state]:
            return False
        previous = transition.to_state
    return True
