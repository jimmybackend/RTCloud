from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def restore_manifest(repo_root: str | Path, manifest_path: str | Path, output_path: str | Path) -> Path:
    repo = Repository(repo_root)
    repo.init()
    return repo.restore_file(manifest_path, output_path)
