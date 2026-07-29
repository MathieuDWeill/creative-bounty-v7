# CREATIVE//BOUNTY

## Overview

CREATIVE//BOUNTY is a demand-before-generation pipeline for AI media work.
Instead of starting with a prompt, it starts with an observable creative
opportunity, checks whether generative AI is permitted, evaluates whether the
work is economically rational, authorizes generation only within budget, and
stores evidence for replay.

The final build includes one verified LIVE media proof:

- Provider: `pollinations-image`
- Model: `flux`
- Genblaze run id: `86a788b9-e8cd-42d9-a355-562a97669d9b`
- Backblaze B2 asset SHA-256: `6a1e69f82b93dbfadcaf9f86a672f611bf2f76675ee262d4bf79f7ee1f23c441`
- Native Genblaze manifest hash: `d4ae8034cc836a890a7f498bb512341448563a71230c180dddf0efa96c335e13`
- `manifest.verify() == True`
- Recorded provider cost: `0.0`

No marketplace sale, customer, revenue, or win is fabricated. Advertised reward
is never treated as realized revenue.

## Architecture

```text
Opportunity Radar
  -> Rights Gate
  -> Economics
  -> Budget Authorization
  -> Genblaze Pipeline
  -> Pollinations Provider
  -> Backblaze B2 Evidence
  -> Native Manifest Verification
  -> Replay
```

Core files:

- `src/creative_bounty/orchestrator.py`: rights, economics, and budget gates.
- `src/creative_bounty/genblaze_adapter.py`: Genblaze providers and B2 sink.
- `src/creative_bounty/live_service.py`: LIVE proof execution and evidence writing.
- `src/creative_bounty/replay.py`: read-only evidence replay.
- `src/creative_bounty/judge_scorecard.py`: evidence-backed judging scorecard.

## Pipeline

1. Discover a paid creative opportunity.
2. Pass only opportunities with explicit AI permission.
3. Score economics without inventing probability of winning.
4. Authorize spend from realized revenue or explicit free/promotional credits.
5. Run the approved media step through Genblaze.
6. Persist the asset and native manifest to Backblaze B2.
7. Verify SHA-256, manifest hash, audit receipt, and replay.

## LIVE Proof

The verified LIVE proof is stored under:

```text
artifacts/evidence/live-genblaze-pollinations-flux-proof-001
```

Important evidence files:

- `generations/live-001/genblaze-proof.json`
- `generations/live-001/genblaze-manifest.json`
- `audit-receipt.json`
- `run.json`
- `events.jsonl`
- `submission/package.json`

The B2 bucket is private. The object is verified using authenticated B2 access,
not by public anonymous download.

## Evidence

Every evidence bundle contains:

- source snapshot
- opportunity JSON
- eligibility assessment
- economics assessment
- production plan
- event log
- generation proof
- decision certificate
- submission package
- audit receipt

Sample evidence remains explicitly labeled SAMPLE. Failed LIVE attempts are
included in the Judge Pack for transparency, but they are not treated as
successful proof.

## Replay

Replay is read-only. It reconstructs evidence without making provider calls and
without spending money.

```bash
python scripts/replay_evidence.py artifacts/evidence/live-genblaze-pollinations-flux-proof-001
```

Expected result:

```text
verified: true
accepted_attempt: 1
errors: []
```

## Backblaze

Backblaze B2 is used as the durable evidence warehouse. The verified LIVE run
persisted both the generated asset and the native Genblaze manifest under the
`genblaze/runs/` prefix.

The project distinguishes:

- B2 object persistence
- local CREATIVE//BOUNTY audit receipts
- native Genblaze manifests
- sample-only SHA-256 integrity checks

Truth distinctions:

- reward ≠ revenue
- sample hash ≠ Genblaze provenance

## Genblaze

Genblaze provides the pipeline execution layer, native run manifest, asset
metadata, canonical manifest hash, and `manifest.verify()` verification.

The final scorecard unlocks the B2 and Genblaze judging criteria only when a
verified LIVE proof exists.

## How To Run

Install dependencies:

```bash
python -m pip install -e .[genblaze]
```

Start the local demo:

```bash
PYTHONPATH=src CREATIVE_BOUNTY_PROVIDER=pollinations uvicorn creative_bounty.app:app --host 127.0.0.1 --port 8007
```

Useful endpoints:

```text
http://127.0.0.1:8007/api/status
http://127.0.0.1:8007/api/judge-scorecard
http://127.0.0.1:8007/api/replay/live-genblaze-pollinations-flux-proof-001
http://127.0.0.1:8007/api/evidence/live-genblaze-pollinations-flux-proof-001
```

Run validation:

```bash
pytest -q
python scripts/validate_submission.py
python scripts/release_candidate_check.py
python scripts/build_judge_pack.py
```

## Screenshots

Final submission screenshots are generated in:

```text
artifacts/final_submission/screenshots/
```

The final package also contains `architecture.png`, `thumbnail.png`, and a
captioned demo video.

## License

See `LICENSE`.

## Known Limitations

- Pollinations is a free public endpoint and not a paid production SLA.
- The verified LIVE proof is a controlled proof run, not a marketplace entry.
- The generated proof asset is an image, while some curated opportunities are
  video opportunities; the proof validates the pipeline, not a real submitted
  contest deliverable.
- Backblaze B2 is private, so object verification uses authenticated access.
- No revenue, customer, contest win, or commercial outcome is claimed.
