# PEG/1 — the Governed Employee Protocol

PEG/1 is how a governor and an employee agree on work before any of it happens, hand it over
without transferring authority, and attest what came back. It belongs to El Estatuto: the
documents below are rendered from `estatuto.peg.contracts` to `schemas/peg/` and vendored
verbatim by every framework under `contracts/peg/`. It is transport-neutral; an implementation may
change how it moves bytes without changing capability, authority, evidence, cost or states.

## Documents

| Document | Purpose |
|---|---|
| `peg.manifest/1.0.0` | What an employee publishes about itself: identity, protocol versions, profiles, capabilities and their exact contracts, modes, error codes, packs, a self-verifiable digest. |
| `peg.compatibility-demand/1.0.0` | What a governor requires before assigning: protocol version, profiles, capability id and version, the three contracts, mode, checkpoint. |
| `peg.negotiation-decision/1.0.0` | `accept` or `reject` with stable reasons, decided before an assignment exists. |
| `peg.tenant-binding/1.0.0` | The governed correspondence between the governor's tenant and a provider's tenant. |
| `peg.workload-binding/1.0.0` | Authenticates a workload; `conveys_tenant` is always `false`. |
| `peg.health-capacity-observation/1.0.0` | A dated, expiring health and capacity signal for one capability. Never a selection. |
| `peg.health-report/1.0.0` | What `GET /peg/v1/health` returns: one observation per capability. |
| `peg.assignment/1.0.0` | The exact context capsule and identity sent to an employee. `conveys_authority` is always `false`. |
| `peg.result/1.0.0` | The employee's proposal, attesting the assignment it answers. |
| `peg.refusal/1.0.0` | A typed refusal when nothing can be executed. |
| `peg.context-transport-support/1.0.0` | Additive, exact support for composed context, published separately from the manifest. |

## Profiles

- **CORE** — mandatory. Identity and versions, capabilities, negotiation, states, evidence, errors,
  cost, idempotency, cancellation and the proposed result.
- **FRAMEWORK** — a persistent service with its own administration and health; every interaction
  keeps causality and authority.
- **CONTEXT_PROVIDER** — requests and delivers context with provenance, sufficiency, partiality,
  receipt and validity, without becoming an authority over the mission. La Bibliotecaria declares
  all three.

## Modes

`job` (one assignment, one result), `request` (synchronous exchange), `session` (a sequence under
one grant), `service/subscription` (continuous delivery under a standing grant). A manifest lists
the modes it supports; a demand names one.

## Negotiation

The governor holds the manifest and sends a demand. Compatibility requires every material field to
match a declared capability exactly; a deprecated input contract still listed by the capability is
accepted. The reasons, in order, are `PROTOCOL_UNSUPPORTED`, `PROFILE_UNSUPPORTED`,
`MODE_UNSUPPORTED`, `CAPABILITY_UNSUPPORTED`, `INPUT_CONTRACT_MISMATCH`, `OUTPUT_CONTRACT_MISMATCH`,
`EVIDENCE_CONTRACT_MISMATCH`, `CHECKPOINT_UNSUPPORTED`. On `accept` the governor issues a
compatibility token — the SHA-256 of the canonical JSON of employee id and version, protocol
version, capability id and version, and mode — and places it in every assignment. The reference
implementation is `estatuto.peg.negotiation.negotiate`; a governor may reimplement it, and its
decisions must equal the reference on the conformance corpus.

## Exchange

```text
manifest ──► demand ──► decision (accept | reject)
                            │ accept
                            ▼
   assignment (capsule + digest, no authority) ──► employee
                                                    │
                       result (attests the capsule) ◄┘  or  refusal (typed, with HTTP status)
                            │
                            ▼
            governor verifies, validates, accepts or rejects
```

An assignment names tenant, mission, run, obligation, assignment, employee id and version,
capability id and version, the compatibility token, the generation, the purpose, the acceptance
criteria, the context and its digest. The employee refuses when the digest does not match the
context, when its identity or the capability is not the one declared, or when the context does not
carry a document of the capability's input contract.

