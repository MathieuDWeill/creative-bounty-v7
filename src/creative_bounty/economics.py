from .models import EconomicAssessment, Opportunity, RightsAssessment, Decision


def assess_economics(
    op: Opportunity,
    rights: RightsAssessment,
    available_budget: float = 0.0,
    *,
    estimated_unit_cost: float = 0.0,
) -> EconomicAssessment:
    """Transparent zero-capital prioritization heuristic.

    It never estimates probability of winning. Mandatory paid access is a hard
    rejection regardless of advertised prize size.
    """
    reward_score = min(45.0, (op.reward / 500.0) * 45.0)
    media_complexity = {"image": 8, "audio": 12, "video": 22, "multimodal": 28}.get(op.media_type.lower(), 18)
    rights_bonus = {Decision.PASS: 25, Decision.REVIEW: 0, Decision.REJECT: -100}[rights.decision]
    max_attempts = 3
    generation_cost = round(max_attempts * max(0.0, estimated_unit_cost), 4)

    mandatory_access_cost = 0.0
    hard_zero_capital_barrier = False
    access_reason = None
    if op.requires_paid_plan:
        hard_zero_capital_barrier = True
        access_reason = f"Mandatory paid access is required{f' on {op.mandatory_platform}' if op.mandatory_platform else ''}."
    elif op.entry_cost_verified and (op.entry_cost or 0) > 0:
        mandatory_access_cost = float(op.entry_cost or 0)
        hard_zero_capital_barrier = mandatory_access_cost > available_budget
        access_reason = f"Verified mandatory entry cost is {mandatory_access_cost:.2f} {op.currency}."

    estimated_cost = round(generation_cost + mandatory_access_cost, 4)
    budget_penalty = 0 if estimated_cost <= available_budget else min(25.0, 10.0 + estimated_cost * 10.0)
    review_penalty = 15.0 if op.human_review_flags else 0.0
    score = max(0.0, min(100.0, 45 + reward_score + rights_bonus - media_complexity - budget_penalty - review_penalty))

    pursue = (
        rights.decision == Decision.PASS
        and estimated_cost <= available_budget
        and not hard_zero_capital_barrier
        and not op.human_review_flags
        and score >= 60
    )
    rationale = [
        f"Reward contributes {reward_score:.1f}/45 points.",
        f"Media complexity penalty is {media_complexity} points.",
        f"Rights decision contributes {rights_bonus} points.",
        f"Maximum planned generation spend is {generation_cost:.4f} {op.currency}.",
        f"Available authorized generation budget is {available_budget:.4f} {op.currency}.",
        "No probability of winning is fabricated; this is a deterministic prioritization heuristic.",
    ]
    if access_reason:
        rationale.append(access_reason)
    if hard_zero_capital_barrier:
        rationale.append("ZERO-CAPITAL HARD STOP: the opportunity cannot be pursued with current funds.")
    if op.human_review_flags:
        rationale.append("Human-review flags: " + "; ".join(op.human_review_flags))
    return EconomicAssessment(
        score=round(score, 1),
        estimated_cost=estimated_cost,
        max_attempts=max_attempts,
        rationale=rationale,
        pursue=pursue,
    )
