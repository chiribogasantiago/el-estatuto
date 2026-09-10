# 0004 — A repository's identity is its remote; local paths are descriptive

**Status:** accepted 2026-09-10.

## Context

La Generala recorded its local path as a decision (DK0-001); La Bibliotecaria lived inside a
session output folder; documentation across the house carried machine-specific paths.

## Decision

A framework is identified by its persona, slug and git remote. Local paths never appear in the
live surface (E-4.2); `registry/frameworks.json` records remotes. The owner moved La Bibliotecaria
to a first-level folder alongside the others for convenience; that move is not a clause.

## Consequences

Documentation stays valid on any machine and in CI. The gate never reads absolute paths.
