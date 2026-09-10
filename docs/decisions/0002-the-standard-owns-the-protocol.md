# 0002 — The standard owns PEG/1 under the neutral `peg.` namespace

**Status:** accepted 2026-09-10 by the owner.

## Context

The protocol lived in La Generala as `generala.peg-*` documents. El Corresponsal, self-contained by
design, renamed its manifest to `corresponsal.employee-manifest/1.0.0`; the governor's strict
models would then reject it. La Bibliotecaria published no manifest at all and was consumed through
its native API. Three ways to connect, none shared.

## Decision

PEG keeps its acronym with a neutral reading — the Governed Employee Protocol — and belongs to El
Estatuto. Every document is published under `peg.` (`peg.manifest/1.0.0`, `peg.assignment/1.0.0`,
`peg.result/1.0.0`, …), rendered from `estatuto.peg.contracts` and vendored verbatim by every
framework under `contracts/peg/`. The shapes are the governor's candidate shapes with three
changes: `governor_tenant_id` replaces `generala_tenant_id`; capabilities gain
`deprecated_input_contracts` and manifests gain `packs` (El Corresponsal's additive fields); and
two documents are added (decision 0006).

## Consequences

La Generala renames its schema ids and adapters and becomes a consumer of the protocol, not its
owner. El Corresponsal returns to the common manifest schema. La Bibliotecaria publishes a manifest
with the `CONTEXT_PROVIDER` profile and the three routes. Future employees vendor the schemas and
never define protocol shapes of their own.
