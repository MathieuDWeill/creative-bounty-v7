import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from creative_bounty.app import app
from creative_bounty.events import EventLog
from creative_bounty.ledger import Ledger
from creative_bounty.models import LedgerEntry, Opportunity, Decision
from creative_bounty.orchestrator import GateError, preflight
from creative_bounty.planning import build_plan
from creative_bounty.provenance import verify_sample_asset
from creative_bounty.rights import assess_rights


def op(**kw):
    base=dict(id="ctl",source="test",title="paid brief",url="https://example.invalid/brief",reward=500,currency="EUR",deadline="2026-08-01",media_type="image",deliverables=["hero image"],ai_policy="Explicitly allowed",policy_evidence="Generative AI explicitly allowed",sample=True)
    base.update(kw)
    return Opportunity(**base)


def test_production_plan_fail_closed_on_review():
    o=op(ai_policy="unspecified", policy_evidence="No AI statement")
    r=assess_rights(o)
    plan=build_plan(o,r)
    assert r.decision is Decision.REVIEW
    assert plan.blockers


def test_preflight_blocks_uncertain_rights(tmp_path):
    l=Ledger(tmp_path/"ledger.jsonl")
    with pytest.raises(GateError):
        preflight(op(ai_policy="unknown",policy_evidence="nothing explicit"), l, tmp_path/"events.jsonl")


def test_preflight_enforces_budget_for_real_cost(tmp_path):
    l=Ledger(tmp_path/"ledger.jsonl")
    with pytest.raises(GateError):
        preflight(op(), l, tmp_path/"events.jsonl", estimated_unit_cost=0.2)


def test_preflight_authorizes_with_promotional_credit(tmp_path):
    l=Ledger(tmp_path/"ledger.jsonl")
    l.append(LedgerEntry(kind="promotional_credits",amount=1.0,reference="free-tier"))
    rights,econ,plan=preflight(op(),l,tmp_path/"events.jsonl",estimated_unit_cost=0.2)
    assert rights.decision is Decision.PASS
    assert econ.pursue
    assert plan.estimated_max_spend == 0.6
    assert len(EventLog(tmp_path/"events.jsonl").read()) == 4


def test_sample_integrity_detects_tampering(tmp_path):
    p=tmp_path/"asset.bin"; p.write_bytes(b"original")
    import hashlib
    expected=hashlib.sha256(b"original").hexdigest()
    assert verify_sample_asset(p, expected).verified
    p.write_bytes(b"tampered")
    assert not verify_sample_asset(p, expected).verified


def test_status_and_opportunity_api():
    c=TestClient(app)
    s=c.get("/api/status")
    assert s.status_code == 200
    assert "ledger" in s.json() and "live_ready" in s.json()
    o=c.get("/api/opportunities")
    assert o.status_code == 200 and len(o.json()) >= 1


def test_artifact_endpoint_rejects_path_escape():
    c=TestClient(app)
    r=c.get("/artifact", params={"path":"/etc/passwd"})
    assert r.status_code == 403
