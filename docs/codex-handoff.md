# Codex handoff — final mile only

Do **not** redesign CREATIVE//BOUNTY. The product logic, UI, domain model, truth protocol, tests, curated live opportunities, Genblaze adapter, B2 sink, and evidence model are already implemented.

## Current validation

- `36 passed`
- `scripts/validate_submission.py` => PASS
- `scripts/release_candidate_check.py` => PASS with `live_claimed=false`
- FastAPI routes smoke-tested
- two real LIVE-CURATED opportunity snapshots seeded
- SAMPLE and LIVE execution paths are hard-separated
- mixed currencies are never FX-summed
- inspected Genblaze package versions: `genblaze-core==0.3.7`, `genblaze-s3==0.3.6`, `genblaze-openai==0.3.3`, `google-genai==2.14.0`
- B2-only preflight verified `creative-bounty-mathieu-2026` in `us-east-005`: authenticated list/write/read/delete, private anonymous list blocked, default AES256 encryption, Object Lock enabled
- LIVE generation is blocked because the supplied Gemini project has Free Tier image quota limit `0` for `gemini-3.1-flash-lite-image`; the prepared path is `CREATIVE_BOUNTY_PROVIDER=google` with Google Gemini image

## Your job

1. Install the current Genblaze packages from the official installation source available in the user's environment.
2. Resolve only API drift if the installed Genblaze version differs from the documented interfaces used in `genblaze_adapter.py`.
3. Configure a Backblaze B2 bucket and least-privilege app key.
4. Configure **one** legitimate provider/free-credit key.
5. Run `PYTHONPATH=src python scripts/live_preflight.py`. Do not proceed until the report is READY.
6. Execute **one minimal authorized LIVE generation** from a human-approved opportunity or purpose-built demo brief.
7. Verify:
   - asset persisted in B2;
   - Genblaze manifest exists;
   - canonical manifest hash is recorded;
   - `manifest.verify()` succeeds;
   - evidence tree contains the live proof.
8. Reconcile actual provider spend into the ledger only after the provider reports it; never record an estimate as actual spend.
9. Deploy the FastAPI app.
10. Run the full test suite and submission validator again.
11. Capture the final 3-minute demo using `docs/demo-script.md`.

## Hard constraints

- Do not fabricate revenue or wins.
- Do not turn LIVE-CURATED snapshots into "live crawling" unless a source adapter is actually implemented.
- Do not bypass `preflight()` or the budget gate.
- Do not change the zero-capital thesis.
- Do not add paid services unless explicitly approved by the user.
- Do not replace B2 with local storage in the final live proof.

## Expected final response

Report only:
1. live provider/model used;
2. B2 object evidence;
3. Genblaze manifest verification result;
4. actual external spend;
5. deployment URL;
6. test/validator output;
7. remaining submission actions the user must do manually.
