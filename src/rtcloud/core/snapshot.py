from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from rtcloud.core.manifest import canonical_json, sha256_hex

SCHEMA = "rtcloud.snapshot/v1"


@dataclass(frozen=True)
class SnapshotEntry:
    logical_name: str
    manifest_id: str


@dataclass
class Snapshot:
    name: str
    entries: list[SnapshotEntry]
    created_at: str = ""
    parent_snapshot_id: str | None = None
    snapshot_id: str = ""

    def payload(self) -> dict[str, Any]:
        created_at = self.created_at or datetime.now(timezone.utc).isoformat()
        return {
            "schema": SCHEMA,
            "name": self.name,
            "created_at": created_at,
            "parent_snapshot_id": self.parent_snapshot_id,
            "entries": [asdict(entry) for entry in self.entries],
        }

    def finalize(self) -> "Snapshot":
        payload = self.payload()
        self.created_at = payload["created_at"]
        self.snapshot_id = f"sha256:{sha256_hex(canonical_json(payload))}"
        return self

    def to_dict(self) -> dict[str, Any]:
        if not self.snapshot_id:
            self.finalize()
        payload = self.payload()
        payload["snapshot_id"] = self.snapshot_id
        return payload

    def save(self, repo_root: str | Path) -> Path:
        repo_root = Path(repo_root)
        if not self.snapshot_id:
            self.finalize()
        digest = self.snapshot_id.split(":", 1)[1]
        path = repo_root / "snapshots" / "sha256" / digest[:2] / f"{digest}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Snapshot":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        entries = [SnapshotEntry(**entry) for entry in raw["entries"]]
        return cls(
            name=raw["name"],
            created_at=raw["created_at"],
            parent_snapshot_id=raw.get("parent_snapshot_id"),
            entries=entries,
            snapshot_id=raw["snapshot_id"],
        )
