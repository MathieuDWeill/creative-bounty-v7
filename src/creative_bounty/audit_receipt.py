from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXCLUDED = {"audit-receipt.json"}

def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build_receipt(root: str | Path, *, opportunity_id: str, mode: str) -> dict[str, Any]:
    """Build a deterministic Merkle-style receipt over an evidence directory.

    The receipt excludes itself. Every file is hashed, then the sorted
    path:hash leaves are hashed into one root. This is not a blockchain claim;
    it is a portable tamper-detection receipt for the submission bundle.
    """
    root = Path(root)
    files=[]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in EXCLUDED:
            continue
        rel=p.relative_to(root).as_posix()
        digest=_sha256_bytes(p.read_bytes())
        files.append({"path":rel,"sha256":digest,"bytes":p.stat().st_size})
    leaves="\n".join(f"{x['path']}:{x['sha256']}" for x in files).encode()
    return {
        "schema":"creative-bounty/audit-receipt/v1",
        "opportunity_id":opportunity_id,
        "mode":mode,
        "created_at":datetime.now(timezone.utc).isoformat(),
        "algorithm":"sha256(sorted(path:sha256))",
        "file_count":len(files),
        "evidence_root_sha256":_sha256_bytes(leaves),
        "files":files,
        "claims":{
            "is_genblaze_manifest":False,
            "is_blockchain_proof":False,
            "purpose":"portable tamper detection for the CREATIVE//BOUNTY evidence bundle"
        }
    }

def write_receipt(root: str | Path, *, opportunity_id: str, mode: str) -> Path:
    root=Path(root); root.mkdir(parents=True, exist_ok=True)
    receipt=build_receipt(root, opportunity_id=opportunity_id, mode=mode)
    path=root/"audit-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def verify_receipt(root: str | Path) -> tuple[bool, list[str]]:
    root=Path(root); path=root/"audit-receipt.json"
    if not path.exists(): return False,["audit-receipt.json missing"]
    expected=json.loads(path.read_text(encoding="utf-8"))
    current=build_receipt(root, opportunity_id=expected["opportunity_id"], mode=expected["mode"])
    errors=[]
    if current["evidence_root_sha256"] != expected.get("evidence_root_sha256"):
        errors.append("evidence root hash mismatch")
    exp={x["path"]:x["sha256"] for x in expected.get("files",[])}
    cur={x["path"]:x["sha256"] for x in current.get("files",[])}
    if exp != cur: errors.append("file inventory/hash mismatch")
    return not errors,errors
