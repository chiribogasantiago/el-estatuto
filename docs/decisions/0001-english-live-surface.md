# 0001 — The live surface of every framework is English; the archive keeps its language

**Status:** accepted 2026-09-10 by the owner.

## Context

La Generala mixed English code and public docs with Spanish plans and decisions; El Corresponsal
had already moved to English only (its ADR 0008); La Bibliotecaria was Spanish throughout. An agent
continuing any of them could not tell which language to write next, and the three could not share
one documentation shape.

## Decision

Everything in the live surface — code, contracts, README, AGENTS, CONTRIBUTING, CHANGELOG,
PROJECT_MAP, the published documentation, commits — is English. Frozen baselines (hashed SDDs),
historical plans, evidence and history indexes keep the language they were written in and are
archived from the language check. Test fixture payloads may use any language when language
neutrality is under test. The standard itself has an owner's edition in Spanish, kept in parity by
clause identifiers.

## Consequences

One convention to learn. Frozen documents are never translated, because translation would change
their hash. La Bibliotecaria's live documents are translated; its SDD and Núcleo Rector are not.
