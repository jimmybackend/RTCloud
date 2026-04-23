from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def build_inventory(repo_root: str | Path) -> dict[str, list[str]]:
    """Return a local inventory of immutable object ids.

    This is a small v0 helper for future sync work. A real network protocol
    would compare this inventory with a remote repository and request only the
    missing chunks, manifests, and snapshots.
    """
    repo = Repository(repo_root)
    repo.init()
    return repo.inventory()
