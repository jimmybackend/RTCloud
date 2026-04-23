from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from rtcloud.core.manifest import ChunkRef, Manifest, canonical_json, sha256_hex
from rtcloud.core.snapshot import Snapshot, SnapshotEntry
from rtcloud.index.sqlite_index import SQLiteIndex


class Repository:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.index = SQLiteIndex(self.root / "index" / "rtcloud.db")

    def init(self) -> None:
        for relative in ["chunks", "manifests", "snapshots", "refs", "index"]:
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        self.index.init()

    def chunk_store_relpath(self, digest: str, algo: str = "sha256") -> str:
        return f"chunks/{algo}/{digest[:2]}/{digest}.bin"

    def write_chunk_if_missing(self, content: bytes, algo: str = "sha256") -> str:
        if algo != "sha256":
            raise ValueError(f"unsupported hash algorithm: {algo}")
        digest = hashlib.sha256(content).hexdigest()
        relpath = self.chunk_store_relpath(digest, algo)
        fullpath = self.root / relpath
        fullpath.parent.mkdir(parents=True, exist_ok=True)
        if not fullpath.exists():
            fullpath.write_bytes(content)
        return relpath

    def ingest_file(self, source_path: str | Path, logical_name: str | None = None, chunk_size: int = 1024 * 1024) -> Manifest:
        source_path = Path(source_path)
        logical_name = logical_name or source_path.name

        chunks: list[ChunkRef] = []
        offset = 0
        index = 0

        with source_path.open("rb") as fh:
            while True:
                piece = fh.read(chunk_size)
                if not piece:
                    break
                digest = hashlib.sha256(piece).hexdigest()
                relpath = self.write_chunk_if_missing(piece)
                chunks.append(
                    ChunkRef(index=index, offset=offset, size=len(piece), hash=f"sha256:{digest}", store=relpath)
                )
                offset += len(piece)
                index += 1

        manifest = Manifest(
            logical_name=logical_name,
            content_size=offset,
            chunking_mode="fixed",
            chunk_size=chunk_size,
            hash_algo="sha256",
            chunks=chunks,
        ).finalize()

        manifest_path = manifest.save(self.root)
        self.index.add_manifest(manifest, manifest_path)
        return manifest

    def manifest_path_for_id(self, manifest_id: str) -> Path:
        algo, digest = manifest_id.split(":", 1)
        return self.root / "manifests" / algo / digest[:2] / f"{digest}.json"

    def snapshot_path_for_id(self, snapshot_id: str) -> Path:
        algo, digest = snapshot_id.split(":", 1)
        return self.root / "snapshots" / algo / digest[:2] / f"{digest}.json"

    def create_snapshot(self, name: str, logical_names: Iterable[str], ref_name: str | None = None) -> Snapshot:
        entries: list[SnapshotEntry] = []
        for logical_name in logical_names:
            manifest_id = self.index.latest_manifest_id(logical_name)
            if manifest_id is None:
                raise FileNotFoundError(f"no manifest found for logical name: {logical_name}")
            entries.append(SnapshotEntry(logical_name=logical_name, manifest_id=manifest_id))

        parent_snapshot_id = self.index.latest_snapshot_id_for_name(name)
        snapshot = Snapshot(name=name, entries=entries, parent_snapshot_id=parent_snapshot_id).finalize()
        snapshot_path = snapshot.save(self.root)
        self.index.add_snapshot(snapshot, snapshot_path)
        if ref_name:
            self.update_ref(ref_name, snapshot.snapshot_id)
        return snapshot

    def update_ref(self, ref_name: str, snapshot_id: str) -> None:
        path = self.root / "refs" / ref_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(snapshot_id + "\n", encoding="utf-8")

    def read_ref(self, ref_name: str) -> str | None:
        path = self.root / "refs" / ref_name
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8").strip() or None

    def load_manifest(self, manifest_path: str | Path) -> Manifest:
        return Manifest.load(manifest_path)

    def restore_file(self, manifest_path: str | Path, output_path: str | Path) -> Path:
        manifest = self.load_manifest(manifest_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as out:
            for chunk in manifest.chunks:
                out.write((self.root / chunk.store).read_bytes())
        return output_path

    def read_range(self, manifest_path: str | Path, start: int, length: int) -> bytes:
        if start < 0 or length < 0:
            raise ValueError("start and length must be non-negative")
        if length == 0:
            return b""

        manifest = self.load_manifest(manifest_path)
        end = start + length
        if start >= manifest.content_size:
            return b""

        parts: list[bytes] = []
        for chunk in manifest.chunks:
            chunk_start = chunk.offset
            chunk_end = chunk.offset + chunk.size
            if chunk_end <= start:
                continue
            if chunk_start >= end:
                break

            local_start = max(start, chunk_start) - chunk_start
            local_end = min(end, chunk_end) - chunk_start
            content = (self.root / chunk.store).read_bytes()
            parts.append(content[local_start:local_end])

        return b"".join(parts)

    def verify_manifest_file(self, manifest_path: str | Path) -> tuple[bool, str]:
        raw = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        expected_id = raw.get("manifest_id", "")
        payload = {
            "schema": raw["schema"],
            "logical_name": raw["logical_name"],
            "content_size": raw["content_size"],
            "chunking": raw["chunking"],
            "chunks": raw["chunks"],
        }
        actual_id = f"sha256:{sha256_hex(canonical_json(payload))}"
        if actual_id != expected_id:
            return False, f"manifest hash mismatch: expected={expected_id} actual={actual_id}"
        return True, "manifest OK"

    def verify_chunks(self, manifest_path: str | Path) -> tuple[bool, list[str]]:
        manifest = self.load_manifest(manifest_path)
        errors: list[str] = []
        total_size = 0
        expected_offset = 0

        for chunk in manifest.chunks:
            algo, expected_digest = chunk.hash.split(":", 1)
            if algo != "sha256":
                errors.append(f"unsupported hash algorithm: {algo}")
                continue

            chunk_path = self.root / chunk.store
            if not chunk_path.exists():
                errors.append(f"missing chunk: {chunk.hash} -> {chunk_path}")
                continue

            content = chunk_path.read_bytes()
            actual_digest = hashlib.sha256(content).hexdigest()
            if actual_digest != expected_digest:
                errors.append(f"corrupt chunk: {chunk.hash} -> actual sha256:{actual_digest}")
            if len(content) != chunk.size:
                errors.append(f"size mismatch: {chunk.hash} expected={chunk.size} actual={len(content)}")
            if chunk.offset != expected_offset:
                errors.append(f"offset gap/overlap at chunk {chunk.index}: expected offset {expected_offset}, got {chunk.offset}")
            expected_offset = chunk.offset + chunk.size
            total_size += len(content)

        if total_size != manifest.content_size:
            errors.append(f"content_size mismatch: manifest={manifest.content_size} actual={total_size}")
        return len(errors) == 0, errors

    def inventory(self) -> dict[str, list[str]]:
        manifests = []
        snapshots = []
        chunks = []
        for path in (self.root / "manifests").rglob("*.json"):
            manifests.append(path.stem)
        for path in (self.root / "snapshots").rglob("*.json"):
            snapshots.append(path.stem)
        for path in (self.root / "chunks").rglob("*.bin"):
            chunks.append(path.stem)
        return {
            "chunks": sorted(chunks),
            "manifests": sorted(manifests),
            "snapshots": sorted(snapshots),
        }
