# Project map and hand-off guide

This document lets another agent pick up work on **__NAME__** without depending on conversation
history.

## 1. Identity and current state

- **Persona:** __NAME__ · **slug:** `__SLUG__` · **package:** `__PACKAGE__` · **employee id:**
  `__EMPLOYEE_ID__` · **role:** employee under El Estatuto __STANDARD_VERSION__.
- **Version:** single source in `src/__PACKAGE__/version.py`; `pyproject.toml`, `manifest.json`
  and `CHANGELOG.md` must agree, and conformance fails if they drift.
- **State:** scaffolded on __DATE__. The method is a placeholder; the charter and baseline are
  skeletons. No horizon is approved.

## 2. Authority hierarchy

Read from highest to lowest authority; when two disagree, the higher one wins and the lower one
is corrected.

1. El Estatuto — the standard this repository conforms to (form: repository, documentation,
   naming, protocol, gates).
2. `docs/governance/CHARTER.md` — what this employee is and is not (substance).
3. `docs/governance/baseline/` — the frozen design description, hashed in `BASELINE.sha256`.
4. `docs/decisions/` — decisions the code depends on; superseded, never edited.
5. `src/__PACKAGE__/capabilities.py` and `contracts.py` — the declared, rendered public surface.
6. Tests, `conformance.py` and `gates/` — executable proof.
7. `docs/governance/program-status.md` — derived state; never edited by hand.
8. `README.md` — orientation. If it diverges from the above, the above prevails.

## 3. Layout

| Path | Role |
|---|---|
| `src/__PACKAGE__/contracts.py` | Published domain contracts (Pydantic, closed). |
| `src/__PACKAGE__/capabilities.py` | Capabilities, error codes, manifest and contract rendering. |
| `src/__PACKAGE__/employee.py` | The method. Invariants here; policy injected. |
| `src/__PACKAGE__/peg.py` | PEG/1 adapter: assignment in, result or refusal out. |
| `src/__PACKAGE__/transports.py` | Direct, JSON-bytes and HTTP transports. |
| `src/__PACKAGE__/cli.py` | `__SLUG__ render`, `__SLUG__ serve`. |
| `contracts/peg/` | The protocol schemas, vendored verbatim from the standard. |
| `contracts/*.json` | Rendered domain contracts. |
| `manifest.json` | Rendered `peg.manifest/1.0.0`. |
| `conformance.py` | Executable conformance. |
| `gates/` | Gate corpora naming the tests that prove each promise. |
| `tests/` | Deterministic tests, named after their subject. |
| `docs/` | Diátaxis documentation, decisions, governance. |
| `work/` | Disposable outputs. Never a source of truth. |

## 4. How to change it

- Add a capability: declare it in `capabilities.py`, add its contracts, render, test, document
  (`docs/howto/add-a-capability.md`), record it in the changelog.
- Change a contract: publish a new version; never edit a published one in place.
- Take a decision: add `docs/decisions/NNNN-slug.md` and list it in the index.
- Deviate from the standard: only with an `[[exception]]` in `estatuto.toml` backed by a decision
  and a sunset date.

## 5. Verification

The chain in `CONTRIBUTING.md`; CI runs it. `estatuto gate .` measures conformance to the
standard and writes `work/framework-standard-gate.json`.
