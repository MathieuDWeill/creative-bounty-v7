# Truth protocol

CREATIVE//BOUNTY treats demo truthfulness as a product requirement.

## Claim classes

| Claim | Allowed evidence |
|---|---|
| Advertised reward | Captured opportunity source / imported brief |
| AI permitted | Explicit source policy evidence |
| SAMPLE generation | Deterministic local artifact, visibly marked SAMPLE |
| LIVE generation | Native Genblaze provider result |
| B2 stored | Durable URL/object produced by the configured B2 sink |
| Provenance verified | Native Genblaze manifest `verify()` result |
| Revenue | Realized payment evidence only |

## Never collapse these concepts

- **reward ≠ revenue**
- **free credit ≠ external capital**
- **sample SHA-256 ≠ Genblaze provenance**
- **qualified opportunity ≠ won opportunity**
- **authorization ceiling ≠ actual provider charge**

The UI and JSON APIs should preserve these distinctions.

## Source-change protocol

LIVE-CURATED records are snapshots, not claims of continuous freshness. `scripts/refresh_sources.py` can fetch each official rule page and store only technical evidence (timestamp, HTTP status, byte length, SHA-256). It deliberately does **not** let an LLM silently reinterpret rights. If the source hash changes, LIVE execution must return to human review until the structured facts are revalidated.
