"""PEG/1 — the Governed Employee Protocol: every document a governor and an employee exchange.

These models are the normative source of the ``peg.*`` schemas. ``schemas/peg/*.json`` is
rendered from them (``estatuto render``) and vendored verbatim under ``contracts/peg/`` by every
conforming framework; the standard gate compares the copies byte for byte.

The protocol is transport-neutral. A conforming employee offers the same semantics through an
in-process port and through HTTP (``POST /peg/v1/assignments``); a JSON round trip must change
nothing. Payloads of the employee's own domain travel by contract reference, never redefined here.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PROTOCOL_NAME = "PEG"
PROTOCOL_VERSION = "1.0.0"
SCHEMA_OWNER = "peg"

SEMVER = r"^[0-9]+\.[0-9]+\.[0-9]+$"
EMPLOYEE_ID = r"^emp_[a-z0-9][a-z0-9_-]{7,63}$"
CAPABILITY_ID = r"^cap_[a-z0-9][a-z0-9_-]{7,63}$"
PACK_ID = r"^pack_[a-z0-9][a-z0-9_-]{3,63}$"
TENANT_ID = r"^ten_[a-z0-9][a-z0-9_-]{7,63}$"
CONTRACT_ID = r"^[a-z][a-z0-9]*\.[a-z0-9]+(-[a-z0-9]+)*/[0-9]+\.[0-9]+\.[0-9]+$"
DIGEST = r"^[a-f0-9]{64}$"
ERROR_CODE = r"^[A-Z][A-Z0-9_]{2,63}$"

Profile = Literal["CORE", "FRAMEWORK", "CONTEXT_PROVIDER"]
Mode = Literal["job", "request", "session", "service/subscription"]
BindingStatus = Literal["active", "suspended", "revoked"]
HealthState = Literal["healthy", "degraded", "unavailable", "unknown"]

Semver = Annotated[str, Field(pattern=SEMVER)]
ContractId = Annotated[str, Field(pattern=CONTRACT_ID)]
Digest = Annotated[str, Field(pattern=DIGEST)]
ErrorCode = Annotated[str, Field(pattern=ERROR_CODE)]

#: Error codes whose meaning the protocol reserves. An employee may publish more; it may not
#: publish one of these with another meaning.
RESERVED_ERROR_CODES: tuple[str, ...] = (
    "CONTRACT_INVALID",
    "PROTOCOL_UNSUPPORTED",
    "CAPABILITY_UNSUPPORTED",
    "AUTHORITY_REQUIRED",
    "POLICY_BLOCKED",
    "BUDGET_EXCEEDED",
    "PROVIDER_UNAVAILABLE",
    "DEPENDENCY_UNAVAILABLE",
    "EVIDENCE_INSUFFICIENT",
    "HUMAN_INTERVENTION_REQUIRED",
    "TERMINAL_CONDITION_UNMET",
    "IDEMPOTENCY_CONFLICT",
    "CANCELLED",
)


class StrictModel(BaseModel):
    """Every protocol document is closed, immutable and addressable by name or alias."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class Capability(StrictModel):
    """One thing an employee can be assigned, with the exact contracts it speaks."""

    capability_id: str = Field(pattern=CAPABILITY_ID)
    version: Semver
    input_contract: ContractId
    output_contract: ContractId
    evidence_contract: ContractId
    cost_unit: str = Field(min_length=1)
    supports_checkpoint: bool
    deprecated_input_contracts: list[ContractId] = Field(default_factory=list)


class Pack(StrictModel):
    """A versioned, recommended procedure over declared capabilities. A pack grants nothing."""

    pack_id: str = Field(pattern=PACK_ID)
    version: Semver
    capabilities: list[str] = Field(min_length=1)


class Manifest(StrictModel):
    """``peg.manifest/1.0.0``: what an employee publishes about itself before any work."""

    schema_name: Literal["peg.manifest/1.0.0"] = Field(alias="schema")
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    protocol_versions: list[Semver] = Field(min_length=1)
    profiles: list[Profile] = Field(min_length=1)
    capabilities: list[Capability] = Field(min_length=1)
    modes: list[Mode] = Field(min_length=1)
    error_codes: list[ErrorCode] = Field(min_length=1)
    packs: list[Pack] = Field(default_factory=list)
    integrity_digest: Digest

    @model_validator(mode="after")
    def _coherent(self) -> Manifest:
        if "CORE" not in self.profiles:
            raise ValueError("every employee implements the CORE profile")
        identities = {(item.capability_id, item.version) for item in self.capabilities}
        if len(identities) != len(self.capabilities):
            raise ValueError("a capability id and version pair must be unique")
        if len(set(self.error_codes)) != len(self.error_codes):
            raise ValueError("error codes must be unique")
        declared = {item.capability_id for item in self.capabilities}
        for pack in self.packs:
            missing = sorted(set(pack.capabilities) - declared)
            if missing:
                raise ValueError(f"pack {pack.pack_id} names undeclared capabilities: {missing}")
        return self


