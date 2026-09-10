"""The controls of the framework-standard gate, one function per clause group.

A control receives the repository root and its declaration and returns findings: stable, short
strings a person or an agent can act on. No findings means the control passes. Controls observe
the tree only; they never run the repository's own tooling, which the repository's CI already
does. Each control's identifier is the clause it enforces in ``docs/standard/STANDARD.md``.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from estatuto.gate.config import FrameworkConfig
from estatuto.gate.text import clause_ids, live_markdown, machine_paths, spanish_hits
from estatuto.peg.contracts import (
    CAPABILITY_ID,
    DOCUMENTS,
    ERROR_CODE,
    RESERVED_ERROR_CODES,
    Manifest,
    schema_filename,
)
from estatuto.peg.negotiation import integrity_digest
from estatuto.render import rendered_schema

Check = Callable[[Path, FrameworkConfig], list[str]]

ROOT_FILES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "PROJECT_MAP.md",
    "pyproject.toml",
    "uv.lock",
    "mkdocs.yml",
    ".gitignore",
    ".python-version",
    "estatuto.toml",
)
ROOT_DIRECTORIES: tuple[str, ...] = ("src", "tests", "docs", ".github/workflows", "gates")
DIATAXIS: tuple[str, ...] = ("tutorials", "howto", "topics", "reference")
README_SECTIONS: tuple[tuple[str, str], ...] = (
    ("what it", "What it does / What it is"),
    ("quickstart", "Quickstart"),
    ("documentation", "Documentation"),
    ("verif", "Verifying a change"),
    ("status", "Status"),
)
PROJECT_MAP_SECTIONS: tuple[str, ...] = ("identity", "authority", "layout", "change", "verif")
CI_MARKERS: tuple[str, ...] = (
    "uv ",
    "ruff check",
    "ruff format --check",
    "mypy",
    "pytest",
    "pip-audit",
    "mkdocs build --strict",
    "estatuto gate",
    "uv build",
)
DEV_TOOLS: tuple[str, ...] = ("ruff", "mypy", "pytest", "pytest-cov", "mkdocs", "pip-audit")
GITIGNORE_ENTRIES: tuple[str, ...] = (".venv/", "work/", "dist/", "site/")
CONTRACT_FILE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)-v(\d+\.\d+\.\d+)\.json$")
DECISION_FILE = re.compile(r"^(\d{4}|[A-Z]+\d*-\d{3})-[a-z0-9-]+\.md$")
PLAN_FILE = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*-[a-z][a-z0-9-]*\.md$")
TEST_FILE = re.compile(r"^test_[a-z0-9_]+\.py$")
PROCESS_WORDS = re.compile(r"^test_(phase|sprint|increment|session|week|day|fix|refactor)\d*(_|$)")
VERSION_ASSIGNMENT = re.compile(
    r'^(?:__version__|[A-Z][A-Z0-9_]*_VERSION)\s*=\s*"(\d+\.\d+\.\d+)"', re.M
)
PEG_ROUTES: tuple[str, ...] = ("/peg/v1/assignments", "/peg/v1/manifest", "/peg/v1/health")
MIN_PYTHON = (3, 12)


def _read(root: Path, name: str) -> str:
    path = root / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _pyproject(root: Path) -> dict[str, Any]:
    text = _read(root, "pyproject.toml")
    if not text:
        return {}
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return {}


def _headings(text: str) -> list[str]:
    return [line[3:].strip().lower() for line in text.splitlines() if line.startswith("## ")]


def _python_floor(spec: str) -> tuple[int, int] | None:
    match = re.search(r">=\s*(\d+)\.(\d+)", spec)
    return (int(match.group(1)), int(match.group(2))) if match else None


def _package_dir(root: Path, config: FrameworkConfig) -> Path:
    return root / "src" / config.package


def _version_source(root: Path, config: FrameworkConfig) -> str | None:
    text = _read(root, f"src/{config.package}/version.py")
    match = VERSION_ASSIGNMENT.search(text)
    return match.group(1) if match else None


def _manifest(root: Path) -> dict[str, Any] | None:
    text = _read(root, "manifest.json")
    if not text:
        return None
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        return None
    return document if isinstance(document, dict) else None


# --------------------------------------------------------------------------- E1 identity
def e1_1_declaration(root: Path, config: FrameworkConfig) -> list[str]:
    """The declaration is present and coherent (loading it already validated its shape)."""
    findings: list[str] = []
    if config.role == "standard" and config.slug != "estatuto":
        findings.append("only El Estatuto may declare role = standard")
    return findings


def e1_2_distribution(root: Path, config: FrameworkConfig) -> list[str]:
    """Pyproject names the distribution after the slug and the package lives under src/."""
    findings: list[str] = []
    project = _pyproject(root).get("project", {})
    name = project.get("name")
    if name != config.distribution_name:
        findings.append(
            f"project.name is {name!r}; the standard expects {config.distribution_name!r}"
        )
    package = _package_dir(root, config)
    if not (package / "__init__.py").is_file():
        findings.append(f"src/{config.package}/__init__.py is missing")
    return findings


def e1_3_version(root: Path, config: FrameworkConfig) -> list[str]:
    """One version, in version.py, agreed by pyproject, the changelog and the manifest."""
    findings: list[str] = []
    version = _version_source(root, config)
    if version is None:
        findings.append(f"src/{config.package}/version.py must assign a semantic version constant")
        return findings
    declared = _pyproject(root).get("project", {}).get("version")
    if declared != version:
        findings.append(f"pyproject version {declared!r} differs from version.py {version!r}")
    changelog = _read(root, "CHANGELOG.md")
    if re.search(rf"^## {re.escape(version)}\b", changelog, re.M) is None:
        findings.append(f"CHANGELOG.md has no '## {version}' section")
    manifest = _manifest(root)
    if (
        config.role == "employee"
        and manifest is not None
        and manifest.get("employee_version") != version
    ):
        findings.append("manifest.json employee_version differs from version.py")
    return findings


# --------------------------------------------------------------------------- E2 root layout
def e2_1_root_files(root: Path, config: FrameworkConfig) -> list[str]:
    """Every mandatory root file exists."""
    missing = [name for name in ROOT_FILES if not (root / name).is_file()]
    if config.role == "employee" and not (root / "manifest.json").is_file():
        missing.append("manifest.json")
    text = _read(root, "AGENTS.md") + _read(root, "CONTRIBUTING.md")
    needs_conformance = config.role in {"employee", "governor"}
    if needs_conformance and not (root / "conformance.py").is_file() and " conformance" not in text:
        missing.append("conformance.py (or a documented `<cli> conformance` command)")
    return [f"missing {name}" for name in missing]


def e2_2_root_directories(root: Path, config: FrameworkConfig) -> list[str]:
    """Every mandatory directory exists; contracts/ for frameworks that publish contracts."""
    required = list(ROOT_DIRECTORIES)
    if config.role in {"employee", "governor"}:
        required.append("contracts")
    findings = [f"missing directory {name}/" for name in required if not (root / name).is_dir()]
    workflows = list((root / ".github" / "workflows").glob("*.yml")) + list(
        (root / ".github" / "workflows").glob("*.yaml")
    )
    if (root / ".github" / "workflows").is_dir() and not workflows:
        findings.append(".github/workflows/ has no workflow")
    if (root / "gates").is_dir() and not list((root / "gates").glob("*-gate-v*.json")):
        findings.append("gates/ has no gate corpus named <name>-gate-v<version>.json")
    return findings


def e2_3_gitignore(root: Path, config: FrameworkConfig) -> list[str]:
    """Disposable and generated trees are ignored, so nothing there can pose as truth."""
    text = _read(root, ".gitignore")
    return [
        f".gitignore does not ignore {entry}" for entry in GITIGNORE_ENTRIES if entry not in text
    ]


# --------------------------------------------------------------------------- E3 documentation
def e3_1_diataxis(root: Path, config: FrameworkConfig) -> list[str]:
    """docs/ follows Diátaxis: index plus the four quadrants, each with content."""
    findings: list[str] = []
    docs = root / "docs"
    if not (docs / "index.md").is_file():
        findings.append("docs/index.md is missing")
    for quadrant in DIATAXIS:
        if not list((docs / quadrant).glob("*.md")):
            findings.append(f"docs/{quadrant}/ has no Markdown page")
    return findings


def e3_2_decisions(root: Path, config: FrameworkConfig) -> list[str]:
    """Decision records are numbered, slugged and indexed."""
    findings: list[str] = []
    decisions = root / "docs" / "decisions"
    if not decisions.is_dir():
        return ["docs/decisions/ is missing"]
    index = _read(root, "docs/decisions/index.md")
    if not index:
        findings.append("docs/decisions/index.md is missing")
    for path in sorted(decisions.glob("*.md")):
        if path.name == "index.md":
            continue
        if DECISION_FILE.match(path.name) is None:
            findings.append(f"decision {path.name} is not named NNNN-slug.md")
        if index and path.name not in index:
            findings.append(f"decision {path.name} is not listed in docs/decisions/index.md")
    return findings


def e3_3_governance(root: Path, config: FrameworkConfig) -> list[str]:
    """The charter, a verified frozen baseline and a derived program status exist."""
    findings: list[str] = []
    governance = root / "docs" / "governance"
    if not (governance / "CHARTER.md").is_file():
        findings.append("docs/governance/CHARTER.md is missing")
    if not (governance / "program-status.md").is_file():
        findings.append("docs/governance/program-status.md is missing")
    baseline = governance / "baseline" / "BASELINE.sha256"
    if not baseline.is_file():
        findings.append("docs/governance/baseline/BASELINE.sha256 is missing")
        return findings
    entries = [line.split() for line in baseline.read_text().splitlines() if line.strip()]
    if not entries:
        findings.append("BASELINE.sha256 lists no file")
    for parts in entries:
        if len(parts) != 2 or not re.fullmatch(r"[a-f0-9]{64}", parts[0]):
            findings.append(f"BASELINE.sha256 line is not '<sha256>  <path>': {' '.join(parts)}")
            continue
        digest, relative = parts
        target = governance / "baseline" / relative
        if not target.is_file():
            findings.append(f"baseline file {relative} is missing")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            findings.append(f"baseline file {relative} does not match its recorded hash")
    return findings


def e3_4_project_map(root: Path, config: FrameworkConfig) -> list[str]:
    """PROJECT_MAP.md carries the sections another agent needs to continue the work."""
    headings = " ".join(_headings(_read(root, "PROJECT_MAP.md")))
    return [
        f"PROJECT_MAP.md has no section about {word}"
        for word in PROJECT_MAP_SECTIONS
        if word not in headings
    ]


def e3_5_agents(root: Path, config: FrameworkConfig) -> list[str]:
    """AGENTS.md points at the charter and names the standard gate in its verification chain."""
    text = _read(root, "AGENTS.md")
    findings: list[str] = []
    if "docs/governance/CHARTER.md" not in text:
        findings.append("AGENTS.md does not point at docs/governance/CHARTER.md")
    if "estatuto gate" not in text:
        findings.append("AGENTS.md does not run `estatuto gate` before declaring work done")
    return findings


def e3_6_readme(root: Path, config: FrameworkConfig) -> list[str]:
    """README.md has the sections the standard names."""
    headings = " ".join(_headings(_read(root, "README.md")))
    return [
        f"README.md has no '{label}' section"
        for key, label in README_SECTIONS
        if key not in headings
    ]


def e3_7_mkdocs(root: Path, config: FrameworkConfig) -> list[str]:
    """The site builds strictly from an explicit navigation."""
    text = _read(root, "mkdocs.yml")
    findings: list[str] = []
    if re.search(r"^strict:\s*true", text, re.M) is None:
        findings.append("mkdocs.yml is not strict: true")
    if re.search(r"^nav:", text, re.M) is None:
        findings.append("mkdocs.yml has no explicit nav")
    return findings


def e3_8_changelog(root: Path, config: FrameworkConfig) -> list[str]:
    """CHANGELOG.md keeps an Unreleased section in Keep a Changelog form."""
    text = _read(root, "CHANGELOG.md")
    findings: list[str] = []
    if "\n## Unreleased\n" not in text:
        findings.append("CHANGELOG.md has no '## Unreleased' section")
    if "keep a changelog" not in text.lower():
        findings.append("CHANGELOG.md does not state that it follows Keep a Changelog")
    return findings


# --------------------------------------------------------------------------- E4 language
def e4_1_english(root: Path, config: FrameworkConfig) -> list[str]:
    """The live surface is English; the archive keeps its language."""
    findings: list[str] = []
    for path in live_markdown(root, config.archive):
        hits = spanish_hits(path.read_text(encoding="utf-8"), config.proper_nouns)
        if hits:
            sample = ", ".join(sorted(set(hits))[:6])
            findings.append(f"{path.relative_to(root).as_posix()} has Spanish prose: {sample}")
    return findings


def e4_2_machine_paths(root: Path, config: FrameworkConfig) -> list[str]:
    """No machine-specific path in the live surface."""
    findings: list[str] = []
    for path in live_markdown(root, config.archive):
        if machine_paths(path.read_text(encoding="utf-8")):
            findings.append(f"{path.relative_to(root).as_posix()} contains a machine-specific path")
    return findings


# --------------------------------------------------------------------------- E5 naming
def e5_1_contract_files(root: Path, config: FrameworkConfig) -> list[str]:
    """Published contracts are JSON Schemas named <name>-v<semver>.json whose $id matches."""
    findings: list[str] = []
    contracts = root / "contracts"
    if not contracts.is_dir():
        return findings
    for path in sorted(contracts.rglob("*.json")):
        relative = path.relative_to(contracts).as_posix()
        match = CONTRACT_FILE.match(path.name)
        if match is None:
            findings.append(f"contracts/{relative} is not named <name>-v<semver>.json")
            continue
        owner = "peg" if relative.startswith("peg/") else config.slug
        expected = f"{owner}.{match.group(1)}/{match.group(2)}"
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            findings.append(f"contracts/{relative} is not valid JSON")
            continue
        if not isinstance(document, dict) or document.get("$id") != expected:
            findings.append(f'contracts/{relative} must publish "$id": "{expected}"')
    return findings


def e5_2_tests(root: Path, config: FrameworkConfig) -> list[str]:
    """Test files are named after the subject they protect, never after the process."""
    findings: list[str] = []
    for path in sorted((root / "tests").rglob("test_*.py")):
        if TEST_FILE.match(path.name) is None:
            findings.append(
                f"{path.relative_to(root).as_posix()} is not a lowercase test_<subject>.py"
            )
        if PROCESS_WORDS.match(path.name):
            findings.append(
                f"{path.relative_to(root).as_posix()} is named after a process, not a subject"
            )
    return findings


def e5_3_identifiers(root: Path, config: FrameworkConfig) -> list[str]:
    """An employee's published identifiers follow the protocol patterns."""
    if config.role != "employee":
        return []
    manifest = _manifest(root)
    if manifest is None:
        return ["manifest.json is missing or not a JSON object"]
    findings: list[str] = []
    if manifest.get("employee_id") != config.employee_id:
        findings.append(f"employee_id must be {config.employee_id}")
    for capability in manifest.get("capabilities", []):
        identifier = str(capability.get("capability_id", ""))
        if re.fullmatch(CAPABILITY_ID, identifier) is None:
            findings.append(f"capability id {identifier!r} does not match {CAPABILITY_ID}")
    for code in manifest.get("error_codes", []):
        if re.fullmatch(ERROR_CODE, str(code)) is None:
            findings.append(f"error code {code!r} is not UPPER_SNAKE_CASE")
    return findings


