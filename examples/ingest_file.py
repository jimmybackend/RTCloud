from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from rtcloud.storage.repository import Repository


def main() -> None:
    repo = Repository("demo_repo")
    repo.init()

    sample = Path("demo_repo") / "sample.txt"
    sample.write_text("RTCloud demo file for chunking and manifest creation.\n" * 50, encoding="utf-8")

    manifest = repo.ingest_file(sample, logical_name="docs/sample.txt", chunk_size=128)
    print("Created manifest:", manifest.manifest_id)
    print("Manifest path   :", repo.manifest_path_for_id(manifest.manifest_id))


if __name__ == "__main__":
    main()
