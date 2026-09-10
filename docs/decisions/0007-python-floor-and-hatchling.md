# 0007 — Python 3.12 floor, uv and hatchling for every framework

**Status:** accepted 2026-09-10.

## Context

La Generala and El Corresponsal used uv with hatchling on Python 3.12–3.13; La Bibliotecaria used
setuptools with a Makefile on Python 3.14.

## Decision

Every framework declares `requires-python = ">=3.12"` or higher, builds with hatchling, resolves
with uv, and exposes its maintenance steps through its own CLI rather than a Makefile. A framework
may require a newer interpreter; it records why in a decision.

## Consequences

La Bibliotecaria migrates its build backend and keeps its 3.14 requirement with a decision; the
verification chain becomes the same shape in the three repositories.
