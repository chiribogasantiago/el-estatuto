"""The employee factory: a complete, conforming employee framework from a name and a slug.

The template under ``template/`` is a whole repository. Placeholders are replaced, the protocol
schemas are vendored from the standard, the manifest and the domain contracts are rendered by the
generated code itself, the baseline is hashed, and ``uv lock`` runs when ``uv`` is available.
Creating an employee never touches the governor or the standard.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from estatuto.peg.contracts import DOCUMENTS, schema_filename
from estatuto.render import rendered_schema
from estatuto.version import STANDARD_VERSION

TEMPLATE = Path(__file__).resolve().parent / "template"
SLUG = re.compile(r"^[a-z][a-z0-9]{2,40}$")
PACKAGE = re.compile(r"^[a-z][a-z0-9_]{2,40}$")
NAME = re.compile(r"^(El|La) [A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+( [A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*$")
TEXT_NAMES = {".gitignore", ".python-version", "py.typed"}
SKIPPED_DIRECTORIES = {"__pycache__", ".ruff_cache", ".pytest_cache", ".mypy_cache", ".venv"}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".gitignore",
    ".cfg",
    ".in",
    "",
}


class ScaffoldError(ValueError):
    """The destination or the identifiers cannot produce a conforming employee."""


def sync_peg_schemas(repository: Path) -> list[Path]:
    """Vendor every protocol schema under ``<repository>/contracts/peg`` verbatim."""
    target = repository / "contracts" / "peg"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    expected = {schema_filename(document): rendered_schema(document) for document in DOCUMENTS}
    for name, text in expected.items():
        path = target / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    for stray in target.glob("*.json"):
        if stray.name not in expected:
            stray.unlink()
    return written


def _substitutions(name: str, slug: str, package: str) -> dict[str, str]:
    return {
        "__NAME__": name,
        "__SLUG__": slug,
        "__PACKAGE__": package,
        "__EMPLOYEE_ID__": f"emp_{slug}01",
        "__DATE__": datetime.now(UTC).date().isoformat(),
        "__STANDARD_VERSION__": STANDARD_VERSION,
    }


def _render_publication(destination: Path, package: str) -> None:
    """Run the generated repository's own renderer so manifest and contracts are its projection."""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(destination / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", f"{package}.cli", "render"],
        cwd=destination,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ScaffoldError(
            f"the generated renderer failed:\n{completed.stdout}\n{completed.stderr}"
        )


def _freeze_baseline(destination: Path) -> None:
    baseline = destination / "docs" / "governance" / "baseline"
    lines = []
    for path in sorted(baseline.glob("*.md")):
        if path.name == "README.md":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (baseline / "BASELINE.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _lock(destination: Path) -> bool:
    executable = shutil.which("uv")
    if executable is None:
        return False
    completed = subprocess.run(
        [executable, "lock"], cwd=destination, capture_output=True, text=True, check=False
    )
    return completed.returncode == 0


def _format(destination: Path) -> None:
    """Format the generated tree so `ruff format --check` passes for any identifier length."""
    executable = shutil.which("uvx") or shutil.which("uv")
    if executable is None:
        return
    prefix = [executable] if executable.endswith("uvx") else [executable, "tool", "run"]
    for arguments in (
        ["ruff", "check", "--fix", "--quiet", "."],
        ["ruff", "format", "--quiet", "."],
    ):
        subprocess.run([*prefix, *arguments], cwd=destination, capture_output=True, check=False)


def scaffold_employee(
    destination: Path,
    *,
    name: str,
    slug: str,
    package: str | None = None,
    lock: bool = True,
) -> tuple[Path, ...]:
    """Create a conforming employee framework at ``destination`` and return the written files.

    Raises:
        ScaffoldError: when identifiers are malformed or the destination is not empty.
    """
    package = package or slug
    if NAME.fullmatch(name) is None:
        raise ScaffoldError('name must be a persona such as "El Archivero"')
    if SLUG.fullmatch(slug) is None:
        raise ScaffoldError("slug must be a lowercase identifier of 3 to 41 characters")
    if PACKAGE.fullmatch(package) is None:
        raise ScaffoldError("package must be a lowercase Python identifier")
    if destination.exists() and any(destination.iterdir()):
        raise ScaffoldError("destination must not exist or must be empty")
    substitutions = _substitutions(name, slug, package)
    written: list[Path] = []
    for source in sorted(path for path in TEMPLATE.rglob("*") if path.is_file()):
        if SKIPPED_DIRECTORIES & set(source.relative_to(TEMPLATE).parts[:-1]):
            continue
        relative = source.relative_to(TEMPLATE).as_posix()
        for key, value in substitutions.items():
            relative = relative.replace(key, value)
        target = destination / relative.removesuffix(".tmpl")
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix in TEXT_SUFFIXES or source.name in TEXT_NAMES:
            text = source.read_text(encoding="utf-8")
            for key, value in substitutions.items():
                text = text.replace(key, value)
            target.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(source, target)
        written.append(target)
    written.extend(sync_peg_schemas(destination))
    _render_publication(destination, package)
    written.extend(sorted((destination / "contracts").glob("*.json")))
    written.append(destination / "manifest.json")
    _freeze_baseline(destination)
    written.append(destination / "docs" / "governance" / "baseline" / "BASELINE.sha256")
    (destination / "work").mkdir(exist_ok=True)
    (destination / "work" / ".gitkeep").touch()
    if lock:
        _format(destination)
        if _lock(destination):
            written.append(destination / "uv.lock")
    return tuple(written)


__all__ = ["TEMPLATE", "ScaffoldError", "scaffold_employee", "sync_peg_schemas"]
