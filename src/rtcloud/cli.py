from __future__ import annotations

import argparse
from pathlib import Path

from rtcloud.storage.repository import Repository


def cmd_init(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    print(f"Repository initialized at: {repo.root}")
    print(f"SQLite index           : {repo.index.path}")


def cmd_ingest(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    manifest = repo.ingest_file(args.file, logical_name=args.name, chunk_size=args.chunk_size)
    print(f"Manifest ID : {manifest.manifest_id}")
    print(f"Logical name: {manifest.logical_name}")
    print(f"Content size: {manifest.content_size}")
    print(f"Chunks      : {len(manifest.chunks)}")
    print(f"Manifest    : {repo.manifest_path_for_id(manifest.manifest_id)}")


def cmd_versions(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    rows = repo.index.list_versions(args.name)
    if not rows:
        print("No versions found")
        return
    for version_no, manifest_id, created_at in rows:
        print(f"v{version_no:04d} {created_at} {manifest_id}")


def cmd_snapshot(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    snapshot = repo.create_snapshot(name=args.name, logical_names=args.logical_names, ref_name=args.ref)
    print(f"Snapshot ID : {snapshot.snapshot_id}")
    print(f"Entries     : {len(snapshot.entries)}")
    print(f"Snapshot    : {repo.snapshot_path_for_id(snapshot.snapshot_id)}")
    if args.ref:
        print(f"Ref updated : {args.ref}")


def cmd_verify(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    ok_manifest, manifest_msg = repo.verify_manifest_file(args.manifest)
    print(manifest_msg)
    ok_chunks, errors = repo.verify_chunks(args.manifest)
    if ok_manifest and ok_chunks:
        print("Integrity OK")
        return
    print("Integrity ERROR")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)


def cmd_restore(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    repo.restore_file(args.manifest, args.output)
    print(f"Restored to: {args.output}")


def cmd_restore_range(args: argparse.Namespace) -> None:
    repo = Repository(args.repo)
    repo.init()
    data = repo.read_range(args.manifest, args.start, args.length)
    output = Path(args.output)
    output.write_bytes(data)
    print(f"Wrote {len(data)} bytes to: {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RTCloud v0 prototype CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a repository")
    p_init.add_argument("--repo", required=True, help="Repository root path")
    p_init.set_defaults(func=cmd_init)

    p_ingest = sub.add_parser("ingest", help="Chunk a file, store chunks, write manifest and index version")
    p_ingest.add_argument("--repo", required=True, help="Repository root path")
    p_ingest.add_argument("--file", required=True, help="Source file path")
    p_ingest.add_argument("--name", required=False, help="Logical name inside the repository")
    p_ingest.add_argument("--chunk-size", type=int, default=1024 * 1024, help="Chunk size in bytes")
    p_ingest.set_defaults(func=cmd_ingest)

    p_versions = sub.add_parser("versions", help="List versions for a logical object")
    p_versions.add_argument("--repo", required=True, help="Repository root path")
    p_versions.add_argument("--name", required=True, help="Logical name")
    p_versions.set_defaults(func=cmd_versions)

    p_snapshot = sub.add_parser("snapshot", help="Create a snapshot from the latest manifests")
    p_snapshot.add_argument("--repo", required=True, help="Repository root path")
    p_snapshot.add_argument("--name", required=True, help="Snapshot name")
    p_snapshot.add_argument("--logical-name", dest="logical_names", action="append", required=True, help="Logical name to include; repeatable")
    p_snapshot.add_argument("--ref", required=False, help="Optional ref to update, for example main or stable")
    p_snapshot.set_defaults(func=cmd_snapshot)

    p_verify = sub.add_parser("verify", help="Verify manifest and chunk integrity")
    p_verify.add_argument("--repo", required=True, help="Repository root path")
    p_verify.add_argument("--manifest", required=True, help="Manifest JSON path")
    p_verify.set_defaults(func=cmd_verify)

    p_restore = sub.add_parser("restore", help="Restore a full file from a manifest")
    p_restore.add_argument("--repo", required=True, help="Repository root path")
    p_restore.add_argument("--manifest", required=True, help="Manifest JSON path")
    p_restore.add_argument("--output", required=True, help="Output file path")
    p_restore.set_defaults(func=cmd_restore)

    p_range = sub.add_parser("restore-range", help="Restore a byte range from a manifest")
    p_range.add_argument("--repo", required=True, help="Repository root path")
    p_range.add_argument("--manifest", required=True, help="Manifest JSON path")
    p_range.add_argument("--start", type=int, required=True, help="Start offset")
    p_range.add_argument("--length", type=int, required=True, help="Number of bytes to read")
    p_range.add_argument("--output", required=True, help="Output file path")
    p_range.set_defaults(func=cmd_restore_range)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
