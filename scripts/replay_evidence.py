from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from creative_bounty.replay import replay_evidence

p=argparse.ArgumentParser()
p.add_argument("evidence_dir")
args=p.parse_args()
r=replay_evidence(args.evidence_dir)
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
raise SystemExit(0 if r.verified else 1)
