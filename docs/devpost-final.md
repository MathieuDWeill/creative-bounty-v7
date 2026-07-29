# CREATIVE//BOUNTY Devpost Submission

## Elevator Pitch

CREATIVE//BOUNTY is a verifiable AI production pipeline. It starts from paid
creative demand, checks rights and economics, authorizes generation only when
budget allows, executes through Genblaze, stores evidence in Backblaze B2, and
supports read-only replay.

## Problem

AI content generation is easy. Trustworthy AI production is harder.

Most workflows cannot prove:

- why a piece of media was generated;
- whether generative AI was permitted;
- what budget authorized the run;
- where the source, decision, asset, and manifest were stored;
- whether a later demo is replaying evidence or silently regenerating content.

## Solution

CREATIVE//BOUNTY reverses the usual prompt-first workflow. It requires demand,
permission, economics, and budget authorization before generation. Every run
produces an evidence bundle with source snapshots, assessments, events,
generation proof, decision certificate, audit receipt, and replay metadata.

The final release includes a real verified LIVE proof:

- Provider: `pollinations-image`
- Model: `flux`
- Genblaze run id: `86a788b9-e8cd-42d9-a355-562a97669d9b`
- Backblaze B2 asset SHA-256: `6a1e69f82b93dbfadcaf9f86a672f611bf2f76675ee262d4bf79f7ee1f23c441`
- Native manifest hash: `d4ae8034cc836a890a7f498bb512341448563a71230c180dddf0efa96c335e13`
- `manifest.verify() == True`
- Replay verified
- Recorded provider cost: `0.0`

## Architecture

```text
Opportunity -> Rights -> Economics -> Budget Authorization
            -> Genblaze -> Pollinations -> Backblaze B2
            -> Verified Manifest -> Replay
```

The FastAPI app exposes judge-friendly endpoints for status, opportunity
evidence, replay, decision certificates, and the scorecard.

## What We Learned

The most important work was not generating an image. It was separating true
LIVE evidence from sample assets, failed attempts, advertised rewards, and
unverified claims. The product became stronger when failed provider attempts
were preserved instead of hidden.

## Challenges

NVIDIA NIM credentials were available, but the Flux image endpoint timed out.
Google/Gemini image generation was not a safe zero-cost path. The final build
uses Pollinations because it provided a real free image endpoint without API
keys or billing, while Genblaze and B2 still supplied the verifiable pipeline
and storage proof.

## Future Work

- Add paid provider reconciliation when real revenue or sponsor credits exist.
- Add richer media evaluation beyond manifest verification.
- Support production-grade provider fallback policies with explicit budget caps.
- Add a hosted dashboard for browsing B2 evidence bundles.
- Extend the proof flow from controlled image proof to full contest-ready video.

## Sponsor Usage

Backblaze B2 stores the durable evidence layer: asset, native Genblaze manifest,
source snapshots, decisions, events, receipts, and replay metadata.

Genblaze orchestrates the media pipeline, writes the native manifest, records
asset metadata, and verifies the manifest through `manifest.verify()`.

Pollinations provides the final free generation endpoint used for the verified
LIVE proof.
