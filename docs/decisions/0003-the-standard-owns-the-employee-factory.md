# 0003 — The employee factory moves from the governor to the standard

**Status:** accepted 2026-09-10.

## Context

La Generala's increment UE-04 produced a minimal employee starter kit whose own gate required that
adding an employee change nothing in the governor's core. A factory that lives inside the governor
still couples every new employee to the governor's repository, and could only scaffold the
protocol files, not a conforming repository.

## Decision

`estatuto new-employee` creates a complete repository — root files, declaration, documentation,
tooling, CI, protocol adapter, transports, tests, conformance — that passes the standard's gate
and its own tests at birth. La Generala retires its starter kit and points at the standard; its
UE-04 plan stays in its history.

## Consequences

The template is the executable form of the standard; a change to a clause is proven by the
template still passing the gate. The governor keeps its tutorials for in-process employees, which
are compositions, not frameworks.
