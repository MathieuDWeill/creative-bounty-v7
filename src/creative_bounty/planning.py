from __future__ import annotations
from pydantic import BaseModel, Field
from .models import Opportunity, RightsAssessment, Decision

class ProductionPlan(BaseModel):
    opportunity_id: str
    modality: str
    prompt: str
    target_quality: float = Field(ge=0, le=100)
    max_attempts: int = Field(ge=1, le=5)
    estimated_max_spend: float = Field(ge=0)
    disclosure_text: str | None = None
    blockers: list[str] = []


def build_plan(op: Opportunity, rights: RightsAssessment, *, max_attempts: int = 3,
               estimated_unit_cost: float = 0.0, target_quality: float = 80.0) -> ProductionPlan:
    blockers: list[str] = []
    if rights.decision is not Decision.PASS:
        blockers.append(f"Rights status is {rights.decision.value}; production is fail-closed.")
    deliverables = ", ".join(op.deliverables)
    prompt = (
        f"Create a submission-ready {op.media_type} asset for this paid creative brief: {op.title}. "
        f"Required deliverables: {deliverables}. Respect the brief faithfully; do not invent brand claims."
    )
    disclosure = "AI-generated media; disclose use of generative AI." if op.disclosure_required else None
    return ProductionPlan(
        opportunity_id=op.id,
        modality=op.media_type.lower(),
        prompt=prompt,
        target_quality=target_quality,
        max_attempts=max_attempts,
        estimated_max_spend=round(max_attempts * estimated_unit_cost, 4),
        disclosure_text=disclosure,
        blockers=blockers,
    )
