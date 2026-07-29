# B2 governance design

CREATIVE//BOUNTY treats B2 as an evidence warehouse, not merely an image host.

## Prefix policy

- `evidence/`: accepted assets, source snapshots, decisions, native Genblaze manifests and audit receipts.
- `intermediates/`: retry candidates and temporary production artifacts.

## Lifecycle intent

Intermediate assets are candidates for short lifecycle expiration (default design target: 7 days). Evidence is retained longer (default design target: 30 days). The app exposes these values as **configuration intent**, never as a claim that the remote bucket has been configured.

## Object Lock

Backblaze highlights Object Lock as a way to make provenance records tamper-resistant. CREATIVE//BOUNTY therefore supports an `B2_OBJECT_LOCK` intent flag, but the UI/API must not say Object Lock is active until the remote bucket setting has been independently verified.

## Two provenance layers

1. **Native Genblaze provenance** for real LIVE generations, including the canonical manifest hash and `manifest.verify()` result.
2. **CREATIVE//BOUNTY audit receipt**, a SHA-256 root over the complete evidence directory. This is explicitly *not* represented as a blockchain proof or a Genblaze manifest.

This makes tampering detectable even for non-media decision files such as rights checks, economics and source evidence.
