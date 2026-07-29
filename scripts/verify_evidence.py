#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from creative_bounty.audit_receipt import verify_receipt

p=argparse.ArgumentParser(description='Verify a CREATIVE//BOUNTY evidence receipt')
p.add_argument('path', type=Path)
a=p.parse_args()
ok, errors=verify_receipt(a.path)
print('VERIFIED' if ok else 'FAILED')
for e in errors: print('-',e)
raise SystemExit(0 if ok else 2)
