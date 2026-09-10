"""Published contracts of __NAME__: the documents the employee accepts and proposes.

Every contract is a closed Pydantic model. ``contracts/<name>-v<version>.json`` is rendered from
these classes and never edited by hand; a published version's rules never change in place.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DIGEST = r"^[a-f0-9]{64}$"
State = Literal["completed", "partial", "blocked", "rejected"]


class StrictModel(BaseModel):
    """Closed, immutable, addressable by field name or alias."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class WorkAssignment(StrictModel):
    """``__SLUG__.work-assignment/1.0.0``: what the employee is asked to do, and with what budget."""

    schema_name: Literal["__SLUG__.work-assignment/1.0.0"] = Field(alias="schema")
    tenant_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    budget_micros: int = Field(ge=0)
    inputs: dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(StrictModel):
    """One piece of evidence: what kind, its digest and where it can be fetched."""

    evidence_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    digest: str = Field(pattern=DIGEST)
    ref: str = Field(min_length=1)


class EvidenceBundle(StrictModel):
    """``__SLUG__.evidence-bundle/1.0.0``: everything a result rests on."""

    schema_name: Literal["__SLUG__.evidence-bundle/1.0.0"] = Field(alias="schema")
    items: list[EvidenceItem] = Field(default_factory=list)


class Receipt(StrictModel):
    """A unit of cost actually incurred. The result's total equals the sum of its receipts."""

    receipt_id: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    cost_micros: int = Field(ge=0)


class WorkResult(StrictModel):
    """``__SLUG__.work-result/1.0.0``: the evidence-first envelope. Always a proposal.

    States are honest: anything other than ``completed`` names its ``error_code``, at least one
    limitation and one actionable next step. The employee never declares acceptance.
    """

    schema_name: Literal["__SLUG__.work-result/1.0.0"] = Field(alias="schema")
    state: State
    employee_id: str = Field(min_length=1)
    employee_version: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    limitations: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    error_code: str | None = None
    evidence: EvidenceBundle
    receipts: list[Receipt] = Field(default_factory=list)
    observed_cost_micros: int = Field(ge=0)
    proposed: Literal[True] = True

    @model_validator(mode="after")
    def _honest(self) -> WorkResult:
        if self.state != "completed":
            if not self.error_code:
                raise ValueError(f"a {self.state} result names its error_code")
            if not self.limitations or not self.next_steps:
                raise ValueError(f"a {self.state} result carries a limitation and a next step")
        if self.observed_cost_micros != sum(item.cost_micros for item in self.receipts):
            raise ValueError("observed_cost_micros must equal the sum of the receipts")
        return self


__all__ = [
    "EvidenceBundle",
    "EvidenceItem",
    "Receipt",
    "State",
    "StrictModel",
    "WorkAssignment",
    "WorkResult",
]
