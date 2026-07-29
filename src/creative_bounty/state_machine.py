from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Lifecycle(str, Enum):
    DISCOVERED='DISCOVERED'; RIGHTS_PASSED='RIGHTS_PASSED'; ECONOMICALLY_QUALIFIED='ECONOMICALLY_QUALIFIED'; BUDGET_AUTHORIZED='BUDGET_AUTHORIZED'; GENERATING='GENERATING'; READY='READY'; SUBMITTED='SUBMITTED'; WON='WON'; LOST='LOST'; REVIEW='REVIEW'; REJECTED='REJECTED'

_ALLOWED={
 Lifecycle.DISCOVERED:{Lifecycle.RIGHTS_PASSED,Lifecycle.REVIEW,Lifecycle.REJECTED},
 Lifecycle.RIGHTS_PASSED:{Lifecycle.ECONOMICALLY_QUALIFIED,Lifecycle.REVIEW,Lifecycle.REJECTED},
 Lifecycle.ECONOMICALLY_QUALIFIED:{Lifecycle.BUDGET_AUTHORIZED,Lifecycle.REVIEW,Lifecycle.REJECTED},
 Lifecycle.BUDGET_AUTHORIZED:{Lifecycle.GENERATING,Lifecycle.REVIEW},
 Lifecycle.GENERATING:{Lifecycle.GENERATING,Lifecycle.READY,Lifecycle.REVIEW,Lifecycle.REJECTED},
 Lifecycle.READY:{Lifecycle.SUBMITTED,Lifecycle.REVIEW},
 Lifecycle.SUBMITTED:{Lifecycle.WON,Lifecycle.LOST,Lifecycle.REVIEW},
 Lifecycle.REVIEW:{Lifecycle.RIGHTS_PASSED,Lifecycle.REJECTED},
 Lifecycle.REJECTED:set(), Lifecycle.WON:set(), Lifecycle.LOST:set(),
}

class InvalidTransition(RuntimeError): pass

@dataclass(frozen=True)
class Transition:
    before: Lifecycle; after: Lifecycle; reason: str

def transition(current: Lifecycle, target: Lifecycle, reason: str) -> Transition:
    if target not in _ALLOWED[current]:
        raise InvalidTransition(f'illegal lifecycle transition: {current.value} -> {target.value}')
    if not reason.strip(): raise ValueError('transition reason is required')
    return Transition(current,target,reason.strip())
