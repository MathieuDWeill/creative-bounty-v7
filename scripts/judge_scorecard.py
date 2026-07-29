from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from creative_bounty.judge_scorecard import build_scorecard

card=build_scorecard(ROOT)
out=ROOT/"artifacts"/"judge-scorecard.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(card.as_dict(),indent=2)+"\n",encoding="utf-8")
print(json.dumps(card.as_dict(),indent=2))
