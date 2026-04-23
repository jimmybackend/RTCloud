from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


class RangeReader:
    def __init__(self, repo_root: str | Path):
        self.repo = Repository(repo_root)

    def read(self, manifest_path: str | Path, start: int, length: int) -> bytes:
        return self.repo.read_range(manifest_path, start, length)
