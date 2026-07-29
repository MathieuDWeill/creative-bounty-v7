from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class ProviderOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"
    QUALITY_REJECT = "QUALITY_REJECT"

@dataclass(frozen=True)
class ProviderCandidate:
    provider: str
    model: str
    estimated_cost: float
    quality_floor: float = 80.0

@dataclass(frozen=True)
class SimulatedAttempt:
    provider: str
    model: str
    outcome: ProviderOutcome
    cost: float
    accepted: bool

@dataclass(frozen=True)
class ResilienceSimulation:
    attempts: tuple[SimulatedAttempt, ...]
    accepted_provider: str | None
    accepted_model: str | None
    total_cost: float
    exhausted: bool

def simulate_failover(
    candidates: Iterable[ProviderCandidate],
    scripted_outcomes: dict[tuple[str, str], ProviderOutcome],
    *,
    authorized_budget: float,
) -> ResilienceSimulation:
    """Deterministic zero-cost simulation of provider failover.

    This exercises control-plane behavior without claiming a real provider call.
    Every simulated attempt is explicitly labeled and the budget ceiling is
    enforced before the attempt is admitted.
    """
    if authorized_budget < 0:
        raise ValueError("authorized_budget cannot be negative")
    spent = 0.0
    attempts: list[SimulatedAttempt] = []
    accepted_provider = None
    accepted_model = None

    for candidate in candidates:
        if candidate.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative")
        if spent + candidate.estimated_cost > authorized_budget:
            break
        outcome = scripted_outcomes.get(
            (candidate.provider, candidate.model),
            ProviderOutcome.PERMANENT_FAILURE,
        )
        spent += candidate.estimated_cost
        accepted = outcome is ProviderOutcome.SUCCESS
        attempts.append(SimulatedAttempt(
            provider=candidate.provider,
            model=candidate.model,
            outcome=outcome,
            cost=round(candidate.estimated_cost, 4),
            accepted=accepted,
        ))
        if accepted:
            accepted_provider = candidate.provider
            accepted_model = candidate.model
            break

    return ResilienceSimulation(
        attempts=tuple(attempts),
        accepted_provider=accepted_provider,
        accepted_model=accepted_model,
        total_cost=round(spent, 4),
        exhausted=accepted_provider is None,
    )
