# CODEX FINAL MILE — v7

You are not designing the product. The architecture and concept are frozen.

## Non-negotiable
DO NOT:
- redesign the UI;
- rename the product;
- add speculative features;
- change the rights/economic/budget semantics;
- fabricate LIVE results;
- convert advertised rewards into revenue;
- weaken SAMPLE/LIVE separation.

## Goal
Produce exactly one truthful end-to-end LIVE proof using the current repository.

## Steps
1. Create a clean Python 3.11+ environment.
2. `pip install -e '.[genblaze,dev]'`.
3. Configure:
   - `B2_KEY_ID`
   - `B2_APP_KEY`
   - `B2_BUCKET`
   - one legitimate provider key (prefer free/promotional credit if available).
4. Run:
   - `pytest -q`
   - `python scripts/validate_submission.py`
   - `python scripts/live_preflight.py`
   - `python scripts/release_candidate_check.py`
5. Execute ONE approved real image generation through `live_service.py`.
6. Verify and record:
   - durable B2 asset URL;
   - asset SHA-256;
   - Genblaze manifest canonical hash;
   - `manifest.verify() == True`;
   - CREATIVE//BOUNTY audit receipt verifies.
7. If provider/model names differ in the installed Genblaze version, patch only integration drift.
8. Prefer conservative retry policy and a hard timeout.
9. Do not add a second paid generation unless the first proof is inadequate.
10. Deploy the FastAPI app.
11. Run HTTP smoke tests on:
    - `/`
    - `/api/status`
    - `/api/opportunities`
    - `/api/judge-scorecard`
    - `/api/replay/opp-ai-permitted-001`
12. Capture the 3-minute demo following `docs/v7-jury-story.md`.

## Required final report
Return:
- exact commit hash;
- exact installed Genblaze package versions;
- exact provider/model used;
- whether provider cost was free/promotional/paid;
- actual known cost, or `UNKNOWN` if not observable;
- B2 object URL;
- Genblaze canonical manifest hash;
- manifest verification result;
- audit receipt verification result;
- deployment URL;
- test output;
- any remaining limitation.

Do not say "production ready" unless all claims are evidenced.
