.PHONY: test validate judge-pack demo scorecard replay release-candidate

test:
	pytest -q

validate:
	python scripts/validate_submission.py

judge-pack: test validate
	python scripts/build_judge_pack.py

demo:
	PYTHONPATH=src python -m creative_bounty scan
	@echo "Start UI with: uvicorn creative_bounty.app:app --reload"

scorecard:
	python scripts/judge_scorecard.py

replay:
	python scripts/replay_evidence.py artifacts/evidence/opp-ai-permitted-001

release-candidate:
	python scripts/release_candidate_check.py
