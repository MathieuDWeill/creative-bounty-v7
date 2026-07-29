# Devpost submission draft

## CREATIVE//BOUNTY — Demand before generation

Most generative-media apps begin with a prompt. They generate first and search for value later. CREATIVE//BOUNTY reverses the sequence: it starts from a paid creative opportunity, verifies whether generative AI is actually permitted, evaluates whether the work is economically rational, and only then authorizes a media pipeline.

The product is built around a simple constitution: no user capital, no generation without demand, no AI without explicit permission, no fabricated revenue, and an auditable evidence trail for every decision.

### How it works
1. **Discover:** ingest an observable paid creative brief.
2. **Qualify:** extract reward, deadline, deliverables and media type.
3. **Rights gate:** PASS only when evidence explicitly permits AI; ambiguity becomes REVIEW and prohibition becomes REJECT.
4. **Economic gate:** rank opportunities using a transparent deterministic heuristic without pretending to know the probability of winning.
5. **Generate:** execute the approved media workflow through Genblaze.
6. **Evaluate and retry/fallback:** reject weak candidates and iterate until the quality threshold or attempt limit is reached.
7. **Evidence:** store source brief, assessments, rejected attempts, accepted asset, evaluations and provenance manifests in Backblaze B2.
8. **Outcome:** record actual results separately from advertised reward. A €500 bounty is never €500 of revenue until it is truly realized.

### Why Genblaze
Genblaze is not a wrapper added for eligibility. It is the intended execution fabric: provider-neutral pipelines, retry/fallback behavior, agent loops, streaming progress and verifiable provenance. This makes it possible to change the underlying media supplier without redesigning the opportunity engine.

### Why Backblaze B2
B2 is the evidence warehouse. Every opportunity has a durable audit tree containing the original brief, policy evidence, economic decision, every candidate generation, evaluation result, accepted media and provenance record. The storage layer is therefore part of the trust model rather than a final upload destination.

### What is real vs sample
The repository ships with a deterministic SAMPLE mode so judges and developers can inspect the complete control flow without API cost. SAMPLE data and assets are visibly labeled. The final hackathon demo also includes one real Genblaze provider execution stored in B2: a Pollinations `flux` image run with native Genblaze manifest verification. No sample artifact will be presented as a real marketplace submission, customer, sale or revenue event.

### LIVE proof
- Provider: `pollinations-image`
- Model: `flux`
- Genblaze run id: `86a788b9-e8cd-42d9-a355-562a97669d9b`
- B2 asset SHA-256: `6a1e69f82b93dbfadcaf9f86a672f611bf2f76675ee262d4bf79f7ee1f23c441`
- Native manifest hash: `d4ae8034cc836a890a7f498bb512341448563a71230c180dddf0efa96c335e13`
- `manifest.verify() == True`
- Recorded provider cost: `0.0`

### The larger idea
Generative media is becoming cheap. Attention, rights and economic demand are scarcer. CREATIVE//BOUNTY treats media generation as a resource that should only be deployed after demand and permission exist.