A result repeats tenant, mission, obligation, assignment, employee identity, generation and context
digest; it carries an output reference and digest, evidence references, event types, provenance
references, satisfied deliverables, observed and unsettled cost in micro-units, the execution count
and the domain payload in `handoff_payload`. `conveys_authority` must be `false`; a governor rejects
otherwise.

A refusal carries the assignment id, the employee identity, an error code, reasons, the cost
observed before refusing and the time. Its HTTP status follows the code (E-7.9 of the standard).

## Transports

Every employee offers an in-process port — `handle(assignment) -> (status, document)` in the
factory's template — and, when it runs as a service, HTTP:

| Route | Method | Answer |
|---|---|---|
| `/peg/v1/assignments` | `POST` | `200` with `peg.result/1.0.0`, or the refusal's status with `peg.refusal/1.0.0` |
| `/peg/v1/manifest` | `GET` | `200` with `peg.manifest/1.0.0` |
| `/peg/v1/health` | `GET` | `200` with `peg.health-report/1.0.0` |

Bodies are JSON; request bodies are bounded (the template refuses above 1 MiB). A JSON round trip
changes nothing: a test in every employee proves that the direct and the JSON-bytes exchange are
identical. No route grants authority: the governor's grant never travels as a bearer of rights, and
an open port conveys nothing.

## Idempotency and cancellation

`assignment_id` together with `generation` is the idempotency key. Repeating an assignment with the
same key and the same capsule returns the same result; the same key with a different capsule is
`IDEMPOTENCY_CONFLICT`. A new generation replaces the previous one for the assignment and needs the
governor's grant reissued. Cancellation is scoped to the assignment and revokes no grant.

## Bindings and double grant

Tenant identifiers of two frameworks are local to two namespaces; their textual equality is never
proof. A `peg.tenant-binding/1.0.0` declares the correspondence with version, status and validity.
A `peg.workload-binding/1.0.0` binds an employee version to an authenticated principal and a
consumer id and conveys no tenant. Consuming a `CONTEXT_PROVIDER` requires the governor's
assignment grant *and* the provider's own context grant; neither is derived from the other, and a
context package is evidence, not authority.

## Composed context

An employee that consumes context capsules publishes `peg.context-transport-support/1.0.0`
separately, bound exactly to employee, capability and protocol version. The offer carries
references, digests, generation and scope, never raw material or authority; the acknowledgement
names every material observed; the result carries its own digest and a second digest binding it to
the capsule and materials used.

## Canonical JSON and digests

Wherever the protocol digests a document — the manifest's `integrity_digest`, the assignment's
`context_digest`, a result's `output_digest`, the compatibility token — the digest is SHA-256 over
the UTF-8 bytes of the JSON serialization with keys sorted, separators `,` and `:` without spaces
and non-ASCII unescaped. The manifest digest excludes the `integrity_digest` field itself and is
computed over the manifest as published; a publisher therefore writes every field explicitly.

## Versioning

Versions are exact; there is no `latest` and no silent downgrade. An additive change to a document
is a new minor version with a coexistence window; a breaking change is a new major. Every active
mission pins its protocol, employee and capability versions. See
[Version a protocol document](../howto/version-a-protocol-document.md).

## Reserved error codes

`CONTRACT_INVALID`, `PROTOCOL_UNSUPPORTED`, `CAPABILITY_UNSUPPORTED`, `AUTHORITY_REQUIRED`,
`POLICY_BLOCKED`, `BUDGET_EXCEEDED`, `PROVIDER_UNAVAILABLE`, `DEPENDENCY_UNAVAILABLE`,
`EVIDENCE_INSUFFICIENT`, `HUMAN_INTERVENTION_REQUIRED`, `TERMINAL_CONDITION_UNMET`,
`IDEMPOTENCY_CONFLICT`, `CANCELLED`. An employee may publish more; it may not publish one of these
with another meaning.

## Lineage

PEG/1 was designed inside La Generala as *Protocolo de Empleados de La Generala* (increments UE-00
to UE-04, CCF-03). El Estatuto adopts its shapes, renames its owner, adds the refusal and the health
report, and freezes it as the house protocol. La Generala's historical documents remain in its
archive.
