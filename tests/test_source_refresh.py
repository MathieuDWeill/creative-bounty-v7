from pathlib import Path
from types import SimpleNamespace
import json

from creative_bounty.models import Opportunity
import creative_bounty.source_refresh as sr


def _op():
    return Opportunity(
        id="x", source="official", title="x", url="https://example.test/rules",
        reward=10, deadline="2026-08-01", media_type="image", deliverables=["x"],
        ai_policy="AI allowed", policy_evidence="AI allowed", ai_permission_explicit=True,
    )


class FakeResponse:
    status=200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return b"rules-v1"


def test_source_fingerprint_does_not_interpret_content(monkeypatch):
    monkeypatch.setattr(sr, "urlopen", lambda req, timeout: FakeResponse())
    report=sr.fetch_source_fingerprint(_op())
    assert report["ok"] is True
    assert len(report["content_sha256"]) == 64
    assert "rights" not in report


def test_source_refresh_detects_change(monkeypatch, tmp_path):
    bodies=iter([b"rules-v1", b"rules-v2"])
    class DynamicResponse(FakeResponse):
        def read(self): return next(bodies)
    monkeypatch.setattr(sr, "urlopen", lambda req, timeout: DynamicResponse())
    p1=sr.write_refresh_report(_op(), tmp_path)
    p2=sr.write_refresh_report(_op(), tmp_path)
    r1=json.loads(p1.read_text()); r2=json.loads(p2.read_text())
    assert r1["changed_since_previous"] is False
    assert r2["changed_since_previous"] is True
