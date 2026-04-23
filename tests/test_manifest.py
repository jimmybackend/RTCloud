from __future__ import annotations

from rtcloud.core.manifest import ChunkRef, Manifest


def test_manifest_id_is_stable_for_same_payload() -> None:
    chunks = [ChunkRef(index=0, offset=0, size=3, hash="sha256:abc", store="chunks/sha256/ab/abc.bin")]
    a = Manifest("docs/a.txt", 3, "fixed", 3, "sha256", chunks).finalize()
    b = Manifest("docs/a.txt", 3, "fixed", 3, "sha256", chunks).finalize()
    assert a.manifest_id == b.manifest_id
