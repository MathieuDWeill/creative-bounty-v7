import pytest
from creative_bounty.state_machine import Lifecycle, InvalidTransition, transition
from creative_bounty.decision_certificate import build_certificate, verify_certificate
from creative_bounty.models import Opportunity
from creative_bounty.rights import assess_rights
from creative_bounty.economics import assess_economics

def op(**kw):
 b=dict(id='v5',source='test',title='brief',url='https://example.invalid',reward=100,currency='EUR',deadline='2026-08-01',media_type='image',deliverables=['image'],ai_policy='explicitly allowed',policy_evidence='Generative AI explicitly allowed',sample=True); b.update(kw); return Opportunity(**b)

def test_state_machine_happy_path_and_illegal_skip():
 assert transition(Lifecycle.DISCOVERED,Lifecycle.RIGHTS_PASSED,'explicit AI permission').after is Lifecycle.RIGHTS_PASSED
 with pytest.raises(InvalidTransition): transition(Lifecycle.DISCOVERED,Lifecycle.GENERATING,'skip gates')

def test_terminal_state_cannot_reopen():
 with pytest.raises(InvalidTransition): transition(Lifecycle.REJECTED,Lifecycle.GENERATING,'try again')

def test_decision_certificate_is_tamper_evident():
 o=op(); r=assess_rights(o); e=assess_economics(o,r,0,estimated_unit_cost=0)
 c=build_certificate(o,r,e,budget_available=0,mode='SAMPLE')
 assert verify_certificate(c)
 c['reward']['amount']=999
 assert not verify_certificate(c)

def test_certificate_truth_flags():
 o=op(); r=assess_rights(o); e=assess_economics(o,r,0,estimated_unit_cost=0)
 c=build_certificate(o,r,e,budget_available=0,mode='SAMPLE')
 assert c['truth']=={'reward_is_revenue':False,'qualified_is_won':False,'sample_is_live':False}

def test_decision_certificate_api():
 from fastapi.testclient import TestClient
 from creative_bounty.app import app
 c=TestClient(app)
 ops=c.get('/api/opportunities').json()
 oid=ops[0]['opportunity']['id']
 r=c.get(f'/api/decision-certificate/{oid}')
 assert r.status_code==200
 body=r.json()
 assert body['decision'] in {'PURSUE','REVIEW','REJECT'}
 assert verify_certificate(body)
