from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field

class Event(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    opportunity_id: str
    kind: str
    status: str = "OK"
    message: str
    data: dict = {}

class EventLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: Event) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")

    def read(self) -> list[Event]:
        if not self.path.exists():
            return []
        return [Event.model_validate_json(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]
