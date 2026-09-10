# Changelog

All notable changes are recorded here. The format follows Keep a Changelog; the standard follows
semantic versioning: a clause that becomes stricter or a protocol document that changes shape is
a major version, an additive clause or document is a minor, wording and tooling are patches.

## Unreleased

## 1.0.0 — 2026-09-10

### Added
- The standard: `docs/standard/STANDARD.md` (normative rendering) and `ESTATUTO.md` (owner's
  edition), with shared clause identifiers `E-n.m` verified by the gate.
- The Governed Employee Protocol, PEG/1, owned by the standard: eleven `peg.*` documents rendered
  to `schemas/peg/`, including `peg.refusal/1.0.0` and `peg.health-report/1.0.0`, which the
  candidate protocol lacked; the reference negotiation and the manifest integrity digest.
- `estatuto gate`: thirty-three executable controls over a repository's declaration
  (`estatuto.toml`), root, documentation, language, naming, tooling, protocol and change discipline,
  with dated exceptions backed by decision records.
- `estatuto new-employee`: the employee factory, producing a complete conforming repository that
  passes its own tests, conformance and the gate.
- `estatuto sync-peg`, `estatuto changelog-gate`, `estatuto render`.
- The agent directive and the new-employee procedure, in both editions.
- The registry of the house's frameworks (`registry/frameworks.json`).
