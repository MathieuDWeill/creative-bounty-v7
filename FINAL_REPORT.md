# FINAL REPORT

## Files Produced

Final submission directory:

```text
artifacts/final_submission/
```

Produced files:

- `video.mp4`
- `thumbnail.png`
- `README.pdf`
- `devpost-final.md`
- `creative-bounty-v7-judge-pack.zip`
- `architecture.png`
- `screenshots/home.png`
- `screenshots/status.png`
- `screenshots/scorecard.png`
- `screenshots/replay.png`
- `screenshots/evidence.png`
- `subtitles.srt`
- `narration.txt`
- `video_manifest.json`
- `submission_checklist.md`

Additional release files:

- `README.md`
- `docs/devpost-final.md`
- `artifacts/creative-bounty-v7-judge-pack.zip`
- `artifacts/release-candidate.json`
- `artifacts/judge-scorecard.json`

## LIVE Proof Summary

- Provider: `pollinations-image`
- Model: `flux`
- Genblaze run id: `86a788b9-e8cd-42d9-a355-562a97669d9b`
- B2 asset SHA-256: `6a1e69f82b93dbfadcaf9f86a672f611bf2f76675ee262d4bf79f7ee1f23c441`
- Native manifest hash: `d4ae8034cc836a890a7f498bb512341448563a71230c180dddf0efa96c335e13`
- `manifest.verify() == True`
- LIVE replay verified
- Recorded provider cost: `0.0`

## Checks Performed

Commands executed:

```bash
python scripts/build_judge_pack.py
python scripts/build_final_submission.py
python -m pytest -q
python scripts/validate_submission.py
python scripts/release_candidate_check.py
python scripts/judge_scorecard.py
python scripts/replay_evidence.py artifacts/evidence/live-genblaze-pollinations-flux-proof-001
python scripts/verify_evidence.py artifacts/evidence/live-genblaze-pollinations-flux-proof-001
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration -of json artifacts/final_submission/video.mp4
```

Results:

- `pytest`: 36 passed
- submission validation: PASS
- release candidate: PASS
- release `live_claimed`: true
- judge scorecard: 96/100
- LIVE replay: verified
- audit receipt: verified
- video codec: H.264
- video resolution: 1920x1080
- video frame rate: 30 fps
- video duration: 132.633333 seconds

## Remaining Limitations

- Pollinations is a free public endpoint, not a paid production SLA.
- The verified LIVE proof is a controlled proof run, not a marketplace contest submission.
- The proof asset is an image; some curated opportunities are video opportunities.
- Backblaze B2 is private, so verification uses authenticated B2 access.
- No revenue, customer, contest win, or commercial outcome is claimed.
- Captions are burned directly into rendered video frames because the local ffmpeg build does not include the `subtitles` filter.
- No music is included because no local royalty-free background track was available.

## Exact Commands For Judges

Start local demo:

```bash
PYTHONPATH=src CREATIVE_BOUNTY_PROVIDER=pollinations uvicorn creative_bounty.app:app --host 127.0.0.1 --port 8007
```

Open:

```text
http://127.0.0.1:8007
http://127.0.0.1:8007/api/judge-scorecard
http://127.0.0.1:8007/api/replay/live-genblaze-pollinations-flux-proof-001
http://127.0.0.1:8007/api/evidence/live-genblaze-pollinations-flux-proof-001
```

## Expected Devpost Upload Order

1. Upload `artifacts/final_submission/video.mp4` as the main demo video.
2. Upload `artifacts/final_submission/thumbnail.png` as the project thumbnail.
3. Use `artifacts/final_submission/devpost-final.md` for the Devpost text.
4. Attach `artifacts/final_submission/creative-bounty-v7-judge-pack.zip`.
5. Attach `artifacts/final_submission/architecture.png`.
6. Add screenshots from `artifacts/final_submission/screenshots/`.
7. Link the GitHub repository.
8. Mention that the B2 object is private and verified through authenticated evidence plus native Genblaze manifest.

## Manual Action Remaining

The only remaining manual action is uploading the produced files to Devpost.
