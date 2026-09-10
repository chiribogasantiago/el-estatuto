"""``estatuto.toml``: what a repository declares about itself to the standard gate."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

Role = Literal["governor", "employee", "standard"]
ROLES: tuple[str, ...] = ("governor", "employee", "standard")
NAME_PATTERN = re.compile(r"^(El|La) [A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+( [A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*$")
SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]{2,40}$")
PACKAGE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,40}$")
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

DEFAULT_ARCHIVE: tuple[str, ...] = (
    "docs/plans/**",
    "docs/evidence/**",
    "docs/history/**",
    "docs/governance/baseline/**",
    "docs/protocol/**",
)
DEFAULT_PROPER_NOUNS: tuple[str, ...] = (
    "La Generala",
    "El Corresponsal",
    "La Bibliotecaria",
    "El Estatuto",
    "El Secretario",
    "El Directorio",
    "Núcleo Rector",
)
DEFAULT_NORMATIVE_PREFIXES: tuple[str, ...] = (
    "src/",
    "contracts/",
    "gates/",
    "scripts/",
    "schemas/",
)
DEFAULT_NORMATIVE_FILES: tuple[str, ...] = (
    "manifest.json",
    "pyproject.toml",
    "conformance.py",
    "estatuto.toml",
)


class ConfigError(ValueError):
    """``estatuto.toml`` is missing or does not declare what the gate needs."""


@dataclass(frozen=True, slots=True)
class Exception_:
    """A recorded, dated deviation from one control, backed by a decision record."""

    control: str
    decision: str
    sunset: date
    reason: str


@dataclass(frozen=True, slots=True)
class FrameworkConfig:
    """The declaration the gate reads. Everything else it observes from the tree."""

    name: str
    slug: str
    role: Role
    package: str
    standard: str
    archive: tuple[str, ...] = DEFAULT_ARCHIVE
    proper_nouns: tuple[str, ...] = DEFAULT_PROPER_NOUNS
    normative_prefixes: tuple[str, ...] = DEFAULT_NORMATIVE_PREFIXES
    normative_files: tuple[str, ...] = DEFAULT_NORMATIVE_FILES
    exceptions: tuple[Exception_, ...] = field(default_factory=tuple)

    @property
    def distribution_name(self) -> str:
        """The ``project.name`` the standard expects in ``pyproject.toml``."""
        return "estatuto" if self.role == "standard" else f"{self.slug}-framework"

    @property
    def employee_id(self) -> str:
        """The employee identifier an employee framework must publish."""
        return f"emp_{self.slug}01"

    def waiver_for(self, control_id: str) -> Exception_ | None:
        """The recorded exception covering ``control_id``, if any."""
        return next((item for item in self.exceptions if item.control == control_id), None)


def _string(table: dict[str, Any], key: str, pattern: re.Pattern[str] | None = None) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"[framework].{key} must be a non-empty string")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ConfigError(f"[framework].{key} = {value!r} does not match {pattern.pattern}")
    return value


def _strings(table: dict[str, Any], key: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = table.get(key)
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{key} must be a list of strings")
    return tuple(value)


def load_config(root: Path) -> FrameworkConfig:
    """Read and validate ``<root>/estatuto.toml``."""
    path = root / "estatuto.toml"
    if not path.is_file():
        raise ConfigError("estatuto.toml is missing at the repository root")
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    framework = document.get("framework")
    if not isinstance(framework, dict):
        raise ConfigError("estatuto.toml needs a [framework] table")
    role = _string(framework, "role")
    if role not in ROLES:
        raise ConfigError(f"[framework].role must be one of {ROLES}")
    language = document.get("language", {})
    changelog = document.get("changelog", {})
    exceptions: list[Exception_] = []
    for index, item in enumerate(document.get("exception", [])):
        if not isinstance(item, dict):
            raise ConfigError(f"[[exception]] #{index} must be a table")
        sunset = item.get("sunset")
        if not isinstance(sunset, date):
            raise ConfigError(f"[[exception]] #{index}.sunset must be a date (YYYY-MM-DD)")
        exceptions.append(
            Exception_(
                control=_string(item, "control"),
                decision=_string(item, "decision"),
                sunset=sunset,
                reason=_string(item, "reason"),
            )
        )
    return FrameworkConfig(
        name=_string(framework, "name", NAME_PATTERN),
        slug=_string(framework, "slug", SLUG_PATTERN),
        role=role,  # type: ignore[arg-type]
        package=_string(framework, "package", PACKAGE_PATTERN),
        standard=_string(framework, "standard", SEMVER_PATTERN),
        archive=_strings(language, "archive", DEFAULT_ARCHIVE),
        proper_nouns=_strings(language, "proper_nouns", DEFAULT_PROPER_NOUNS),
        normative_prefixes=_strings(changelog, "normative_prefixes", DEFAULT_NORMATIVE_PREFIXES),
        normative_files=_strings(changelog, "normative_files", DEFAULT_NORMATIVE_FILES),
        exceptions=tuple(exceptions),
    )


__all__ = [
    "DEFAULT_ARCHIVE",
    "DEFAULT_NORMATIVE_FILES",
    "DEFAULT_NORMATIVE_PREFIXES",
    "DEFAULT_PROPER_NOUNS",
    "ROLES",
    "ConfigError",
    "Exception_",
    "FrameworkConfig",
    "Role",
    "load_config",
]
