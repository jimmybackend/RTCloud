# Sync Protocol v1 (draft)

This document describes the intended direction for repository-to-repository synchronization.

## Goals

- compare repository state without sending all data
- transfer only missing immutable objects
- verify everything before publication
- update refs only after a consistent snapshot exists

## Proposed sequence

1. Peer A advertises refs and snapshot heads.
2. Peer B requests missing snapshots.
3. Peer B requests missing manifests.
4. Peer B computes missing chunk ids.
5. Peer A streams only required chunks.
6. Peer B verifies hashes.
7. Peer B writes new refs.

## v0 implementation note

The current code includes inventory helpers but does not yet implement network transport. That is left as the next practical phase.
