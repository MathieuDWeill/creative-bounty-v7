import json
from pathlib import Path
from creative_bounty.audit_receipt import write_receipt, verify_receipt
from creative_bounty.ledger import Ledger
from creative_bounty.models import LedgerEntry
from creative_bounty.b2_governance import B2GovernancePlan, describe_plan

def test_receipt_detects_tampering(tmp_path):
    root=tmp_path/'evidence'; root.mkdir(); (root/'a.txt').write_text('alpha')
    write_receipt(root, opportunity_id='x', mode='SAMPLE')
    ok, errors=verify_receipt(root); assert ok and not errors
    (root/'a.txt').write_text('tampered')
    ok, errors=verify_receipt(root); assert not ok and errors

def test_ledger_is_currency_isolated(tmp_path):
    l=Ledger(tmp_path/'ledger.jsonl')
    l.append(LedgerEntry(kind='realized_revenue', amount=10, currency='EUR', reference='e'))
    l.append(LedgerEntry(kind='realized_revenue', amount=100, currency='USD', reference='u'))
    l.append(LedgerEntry(kind='generation_spend', amount=3, currency='EUR', reference='s'))
    assert l.totals('EUR')['available_paid_generation_budget']==7
    assert l.totals('USD')['available_paid_generation_budget']==100
    assert l.totals_by_currency()['USD']['realized_revenue']==100

def test_b2_governance_truth_language():
    d=describe_plan(B2GovernancePlan(bucket='x', object_lock_requested=True))
    assert d['object_lock_requested'] is True
    assert 'requested != enabled' in d['truth_note']
