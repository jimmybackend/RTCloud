from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def test_ingest_creates_manifest_and_chunks(tmp_path: Path) -> None:
    repo = Repository(tmp_path / "repo")
    repo.init()

    source = tmp_path / "source.bin"
    source.write_bytes(b"abcdefghij" * 100)

    manifest = repo.ingest_file(source, logical_name="data/source.bin", chunk_size=64)

    assert manifest.logical_name == "data/source.bin"
    assert manifest.content_size == 1000
    assert len(manifest.chunks) > 1
    assert repo.manifest_path_for_id(manifest.manifest_id).exists()
    for chunk in manifest.chunks:
        assert (repo.root / chunk.store).exists()