class CompatibilityDemand(StrictModel):
    """``peg.compatibility-demand/1.0.0``: what a governor requires before assigning work."""

    schema_name: Literal["peg.compatibility-demand/1.0.0"] = Field(alias="schema")
    protocol_version: Semver
    required_profiles: list[Profile]
    capability_id: str = Field(pattern=CAPABILITY_ID)
    capability_version: Semver
    input_contract: ContractId
    output_contract: ContractId
    evidence_contract: ContractId
    mode: Mode
    checkpoint_required: bool


class NegotiationDecision(StrictModel):
    """``peg.negotiation-decision/1.0.0``: accept or reject with stable reasons, before work."""

    schema_name: Literal["peg.negotiation-decision/1.0.0"] = Field(alias="schema")
    disposition: Literal["accept", "reject"]
    reasons: list[str]
    decided_at: datetime


class TenantBinding(StrictModel):
    """``peg.tenant-binding/1.0.0``: the governed correspondence between two tenant namespaces.

    Textual equality of identifiers is never accepted as proof; the binding is.
    """

    schema_name: Literal["peg.tenant-binding/1.0.0"] = Field(alias="schema")
    binding_id: str = Field(min_length=1)
    governor_tenant_id: str = Field(min_length=1)
    provider_tenant_id: str = Field(min_length=1)
    provider_namespace: str = Field(min_length=1)
    version: int = Field(ge=1)
    status: BindingStatus
    valid_from: datetime
    valid_until: datetime


class WorkloadBinding(StrictModel):
    """``peg.workload-binding/1.0.0``: authenticates a workload; conveys no tenant membership."""

    schema_name: Literal["peg.workload-binding/1.0.0"] = Field(alias="schema")
    binding_id: str = Field(min_length=1)
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    principal_subject: str = Field(min_length=1)
    consumer_id: str = Field(min_length=1)
    trust_domain: str = Field(min_length=1)
    status: BindingStatus
    valid_until: datetime
    conveys_tenant: Literal[False]


class HealthCapacityObservation(StrictModel):
    """``peg.health-capacity-observation/1.0.0``: a dated, expiring signal; never a selection."""

    schema_name: Literal["peg.health-capacity-observation/1.0.0"] = Field(alias="schema")
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    capability_id: str = Field(pattern=CAPABILITY_ID)
    state: HealthState
    available_units: int = Field(ge=0)
    observed_at: datetime
    valid_until: datetime
    provenance: str = Field(min_length=1)


class HealthReport(StrictModel):
    """``peg.health-report/1.0.0``: the answer of ``GET /peg/v1/health``, one row per capability."""

    schema_name: Literal["peg.health-report/1.0.0"] = Field(alias="schema")
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    observed_at: datetime
    observations: list[HealthCapacityObservation] = Field(min_length=1)


class Assignment(StrictModel):
    """``peg.assignment/1.0.0``: the exact context capsule and identity sent to an employee.

    It conveys no authority: the grant stays with the governor, and the employee works only
    within ``purpose`` and ``acceptance_criteria`` over the capsule whose digest it attests back.
    """

    schema_name: Literal["peg.assignment/1.0.0"] = Field(alias="schema")
    tenant_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    capability_id: str = Field(pattern=CAPABILITY_ID)
    capability_version: Semver
    compatibility_token: str = Field(min_length=1)
    generation: int = Field(ge=1)
    purpose: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)
    context_digest: Digest
    context: dict[str, Any]
    conveys_authority: Literal[False] = False


class Result(StrictModel):
    """``peg.result/1.0.0``: an employee's proposal, attesting the assignment it answers.

    A governor rejects a result that conveys authority or whose identity fields differ from the
    assignment. The domain payload travels in ``handoff_payload`` under the capability's output
    contract; the protocol never redefines it.
    """

    schema_name: Literal["peg.result/1.0.0"] = Field(alias="schema")
    tenant_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    generation: int = Field(ge=1)
    context_digest: Digest
    output_ref: str = Field(min_length=1)
    output_digest: Digest
    evidence_refs: list[str] = Field(min_length=1)
    event_types: list[str]
    provenance_refs: list[str]
    satisfied_deliverables: list[str]
    observed_cost_micros: int = Field(ge=0)
    unsettled_cost_micros: int = Field(ge=0)
    execution_count: int = Field(ge=1)
    handoff_payload: dict[str, Any]
    conveys_authority: bool = False


