"""B2 governance helpers. No mutation happens unless called explicitly."""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class B2GovernancePlan:
    bucket: str
    evidence_prefix: str = "evidence/"
    intermediates_prefix: str = "intermediates/"
    retain_evidence_days: int = 30
    expire_intermediates_days: int = 7
    object_lock_requested: bool = False


def plan_from_env() -> B2GovernancePlan:
    return B2GovernancePlan(
        bucket=os.getenv("B2_BUCKET", ""),
        retain_evidence_days=int(os.getenv("B2_EVIDENCE_RETENTION_DAYS", "30")),
        expire_intermediates_days=int(os.getenv("B2_INTERMEDIATE_EXPIRY_DAYS", "7")),
        object_lock_requested=os.getenv("B2_OBJECT_LOCK", "false").lower()=="true",
    )

def describe_plan(plan: B2GovernancePlan) -> dict:
    return {
        "bucket":plan.bucket,
        "evidence_prefix":plan.evidence_prefix,
        "intermediates_prefix":plan.intermediates_prefix,
        "evidence_retention_days":plan.retain_evidence_days,
        "intermediate_expiry_days":plan.expire_intermediates_days,
        "object_lock_requested":plan.object_lock_requested,
        "truth_note":"Object Lock is reported as active only after remote verification; requested != enabled.",
    }
