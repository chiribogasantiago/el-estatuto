"""Executable conformance of __NAME__: what must be true before any change is declared done.

Each check is a function returning findings; an empty tuple passes. ``python conformance.py``
prints the verdict as JSON and exits 1 when any check fails.
"""

from __future__ import annotations

import ast
import json
import sys
import tomllib
from pathlib import Path

from jsonschema import Draft202012Validator

from __PACKAGE__.capabilities import (
    EMPLOYEE_ID,
    canonical_digest,
    manifest_document,
    render_publication,
)
from __PACKAGE__.peg import PegEmployee, load_schema
from __PACKAGE__.transports import DirectTransport, JsonBytesTransport
from __PACKAGE__.version import EMPLOYEE_VERSION

ROOT = Path(__file__).resolve().parent


def fixture_assignment() -> dict[str, object]:
    """A valid ``peg.assignment/1.0.0`` for the declared capability."""
    request = {
        "schema": "__SLUG__.work-assignment/1.0.0",
        "tenant_id": "ten_fixture0001",
        "request_id": "req_conformance",
        "objective": "Prove the protocol round trip.",
        "budget_micros": 0,
        "inputs": {},
    }
    context = {"request": request}
    return {
        "schema": "peg.assignment/1.0.0",
        "tenant_id": "ten_fixture0001",
        "mission_id": "mis_fixture0001",
        "run_id": "run_1",
        "obligation_id": "obl_1",
        "assignment_id": "asg_1",
        "employee_id": EMPLOYEE_ID,
        "employee_version": EMPLOYEE_VERSION,
        "capability_id": "cap___SLUG___work01",
        "capability_version": EMPLOYEE_VERSION,
        "compatibility_token": "a" * 64,
        "generation": 1,
        "purpose": "conformance",
        "acceptance_criteria": ["a proposal with evidence comes back"],
        "context_digest": canonical_digest(context),
        "context": context,
        "conveys_authority": False,
    }


def publication_is_current() -> tuple[str, ...]:
    """manifest.json and contracts/ equal their rendering."""
    stale = render_publication(ROOT, check=True)
    return tuple(f"stale: {name}" for name in stale)


def manifest_conforms() -> tuple[str, ...]:
    """The manifest validates against the vendored protocol schema and self-verifies its digest."""
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    findings = [
        error.message
        for error in Draft202012Validator(load_schema("manifest")).iter_errors(manifest)
    ]
    material = {key: value for key, value in manifest.items() if key != "integrity_digest"}
    if manifest.get("integrity_digest") != canonical_digest(material):
        findings.append("integrity_digest does not verify")
    if manifest != manifest_document():
        findings.append("manifest.json differs from the declaration")
    return tuple(findings)


def transports_agree() -> tuple[str, ...]:
    """Direct and JSON-bytes exchanges return identical documents."""
    peg = PegEmployee()
    direct = DirectTransport(peg).exchange(fixture_assignment())
    wire = JsonBytesTransport(peg).exchange(fixture_assignment())
    return (
        () if direct == wire and direct[0] == 200 else ("transports disagree or the fixture fails",)
    )


def invalid_document_is_refused() -> tuple[str, ...]:
    """A document that is not an assignment yields a typed refusal, never a result."""
    status, answer = PegEmployee().handle({"schema": "peg.assignment/1.0.0"})
    ok = (
        status == 400
        and answer["schema"] == "peg.refusal/1.0.0"
        and answer["error_code"] == "CONTRACT_INVALID"
    )
    return () if ok else ("an invalid assignment was not refused as CONTRACT_INVALID",)


def one_version_everywhere() -> tuple[str, ...]:
    """pyproject, version.py, manifest and changelog agree."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    findings = []
    if pyproject["project"]["version"] != EMPLOYEE_VERSION:
        findings.append("pyproject version differs from version.py")
    if manifest["employee_version"] != EMPLOYEE_VERSION:
        findings.append("manifest employee_version differs from version.py")
    if f"\n## {EMPLOYEE_VERSION}" not in changelog:
        findings.append("CHANGELOG.md has no section for the current version")
    return tuple(findings)


def gate_corpora_name_real_tests() -> tuple[str, ...]:
    """Every gate corpus names tests that exist, so no gate passes by collecting nothing."""
    findings = []
    for corpus in sorted((ROOT / "gates").glob("*-gate-v*.json")):
        document = json.loads(corpus.read_text(encoding="utf-8"))
        for case in document["cases"]:
            for nodeid in case["test_nodeids"]:
                path, _, name = nodeid.partition("::")
                source = ROOT / path
                if not source.is_file():
                    findings.append(f"{corpus.name}: {nodeid} names a missing file")
                    continue
                if name:
                    defined = {
                        node.name
                        for node in ast.parse(source.read_text()).body
                        if isinstance(node, ast.FunctionDef)
                    }
                    if name.split("[")[0] not in defined:
                        findings.append(f"{corpus.name}: {nodeid} names a missing test")
    return tuple(findings)


CHECKS = (
    publication_is_current,
    manifest_conforms,
    transports_agree,
    invalid_document_is_refused,
    one_version_everywhere,
    gate_corpora_name_real_tests,
)


def run() -> dict[str, list[str]]:
    """Every check's findings, by name."""
    return {check.__name__: list(check()) for check in CHECKS}


def main() -> int:
    """Print the verdict and exit 1 on any finding."""
    findings = run()
    print(json.dumps({"conformance": findings, "passed": not any(findings.values())}, indent=2))
    return 0 if not any(findings.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