class Refusal(StrictModel):
    """``peg.refusal/1.0.0``: a typed refusal before or instead of a result.

    Returned when the assignment cannot be executed at all: an invalid document, an
    incompatible demand, a missing authority, an exhausted budget or an unavailable
    dependency. The employee still attests which assignment it refused and what it cost.
    """

    schema_name: Literal["peg.refusal/1.0.0"] = Field(alias="schema")
    assignment_id: str = Field(min_length=1)
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    error_code: ErrorCode
    reasons: list[str] = Field(min_length=1)
    observed_cost_micros: int = Field(ge=0)
    refused_at: datetime
    conveys_authority: Literal[False] = False


class ContextTransportSupport(StrictModel):
    """``peg.context-transport-support/1.0.0``: additive, exact support for composed context.

    Published separately from the manifest so a historical manifest never acquires support by
    inference, and a ``CONTEXT_PROVIDER`` never equals a consumer of assignment context.
    """

    schema_name: Literal["peg.context-transport-support/1.0.0"] = Field(alias="schema")
    employee_id: str = Field(pattern=EMPLOYEE_ID)
    employee_version: Semver
    capability_id: str = Field(pattern=CAPABILITY_ID)
    capability_version: Semver
    protocol_version: Semver
    capsule_contract: ContractId
    receipt_contract: ContractId
    result_attestation_contract: ContractId
    supports_progressive_disclosure: bool
    integrity_digest: Digest


#: Every published protocol document, in the order the schemas are rendered.
DOCUMENTS: tuple[type[StrictModel], ...] = (
    Manifest,
    CompatibilityDemand,
    NegotiationDecision,
    TenantBinding,
    WorkloadBinding,
    HealthCapacityObservation,
    HealthReport,
    Assignment,
    Result,
    Refusal,
    ContextTransportSupport,
)

#: HTTP status a refusal travels with, by reserved error code. Unlisted codes use 422.
REFUSAL_HTTP_STATUS: dict[str, int] = {
    "CONTRACT_INVALID": 400,
    "PROTOCOL_UNSUPPORTED": 422,
    "CAPABILITY_UNSUPPORTED": 422,
    "AUTHORITY_REQUIRED": 403,
    "POLICY_BLOCKED": 403,
    "BUDGET_EXCEEDED": 402,
    "IDEMPOTENCY_CONFLICT": 409,
    "PROVIDER_UNAVAILABLE": 503,
    "DEPENDENCY_UNAVAILABLE": 503,
}


def schema_id(document: type[StrictModel]) -> str:
    """The ``schema`` constant a document class publishes, e.g. ``peg.manifest/1.0.0``."""
    field = document.model_fields["schema_name"]
    literal = field.annotation
    values: tuple[Any, ...] = getattr(literal, "__args__", ())
    if len(values) != 1 or not isinstance(values[0], str):
        raise TypeError(f"{document.__name__} must declare exactly one schema literal")
    return values[0]


def schema_filename(document: type[StrictModel]) -> str:
    """``peg.manifest/1.0.0`` becomes ``manifest-v1.0.0.json``."""
    owner_and_name, _, version = schema_id(document).partition("/")
    _, _, name = owner_and_name.partition(".")
    return f"{name}-v{version}.json"


__all__ = [
    "CAPABILITY_ID",
    "CONTRACT_ID",
    "DIGEST",
    "DOCUMENTS",
    "EMPLOYEE_ID",
    "ERROR_CODE",
    "PACK_ID",
    "PROTOCOL_NAME",
    "PROTOCOL_VERSION",
    "REFUSAL_HTTP_STATUS",
    "RESERVED_ERROR_CODES",
    "SCHEMA_OWNER",
    "SEMVER",
    "TENANT_ID",
    "Assignment",
    "Capability",
    "CompatibilityDemand",
    "ContextTransportSupport",
    "HealthCapacityObservation",
    "HealthReport",
    "Manifest",
    "Mode",
    "NegotiationDecision",
    "Pack",
    "Profile",
    "Refusal",
    "Result",
    "StrictModel",
    "TenantBinding",
    "WorkloadBinding",
    "schema_filename",
    "schema_id",
]
