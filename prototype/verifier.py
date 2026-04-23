from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def verify_manifest_file(manifest_path: str | Path):
    repo = Repository(Path(manifest_path).resolve().parents[3])
    return repo.verify_manifest_file(manifest_path)


def verify_chunks(repo_root: str | Path, manifest_path: str | Path):
    repo = Repository(repo_root)
    return repo.verify_chunks(manifest_path)
