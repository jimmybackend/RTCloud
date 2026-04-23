# RTCloud

RTCloud is the cloud and storage layer of **RT Stack** by **Rethra Communications**.

`RT` means **Resilient Transmission**.

RTCloud stores data internally as RT-compatible structures built around:

- content-addressed chunks
- immutable manifests
- version history
- snapshots
- partial reconstruction
- replication and controlled synchronization

The project is intentionally designed so that **external compatibility lives at the edges** (import, export, controlled sync, decode), while the internal model remains RT-native.

## Relationship with the rest of RT Stack

- **RTCore**: core primitives, identities, schema rules, integrity rules
- **RTPack**: packaging, archival bundles, import/export containers
- **RTStream**: transport, progressive delivery, range and partial read semantics
- **RTCloud**: persistent chunk storage, manifests, versions, snapshots, sync, replication

## Project goals

RTCloud aims to provide a repository model for:

- chunks
- hashes
- future deduplication
- versioning
- snapshots
- partial streaming
- replication
- synchronization

## Design principles

1. **Immutable content**: chunks and manifests are never rewritten.
2. **Mutable references**: refs and heads can move forward.
3. **Content addressing**: object identity comes from hashes.
4. **Reconstructible indexes**: the database is an acceleration layer, not the source of truth.
5. **Partial access**: byte ranges should be resolvable without reconstructing everything.
6. **Public and extensible**: the repository is structured so humans and tools like Codex can continue the work.

## Current repository status

This repository ships a **v0 prototype in Python** with:

- fixed-size chunking
- SHA-256 hashes
- JSON manifests
- SQLite index
- logical version history
- manifest and chunk verification
- full restore and partial range restore

It is intentionally small but executable.

## Repository layout

```text
rtcloud/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── ROADMAP.md
├── pyproject.toml
├── Makefile
├── .gitignore
├── docs/
├── specs/
├── prototype/
├── src/
├── tests/
└── examples/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

rtcloud init --repo ./repo
rtcloud ingest --repo ./repo --file ./sample.bin --name data/sample.bin
rtcloud versions --repo ./repo --name data/sample.bin
rtcloud verify --repo ./repo --manifest ./repo/manifests/sha256/ab/abcdef.json
```

## Development notes for Codex and contributors

The most important contracts to preserve are:

- canonical JSON hashing for manifests and snapshots
- deterministic chunk ordering
- repository layout under `chunks/`, `manifests/`, `snapshots/`, `refs/`, `index/`
- append-only version and snapshot semantics
- index rebuildability from immutable objects

When continuing the implementation, prefer evolving these layers in order:

1. repository format stability
2. manifest and snapshot schemas
3. chunk storage
4. index and rebuild
5. partial read and restore
6. sync protocol
7. backend abstraction for cloud object stores

## Public repository readiness

This repository includes:

- a permissive open-source license
- contributor guidance
- architecture notes
- machine-readable schemas
- working code and tests

That makes it suitable as a public starting point for GitHub and collaborative development.
