from __future__ import annotations
import os
from collections import defaultdict
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .demo import run_sample
from .economics import assess_economics
from .events import EventLog
from .genblaze_adapter import live_ready
from .ledger import Ledger
from .repository import load_all_opportunities
from .rights import assess_rights
from .source_audit import build_source_snapshot
from .audit_receipt import verify_receipt
from .b2_governance import plan_from_env, describe_plan
from .decision_certificate import build_certificate
from .judge_scorecard import build_scorecard
from .replay import replay_evidence

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"data"/"opportunities.sample.json"
EVIDENCE=ROOT/"artifacts"/"evidence"
ledger=Ledger(ROOT/"data"/"ledger.jsonl")
app=FastAPI(title="CREATIVE//BOUNTY", version="0.7.0")
app.mount("/static", StaticFiles(directory=ROOT/"static"), name="static")
templates=Jinja2Templates(directory=ROOT/"templates")


def configured_provider() -> str:
    return os.getenv("CREATIVE_BOUNTY_PROVIDER", "openai")


def snapshot():
    ops=load_all_opportunities(DATA)
    rows=[]
    budget=ledger.totals()["available_paid_generation_budget"]
    rewards=defaultdict(float); ai_compatible=defaultdict(float)
    for op in ops:
        rights=assess_rights(op)
        econ=assess_economics(op, rights, budget, estimated_unit_cost=0.0)
        rows.append({"op":op,"rights":rights,"econ":econ})
        rewards[op.currency]+=op.reward
        if rights.decision.value=="PASS": ai_compatible[op.currency]+=op.reward
    totals={
        "count":len(ops),
        "rewards_by_currency":dict(sorted(rewards.items())),
        "ai_compatible_by_currency":dict(sorted(ai_compatible.items())),
        "qualified":sum(1 for r in rows if r["econ"].pursue),
        "live_curated":sum(1 for o in ops if not o.sample),
    }
    return rows, totals


def _ops_by_id():
    return {o.id:o for o in load_all_opportunities(DATA)}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    rows, totals=snapshot(); ready, missing=live_ready(configured_provider())
    return templates.TemplateResponse(request, "index.html", {
        "rows":rows,"totals":totals,"ledger":ledger.totals(),"live_ready":ready,
        "missing":missing,"mode":os.getenv("CREATIVE_BOUNTY_MODE","SAMPLE")
    })

@app.get("/opportunity/{opportunity_id}", response_class=HTMLResponse)
def opportunity_detail(request: Request, opportunity_id: str):
    ops=_ops_by_id()
    if opportunity_id not in ops: raise HTTPException(404)
    op=ops[opportunity_id]
    rights=assess_rights(op)
    econ=assess_economics(op, rights, ledger.totals()["available_paid_generation_budget"], estimated_unit_cost=0.0)
    return templates.TemplateResponse(request, "opportunity.html", {
        "op":op,"rights":rights,"econ":econ,"source_snapshot":build_source_snapshot(op)
    })

@app.post("/run/{opportunity_id}", response_class=HTMLResponse)
def run(request: Request, opportunity_id: str):
    ops=_ops_by_id()
    if opportunity_id not in ops: raise HTTPException(404)
    op=ops[opportunity_id]
    if not op.sample:
        raise HTTPException(409, "LIVE-CURATED opportunities cannot be executed by the SAMPLE runner.")
    record=run_sample(op, EVIDENCE, ledger)
    events=EventLog(Path(record.evidence_dir)/"events.jsonl").read()
    return templates.TemplateResponse(request, "run.html", {"record":record,"op":op,"events":events})

@app.get("/api/status")
def api_status():
    provider = configured_provider()
    ready, missing=live_ready(provider)
    _, totals=snapshot()
    return {"mode":os.getenv("CREATIVE_BOUNTY_MODE","SAMPLE"),"provider":provider,"live_ready":ready,"missing":missing,"ledger":ledger.totals(),"ledger_by_currency":ledger.totals_by_currency(),"b2_governance":describe_plan(plan_from_env()),"opportunities":totals}

@app.get("/api/opportunities")
def api_opportunities():
    rows,_=snapshot()
    return [{"opportunity":r["op"].model_dump(mode="json"),"rights":r["rights"].model_dump(mode="json"),"economics":r["econ"].model_dump(mode="json")} for r in rows]

@app.get("/api/opportunities/{opportunity_id}")
def api_opportunity(opportunity_id: str):
    ops=_ops_by_id()
    if opportunity_id not in ops: raise HTTPException(404)
    op=ops[opportunity_id]; rights=assess_rights(op)
    econ=assess_economics(op, rights, ledger.totals()["available_paid_generation_budget"], estimated_unit_cost=0.0)
    return {"opportunity":op.model_dump(mode="json"),"rights":rights.model_dump(mode="json"),"economics":econ.model_dump(mode="json"),"source_snapshot":build_source_snapshot(op)}

@app.get("/api/evidence/{opportunity_id}")
def api_evidence(opportunity_id: str):
    root=(EVIDENCE/opportunity_id).resolve()
    if EVIDENCE.resolve() not in root.parents: raise HTTPException(403)
    if not root.exists(): raise HTTPException(404)
    files=[str(p.relative_to(root)) for p in sorted(root.rglob("*")) if p.is_file()]
    events=[e.model_dump(mode="json") for e in EventLog(root/"events.jsonl").read()]
    verified, audit_errors = verify_receipt(root)
    return {"opportunity_id":opportunity_id,"files":files,"events":events,"audit_receipt":{"verified":verified,"errors":audit_errors}}

@app.get("/artifact")
def artifact(path: str):
    p=Path(path).resolve()
    if EVIDENCE.resolve() not in p.parents: raise HTTPException(403)
    if not p.exists(): raise HTTPException(404)
    return FileResponse(p)

@app.get("/api/decision-certificate/{opportunity_id}")
def api_decision_certificate(opportunity_id: str):
    ops=_ops_by_id()
    if opportunity_id not in ops: raise HTTPException(404)
    op=ops[opportunity_id]; rights=assess_rights(op)
    budget=ledger.totals(op.currency)["available_paid_generation_budget"]
    econ=assess_economics(op, rights, budget, estimated_unit_cost=0.0)
    return build_certificate(op, rights, econ, budget_available=budget, mode="SAMPLE" if op.sample else "LIVE-CURATED")


@app.get("/api/judge-scorecard")
def api_judge_scorecard():
    return build_scorecard(ROOT).as_dict()

@app.get("/api/replay/{opportunity_id}")
def api_replay(opportunity_id: str):
    root=(EVIDENCE/opportunity_id).resolve()
    if EVIDENCE.resolve() not in root.parents:
        raise HTTPException(403)
    if not root.exists():
        raise HTTPException(404)
    try:
        r=replay_evidence(root)
    except FileNotFoundError as exc:
        raise HTTPException(409, f"Evidence bundle is incomplete: {exc}") from exc
    return {
        "opportunity_id":r.opportunity_id,
        "mode":r.mode,
        "verified":r.verified,
        "audit_verified":r.audit_verified,
        "certificate_verified":r.certificate_verified,
        "accepted_attempt":r.accepted_attempt,
        "event_count":r.event_count,
        "generation_count":r.generation_count,
        "errors":list(r.errors),
    }
