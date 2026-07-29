#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil
from pathlib import Path
from creative_bounty.genblaze_adapter import build_b2_backend, installed_versions, live_ready

CHECKS = [
    "B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET",
    "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "GOOGLE_GENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
    "NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY",
]

def check_b2_bucket() -> dict:
    if not all(os.getenv(k) for k in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET")):
        return {"checked": False, "accessible": False, "reason": "missing_credentials"}
    try:
        backend = build_b2_backend()
        page = backend.list("", max_keys=1)
        count = len(getattr(page, "objects", []) or getattr(page, "items", []) or [])
        backend.close()
        return {"checked": True, "accessible": True, "listed_object_count": count}
    except Exception as exc:
        return {"checked": True, "accessible": False, "error_type": type(exc).__name__}

def main():
    provider = os.getenv("CREATIVE_BOUNTY_PROVIDER", "openai")
    ready, missing = live_ready(provider)
    b2 = check_b2_bucket()
    if b2["checked"] and not b2["accessible"]:
        ready = False
    report = {
        "live_ready": ready,
        "missing": missing,
        "credentials": {k: bool(os.getenv(k)) for k in CHECKS},
        "b2_bucket": b2,
        "genblaze_versions": installed_versions(),
        "provider": provider,
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "mode": os.getenv("CREATIVE_BOUNTY_MODE", "SAMPLE"),
        "safety": {
            "secrets_echoed": False,
            "live_execution_started": False,
            "provider_cost_incurred": False,
        },
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/live-preflight.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if ready else 2)

if __name__ == "__main__":
    main()
