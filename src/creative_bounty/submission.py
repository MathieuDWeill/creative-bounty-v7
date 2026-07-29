from __future__ import annotations
from pathlib import Path
from .evidence import write_json
from .models import Opportunity, RunRecord


def build_submission_package(op: Opportunity, run: RunRecord, root: str | Path) -> Path:
    status = "READY" if run.accepted_attempt else "BLOCKED"
    package = {
        "schema": "creative-bounty/submission-package-v1",
        "status": status,
        "sample": run.mode == "SAMPLE",
        "opportunity_id": op.id,
        "source_url": op.url,
        "advertised_reward": {"amount": op.reward, "currency": op.currency},
        "ai_rights_decision": run.rights.decision.value,
        "disclosure_required": op.disclosure_required,
        "accepted_attempt": run.accepted_attempt,
        "claim_policy": {
            "reward_is_not_revenue": True,
            "sample_assets_are_not_real_provider_outputs": run.mode == "SAMPLE",
        },
    }
    return write_json(Path(root) / "submission" / "package.json", package)
