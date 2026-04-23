from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def test_verify_detects_corrupted_chunk(tmp_path: Path) -> None:
    repo = Repository(tmp_path / "repo")
    repo.init()

    source = tmp_path / "source.bin"
    source.write_bytes(b"1234567890" * 50)
    manifest = repo.ingest_file(source, logical_name="data/source.bin", chunk_size=32)
    manifest_path = repo.manifest_path_for_id(manifest.manifest_id)

    first_chunk = repo.root / manifest.chunks[0].store
    first_chunk.write_bytes(b"corruption")

    ok_manifest, _ = repo.verify_manifest_file(manifest_path)
    ok_chunks, errors = repo.verify_chunks(manifest_path)

    assert ok_manifest is True
    assert ok_chunks is False
    assert any("corrupt chunk" in error for error in errors)
