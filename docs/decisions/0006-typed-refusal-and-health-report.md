# 0006 — The protocol gains `peg.refusal` and `peg.health-report`

**Status:** accepted 2026-09-10.

## Context

The candidate protocol defined an assignment and a result, but no document for an employee that
cannot execute at all: an invalid assignment, an incompatible capability, a missing authority, an
exhausted budget. The governor's HTTP bridge treated any non-result body as an artifact mismatch.
Health and capacity had an observation document but no route to obtain it.

## Decision

`peg.refusal/1.0.0` is returned with an HTTP status fixed by its reserved error code
(`CONTRACT_INVALID` 400, `AUTHORITY_REQUIRED`/`POLICY_BLOCKED` 403, `BUDGET_EXCEEDED` 402,
`IDEMPOTENCY_CONFLICT` 409, `PROTOCOL_UNSUPPORTED`/`CAPABILITY_UNSUPPORTED` 422,
`PROVIDER_UNAVAILABLE`/`DEPENDENCY_UNAVAILABLE` 503). `peg.health-report/1.0.0` is what
`GET /peg/v1/health` returns, one observation per capability. `GET /peg/v1/manifest` returns the
manifest.

## Consequences

Every employee serves three routes. The governor maps refusals to its own errors instead of
guessing from a malformed body.
