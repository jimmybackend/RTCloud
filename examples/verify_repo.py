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
    ok_manifest, message = repo.verify_manifest_file(manifest_path)
    ok_chunks, errors = repo.verify_chunks(manifest_path)

    print(message)
    if ok_manifest and ok_chunks:
        print("Repository objects verified successfully")
    else:
        for error in errors:
            print("-", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
