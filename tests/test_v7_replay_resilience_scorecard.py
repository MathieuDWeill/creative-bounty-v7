import json
from pathlib import Path
import pytest

from creative_bounty.replay import replay_evidence
from creative_bounty.resilience import (
    ProviderCandidate, ProviderOutcome, simulate_failover
)
from creative_bounty.judge_scorecard import build_scorecard

ROOT=Path(__file__).resolve().parents[1]

def test_replay_verifies_sample_evidence_after_demo_run(tmp_path):
    from creative_bounty.demo import run_sample
    from creative_bounty.ledger import Ledger
    from creative_bounty.repository import load_all_opportunities
    ops=load_all_opportunities(ROOT/"data"/"opportunities.sample.json")
    op=next(o for o in ops if o.id=="opp-ai-permitted-001")
    run_sample(op,tmp_path/"evidence",Ledger(tmp_path/"ledger.jsonl"))
    r=replay_evidence(tmp_path/"evidence"/op.id)
    assert r.verified
    assert r.accepted_attempt==2
    assert r.generation_count==2
    assert r.event_count>=5

def test_replay_detects_tampering(tmp_path):
    from creative_bounty.demo import run_sample
    from creative_bounty.ledger import Ledger
    from creative_bounty.repository import load_all_opportunities
    ops=load_all_opportunities(ROOT/"data"/"opportunities.sample.json")
    op=next(o for o in ops if o.id=="opp-ai-permitted-001")
    root=tmp_path/"evidence"
    run_sample(op,root,Ledger(tmp_path/"ledger.jsonl"))
    econ=root/op.id/"economics.json"
    body=json.loads(econ.read_text())
    body["score"]=99
    econ.write_text(json.dumps(body))
    r=replay_evidence(root/op.id)
    assert not r.verified
    assert not r.audit_verified

def test_failover_simulation_is_budget_bounded_and_accepts_second_provider():
    candidates=[
        ProviderCandidate("provider-a","model-a",0.10),
        ProviderCandidate("provider-b","model-b",0.15),
    ]
    sim=simulate_failover(
        candidates,
        {
            ("provider-a","model-a"):ProviderOutcome.TRANSIENT_FAILURE,
            ("provider-b","model-b"):ProviderOutcome.SUCCESS,
        },
        authorized_budget=0.25,
    )
    assert len(sim.attempts)==2
    assert sim.accepted_provider=="provider-b"
    assert sim.total_cost==0.25
    assert not sim.exhausted

def test_failover_never_crosses_authorized_budget():
    candidates=[
        ProviderCandidate("a","1",0.20),
        ProviderCandidate("b","2",0.20),
    ]
    sim=simulate_failover(
        candidates,
        {("a","1"):ProviderOutcome.TRANSIENT_FAILURE,("b","2"):ProviderOutcome.SUCCESS},
        authorized_budget=0.20,
    )
    assert len(sim.attempts)==1
    assert sim.total_cost==0.20
    assert sim.exhausted

def test_judge_scorecard_never_claims_live_without_live_proof():
    card=build_scorecard(ROOT)
    assert card.max_total==100
    assert card.total<=100
    if not card.live_proof_present:
        gen=next(x for x in card.criteria if x.name=="Use of Genblaze")
        b2=next(x for x in card.criteria if x.name=="B2 Storage & Data Orchestration")
        assert gen.status=="PENDING_LIVE"
        assert b2.status=="PENDING_LIVE"
        assert gen.score<gen.max_score
        assert b2.score<b2.max_score
