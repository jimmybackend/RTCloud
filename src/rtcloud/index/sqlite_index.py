from __future__ import annotations

import sqlite3
from pathlib import Path

from rtcloud.core.manifest import Manifest
from rtcloud.core.snapshot import Snapshot

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS chunks (
    chunk_hash TEXT PRIMARY KEY,
    hash_algo TEXT NOT NULL,
    size INTEGER NOT NULL,
    stored_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS manifests (
    manifest_id TEXT PRIMARY KEY,
    logical_name TEXT NOT NULL,
    content_size INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    chunking_mode TEXT NOT NULL,
    chunk_size INTEGER NOT NULL,
    hash_algo TEXT NOT NULL,
    manifest_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS manifest_chunks (
    manifest_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_hash TEXT NOT NULL,
    chunk_offset INTEGER NOT NULL,
    chunk_size INTEGER NOT NULL,
    PRIMARY KEY (manifest_id, chunk_index),
    FOREIGN KEY (manifest_id) REFERENCES manifests(manifest_id),
    FOREIGN KEY (chunk_hash) REFERENCES chunks(chunk_hash)
);

CREATE TABLE IF NOT EXISTS versions (
    logical_name TEXT NOT NULL,
    version_no INTEGER NOT NULL,
    manifest_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (logical_name, version_no),
    FOREIGN KEY (manifest_id) REFERENCES manifests(manifest_id)
);

CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    parent_snapshot_id TEXT,
    snapshot_path TEXT NOT NULL,
    created_row_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snapshot_entries (
    snapshot_id TEXT NOT NULL,
    logical_name TEXT NOT NULL,
    manifest_id TEXT NOT NULL,
    PRIMARY KEY (snapshot_id, logical_name),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(snapshot_id),
    FOREIGN KEY (manifest_id) REFERENCES manifests(manifest_id)
);
"""


class SQLiteIndex:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def add_manifest(self, manifest: Manifest, manifest_path: str | Path) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO manifests (
                    manifest_id, logical_name, content_size, chunk_count,
                    chunking_mode, chunk_size, hash_algo, manifest_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manifest.manifest_id,
                    manifest.logical_name,
                    manifest.content_size,
                    len(manifest.chunks),
                    manifest.chunking_mode,
                    manifest.chunk_size,
                    manifest.hash_algo,
                    str(manifest_path),
                ),
            )

            for chunk in manifest.chunks:
                algo, _ = chunk.hash.split(":", 1)
                conn.execute(
                    "INSERT OR IGNORE INTO chunks (chunk_hash, hash_algo, size, stored_path) VALUES (?, ?, ?, ?)",
                    (chunk.hash, algo, chunk.size, chunk.store),
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO manifest_chunks (
                        manifest_id, chunk_index, chunk_hash, chunk_offset, chunk_size
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (manifest.manifest_id, chunk.index, chunk.hash, chunk.offset, chunk.size),
                )

            version_no = self.next_version(conn, manifest.logical_name)
            conn.execute(
                "INSERT OR IGNORE INTO versions (logical_name, version_no, manifest_id) VALUES (?, ?, ?)",
                (manifest.logical_name, version_no, manifest.manifest_id),
            )
            conn.commit()

    def add_snapshot(self, snapshot: Snapshot, snapshot_path: str | Path) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO snapshots (snapshot_id, name, created_at, parent_snapshot_id, snapshot_path) VALUES (?, ?, ?, ?, ?)",
                (snapshot.snapshot_id, snapshot.name, snapshot.created_at, snapshot.parent_snapshot_id, str(snapshot_path)),
            )
            for entry in snapshot.entries:
                conn.execute(
                    "INSERT OR IGNORE INTO snapshot_entries (snapshot_id, logical_name, manifest_id) VALUES (?, ?, ?)",
                    (snapshot.snapshot_id, entry.logical_name, entry.manifest_id),
                )
            conn.commit()

    def next_version(self, conn: sqlite3.Connection, logical_name: str) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(version_no), 0) + 1 FROM versions WHERE logical_name = ?",
            (logical_name,),
        ).fetchone()
        return int(row[0])

    def list_versions(self, logical_name: str) -> list[tuple[int, str, str]]:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT version_no, manifest_id, created_at FROM versions WHERE logical_name = ? ORDER BY version_no ASC",
                (logical_name,),
            ).fetchall()
        return [(int(v), str(m), str(c)) for v, m, c in rows]

    def latest_manifest_id(self, logical_name: str) -> str | None:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT manifest_id FROM versions WHERE logical_name = ? ORDER BY version_no DESC LIMIT 1",
                (logical_name,),
            ).fetchone()
        return str(row[0]) if row else None

    def latest_snapshot_id_for_name(self, name: str) -> str | None:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT snapshot_id FROM snapshots WHERE name = ? ORDER BY created_row_at DESC LIMIT 1",
                (name,),
            ).fetchone()
        return str(row[0]) if row else None
