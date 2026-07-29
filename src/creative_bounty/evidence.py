from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536), b""): h.update(chunk)
    return h.hexdigest()

def write_json(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(obj, "model_dump"): obj=obj.model_dump(mode="json")
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
