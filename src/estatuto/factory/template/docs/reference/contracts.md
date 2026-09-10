# Contracts and protocol surface

## Protocol (vendored from El Estatuto)

| Document | Where |
|---|---|
| `peg.manifest/1.0.0` | `GET /peg/v1/manifest`, `manifest.json` |
| `peg.assignment/1.0.0` | request body of `POST /peg/v1/assignments` |
| `peg.result/1.0.0` | `200` answer of `POST /peg/v1/assignments` |
| `peg.refusal/1.0.0` | `4xx`/`5xx` answer of `POST /peg/v1/assignments` |
| `peg.health-report/1.0.0` | `GET /peg/v1/health` |

The schemas live under `contracts/peg/`, byte-identical to the standard's.

## Domain contracts

| Contract | File | Role |
|---|---|---|
| `__SLUG__.work-assignment/1.0.0` | `contracts/work-assignment-v1.0.0.json` | input of `cap___SLUG___work01` |
| `__SLUG__.work-result/1.0.0` | `contracts/work-result-v1.0.0.json` | output; travels in `handoff_payload` |
| `__SLUG__.evidence-bundle/1.0.0` | `contracts/evidence-bundle-v1.0.0.json` | evidence |

## Error codes

`CONTRACT_INVALID`, `CAPABILITY_UNSUPPORTED`, `POLICY_BLOCKED`, `BUDGET_EXCEEDED`,
`PROVIDER_UNAVAILABLE`, `EVIDENCE_INSUFFICIENT`. Reserved codes keep the protocol's meaning.

## API

::: __PACKAGE__.peg
::: __PACKAGE__.transports
