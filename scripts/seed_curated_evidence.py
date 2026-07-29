#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from creative_bounty.opportunity_sources import curated_live_opportunities
from creative_bounty.source_audit import write_source_snapshot


def main():
    root=Path("artifacts/evidence")
    for op in curated_live_opportunities():
        p=write_source_snapshot(op, root/op.id/"source")
        print(f"{op.id}: {p}")

if __name__ == "__main__":
    main()
