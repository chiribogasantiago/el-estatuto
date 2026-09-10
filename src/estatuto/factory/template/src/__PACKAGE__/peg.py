"""The protocol adapter: a ``peg.assignment`` in, a ``peg.result`` or a ``peg.refusal`` out.

The adapter validates against the protocol schemas vendored under ``contracts/peg/`` (copied into
the wheel), checks identity, capability and the context digest, runs the employee and attests the
assignment back. It never conveys authority and never accepts its own work.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from __PACKAGE__.capabilities import (
    CAPABILITIES,
    EMPLOYEE_ID,
    canonical_digest,
    find_capability,
    manifest_document,
)
from __PACKAGE__.employee import Employee
from __PACKAGE__.version import EMPLOYEE_VERSION

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


def schema_directory() -> Path:
    """Where the vendored protocol schemas live: inside the wheel, or the repository in development."""
    packaged = resources.files("__PACKAGE__") / "peg_schemas"
    if packaged.is_dir():
        return Path(str(packaged))
    return Path(__file__).resolve().parents[2] / "contracts" / "peg"


def load_schema(name: str, version: str = "1.0.0") -> dict[str, Any]:
    """The vendored schema for ``peg.<name>/<version>``."""
    path = schema_directory() / f"{name}-v{version}.json"
    document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return document


def validation_errors(document: Any, name: str) -> list[str]:
    """Stable messages for every way ``document`` fails ``peg.<name>/1.0.0``."""
    validator = Draft202012Validator(load_schema(name))
    return sorted(
        f"{'/'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in validator.iter_errors(document)
    )


class PegEmployee:
    """Hands protocol documents to an ``Employee`` and attests what came back."""

    def __init__(self, employee: Employee | None = None) -> None:
        self.employee = employee or Employee()
        self.manifest = manifest_document()

    def refusal(
        self, assignment_id: str, error_code: str, reasons: list[str]
    ) -> tuple[int, dict[str, Any]]:
        """A ``peg.refusal/1.0.0`` with the HTTP status the protocol assigns to its code."""
        document = {
            "schema": "peg.refusal/1.0.0",
            "assignment_id": assignment_id,
            "employee_id": EMPLOYEE_ID,
            "employee_version": EMPLOYEE_VERSION,
            "error_code": error_code,
            "reasons": reasons,
            "observed_cost_micros": 0,
            "refused_at": datetime.now(UTC).isoformat(),
            "conveys_authority": False,
        }
        return REFUSAL_HTTP_STATUS.get(error_code, 422), document

    def handle(self, document: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """Execute one ``peg.assignment/1.0.0``; return the HTTP status and the protocol document."""
        assignment_id = str(document.get("assignment_id") or "unknown")
        errors = validation_errors(document, "assignment")
        if errors:
            return self.refusal(assignment_id, "CONTRACT_INVALID", errors[:8])
        if (
            document["employee_id"] != EMPLOYEE_ID
            or document["employee_version"] != EMPLOYEE_VERSION
        ):
            return self.refusal(
                assignment_id, "CAPABILITY_UNSUPPORTED", ["employee identity mismatch"]
            )
        capability = find_capability(document["capability_id"], document["capability_version"])
        if capability is None:
            return self.refusal(
                assignment_id, "CAPABILITY_UNSUPPORTED", ["capability not declared at this version"]
            )
        context = document["context"]
        if canonical_digest(context) != document["context_digest"]:
            return self.refusal(
                assignment_id, "CONTRACT_INVALID", ["context_digest does not match context"]
            )
        request = context.get("request")
        if (
            not isinstance(request, dict)
            or request.get("schema") != capability.input_contract.contract_id
        ):
            return self.refusal(
                assignment_id,
                "CONTRACT_INVALID",
                [f"context.request must be a {capability.input_contract.contract_id} document"],
            )
        result = self.employee.execute(request)
        if result["state"] == "rejected":
            return self.refusal(
                assignment_id, str(result["error_code"]), list(result["limitations"])
            )
        output_digest = canonical_digest(result)
        evidence_refs = [item["ref"] for item in result["evidence"]["items"]] or [
            f"sha256:{output_digest}"
        ]
        attested = {
            "schema": "peg.result/1.0.0",
            "tenant_id": document["tenant_id"],
            "mission_id": document["mission_id"],
            "obligation_id": document["obligation_id"],
            "assignment_id": document["assignment_id"],
            "employee_id": EMPLOYEE_ID,
            "employee_version": EMPLOYEE_VERSION,
            "generation": document["generation"],
            "context_digest": document["context_digest"],
            "output_ref": f"{capability.output_contract.contract_id}#sha256:{output_digest}",
            "output_digest": output_digest,
            "evidence_refs": evidence_refs,
            "event_types": ["ResultProposed"],
            "provenance_refs": [f"employee:{EMPLOYEE_ID}@{EMPLOYEE_VERSION}"],
            "satisfied_deliverables": ["work-result"] if result["state"] == "completed" else [],
            "observed_cost_micros": result["observed_cost_micros"],
            "unsettled_cost_micros": 0,
            "execution_count": 1,
            "handoff_payload": result,
            "conveys_authority": False,
        }
        problems = validation_errors(attested, "result")
        if problems:  # pragma: no cover - a defect in this module, never a governed outcome
            raise RuntimeError(f"the adapter produced an invalid peg.result: {problems}")
        return 200, attested

    def health_report(self) -> dict[str, Any]:
        """A ``peg.health-report/1.0.0`` with one self-reported observation per capability."""
        now = datetime.now(UTC)
        return {
            "schema": "peg.health-report/1.0.0",
            "employee_id": EMPLOYEE_ID,
            "employee_version": EMPLOYEE_VERSION,
            "observed_at": now.isoformat(),
            "observations": [
                {
                    "schema": "peg.health-capacity-observation/1.0.0",
                    "employee_id": EMPLOYEE_ID,
                    "employee_version": EMPLOYEE_VERSION,
                    "capability_id": item.capability_id,
                    "state": "healthy",
                    "available_units": 1,
                    "observed_at": now.isoformat(),
                    "valid_until": (now + timedelta(seconds=60)).isoformat(),
                    "provenance": "self-report",
                }
                for item in CAPABILITIES
            ],
        }


__all__ = [
    "REFUSAL_HTTP_STATUS",
    "PegEmployee",
    "load_schema",
    "schema_directory",
    "validation_errors",
]
