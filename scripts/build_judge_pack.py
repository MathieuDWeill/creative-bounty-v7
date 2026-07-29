from __future__ import annotations
import json, shutil, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'judge-pack'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

docs=[
    'README.md',
    'docs/architecture.md',
    'docs/judging.md',
    'docs/truth-protocol.md',
    'docs/demo-script.md',
    'docs/live-opportunities.md',
    'docs/b2-governance.md',
    'docs/threat-model.md',
    'docs/v7-jury-story.md',
    'docs/v7-codex-final-mile.md',
]
artifacts=[
    'artifacts/judge-scorecard.json',
    'artifacts/release-candidate.json',
    'artifacts/opportunity-scan.txt',
    'artifacts/submission-validation.txt',
]
for rel in docs + artifacts:
    src=ROOT/rel
    if src.exists():
        dst=OUT/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)

# Include one verified SAMPLE evidence bundle as a concrete audit example.
sample=ROOT/'artifacts'/'evidence'/'opp-ai-permitted-001'
if sample.exists():
    shutil.copytree(sample, OUT/'sample-evidence'/'opp-ai-permitted-001', dirs_exist_ok=True)

# Include verified LIVE proof bundles, if present.
live_root=ROOT/'artifacts'/'evidence'
if live_root.exists():
    for proof in sorted(live_root.glob('*/generations/live-*/genblaze-proof.json')):
        try:
            payload=json.loads(proof.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        if payload.get('manifest_verified') is True:
            evidence_dir=proof.parents[2]
            shutil.copytree(evidence_dir, OUT/'live-evidence'/evidence_dir.name, dirs_exist_ok=True)
        elif payload.get('sample') is False:
            evidence_dir=proof.parents[2]
            shutil.copytree(evidence_dir, OUT/'failed-attempts'/evidence_dir.name, dirs_exist_ok=True)

manifest=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file():
        manifest.append({
            'path':str(p.relative_to(OUT)),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'bytes':p.stat().st_size,
        })
payload={
    'schema':'creative-bounty/judge-pack/v7',
    'files':manifest,
    'truth_note':'This pack contains documentation, validation artifacts, explicitly labeled SAMPLE evidence, verified LIVE Genblaze/B2 evidence, and failed LIVE attempts kept for audit transparency.',
}
(OUT/'judge-pack-manifest.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
archive=shutil.make_archive(str(ROOT/'artifacts'/'creative-bounty-v7-judge-pack'),'zip',OUT)
print(archive)
