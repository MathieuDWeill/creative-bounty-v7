from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class Decision(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"

class OpportunityStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUALIFIED = "QUALIFIED"
    PURSUED = "PURSUED"
    READY = "READY"
    WON = "WON"
    LOST = "LOST"

class SourceEvidence(BaseModel):
    url: str
    verified_at: str | None = None
    facts: list[str] = Field(default_factory=list)
    source_kind: str = "official"
    live: bool = False

class Opportunity(BaseModel):
    id: str
    source: str
    title: str
    url: str
    reward: float = Field(ge=0)
    currency: str = "EUR"
    deadline: str
    media_type: str
    deliverables: list[str]
    ai_policy: str
    disclosure_required: bool = False
    commercial_rights_required: bool = True
    policy_evidence: str
    sample: bool = True
    status: OpportunityStatus = OpportunityStatus.DISCOVERED

    # Truthful source/constraint metadata. Defaults preserve old fixtures.
    source_evidence: SourceEvidence | None = None
    ai_permission_explicit: bool | None = None
    ai_prohibition_explicit: bool = False
    requires_paid_plan: bool = False
    mandatory_platform: str | None = None
    entry_cost: float | None = None
    entry_cost_verified: bool = False
    human_review_flags: list[str] = Field(default_factory=list)

class RightsAssessment(BaseModel):
    decision: Decision
    confidence: float = Field(ge=0, le=1)
    reasons: list[str]
    evidence: str

class EconomicAssessment(BaseModel):
    score: float = Field(ge=0, le=100)
    estimated_cost: float = Field(ge=0)
    max_attempts: int = Field(ge=1)
    rationale: list[str]
    pursue: bool

class LedgerEntry(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    kind: str
    amount: float
    currency: str = "EUR"
    reference: str
    note: str = ""

class Attempt(BaseModel):
    attempt: int
    provider: str
    model: str
    score: float
    passed: bool
    cost: float
    asset_path: str
    sha256: str
    feedback: str | None = None

class RunRecord(BaseModel):
    opportunity_id: str
    rights: RightsAssessment
    economics: EconomicAssessment
    attempts: list[Attempt]
    accepted_attempt: int | None
    evidence_dir: str
    mode: str
