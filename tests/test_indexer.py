from __future__ import annotations

from pathlib import Path

from rtcloud.storage.repository import Repository


def test_versions_increment_for_same_logical_name(tmp_path: Path) -> None:
    repo = Repository(tmp_path / "repo")
    repo.init()

    source = tmp_path / "file.bin"
    source.write_bytes(b"a" * 10)
    repo.ingest_file(source, logical_name="data/file.bin", chunk_size=4)

    source.write_bytes(b"b" * 10)
    repo.ingest_file(source, logical_name="data/file.bin", chunk_size=4)

    versions = repo.index.list_versions("data/file.bin")
    assert [row[0] for row in versions] == [1, 2]
