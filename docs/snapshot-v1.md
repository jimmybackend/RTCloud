# Snapshot v1

A snapshot captures a consistent state for a set of manifests.

## Fields

- `schema`: fixed string `rtcloud.snapshot/v1`
- `name`: snapshot name or namespace
- `created_at`: UTC timestamp
- `parent_snapshot_id`: optional parent snapshot id
- `entries[]`: logical entries captured by the snapshot
- `snapshot_id`: content-derived id added after payload hashing

## Entry fields

- `logical_name`: logical object name
- `manifest_id`: immutable manifest id

## Notes

Snapshots are append-only historical checkpoints. They are the natural publication boundary for synchronization and replication.
