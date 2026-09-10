"""The employee factory: fast, complete, deterministic, and it never touches the standard's core."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, cast

import pytest

from estatuto.factory.scaffold import ScaffoldError, scaffold_employee
from estatuto.peg import Manifest, integrity_digest

ROOT = Path(__file__).resolve().parents[1]
PEG_CORE = ("src/estatuto/peg/contracts.py", "src/estatuto/peg/negotiation.py")


def run_in(destination: Path, code: str) -> dict[str, Any]:
    environment = {
        **os.environ,
        "PYTHONPATH": str(destination / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=destination,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return cast(dict[str, Any], json.loads(completed.stdout))


EXCHANGE = """
import json, sys
sys.path.insert(0, ".")
from conformance import fixture_assignment
from archivero.employee import Employee
from archivero.peg import PegEmployee
from archivero.transports import DirectTransport, JsonBytesTransport
import archivero.version as version_module
version_module.EMPLOYEE_VERSION = {version!r}
import archivero.peg as peg_module, archivero.capabilities as capabilities_module
peg_module.EMPLOYEE_VERSION = capabilities_module.EMPLOYEE_VERSION = {version!r}
document = fixture_assignment()
document["employee_version"] = document["capability_version"] = {version!r}
document["tenant_id"] = document["context"]["request"]["tenant_id"] = {tenant!r}
from archivero.capabilities import canonical_digest
document["context_digest"] = canonical_digest(document["context"])
peg = PegEmployee(Employee(version={version!r}))
transport = {{"direct": DirectTransport, "json": JsonBytesTransport}}[{transport!r}](peg)
status, answer = transport.exchange(document)
print(json.dumps({{"status": status, "answer": answer}}, sort_keys=True))
"""


def exchange(
    destination: Path,
    *,
    version: str = "0.1.0",
    tenant: str = "ten_aurora0001",
    transport: str = "direct",
) -> dict[str, Any]:
    return run_in(destination, EXCHANGE.format(version=version, tenant=tenant, transport=transport))


def test_kit_001_scaffold_is_fast_complete_and_deterministic(tmp_path: Path) -> None:
    started = time.perf_counter()
    first = tmp_path / "one"
    scaffold_employee(first, name="El Archivero", slug="archivero", lock=False)
    assert time.perf_counter() - started < 10
    second = tmp_path / "two"
    scaffold_employee(second, name="El Archivero", slug="archivero", lock=False)
    names = sorted(
        path.relative_to(first).as_posix() for path in first.rglob("*") if path.is_file()
    )
    assert names == sorted(
        path.relative_to(second).as_posix() for path in second.rglob("*") if path.is_file()
    )
    for relative in names:
        if (
            "BASELINE" in relative
            or relative.endswith("CHANGELOG.md")
            or "decisions/0001" in relative
        ):
            continue
        assert (first / relative).read_bytes() == (second / relative).read_bytes(), relative
    assert {
        "README.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "PROJECT_MAP.md",
        "estatuto.toml",
        "manifest.json",
        "conformance.py",
    } <= {p.name for p in first.iterdir()}


def test_kit_002_generated_manifest_conforms_to_peg1(employee: Path) -> None:
    document = json.loads((employee / "manifest.json").read_text())
    manifest = Manifest.model_validate(document)
    assert manifest.employee_id == "emp_archivero01" and manifest.profiles == ["CORE"]
    assert document["integrity_digest"] == integrity_digest(document)


def test_kit_003_generated_conformance_is_green(employee: Path) -> None:
    environment = {
        **os.environ,
        "PYTHONPATH": str(employee / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    completed = subprocess.run(
        [sys.executable, "conformance.py"],
        cwd=employee,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_kit_004_two_transports_preserve_identical_semantics(employee: Path) -> None:
    assert exchange(employee, transport="direct") == exchange(employee, transport="json")
    assert exchange(employee)["status"] == 200


def test_kit_005_two_tenants_remain_explicit_and_distinct(employee: Path) -> None:
    aurora = exchange(employee, tenant="ten_aurora0001")["answer"]
    boreal = exchange(employee, tenant="ten_boreal00001")["answer"]
    assert aurora["tenant_id"] == "ten_aurora0001" and boreal["tenant_id"] == "ten_boreal00001"
    assert aurora["output_digest"] != boreal["output_digest"]


def test_kit_006_invalid_document_is_a_typed_refusal_without_result(employee: Path) -> None:
    answer = run_in(
        employee,
        "import json; from archivero.peg import PegEmployee; s, d = PegEmployee().handle({'schema': 'peg.assignment/1.0.0'}); print(json.dumps({'status': s, 'answer': d}))",
    )
    assert answer["status"] == 400
    assert (
        answer["answer"]["schema"] == "peg.refusal/1.0.0"
        and answer["answer"]["error_code"] == "CONTRACT_INVALID"
    )


def test_kit_007_upgrade_and_rollback_are_reproducible(employee: Path) -> None:
    baseline = exchange(employee, version="0.1.0")["answer"]
    candidate = exchange(employee, version="0.2.0")["answer"]
    rollback = exchange(employee, version="0.1.0")["answer"]
    assert candidate["output_digest"] != baseline["output_digest"]
    assert rollback == baseline


def test_kit_008_scaffold_refuses_bad_identifiers_and_nonempty_targets(
    tmp_path: Path, employee: Path
) -> None:
    with pytest.raises(ScaffoldError, match="persona"):
        scaffold_employee(tmp_path / "a", name="archivero", slug="archivero", lock=False)
    with pytest.raises(ScaffoldError, match="slug"):
        scaffold_employee(tmp_path / "b", name="El Archivero", slug="Archivero", lock=False)
    with pytest.raises(ScaffoldError, match="package"):
        scaffold_employee(
            tmp_path / "c", name="El Archivero", slug="archivero", package="1bad", lock=False
        )
    with pytest.raises(ScaffoldError, match="empty"):
        scaffold_employee(employee, name="El Archivero", slug="archivero", lock=False)


def test_kit_009_adding_an_employee_changes_no_protocol_core(tmp_path: Path) -> None:
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PEG_CORE}
    scaffold_employee(tmp_path / "x", name="La Cronista", slug="cronista", lock=False)
    after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PEG_CORE}
    assert before == after
    guide = (ROOT / "docs" / "standard" / "NEW-EMPLOYEE.md").read_text().lower()
    assert all(
        word in guide
        for word in ("charter", "capability", "evidence", "refusal", "rollback", "estatuto gate")
    )
