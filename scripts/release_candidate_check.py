from __future__ import annotations
from pathlib import Path
import json, subprocess, sys, hashlib, time

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"artifacts"
ART.mkdir(parents=True,exist_ok=True)

def run(name, cmd, timeout=45):
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    payload={"name":name,"command":cmd,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
    (ART/f"rc-{name}.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    if p.returncode:
        print(p.stdout)
        print(p.stderr,file=sys.stderr)
        raise SystemExit(f"{name} failed")
    return payload

checks=[]
checks.append(run("pytest",[sys.executable,"-m","pytest","-q"]))
checks.append(run("submission",[sys.executable,"scripts/validate_submission.py"]))
checks.append(run("scorecard",[sys.executable,"scripts/judge_scorecard.py"]))
scorecard=json.loads((ART/"judge-scorecard.json").read_text(encoding="utf-8"))

# Ensure a deterministic sample evidence bundle exists through the public Python API.
sample_root=ROOT/"artifacts"/"evidence"/"opp-ai-permitted-001"
code = (
    "from pathlib import Path;"
    "from creative_bounty.repository import load_all_opportunities;"
    "from creative_bounty.demo import run_sample;"
    "from creative_bounty.ledger import Ledger;"
    "r=Path('.');"
    "ops=load_all_opportunities(r/'data'/'opportunities.sample.json');"
    "op=next(o for o in ops if o.id=='opp-ai-permitted-001');"
    "run_sample(op,r/'artifacts'/'evidence',Ledger(r/'data'/'ledger.jsonl'))"
)
checks.append(run("sample_api",[sys.executable,"-c",
    "import sys;sys.path.insert(0,'src');"+code]))

checks.append(run("replay",[sys.executable,"scripts/replay_evidence.py",str(sample_root)]))

live_replay = None
if scorecard.get("live_proof_present"):
    live_roots = sorted((ROOT/"artifacts"/"evidence").glob("*/generations/live-*/genblaze-proof.json"))
    for proof_path in live_roots:
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        if proof.get("manifest_verified") is True:
            live_root = proof_path.parents[2]
            live_replay = run("live_replay",[sys.executable,"scripts/replay_evidence.py",str(live_root)])
            checks.append(live_replay)
            break

summary={
    "schema":"creative-bounty/release-candidate/v1",
    "version":"v7",
    "generated_at_epoch":int(time.time()),
    "checks":[{"name":c["name"],"returncode":c["returncode"]} for c in checks],
    "live_claimed":bool(scorecard.get("live_proof_present")),
    "live_requirement":(
        "Satisfied: verified native Genblaze manifest and Backblaze B2 asset evidence are present."
        if scorecard.get("live_proof_present")
        else "One real Genblaze + Backblaze B2 run remains required before claiming LIVE verification."
    ),
}
canonical=json.dumps(summary,sort_keys=True,separators=(",",":")).encode()
summary["sha256"]=hashlib.sha256(canonical).hexdigest()
(ART/"release-candidate.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
