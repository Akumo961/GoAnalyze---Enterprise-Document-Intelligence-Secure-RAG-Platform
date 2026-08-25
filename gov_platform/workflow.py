"""Human-controlled environmental review workflow state machine."""
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable


class CaseState(StrEnum):
    intake = "intake"
    admissibility = "admissibility"
    technical_review = "technical_review"
    legal_review = "legal_review"
    awaiting_information = "awaiting_information"
    recommendation = "recommendation"
    approved = "approved"
    rejected = "rejected"


@dataclass(frozen=True)
class Transition:
    actor: str
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

    def transition(self, actor: str, target: CaseState, reason: str) -> Transition:
        if not actor.strip() or not reason.strip():
            raise ValueError("actor_and_reason_required")
        if target not in _ALLOWED[self.state]:
            raise ValueError(f"invalid_transition:{self.state}->{target}")
        event = Transition(actor, self.state, target, reason)
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
        if transition.to_state not in _ALLOWED[transition.from_state]:
            return False
        previous = transition.to_state
    return True
