# RTCloud Architecture

## Role inside RT Stack

RTCloud is the persistent storage and synchronization layer of RT Stack.

It sits between RT-native object semantics and physical storage backends. Its job is not only to save bytes, but to preserve:

- identity
- integrity
- history
- reconstructibility
- partial access
- synchronization state

## Core model

### Chunks
Chunks are the smallest logical immutable units of stored content.

### Blobs
In v0, one stored blob equals one chunk. In later phases a blob may pack multiple chunks.

### Manifests
A manifest defines how a logical object is reconstructed from ordered chunks.

### Snapshots
A snapshot represents a consistent point-in-time state for one or more logical objects.

### Index
The SQLite database accelerates lookup, but it must always be rebuildable from immutable objects.

### Refs
Refs are mutable named pointers to snapshots.

## Primary invariants

1. Content objects are immutable.
2. References are mutable.
3. Hashes identify content.
4. Hashes are computed from canonical serialization.
5. Indexes can be discarded and rebuilt.
6. Partial byte-range reads are first-class.

## v0 implementation choices

- fixed-size chunking
- SHA-256
- local filesystem backend
- JSON manifests and snapshots
- SQLite index
- single-writer practical model

## Planned evolution

- variable-size chunking
- cloud backends
- pack blobs
- stronger sync protocol
- replication policies
- cryptographic signatures
