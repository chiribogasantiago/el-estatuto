# Agent directive

For every agent — human or model — that continues a framework of the house. The frameworks are not
finished; this directive keeps them buildable without breaking the structure that lets a governor
connect them, an agent continue them and the owner trust what they claim.

## 1. Read before you write

In this order, always: `AGENTS.md` (the rules and the verification chain), `PROJECT_MAP.md` (where
things live and what has authority), `docs/governance/CHARTER.md` (what the framework is and is
not), `docs/governance/program-status.md` (the honest current state), then the decision and the
plan closest to your task, then the tests that protect the code you are about to touch. Only then
the code. If `PROJECT_MAP.md` and the tree disagree, the map is stale: fix the map as part of the
task.

## 2. What never changes

- **Frozen baselines** under `docs/governance/baseline/`: never edited, never translated. A new
  version is a new file and a new hash line.
- **Generated files**: `manifest.json`, `contracts/*.json`, `docs/governance/program-status.md`,
  history indexes, recorded evidence. Change the source, run the renderer, commit both.
- **Vendored protocol schemas** under `contracts/peg/`: never edited at all. Run
  `estatuto sync-peg .` when the standard publishes a new version.
- **Published contract rules**: a payload that was valid stays valid under the same identifier.
- **Decision records**: superseded by a new record, never edited to say something else.
- **The authority hierarchy** in `PROJECT_MAP.md`: a lower document that contradicts a higher one
  is corrected, never obeyed.

## 3. How a change lands

1. **Decide first.** If the change removes an option, a dependency or a guarantee, or chooses a
   technology, write the decision record before the code. Status, context, decision,
   consequences.
2. **Declare, then render.** Capabilities and contracts change in their declaration module; the
   renderer produces the published files.
3. **Prove.** A test named after the subject; a gate entry so the promise cannot lose its proof;
   coverage at or above the floor.
4. **Record.** `## Unreleased` in `CHANGELOG.md` for any normative change. CI fails otherwise.
5. **Verify.** The whole chain in `AGENTS.md`, including `estatuto gate .`. Not part of it; all
   of it.
6. **Describe.** `PROJECT_MAP.md` and the documentation say exactly what exists now. A claim
   without code and a test behind it is removed, not softened.

## 4. Boundaries between frameworks

- An employee never imports the governor or another employee. Interoperability is contracts,
  ports and the protocol.
- The governor never reaches into an employee's stores or internals; it speaks PEG/1 and keeps
  authority, grants, the cost ledger and acceptance.
- Nobody obtains authority from location, text, a model's output or an open port.
- A protocol shape is never defined locally. If the protocol lacks something, the change is a
  decision in El Estatuto, then a new document version, then `estatuto sync-peg` everywhere.

## 5. Policy belongs outside the core

The core keeps invariants only: strict contracts, explicit authority, provenance, honest states,
cost equal to receipts, isolation per assignment. Anything a deployment might want differently —
providers, models, prices, language, limits, templates, rubrics, vocabularies, terminal conditions
— is an injected policy with a named default. A generality test asserts the absence of burned-in
policy; if you add a literal to the core, that test is where it should fail.

## 6. Honesty about state

- A green test means the declared corpus ran. It does not approve a horizon, select a technology
  or promote a candidate. Say which.
- An error code names the cause that occurred. A policy refusal is `POLICY_BLOCKED`, never
  `CONTRACT_INVALID`; a provider payload the contract cannot accept is `PROVIDER_UNAVAILABLE`.
- Evidence is recorded by scripts and hash-linked. If a source must change, re-record with the
  same script in a dated increment. Never type a hash by hand.
- `program-status.md` is derived. If it is wrong, fix the derivation.

## 7. Deviating from the standard

A deviation is an `[[exception]]` in `estatuto.toml`: the control, a decision record, a reason and
a sunset date. The gate shows it as waived until the sunset, then fails. There is no other way. If
a clause is wrong for every framework, open a decision in El Estatuto and change the clause.

## 8. Language and clutter

English in the live surface; the archive keeps its language; fixture payloads may be anything when
neutrality is under test. No machine paths. No compatibility alias without a changelog entry and a
removal version. No test file named after a phase or a sprint. Nothing under `work/`, `dist/` or
`site/` is a source of truth.

## 9. Before you say it is done

Run the chain. Read the gate output. Re-read `PROJECT_MAP.md` and `program-status.md` as the next
agent will. If either would mislead them, you are not done.
