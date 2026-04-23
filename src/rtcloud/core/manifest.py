from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA = "rtcloud.manifest/v1"
HASH_ALGO = "sha256"


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class ChunkRef:
    index: int
    offset: int
    size: int
    hash: str
    store: str


@dataclass
class Manifest:
    logical_name: str
    content_size: int
    chunking_mode: str
    chunk_size: int
    hash_algo: str
    chunks: list[ChunkRef]
    manifest_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "logical_name": self.logical_name,
            "content_size": self.content_size,
            "chunking": {
                "mode": self.chunking_mode,
                "chunk_size": self.chunk_size,
                "hash": self.hash_algo,
            },
            "chunks": [asdict(chunk) for chunk in self.chunks],
        }

    def finalize(self) -> "Manifest":
        self.manifest_id = f"{self.hash_algo}:{sha256_hex(canonical_json(self.payload()))}"
        return self

    def to_dict(self) -> dict[str, Any]:
        if not self.manifest_id:
            self.finalize()
        data = self.payload()
        data["manifest_id"] = self.manifest_id
        return data

    def save(self, repo_root: str | Path) -> Path:
        repo_root = Path(repo_root)
        if not self.manifest_id:
            self.finalize()
        digest = self.manifest_id.split(":", 1)[1]
        path = repo_root / "manifests" / self.hash_algo / digest[:2] / f"{digest}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Manifest":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        chunks = [ChunkRef(**item) for item in raw["chunks"]]
        return cls(
            logical_name=raw["logical_name"],
            content_size=raw["content_size"],
            chunking_mode=raw["chunking"]["mode"],
            chunk_size=raw["chunking"]["chunk_size"],
            hash_algo=raw["chunking"]["hash"],
            chunks=chunks,
            manifest_id=raw["manifest_id"],
        )
