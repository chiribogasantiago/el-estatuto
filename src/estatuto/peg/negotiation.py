"""The reference negotiation: exact compatibility before any assignment.

Compatibility requires every material field to match. Sharing a capability id does not make two
employees substitutable; a version, a contract or a mode that differs is a rejection with a
stable reason, decided before an assignment exists. A governor may reimplement this function;
its decisions must equal these on the conformance corpus.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from estatuto.peg.contracts import Capability, CompatibilityDemand, Manifest, NegotiationDecision

REASONS: tuple[str, ...] = (
    "PROTOCOL_UNSUPPORTED",
    "PROFILE_UNSUPPORTED",
    "MODE_UNSUPPORTED",
    "CAPABILITY_UNSUPPORTED",
    "INPUT_CONTRACT_MISMATCH",
    "OUTPUT_CONTRACT_MISMATCH",
    "EVIDENCE_CONTRACT_MISMATCH",
    "CHECKPOINT_UNSUPPORTED",
)


def select_capability(manifest: Manifest, demand: CompatibilityDemand) -> Capability | None:
    """The declared capability whose id and version equal the demand's, if any."""
    return next(
        (
            item
            for item in manifest.capabilities
            if item.capability_id == demand.capability_id
            and item.version == demand.capability_version
        ),
        None,
    )


def negotiate(
    manifest: Manifest, demand: CompatibilityDemand, *, now: datetime | None = None
) -> NegotiationDecision:
    """Decide ``accept`` or ``reject`` with every applicable reason, in the protocol's order."""
    reasons: list[str] = []
    if demand.protocol_version not in manifest.protocol_versions:
        reasons.append("PROTOCOL_UNSUPPORTED")
    if not set(demand.required_profiles) <= set(manifest.profiles):
        reasons.append("PROFILE_UNSUPPORTED")
    if demand.mode not in manifest.modes:
        reasons.append("MODE_UNSUPPORTED")
    selected = select_capability(manifest, demand)
    if selected is None:
        reasons.append("CAPABILITY_UNSUPPORTED")
    else:
        accepted_inputs = {selected.input_contract, *selected.deprecated_input_contracts}
        if demand.input_contract not in accepted_inputs:
            reasons.append("INPUT_CONTRACT_MISMATCH")
        if selected.output_contract != demand.output_contract:
            reasons.append("OUTPUT_CONTRACT_MISMATCH")
        if selected.evidence_contract != demand.evidence_contract:
            reasons.append("EVIDENCE_CONTRACT_MISMATCH")
        if demand.checkpoint_required and not selected.supports_checkpoint:
            reasons.append("CHECKPOINT_UNSUPPORTED")
    decided_at = now or datetime.now(UTC)
    if reasons:
        return NegotiationDecision(
            schema="peg.negotiation-decision/1.0.0",
            disposition="reject",
            reasons=reasons,
            decided_at=decided_at,
        )
    return NegotiationDecision(
        schema="peg.negotiation-decision/1.0.0",
        disposition="accept",
        reasons=[],
        decided_at=decided_at,
    )


def compatibility_token(manifest: Manifest, demand: CompatibilityDemand) -> str:
    """The digest a governor places in ``Assignment.compatibility_token`` after an ``accept``.

    Raises:
        ValueError: when the demand is not compatible; the message lists the reasons.
    """
    decision = negotiate(manifest, demand)
    if decision.disposition != "accept":
        raise ValueError(",".join(decision.reasons))
    payload = {
        "employee_id": manifest.employee_id,
        "employee_version": manifest.employee_version,
        "protocol_version": demand.protocol_version,
        "capability_id": demand.capability_id,
        "capability_version": demand.capability_version,
        "mode": demand.mode,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def integrity_digest(document: dict[str, object]) -> str:
    """The manifest digest: SHA-256 of the canonical JSON without the digest field itself."""
    material = {key: value for key, value in document.items() if key != "integrity_digest"}
    return hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


__all__ = ["REASONS", "compatibility_token", "integrity_digest", "negotiate", "select_capability"]
