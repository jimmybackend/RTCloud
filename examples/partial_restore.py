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

    manifests = list((repo.root / "manifests").rglob("*.json"))
    if not manifests:
        raise SystemExit("No manifests found. Run examples/ingest_file.py first.")

    manifest_path = manifests[0]
    data = repo.read_range(manifest_path, start=10, length=64)
    output = Path("tmp_restore.bin")
    output.write_bytes(data)
    print(f"Wrote {len(data)} bytes to {output}")


if __name__ == "__main__":
    main()