def e5_4_plans(root: Path, config: FrameworkConfig) -> list[str]:
    """Increment plans, when kept, are named <FAMILY>-<NN>-slug.md."""
    plans = root / "docs" / "plans"
    if not plans.is_dir():
        return []
    return [
        f"docs/plans/{path.name} is not named <FAMILY>-<NN>-slug.md"
        for path in sorted(plans.glob("*.md"))
        if PLAN_FILE.match(path.name) is None
    ]


# --------------------------------------------------------------------------- E6 tooling
def e6_1_build(root: Path, config: FrameworkConfig) -> list[str]:
    """Uv + hatchling, Python 3.12 floor."""
    document = _pyproject(root)
    findings: list[str] = []
    backend = document.get("build-system", {}).get("build-backend")
    if backend != "hatchling.build":
        findings.append(f"build-backend is {backend!r}; the standard uses hatchling.build")
    floor = _python_floor(str(document.get("project", {}).get("requires-python", "")))
    if floor is None or floor < MIN_PYTHON:
        findings.append("requires-python must declare a floor of at least 3.12")
    pinned = _read(root, ".python-version").strip()
    parts = pinned.split(".")
    if (
        len(parts) < 2
        or not parts[0].isdigit()
        or not parts[1].isdigit()
        or (int(parts[0]), int(parts[1])) < MIN_PYTHON
    ):
        findings.append(".python-version must pin 3.12 or newer")
    return findings


