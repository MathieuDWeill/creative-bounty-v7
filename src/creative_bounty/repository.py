import json
from pathlib import Path
from .models import Opportunity
from .opportunity_sources import curated_live_opportunities


def load_opportunities(path: str|Path) -> list[Opportunity]:
    return [Opportunity.model_validate(x) for x in json.loads(Path(path).read_text(encoding="utf-8"))]


def load_all_opportunities(sample_path: str | Path, *, include_curated_live: bool = True) -> list[Opportunity]:
    ops = load_opportunities(sample_path)
    if include_curated_live:
        ops.extend(curated_live_opportunities())
    # stable ordering for deterministic UI/tests
    return sorted(ops, key=lambda op: (op.sample, op.deadline, op.id))
