from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
required=[
    "README.md","docs/demo-script.md","docs/judging.md","docs/truth-protocol.md",
    "docs/live-checklist.md","src/creative_bounty/genblaze_adapter.py",
    "src/creative_bounty/orchestrator.py","src/creative_bounty/live_service.py",
    "data/opportunities.sample.json",
]
errors=[]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f"missing {rel}")
ops=json.loads((ROOT/"data/opportunities.sample.json").read_text())
if not all(o.get("sample") is True for o in ops): errors.append("sample opportunity not labeled")
for p in (ROOT/"artifacts/evidence").glob("*/generations/attempt-*/manifest.json"):
    m=json.loads(p.read_text())
    if m.get("sample") is not True: errors.append(f"unlabeled demo manifest {p}")
    if "warning" not in m: errors.append(f"sample manifest missing non-Genblaze warning {p}")
readme=(ROOT/"README.md").read_text(encoding="utf-8")
for phrase in ("reward ≠ revenue", "sample hash ≠ Genblaze provenance"):
    if phrase not in readme: errors.append(f"README missing truth distinction: {phrase}")
print("submission validation:", "PASS" if not errors else "FAIL")
for e in errors: print("-",e)
sys.exit(bool(errors))
