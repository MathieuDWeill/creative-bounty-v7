from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .models import Opportunity


def fetch_source_fingerprint(op: Opportunity, *, timeout: float = 12.0) -> dict:
    """Fetch an official source and fingerprint it without interpreting the page.

    This intentionally does not use an LLM or reclassify rights. A changed page
    invalidates stale confidence and should be human-reviewed before LIVE execution.
    """
    req=Request(op.url, headers={"User-Agent":"CreativeBounty/0.3 source-verifier"})
    captured_at=datetime.now(timezone.utc).isoformat()
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 - explicit public URLs from curated records
            body=resp.read()
            return {
                "opportunity_id":op.id,
                "url":op.url,
                "captured_at":captured_at,
                "http_status":getattr(resp, "status", 200),
                "content_length":len(body),
                "content_sha256":sha256(body).hexdigest(),
                "ok":True,
                "error":None,
            }
    except (HTTPError, URLError, TimeoutError) as exc:
        return {
            "opportunity_id":op.id,
            "url":op.url,
            "captured_at":captured_at,
            "http_status":getattr(exc, "code", None),
            "content_length":0,
            "content_sha256":None,
            "ok":False,
            "error":type(exc).__name__,
        }


def write_refresh_report(op: Opportunity, root: str | Path, *, timeout: float = 12.0) -> Path:
    root=Path(root); root.mkdir(parents=True, exist_ok=True)
    report=fetch_source_fingerprint(op, timeout=timeout)
    previous_files=sorted(root.glob("source-refresh-*.json"))
    previous_hash=None
    if previous_files:
        try:
            previous_hash=json.loads(previous_files[-1].read_text(encoding="utf-8")).get("content_sha256")
        except (json.JSONDecodeError, OSError):
            pass
    report["previous_content_sha256"]=previous_hash
    report["changed_since_previous"]=bool(previous_hash and report["content_sha256"] and previous_hash != report["content_sha256"])
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path=root/f"source-refresh-{stamp}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
