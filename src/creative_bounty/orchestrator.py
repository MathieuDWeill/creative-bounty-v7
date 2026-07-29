from __future__ import annotations
from pathlib import Path
from .economics import assess_economics
from .events import Event, EventLog
from .ledger import Ledger
from .models import Opportunity
from .planning import build_plan
from .rights import assess_rights

class GateError(RuntimeError):
    pass


def preflight(op: Opportunity, ledger: Ledger, event_path: str | Path, *, estimated_unit_cost: float = 0.0):
    log = EventLog(event_path)
    log.emit(Event(opportunity_id=op.id, kind="DISCOVER", message="Paid demand recorded before generation."))
    rights = assess_rights(op)
    log.emit(Event(opportunity_id=op.id, kind="RIGHTS", status=rights.decision.value,
                   message=" ".join(rights.reasons), data={"confidence": rights.confidence}))
    economics = assess_economics(op, rights, ledger.totals()["available_paid_generation_budget"],
                                 estimated_unit_cost=estimated_unit_cost)
    log.emit(Event(opportunity_id=op.id, kind="ECONOMICS", status="PURSUE" if economics.pursue else "BLOCK",
                   message="Economic prioritization completed.", data=economics.model_dump(mode="json")))
    plan = build_plan(op, rights, max_attempts=economics.max_attempts,
                      estimated_unit_cost=estimated_unit_cost)
    if plan.blockers or not economics.pursue:
        raise GateError("Production blocked by rights/economic preflight")
    ledger.assert_spend_allowed(plan.estimated_max_spend)
    log.emit(Event(opportunity_id=op.id, kind="BUDGET", message="Maximum planned spend authorized.",
                   data={"max_spend": plan.estimated_max_spend}))
    return rights, economics, plan
