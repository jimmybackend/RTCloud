# RTCloud Repository Format

## Layout

```text
repo/
├── chunks/
│   └── sha256/
├── manifests/
│   └── sha256/
├── snapshots/
│   └── sha256/
├── refs/
└── index/
    └── rtcloud.db
```

## Chunks

Chunk path format:

```text
chunks/<algo>/<prefix>/<digest>.bin
```

Example:

```text
chunks/sha256/ab/ab12cd34....bin
```

## Manifests

Manifest path format:

```text
manifests/<algo>/<prefix>/<digest>.json
```

Manifest identity is `sha256` over canonical JSON of the payload without `manifest_id`.

## Snapshots

Snapshot path format:

```text
snapshots/<algo>/<prefix>/<digest>.json
```

Snapshot identity is `sha256` over canonical JSON of the payload without `snapshot_id`.

## Refs

Refs are stored as simple text files for v0:

```text
refs/<name>
```

The file contains a single snapshot id.

## Index rebuildability

The repository must remain valid even if `index/rtcloud.db` is removed. The database is an optimization layer and can be reconstructed by scanning manifests and snapshots.