def e6_2_dev_tools(root: Path, config: FrameworkConfig) -> list[str]:
    """The verification tools are declared as development dependencies."""
    document = _pyproject(root)
    declared: list[str] = []
    for group in document.get("dependency-groups", {}).values():
        declared.extend(str(item) for item in group if isinstance(item, str))
    for extra in document.get("project", {}).get("optional-dependencies", {}).values():
        declared.extend(str(item) for item in extra)
    names = {re.split(r"[\[><=!~; ]", item, maxsplit=1)[0].lower() for item in declared}
    return [
        f"{tool} is not a declared development dependency"
        for tool in DEV_TOOLS
        if tool not in names
    ]


def e6_3_quality_floors(root: Path, config: FrameworkConfig) -> list[str]:
    """Ruff configured, mypy strict, branch coverage floor of at least 80."""
    document = _pyproject(root)
    tool = document.get("tool", {})
    findings: list[str] = []
    if "ruff" not in tool:
        findings.append("[tool.ruff] is not configured")
    if tool.get("mypy", {}).get("strict") is not True:
        findings.append("[tool.mypy] strict is not true")
    floor = tool.get("coverage", {}).get("report", {}).get("fail_under")
    addopts = str(tool.get("pytest", {}).get("ini_options", {}).get("addopts", ""))
    ci = "".join(path.read_text() for path in (root / ".github" / "workflows").glob("*.yml"))
    match = re.search(r"--cov-fail-under[= ](\d+)", addopts + " " + ci)
    effective = (
        floor if isinstance(floor, int | float) else (int(match.group(1)) if match else None)
    )
    if effective is None or effective < 80:
        findings.append(
            "branch coverage floor of at least 80 is not declared "
            "(coverage.report.fail_under or --cov-fail-under)"
        )
    return findings


