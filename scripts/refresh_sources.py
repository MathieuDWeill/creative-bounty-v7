#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from creative_bounty.opportunity_sources import curated_live_opportunities
from creative_bounty.source_refresh import write_refresh_report


def main():
    failed=0
    for op in curated_live_opportunities():
        path=write_refresh_report(op, Path("artifacts/evidence")/op.id/"source")
        print(f"{op.id}: {path}")
        import json
        report=json.loads(path.read_text())
        if not report["ok"]:
            failed+=1
        if report["changed_since_previous"]:
            print("  WARNING: source content changed; human re-review required before LIVE use")
    raise SystemExit(1 if failed else 0)

if __name__ == "__main__":
    main()
