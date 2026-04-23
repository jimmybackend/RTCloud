from __future__ import annotations

from pathlib import Path

from rtcloud.index.sqlite_index import SQLiteIndex
from rtcloud.storage.repository import Repository


def init_db(repo_root: str | Path):
    repo = Repository(repo_root)
    repo.init()
    return repo.index.path


def index_manifest(repo_root: str | Path, manifest, manifest_path: str | Path) -> None:
    del manifest_path
    repo = Repository(repo_root)
    repo.init()
    repo.index.add_manifest(manifest, repo.manifest_path_for_id(manifest.manifest_id))