def e6_4_ci(root: Path, config: FrameworkConfig) -> list[str]:
    """CI runs the whole verification chain, including the standard gate."""
    ci = "".join(path.read_text() for path in (root / ".github" / "workflows").glob("*.yml"))
    if not ci:
        return ["no CI workflow to inspect"]
    return [f"CI does not run `{marker.strip()}`" for marker in CI_MARKERS if marker not in ci]


# --------------------------------------------------------------------------- E7 protocol
def e7_1_vendored_schemas(root: Path, config: FrameworkConfig) -> list[str]:
    """contracts/peg/ mirrors the standard's schemas byte for byte, with no stray file."""
    if config.role == "standard":
        return []
    findings: list[str] = []
    vendored = root / "contracts" / "peg"
    if not vendored.is_dir():
        return ["contracts/peg/ is missing; run `estatuto sync-peg .`"]
    expected = {schema_filename(document): rendered_schema(document) for document in DOCUMENTS}
    for name, text in expected.items():
        target = vendored / name
        if not target.is_file():
            findings.append(f"contracts/peg/{name} is missing")
        elif target.read_text(encoding="utf-8") != text:
            findings.append(f"contracts/peg/{name} differs from the standard's schema")
    for stray in sorted(path.name for path in vendored.glob("*.json")):
        if stray not in expected:
            findings.append(f"contracts/peg/{stray} is not a protocol schema")
    return findings


