# Manifest v1

A manifest reconstructs one logical object.

## Fields

- `schema`: fixed string `rtcloud.manifest/v1`
- `logical_name`: stable logical path or identifier
- `content_size`: total logical size in bytes
- `chunking.mode`: currently `fixed`
- `chunking.chunk_size`: configured chunk size in bytes
- `chunking.hash`: hash algorithm used by chunks
- `chunks[]`: ordered chunk descriptors
- `manifest_id`: content-derived id added after payload hashing

## Chunk descriptor

- `index`: zero-based order index
- `offset`: starting byte offset in the logical object
- `size`: chunk size in bytes
- `hash`: chunk id such as `sha256:<digest>`
- `store`: repository-relative blob location

## Notes

The manifest is immutable. A new logical version creates a new manifest instead of mutating the previous one.
