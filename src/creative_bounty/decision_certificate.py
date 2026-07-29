from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from .models import Opportunity, RightsAssessment, EconomicAssessment

SCHEMA='creative-bounty/decision-certificate/v1'

def build_certificate(op: Opportunity, rights: RightsAssessment, economics: EconomicAssessment, *, budget_available: float, mode: str):
    action = 'REJECT' if rights.decision.value=='REJECT' else ('REVIEW' if rights.decision.value=='REVIEW' or not economics.pursue else 'PURSUE')
    payload={
      'schema':SCHEMA,'issued_at':datetime.now(timezone.utc).isoformat(),'opportunity_id':op.id,'mode':mode,
      'source':{'url':op.url,'sample':op.sample},
      'reward':{'amount':op.reward,'currency':op.currency},
      'rights':rights.model_dump(mode='json'), 'economics':economics.model_dump(mode='json'),
      'budget':{'available':budget_available,'currency':op.currency}, 'decision':action,
      'truth':{'reward_is_revenue':False,'qualified_is_won':False,'sample_is_live':False},
    }
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    payload['certificate_sha256']=hashlib.sha256(canonical).hexdigest()
    return payload

def verify_certificate(cert: dict) -> bool:
    claimed=cert.get('certificate_sha256',''); payload={k:v for k,v in cert.items() if k!='certificate_sha256'}
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return bool(claimed) and hashlib.sha256(canonical).hexdigest()==claimed

def write_certificate(path: str|Path, cert: dict):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(cert,indent=2,ensure_ascii=False)+'\n'); return p
