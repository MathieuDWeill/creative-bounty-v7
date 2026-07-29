# Threat model — v5

CREATIVE//BOUNTY treats truthfulness as a security property.

| Threat | Control |
|---|---|
| Advertised prize presented as earned money | reward and realized revenue are separate fields and ledgers |
| SAMPLE output mistaken for provider output | hard SAMPLE/LIVE-CURATED separation and explicit manifest schema |
| AI permission inferred from silence | ambiguity fails to REVIEW |
| Generation starts before approval | lifecycle state machine + preflight gates |
| Budget bypass | ledger invariant checked before paid generation |
| Evidence edited after the run | per-file hashes + audit receipt root |
| Decision summary edited | tamper-evident Decision Certificate |
| Official rules silently change | source snapshot refresh + hash-change review |
| USD and EUR summed into a fake total | currency-separated aggregation |
| Path traversal through evidence viewer | resolved-path containment check |
| Object Lock claimed without verification | requested/verified states kept separate |

## Non-goals
The local audit receipt is not a blockchain notarization, a qualified electronic signature, or a native Genblaze manifest. A LIVE run should preserve both the native Genblaze provenance and the CREATIVE//BOUNTY evidence receipt.
