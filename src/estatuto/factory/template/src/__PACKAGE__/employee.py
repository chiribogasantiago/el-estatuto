"""The method of __NAME__: from a typed assignment to an evidence-first proposal.

``Employee`` owns the invariants — strict contracts, honest states, cost equal to receipts,
``proposed: true`` — and leaves every decision a deployment might want differently to injected
policies and ports. Replace the deterministic placeholder in ``_perform`` with the craft.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from __PACKAGE__.capabilities import EMPLOYEE_ID, canonical_digest
from __PACKAGE__.contracts import EvidenceBundle, EvidenceItem, Receipt, WorkAssignment, WorkResult
from __PACKAGE__.version import EMPLOYEE_VERSION


class Employee:
    """Implements ``cap___SLUG___work01``: one assignment in, one proposal out."""

    def __init__(self, *, version: str = EMPLOYEE_VERSION) -> None:
        self.version = version

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate the assignment, perform the work and return a ``__SLUG__.work-result/1.0.0``."""
        try:
            assignment = WorkAssignment.model_validate(request)
        except ValidationError as error:
            return self._rejected(request, error)
        return self._perform(assignment).model_dump(by_alias=True, mode="json")

    def _perform(self, assignment: WorkAssignment) -> WorkResult:
        """The craft. This placeholder acknowledges the objective deterministically."""
        material = {"assignment": assignment.model_dump(by_alias=True), "version": self.version}
        digest = canonical_digest(material)
        evidence = EvidenceBundle(
            schema="__SLUG__.evidence-bundle/1.0.0",
            items=[
                EvidenceItem(
                    evidence_id=f"evd_{digest[:16]}",
                    kind="computation",
                    digest=digest,
                    ref=f"sha256:{digest}",
                )
            ],
        )
        receipts = [
            Receipt(receipt_id=f"rcp_{digest[:16]}", unit="work-unit", quantity=1, cost_micros=0)
        ]
        return WorkResult(
            schema="__SLUG__.work-result/1.0.0",
            state="completed",
            employee_id=EMPLOYEE_ID,
            employee_version=self.version,
            tenant_id=assignment.tenant_id,
            request_id=assignment.request_id,
            objective=assignment.objective,
            summary=f"Objective acknowledged: {assignment.objective}",
            evidence=evidence,
            receipts=receipts,
            observed_cost_micros=sum(item.cost_micros for item in receipts),
        )

    def _rejected(self, request: dict[str, Any], error: ValidationError) -> dict[str, Any]:
        fields = sorted({str(item["loc"][-1]) for item in error.errors() if item.get("loc")})
        result = WorkResult(
            schema="__SLUG__.work-result/1.0.0",
            state="rejected",
            employee_id=EMPLOYEE_ID,
            employee_version=self.version,
            tenant_id=str(request.get("tenant_id") or "unresolved"),
            request_id=str(request.get("request_id") or "unresolved"),
            objective=str(request.get("objective") or "unresolved"),
            summary="The assignment does not satisfy its contract; no work was performed.",
            limitations=[f"invalid or missing fields: {', '.join(fields) or 'document'}"],
            next_steps=["Send a document that validates against __SLUG__.work-assignment/1.0.0."],
            error_code="CONTRACT_INVALID",
            evidence=EvidenceBundle(schema="__SLUG__.evidence-bundle/1.0.0"),
            observed_cost_micros=0,
        )
        return result.model_dump(by_alias=True, mode="json")


__all__ = ["Employee"]
