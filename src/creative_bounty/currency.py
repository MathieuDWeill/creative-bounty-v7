from __future__ import annotations
from collections import defaultdict
from .models import LedgerEntry

def ledger_totals_by_currency(entries: list[LedgerEntry]) -> dict[str, dict[str,float]]:
    out=defaultdict(lambda:{"external_capital":0.0,"promotional_credits":0.0,"realized_revenue":0.0,"generation_spend":0.0})
    for e in entries:
        if e.kind in out[e.currency]: out[e.currency][e.kind]+=e.amount
    for cur,t in out.items():
        t["available_paid_generation_budget"] = t["realized_revenue"]+t["promotional_credits"]-t["generation_spend"]
        out[cur]={k:round(v,4) for k,v in t.items()}
    return dict(sorted(out.items()))
