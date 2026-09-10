# 0005 — The manifest digest covers the manifest itself

**Status:** accepted 2026-09-10.

## Context

El Corresponsal's `integrity_digest` hashed the framework's normative source material — useful to
its maintainers, unverifiable by a consumer that only holds the manifest.

## Decision

`integrity_digest` is the SHA-256 of the canonical JSON of the manifest without the digest field
(sorted keys, compact separators, UTF-8). Any consumer can recompute it; the gate does (E-7.2).
A framework that wants a source digest publishes it elsewhere, for example in its conformance
result.

## Consequences

El Corresponsal re-renders its manifest with the new digest and keeps its source digest in
`conformance.py`'s output.
