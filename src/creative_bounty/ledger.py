from __future__ import annotations
import json
from pathlib import Path
from .models import LedgerEntry
from .currency import ledger_totals_by_currency

class Ledger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self.path.write_text("", encoding="utf-8")

    def entries(self) -> list[LedgerEntry]:
        out=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip(): out.append(LedgerEntry.model_validate_json(line))
        return out

    def append(self, entry: LedgerEntry) -> None:
        # Revenue is only accepted under an explicit realized_revenue kind.
        with self.path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json()+"\n")

    def totals_by_currency(self) -> dict[str, dict[str, float]]:
        return ledger_totals_by_currency(self.entries())

    def totals(self, currency: str = "EUR") -> dict[str, float]:
        t={"external_capital":0.0,"promotional_credits":0.0,"realized_revenue":0.0,"generation_spend":0.0}
        for e in self.entries():
            if e.currency == currency and e.kind in t: t[e.kind]+=e.amount
        t["available_paid_generation_budget"] = t["realized_revenue"] + t["promotional_credits"] - t["generation_spend"]
        return {k: round(v,2) for k,v in t.items()}

    def assert_spend_allowed(self, amount: float, currency: str = "EUR") -> None:
        if amount < 0: raise ValueError("Spend cannot be negative")
        if amount > self.totals(currency)["available_paid_generation_budget"]:
            raise PermissionError("Budget invariant blocked this generation")