def e7_2_manifest(root: Path, config: FrameworkConfig) -> list[str]:
    """An employee's manifest validates and carries a self-verifiable integrity digest."""
    if config.role != "employee":
        return []
    manifest = _manifest(root)
    if manifest is None:
        return ["manifest.json is missing or not a JSON object"]
    findings: list[str] = []
    try:
        Manifest.model_validate(manifest)
    except ValidationError as error:
        for item in error.errors()[:6]:
            location = ".".join(str(part) for part in item["loc"])
            findings.append(f"manifest.json {location}: {item['msg']}")
        return findings
    if manifest.get("integrity_digest") != integrity_digest(manifest):
        findings.append("manifest.json integrity_digest is not the digest of the manifest itself")
    return findings


def e7_3_referenced_contracts(root: Path, config: FrameworkConfig) -> list[str]:
    """Every contract an employee's manifest names is published under contracts/."""
    if config.role != "employee":
        return []
    manifest = _manifest(root)
    if manifest is None:
        return []
    findings: list[str] = []
    seen: set[str] = set()
    for capability in manifest.get("capabilities", []):
        references = [
            capability.get("input_contract"),
            capability.get("output_contract"),
            capability.get("evidence_contract"),
            *capability.get("deprecated_input_contracts", []),
        ]
        for reference in references:
            if not isinstance(reference, str) or reference in seen:
                continue
            seen.add(reference)
            owner_name, _, version = reference.partition("/")
            owner, _, name = owner_name.partition(".")
            if owner == "peg":
                continue
            path = root / "contracts" / f"{name}-v{version}.json"
            if not path.is_file():
                findings.append(f"{reference} has no file at contracts/{name}-v{version}.json")
    return findings


