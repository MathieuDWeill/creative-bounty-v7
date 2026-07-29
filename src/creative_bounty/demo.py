from __future__ import annotations
import json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .economics import assess_economics
from .evidence import sha256, write_json
from .ledger import Ledger
from .events import Event, EventLog
from .planning import build_plan
from .provenance import verify_sample_asset
from .source_audit import write_source_snapshot
from .submission import build_submission_package
from .models import Attempt, Opportunity, RunRecord
from .rights import assess_rights
from .audit_receipt import write_receipt
from .decision_certificate import build_certificate, write_certificate
from .state_machine import Lifecycle, transition

SCORES=[54.0, 88.0, 92.0]

def _make_asset(path: Path, title: str, attempt: int, score: float, passed: bool):
    img=Image.new("RGB", (1280,720), (12,16,28))
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((70,70,1210,650), radius=40, fill=(23,31,51), outline=(95,108,255), width=3)
    d.text((120,120), "CREATIVE//BOUNTY", fill="white")
    d.text((120,190), title[:70], fill=(190,200,225))
    d.text((120,330), f"ATTEMPT {attempt}", fill=(155,170,255))
    d.text((120,400), f"QUALITY SCORE {score:.0f}/100", fill=(255,255,255))
    d.text((120,480), "ACCEPTED" if passed else "REJECTED — retrying", fill=((100,240,170) if passed else (255,120,125)))
    d.text((120,565), "SAMPLE MODE • deterministic artifact • no provider cost", fill=(150,160,180))
    img.save(path)

def run_sample(op: Opportunity, evidence_root: str|Path, ledger: Ledger) -> RunRecord:
    rights=assess_rights(op)
    economics=assess_economics(op, rights, ledger.totals()["available_paid_generation_budget"], estimated_unit_cost=0.0)
    plan=build_plan(op, rights, max_attempts=economics.max_attempts, estimated_unit_cost=0.0)
    root=Path(evidence_root)/op.id
    events=EventLog(root/"events.jsonl")
    lifecycle=Lifecycle.DISCOVERED
    events.emit(Event(opportunity_id=op.id, kind="DISCOVER", message="SAMPLE paid demand loaded.", data={"lifecycle":lifecycle.value}))
    write_json(root/"source"/"opportunity.json", op)
    write_source_snapshot(op, root/"source")
    write_json(root/"eligibility.json", rights)
    write_json(root/"economics.json", economics)
    write_json(root/"production-plan.json", plan)
    if rights.decision.value == "PASS":
        lifecycle=transition(lifecycle,Lifecycle.RIGHTS_PASSED,"explicit rights gate passed").after
    elif rights.decision.value == "REVIEW":
        lifecycle=transition(lifecycle,Lifecycle.REVIEW,"rights ambiguity requires review").after
    else:
        lifecycle=transition(lifecycle,Lifecycle.REJECTED,"rights gate rejected opportunity").after
    events.emit(Event(opportunity_id=op.id, kind="RIGHTS", status=rights.decision.value, message=" ".join(rights.reasons), data={"lifecycle":lifecycle.value}))
    if lifecycle is Lifecycle.RIGHTS_PASSED and economics.pursue:
        lifecycle=transition(lifecycle,Lifecycle.ECONOMICALLY_QUALIFIED,"economic gate passed").after
        lifecycle=transition(lifecycle,Lifecycle.BUDGET_AUTHORIZED,"zero-cost SAMPLE plan authorized").after
    events.emit(Event(opportunity_id=op.id, kind="ECONOMICS", status="PURSUE" if economics.pursue else "BLOCK", message="Deterministic economic gate evaluated.", data={"lifecycle":lifecycle.value}))
    cert=build_certificate(op, rights, economics, budget_available=ledger.totals(op.currency)["available_paid_generation_budget"], mode="SAMPLE")
    write_certificate(root/"decision-certificate.json", cert)
    attempts=[]
    accepted=None
    if economics.pursue:
        lifecycle=transition(lifecycle,Lifecycle.GENERATING,"generation unlocked after all gates").after
        for i,score in enumerate(SCORES[:economics.max_attempts],1):
            passed=score>=80
            p=root/"generations"/f"attempt-{i:03d}"/"asset.png"; p.parent.mkdir(parents=True, exist_ok=True)
            _make_asset(p, op.title, i, score, passed)
            a=Attempt(attempt=i, provider="sample-provider", model="deterministic-demo-v1", score=score,
                      passed=passed, cost=0.0, asset_path=str(p), sha256=sha256(p),
                      feedback=None if passed else "Improve brief fidelity and composition.")
            attempts.append(a)
            events.emit(Event(opportunity_id=op.id, kind="GENERATION", status="ACCEPT" if passed else "REJECT", message=f"SAMPLE attempt {i} scored {score:.0f}/100.", data={"attempt":i,"score":score}))
            write_json(p.parent/"evaluation.json", {"score":score,"passed":passed,"feedback":a.feedback})
            write_json(p.parent/"manifest.json", {"schema":"creative-bounty/sample-manifest-v1","sample":True,"provider":a.provider,"model":a.model,"sha256":a.sha256,"opportunity_id":op.id,"warning":"This is NOT a Genblaze provenance manifest."})
            write_json(p.parent/"integrity.json", verify_sample_asset(p, a.sha256))
            if passed:
                accepted=i
                lifecycle=transition(lifecycle,Lifecycle.READY,"quality threshold passed").after
                break
    record=RunRecord(opportunity_id=op.id, rights=rights, economics=economics, attempts=attempts,
                     accepted_attempt=accepted, evidence_dir=str(root), mode="SAMPLE")
    write_json(root/"run.json", record)
    build_submission_package(op, record, root)
    events.emit(Event(opportunity_id=op.id, kind="SUBMISSION", status="READY" if accepted else "BLOCKED", message="Submission evidence package assembled.", data={"lifecycle":lifecycle.value}))
    write_receipt(root, opportunity_id=op.id, mode="SAMPLE")
    return record
