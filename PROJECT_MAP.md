# Project map and hand-off guide

This document lets another agent pick up work on **El Estatuto** without depending on
conversation history.

## 1. Identity and current state

- **Persona:** El Estatuto · **slug:** `estatuto` · **package:** `estatuto` · **role:** standard.
- **What it is:** the framework standard of the house and the owner of the Governed Employee
  Protocol (PEG/1). It governs *form* — repository, documentation, naming, tooling, protocol,
  gates — for every framework: the governor (La Generala) and every employee (El Corresponsal,
  La Bibliotecaria, and those to come).
- **Version:** single source in `src/estatuto/version.py`; `pyproject.toml`, `estatuto.toml` and
  `CHANGELOG.md` must agree.
- **State:** 1.0.0. Applied to the three existing frameworks in the same increment that created it;
  each framework's conformance is measured by `estatuto gate` in its own CI.

## 2. Authority hierarchy

1. `docs/standard/STANDARD.md` — the normative text (English). `ESTATUTO.md` is the owner's
   edition with identical clause identifiers; on conflict both are fixed, never one alone.
2. `src/estatuto/peg/contracts.py` → `schemas/peg/` — the protocol.
3. `docs/decisions/` — decisions the standard depends on; superseded, never edited.
4. `src/estatuto/gate/controls.py` + `gates/framework-standard-gate-v1.0.0.json` — what is
   enforced, and by which tests.
5. `docs/standard/NEW-EMPLOYEE.md`, `docs/standard/AGENT-DIRECTIVE.md` — procedures derived from
   the clauses.
6. `registry/frameworks.json` — the frameworks of the house; descriptive.
7. `README.md` — orientation.

Each framework's charter governs its *substance*; the standard never does. When form and substance
collide, a decision is opened here, not an exception there.

## 3. Layout

| Path | Role |
|---|---|
| `ESTATUTO.md` | Owner's edition of the standard (Spanish). |
| `docs/standard/STANDARD.md` | Normative standard (English). |
| `docs/standard/NEW-EMPLOYEE.md` · `docs/es/NUEVO-EMPLEADO.md` | Creating an employee from zero. |
| `docs/standard/AGENT-DIRECTIVE.md` · `docs/es/DIRECTIVA-AGENTES.md` | How agents continue a framework without breaking it. |
| `docs/protocol/PEG-1.md` | The protocol specification. |
| `src/estatuto/peg/` | Protocol models and reference negotiation. |
| `src/estatuto/render.py` | Schema rendering. |
| `schemas/peg/` | Rendered protocol schemas; vendored by every framework. |
| `src/estatuto/gate/` | Declaration loader, text heuristics, controls, runner. |
| `gates/framework-standard-gate-v1.0.0.json` | The gate corpus: controls → tests. |
| `src/estatuto/changelog.py` | The changelog gate. |
| `src/estatuto/factory/` | The employee factory and its template. |
| `src/estatuto/cli.py` | `estatuto render · gate · changelog-gate · sync-peg · new-employee`. |
| `registry/frameworks.json` | The frameworks of the house. |
| `tests/` | Named after their subject. |
| `work/` | Disposable outputs. |

## 4. How to change it

See `CONTRIBUTING.md`: clause and control together; protocol documents by new version; template
changes proven by the gate test; every change recorded under `## Unreleased`.

## 5. Verification

The chain in `AGENTS.md`. CI runs it, including `estatuto gate .` on this repository itself.
