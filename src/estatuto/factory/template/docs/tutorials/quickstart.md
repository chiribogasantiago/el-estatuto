# Quickstart

This tutorial takes you from a fresh clone to a served, answered assignment.

## 1. Install and verify

```bash
uv sync --all-groups
uv run pytest
uv run python conformance.py
```

## 2. Serve the protocol

```bash
uv run __SLUG__ serve --port 8765
```

## 3. Read the manifest

```bash
curl -s http://127.0.0.1:8765/peg/v1/manifest
```

The document is `peg.manifest/1.0.0`: identity, protocol versions, profiles, capabilities and
their contracts, modes, error codes, and a digest any consumer can recompute.

## 4. Send an assignment

Build a `peg.assignment/1.0.0` whose `context.request` is a `__SLUG__.work-assignment/1.0.0`
document and whose `context_digest` is the SHA-256 of the canonical JSON of `context`. Post it to
`/peg/v1/assignments`; a `peg.result/1.0.0` comes back with the proposal in `handoff_payload`, or
a `peg.refusal/1.0.0` explains why nothing was executed.
