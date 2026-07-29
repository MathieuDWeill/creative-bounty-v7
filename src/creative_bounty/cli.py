from __future__ import annotations
import argparse
from pathlib import Path
from .demo import run_sample
from .economics import assess_economics
from .ledger import Ledger
from .repository import load_all_opportunities
from .rights import assess_rights

def main():
    p=argparse.ArgumentParser(prog="creative-bounty")
    sub=p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("scan")
    sub.add_parser("scorecard")
    rp=sub.add_parser("replay"); rp.add_argument("opportunity_id")
    r=sub.add_parser("run-sample"); r.add_argument("opportunity_id")
    args=p.parse_args(); root=Path.cwd(); ledger=Ledger(root/"data/ledger.jsonl")
    ops=load_all_opportunities(root/"data/opportunities.sample.json")
    if args.cmd=="list":
        for o in ops:
            label="SAMPLE" if o.sample else "LIVE-CURATED"
            print(f"{o.id}\t{o.reward:.0f} {o.currency}\t{label}\t{o.title}")
        return
    if args.cmd=="scorecard":
        from .judge_scorecard import build_scorecard
        import json
        print(json.dumps(build_scorecard(root).as_dict(), indent=2))
        return
    if args.cmd=="replay":
        from .replay import replay_evidence
        import json
        evidence=root/"artifacts"/"evidence"/args.opportunity_id
        r=replay_evidence(evidence)
        print(json.dumps({
            "opportunity_id":r.opportunity_id,
            "mode":r.mode,
            "verified":r.verified,
            "audit_verified":r.audit_verified,
            "certificate_verified":r.certificate_verified,
            "accepted_attempt":r.accepted_attempt,
            "event_count":r.event_count,
            "generation_count":r.generation_count,
            "errors":list(r.errors),
        }, indent=2))
        if not r.verified:
            raise SystemExit(1)
        return
    if args.cmd=="scan":
        budget=ledger.totals()["available_paid_generation_budget"]
        for o in ops:
            rights=assess_rights(o); econ=assess_economics(o, rights, budget, estimated_unit_cost=0.0)
            decision="PURSUE" if econ.pursue else ("REJECT" if rights.decision.value=="REJECT" or o.requires_paid_plan else "REVIEW")
            print(f"{decision:7} {rights.decision.value:6} {econ.score:5.1f}  {o.reward:>9.0f} {o.currency:3}  {o.title}")
        return
    op=next(o for o in ops if o.id==args.opportunity_id)
    if not op.sample:
        raise SystemExit("run-sample refuses LIVE-CURATED opportunities; use LIVE service after human review.")
    rec=run_sample(op, root/"artifacts/evidence", ledger)
    print(rec.model_dump_json(indent=2))