def e7_4_documented_surface(root: Path, config: FrameworkConfig) -> list[str]:
    """An employee documents its protocol surface: the three routes and the manifest id."""
    if config.role != "employee":
        return []
    reference = "".join(
        path.read_text(encoding="utf-8") for path in (root / "docs" / "reference").glob("*.md")
    )
    findings = [
        f"docs/reference does not document {route}"
        for route in PEG_ROUTES
        if route not in reference
    ]
    if "peg.manifest/1.0.0" not in reference:
        findings.append("docs/reference does not name peg.manifest/1.0.0")
    return findings


def e7_5_reserved_codes(root: Path, config: FrameworkConfig) -> list[str]:
    """An employee publishes at least CONTRACT_INVALID and only well-formed reserved codes."""
    if config.role != "employee":
        return []
    manifest = _manifest(root)
    if manifest is None:
        return []
    codes = set(manifest.get("error_codes", []))
    findings: list[str] = []
    if "CONTRACT_INVALID" not in codes:
        findings.append("manifest.json must publish CONTRACT_INVALID")
    lowered = {code.lower() for code in codes}
    for reserved in RESERVED_ERROR_CODES:
        variants = {reserved.lower().replace("_", ""), reserved.lower().replace("_", "-")}
        if reserved not in codes and any(code.replace("_", "") in variants for code in lowered):
            findings.append(f"a code resembling {reserved} is published under another spelling")
    return findings


# --------------------------------------------------------------------------- E8 change
def e8_1_exceptions(root: Path, config: FrameworkConfig, *, today: date | None = None) -> list[str]:
    """Every exception names an existing decision, a real control and a future sunset."""
    from estatuto.gate.runner import CONTROL_IDS  # local import: the runner imports this module

    findings: list[str] = []
    current = today or date.today()
    for item in config.exceptions:
        if item.control not in CONTROL_IDS:
            findings.append(f"exception for unknown control {item.control}")
        if not (root / item.decision).is_file():
            findings.append(
                f"exception for {item.control} cites a missing decision {item.decision}"
            )
        if item.sunset <= current:
            findings.append(f"exception for {item.control} expired on {item.sunset.isoformat()}")
    return findings


def e8_2_changelog_gate(root: Path, config: FrameworkConfig) -> list[str]:
    """CI refuses a normative change that does not record itself in the changelog."""
    ci = "".join(path.read_text() for path in (root / ".github" / "workflows").glob("*.yml"))
    if "estatuto changelog-gate" in ci or "check_changelog" in ci:
        return []
    return ["CI does not run the changelog gate (`estatuto changelog-gate --base <ref>`)"]


def e8_3_deprecation_policy(root: Path, config: FrameworkConfig) -> list[str]:
    """CONTRIBUTING.md states the deprecation policy."""
    text = _read(root, "CONTRIBUTING.md").lower()
    return [] if "deprecat" in text else ["CONTRIBUTING.md does not state a deprecation policy"]


# --------------------------------------------------------------------------- E9 standard
def e9_1_clause_parity(root: Path, config: FrameworkConfig) -> list[str]:
    """The Spanish edition and the English standard carry the same clause identifiers."""
    if config.role != "standard":
        return []
    spanish = clause_ids(_read(root, "ESTATUTO.md"))
    english = clause_ids(_read(root, "docs/standard/STANDARD.md"))
    findings: list[str] = []
    if not spanish or not english:
        return ["ESTATUTO.md and docs/standard/STANDARD.md must both carry E-n.m clauses"]
    for missing in sorted(english - spanish):
        findings.append(f"{missing} is in STANDARD.md but not in ESTATUTO.md")
    for missing in sorted(spanish - english):
        findings.append(f"{missing} is in ESTATUTO.md but not in STANDARD.md")
    return findings


