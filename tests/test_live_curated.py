from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from creative_bounty.app import app
from creative_bounty.economics import assess_economics
from creative_bounty.ledger import Ledger
from creative_bounty.opportunity_sources import curated_live_opportunities
from creative_bounty.rights import assess_rights
from creative_bounty.source_audit import build_source_snapshot


def _by_id():
    return {o.id:o for o in curated_live_opportunities()}


def test_future_vision_is_rights_pass_but_human_review():
    op=_by_id()["live-future-vision-xprize-2026"]
    rights=assess_rights(op)
    econ=assess_economics(op, rights, 0.0, estimated_unit_cost=0.0)
    assert rights.decision.value == "PASS"
    assert econ.pursue is False
    assert op.human_review_flags


def test_runway_big_ad_is_zero_capital_hard_stop():
    op=_by_id()["live-runway-big-ad-2026"]
    rights=assess_rights(op)
    econ=assess_economics(op, rights, 0.0, estimated_unit_cost=0.0)
    assert rights.decision.value == "PASS"
    assert op.requires_paid_plan is True
    assert econ.pursue is False
    assert any("ZERO-CAPITAL HARD STOP" in x for x in econ.rationale)


def test_source_snapshot_has_integrity_hash():
    op=_by_id()["live-runway-big-ad-2026"]
    snap=build_source_snapshot(op)
    assert len(snap["snapshot_sha256"]) == 64
    assert snap["source_evidence"]["live"] is True


def test_api_never_fx_sums_reward_currencies():
    client=TestClient(app)
    payload=client.get("/api/status").json()
    rewards=payload["opportunities"]["rewards_by_currency"]
    assert "EUR" in rewards
    assert "USD" in rewards
    assert "rewards" not in payload["opportunities"]


def test_sample_runner_refuses_live_curated():
    client=TestClient(app)
    r=client.post("/run/live-runway-big-ad-2026")
    assert r.status_code == 409


def test_live_detail_exposes_paid_access_constraint():
    client=TestClient(app)
    r=client.get("/api/opportunities/live-runway-big-ad-2026")
    assert r.status_code == 200
    data=r.json()
    assert data["opportunity"]["requires_paid_plan"] is True
    assert data["economics"]["pursue"] is False
