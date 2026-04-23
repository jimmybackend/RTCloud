from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository

DEFAULT_CHUNK_SIZE = 1024 * 1024


def chunk_file(repo_root: str | Path, source_path: str | Path, logical_name: str | None = None, chunk_size: int = DEFAULT_CHUNK_SIZE):
    repo = Repository(repo_root)
    return repo.ingest_file(source_path=source_path, logical_name=logical_name, chunk_size=chunk_size)