@dataclass(frozen=True, slots=True)
class Control:
    """One executable control: its clause, a title and the check that enforces it."""

    control_id: str
    title: str
    roles: tuple[str, ...]
    check: Check


ALL_ROLES: tuple[str, ...] = ("governor", "employee", "standard")
FRAMEWORKS: tuple[str, ...] = ("governor", "employee")

CONTROLS: tuple[Control, ...] = (
    Control("E-1.1", "Declaration present and coherent", ALL_ROLES, e1_1_declaration),
    Control("E-1.2", "Distribution named after the slug; src layout", ALL_ROLES, e1_2_distribution),
    Control("E-1.3", "One version everywhere", ALL_ROLES, e1_3_version),
    Control("E-2.1", "Mandatory root files", ALL_ROLES, e2_1_root_files),
    Control("E-2.2", "Mandatory directories", ALL_ROLES, e2_2_root_directories),
    Control("E-2.3", "Disposable trees ignored", ALL_ROLES, e2_3_gitignore),
    Control("E-3.1", "Diátaxis documentation", ALL_ROLES, e3_1_diataxis),
    Control("E-3.2", "Decision records numbered and indexed", ALL_ROLES, e3_2_decisions),
    Control("E-3.3", "Charter, verified baseline, program status", ALL_ROLES, e3_3_governance),
    Control("E-3.4", "Project map sections", ALL_ROLES, e3_4_project_map),
    Control("E-3.5", "AGENTS.md anchors and gate", ALL_ROLES, e3_5_agents),
    Control("E-3.6", "README sections", ALL_ROLES, e3_6_readme),
    Control("E-3.7", "Strict site with explicit nav", ALL_ROLES, e3_7_mkdocs),
    Control("E-3.8", "Keep a Changelog with Unreleased", ALL_ROLES, e3_8_changelog),
    Control("E-4.1", "English live surface", ALL_ROLES, e4_1_english),
    Control("E-4.2", "No machine-specific paths", ALL_ROLES, e4_2_machine_paths),
    Control("E-5.1", "Contract files named and identified", ALL_ROLES, e5_1_contract_files),
    Control("E-5.2", "Tests named after their subject", ALL_ROLES, e5_2_tests),
    Control("E-5.3", "Protocol identifiers", ("employee",), e5_3_identifiers),
    Control("E-5.4", "Plan files named by family", ALL_ROLES, e5_4_plans),
    Control("E-6.1", "uv, hatchling, Python 3.12 floor", ALL_ROLES, e6_1_build),
    Control("E-6.2", "Verification tools declared", ALL_ROLES, e6_2_dev_tools),
    Control("E-6.3", "Quality floors", ALL_ROLES, e6_3_quality_floors),
    Control("E-6.4", "CI runs the verification chain", ALL_ROLES, e6_4_ci),
    Control("E-7.1", "Protocol schemas vendored verbatim", FRAMEWORKS, e7_1_vendored_schemas),
    Control("E-7.2", "Manifest valid and self-verifiable", ("employee",), e7_2_manifest),
    Control("E-7.3", "Referenced contracts published", ("employee",), e7_3_referenced_contracts),
    Control("E-7.4", "Protocol surface documented", ("employee",), e7_4_documented_surface),
    Control("E-7.5", "Reserved error codes respected", ("employee",), e7_5_reserved_codes),
    Control("E-8.1", "Exceptions decided, real and unexpired", ALL_ROLES, e8_1_exceptions),
    Control("E-8.2", "Changelog gate in CI", ALL_ROLES, e8_2_changelog_gate),
    Control("E-8.3", "Deprecation policy stated", ALL_ROLES, e8_3_deprecation_policy),
    Control("E-9.1", "Clause parity between editions", ("standard",), e9_1_clause_parity),
)

__all__ = ["ALL_ROLES", "CONTROLS", "FRAMEWORKS", "Check", "Control"]
