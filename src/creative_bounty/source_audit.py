from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from .models import Opportunity


def build_source_snapshot(op: Opportunity) -> dict:
    evidence = op.source_evidence
    payload = {
        "opportunity_id": op.id,
        "title": op.title,
        "url": op.url,
        "sample": op.sample,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source_evidence": evidence.model_dump(mode="json") if evidence else None,
        "assertions": {
            "reward": op.reward,
            "currency": op.currency,
            "deadline": op.deadline,
            "ai_permission_explicit": op.ai_permission_explicit,
            "ai_prohibition_explicit": op.ai_prohibition_explicit,
            "requires_paid_plan": op.requires_paid_plan,
            "mandatory_platform": op.mandatory_platform,
            "entry_cost": op.entry_cost,
            "entry_cost_verified": op.entry_cost_verified,
            "human_review_flags": op.human_review_flags,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["snapshot_sha256"] = sha256(canonical).hexdigest()
    return payload


def write_source_snapshot(op: Opportunity, root: str | Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "source-snapshot.json"
    path.write_text(json.dumps(build_source_snapshot(op), indent=2, ensure_ascii=False), encoding="utf-8")
    return path
