# ADR 0002: Fixed chunking for v0

## Status
Accepted

## Decision
The first public prototype uses fixed-size chunking.

## Why
It keeps the implementation small, deterministic, easier to test, and sufficient to validate repository semantics before introducing rolling-hash complexity.
