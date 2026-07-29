from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel
from .evidence import sha256

class ProvenanceCheck(BaseModel):
    kind: str
    verified: bool
    asset_sha256: str | None = None
    canonical_hash: str | None = None
    note: str


def verify_sample_asset(path: str | Path, expected_sha256: str) -> ProvenanceCheck:
    actual = sha256(Path(path))
    ok = actual == expected_sha256
    return ProvenanceCheck(
        kind="SAMPLE_SHA256",
        verified=ok,
        asset_sha256=actual,
        note="Local SHA-256 integrity check; not a Genblaze provenance manifest.",
    )


def summarize_genblaze_result(result) -> dict:
    """Convert a native Genblaze result into stable evidence without depending on private internals."""
    step = result.run.steps[0]
    if not step.assets:
        return {
            "sample": False,
            "provider_url": None,
            "asset_sha256": None,
            "canonical_manifest_hash": getattr(getattr(result, "manifest", None), "canonical_hash", None),
            "manifest_verified": False,
            "error": getattr(step, "error", "No provider asset was produced."),
            "provider": getattr(step, "provider", None),
            "model": getattr(step, "model", None),
        }
    asset = step.assets[0]
    manifest = getattr(result, "manifest", None)
    canonical_hash = getattr(manifest, "canonical_hash", None)
    verified = bool(manifest.verify()) if manifest is not None and hasattr(manifest, "verify") else None
    return {
        "sample": False,
        "provider_url": getattr(asset, "url", None),
        "asset_sha256": getattr(asset, "sha256", None),
        "canonical_manifest_hash": canonical_hash,
        "manifest_verified": verified,
    }
