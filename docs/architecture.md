# Architecture

```text
Opportunity source
      │
      ▼
 Rights / policy gate ──────► REVIEW / REJECT
      │ PASS
      ▼
 Economic prioritizer
      │
      ▼
 Hard budget gate
      │
      ▼
 Genblaze pipeline ──► evaluator ──► retry / fallback
      │                           │
      └──────── accepted ◄────────┘
                  │
                  ▼
          Backblaze B2 evidence
 briefs + decisions + rejected takes + accepted media + manifests + outcome
```

LIVE implementation is designed to use Genblaze `Pipeline`, provider adapters, retry/fallback or `AgentLoop`, and `ObjectStorageSink(S3StorageBackend.for_backblaze(...))`.
