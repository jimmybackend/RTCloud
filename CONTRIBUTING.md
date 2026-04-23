# Contributing to RTCloud

Thanks for contributing to RTCloud.

## What matters most

Before implementing new features, preserve these invariants:

- chunks are immutable
- manifests are immutable
- snapshots are immutable
- refs are mutable pointers
- indexes are rebuildable from immutable objects
- object identity is content-derived

## Recommended workflow

1. Open an issue describing the problem or proposal.
2. Keep pull requests focused on one concern.
3. Add or update tests with every change.
4. Update documentation when a format, schema, or protocol changes.
5. When a structural decision is made, add an ADR in `docs/decisions/`.

## Coding style

- Python 3.11+
- type hints required for new public APIs
- keep IO boundaries explicit
- prefer deterministic serialization
- avoid hidden mutable global state

## Commit guidance

Good commits usually indicate the layer being changed, for example:

- `manifest: add snapshot parent linkage`
- `index: rebuild database from manifests`
- `sync: advertise missing chunk inventory`

## Public repository note

This repository is intended to be readable by humans and code-generation tools. Keep module boundaries clear, document assumptions, and avoid introducing undocumented repository formats.
