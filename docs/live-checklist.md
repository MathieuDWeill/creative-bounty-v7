# LIVE finalization checklist

1. Create a B2 bucket and least-privilege application key.
2. Install `genblaze-core`, `genblaze-s3` and exactly one provider package.
3. Add legitimate promotional credits to the ledger only when their amount is known.
4. Import one real or sponsor-sanctioned brief with explicit AI permission evidence.
5. Run preflight and inspect `eligibility.json`, `economics.json`, `production-plan.json`.
6. Execute one LIVE Genblaze image run.
7. Confirm B2 durable asset URL.
8. Confirm native Genblaze `canonical_manifest_hash` and `manifest_verified` in `genblaze-proof.json`.
9. Reconcile actual provider charge into the ledger if any charge occurred.
10. Run `pytest -q` and `python scripts/validate_submission.py`.
11. Capture the demo without presenting SAMPLE artifacts as LIVE.

## Current environment note

The installed Genblaze packages inspected locally are:

- `genblaze-core==0.3.7`
- `genblaze-s3==0.3.6`
- `genblaze-openai==0.3.3`
- `google-genai==2.14.0`
- `genblaze-nvidia==0.3.2`

The B2-only preflight verified `creative-bounty-mathieu-2026` in `us-east-005` with authenticated list/write/read/delete access, anonymous list blocked with 403, default AES256 encryption and Object Lock enabled.

`scripts/live_preflight.py` reports `live_ready: true` with B2 and the configured free provider path.

The verified LIVE run is `live-genblaze-pollinations-flux-proof-001`. It used Genblaze provider `pollinations-image`, model `flux`, persisted the asset and native manifest to B2, verified the B2 asset SHA-256, and verified `manifest.verify() == True`. The recorded provider cost is `0.0`; no API key or billing account was used for Pollinations.
