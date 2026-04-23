# RTCloud Roadmap

## Phase 0 — Repository foundations

- [x] Define repository layout
- [x] Define manifest v1 JSON schema
- [x] Define snapshot v1 JSON schema
- [x] Implement fixed-size chunking
- [x] Implement SHA-256 content addressing
- [x] Implement local filesystem chunk store
- [x] Implement SQLite index
- [x] Implement verification and restore

## Phase 1 — Usable local versioning

- [ ] Add refs (`main`, `stable`, `latest`)
- [ ] Add snapshot creation per logical collection
- [ ] Add restore by version number
- [ ] Add manifest diff and version diff
- [ ] Add reindex command from immutable objects

## Phase 2 — Synchronization

- [ ] Inventory exchange between repositories
- [ ] Transfer only missing chunks and manifests
- [ ] Publish refs after verification
- [ ] Add pull and push commands
- [ ] Add resumable transfer support

## Phase 3 — Physical optimization

- [ ] Group multiple chunks into pack blobs
- [ ] Add compaction policy
- [ ] Add mark-and-sweep reachability GC
- [ ] Add repository scrub command

## Phase 4 — Advanced chunking

- [ ] Add variable-size chunking
- [ ] Add rolling hash boundary selection
- [ ] Benchmark dedup improvements

## Phase 5 — Cloud backends

- [ ] Add S3-compatible backend
- [ ] Add pluggable blob backend abstraction
- [ ] Add edge cache strategy
- [ ] Add replication policies

## Phase 6 — Hardening

- [ ] Add signing
- [ ] Add encryption at rest
- [ ] Add access control hooks
- [ ] Add audit trail and policy enforcement
