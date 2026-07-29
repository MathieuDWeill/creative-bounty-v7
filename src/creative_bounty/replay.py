from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .audit_receipt import verify_receipt
from .decision_certificate import verify_certificate

@dataclass(frozen=True)
class ReplayResult:
    opportunity_id: str
    mode: str
    audit_verified: bool
    certificate_verified: bool
    accepted_attempt: int | None
    event_count: int
    generation_count: int
    errors: tuple[str, ...]

    @property
    def verified(self) -> bool:
        return self.audit_verified and self.certificate_verified and not self.errors

def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def replay_evidence(root: str | Path) -> ReplayResult:
    """Reconstruct a completed evidence bundle without calling a provider.

    Replay is deliberately read-only. It validates the portable audit receipt,
    decision certificate, run metadata and event log. It never regenerates media
    and therefore never incurs provider cost.
    """
    root = Path(root)
    errors: list[str] = []
    run_path = root / "run.json"
    cert_path = root / "decision-certificate.json"
    if not run_path.exists():
        raise FileNotFoundError(run_path)
    if not cert_path.exists():
        raise FileNotFoundError(cert_path)

    run = _read_json(run_path)
    cert = _read_json(cert_path)
    audit_ok, audit_errors = verify_receipt(root)
    errors.extend(audit_errors)

    cert_ok = verify_certificate(cert)
    if not cert_ok:
        errors.append("decision certificate verification failed")

    if cert.get("opportunity_id") != run.get("opportunity_id"):
        errors.append("certificate/run opportunity mismatch")
    if cert.get("mode") != run.get("mode"):
        errors.append("certificate/run mode mismatch")

    events_path = root / "events.jsonl"
    event_count = 0
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)
                event_count += 1
    else:
        errors.append("events.jsonl missing")

    attempts = run.get("attempts") or []
    accepted = run.get("accepted_attempt")
    if accepted is not None and accepted not in [a.get("attempt") for a in attempts]:
        errors.append("accepted attempt missing from run attempts")

    return ReplayResult(
        opportunity_id=str(run.get("opportunity_id")),
        mode=str(run.get("mode")),
        audit_verified=audit_ok,
        certificate_verified=cert_ok,
        accepted_attempt=accepted,
        event_count=event_count,
        generation_count=len(attempts),
        errors=tuple(errors),
    )
