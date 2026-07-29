import json
from pathlib import Path
import pytest
from creative_bounty.models import Opportunity, LedgerEntry, Decision
from creative_bounty.rights import assess_rights
from creative_bounty.economics import assess_economics
from creative_bounty.ledger import Ledger
from creative_bounty.demo import run_sample

def op(**kw):
    base=dict(id="x",source="test",title="brief",url="https://example.invalid",reward=100,currency="EUR",deadline="2026-08-01",media_type="image",deliverables=["image"],ai_policy="Explicitly allowed",policy_evidence="AI explicitly allowed",sample=True)
    base.update(kw); return Opportunity(**base)

def test_uncertain_ai_policy_requires_review():
    a=assess_rights(op(ai_policy="unspecified",policy_evidence="nothing about AI")); assert a.decision==Decision.REVIEW

def test_prohibited_ai_is_rejected():
    assert assess_rights(op(ai_policy="Generative AI prohibited",policy_evidence="not allowed")).decision==Decision.REJECT

def test_scoring_is_deterministic():
    o=op(); r=assess_rights(o); assert assess_economics(o,r).score==assess_economics(o,r).score

def test_budget_invariant(tmp_path):
    l=Ledger(tmp_path/"ledger.jsonl")
    with pytest.raises(PermissionError): l.assert_spend_allowed(0.01)
    l.append(LedgerEntry(kind="promotional_credits",amount=1,reference="credit"))
    l.assert_spend_allowed(0.8)

def test_revenue_not_derived_from_reward(tmp_path):
    l=Ledger(tmp_path/"ledger.jsonl"); assert l.totals()["realized_revenue"]==0

def test_rejected_opportunity_cannot_generate(tmp_path):
    l=Ledger(tmp_path/"l.jsonl"); o=op(ai_policy="AI prohibited",policy_evidence="AI prohibited")
    rec=run_sample(o,tmp_path/"evidence",l); assert rec.attempts==[] and rec.accepted_attempt is None

def test_sample_evidence_and_retry(tmp_path):
    l=Ledger(tmp_path/"l.jsonl"); rec=run_sample(op(reward=500),tmp_path/"evidence",l)
    assert len(rec.attempts)==2 and rec.attempts[0].passed is False and rec.attempts[1].passed is True
    manifest=Path(rec.evidence_dir)/"generations/attempt-002/manifest.json"
    assert manifest.exists() and json.loads(manifest.read_text())["sample"] is True
