"""Run the framework-standard gate against a repository and produce its result document."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from estatuto.gate.config import ConfigError, FrameworkConfig, load_config
from estatuto.gate.controls import CONTROLS, Control
from estatuto.version import STANDARD_VERSION

RESULT_SCHEMA = "estatuto.framework-standard-gate-result/1.0.0"
CONTROL_IDS: frozenset[str] = frozenset(control.control_id for control in CONTROLS)
Status = Literal["passed", "failed", "waived", "skipped"]


@dataclass(frozen=True, slots=True)
class ControlResult:
    """The outcome of one control."""

    control_id: str
    title: str
    status: Status
    findings: list[str] = field(default_factory=list)
    waiver: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class GateResult:
    """The whole gate: every control, the score and the verdict."""

    framework: str
    slug: str
    role: str
    standard_version: str
    executed_at: str
    controls: list[ControlResult]

    @property
    def applicable(self) -> list[ControlResult]:
        """Controls that applied to this role (not skipped)."""
        return [item for item in self.controls if item.status != "skipped"]

    @property
    def score(self) -> int:
        """Controls that passed or were validly waived."""
        return sum(1 for item in self.applicable if item.status in {"passed", "waived"})

    @property
    def maximum_score(self) -> int:
        """Controls that applied."""
        return len(self.applicable)

    @property
    def passed(self) -> bool:
        """Promotion requires every applicable control; there is no averaging."""
        return self.score == self.maximum_score

    def document(self) -> dict[str, Any]:
        """The result as the published JSON document."""
        return {
            "schema": RESULT_SCHEMA,
            "framework": self.framework,
            "slug": self.slug,
            "role": self.role,
            "standard_version": self.standard_version,
            "executed_at": self.executed_at,
            "gate_passed": self.passed,
            "score": self.score,
            "maximum_score": self.maximum_score,
            "controls": [asdict(item) for item in self.controls],
        }


def run_control(control: Control, root: Path, config: FrameworkConfig) -> ControlResult:
    """Evaluate one control, applying a recorded exception when the control fails."""
    if config.role not in control.roles:
        return ControlResult(control.control_id, control.title, "skipped")
    findings = control.check(root, config)
    if not findings:
        return ControlResult(control.control_id, control.title, "passed")
    waiver = config.waiver_for(control.control_id)
    if (
        waiver is not None
        and (root / waiver.decision).is_file()
        and waiver.sunset > datetime.now(UTC).date()
    ):
        return ControlResult(
            control.control_id,
            control.title,
            "waived",
            findings,
            {
                "decision": waiver.decision,
                "sunset": waiver.sunset.isoformat(),
                "reason": waiver.reason,
            },
        )
    return ControlResult(control.control_id, control.title, "failed", findings)


def run_gate(root: Path) -> GateResult:
    """Run every control against ``root``.

    Raises:
        ConfigError: when ``estatuto.toml`` is missing or invalid; a repository without a
            declaration cannot be measured, and the gate says so instead of guessing.
    """
    root = root.resolve()
    config = load_config(root)
    return GateResult(
        framework=config.name,
        slug=config.slug,
        role=config.role,
        standard_version=STANDARD_VERSION,
        executed_at=datetime.now(UTC).isoformat(),
        controls=[run_control(control, root, config) for control in CONTROLS],
    )


def render_text(result: GateResult) -> str:
    """A terminal summary: one line per applicable control, findings indented."""
    lines = [
        f"estatuto gate · {result.framework} ({result.role}) · standard {result.standard_version}",
        f"{'PASS' if result.passed else 'FAIL'} {result.score}/{result.maximum_score}",
    ]
    for item in result.applicable:
        marker = {"passed": "✓", "failed": "✗", "waived": "~"}[item.status]
        lines.append(f"  {marker} {item.control_id} {item.title}")
        for finding in item.findings:
            lines.append(f"      - {finding}")
        if item.waiver:
            lines.append(f"      waived until {item.waiver['sunset']} by {item.waiver['decision']}")
    return "\n".join(lines)


def write_result(result: GateResult, output: Path) -> None:
    """Persist the result document as pretty JSON."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result.document(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


__all__ = [
    "CONTROL_IDS",
    "RESULT_SCHEMA",
    "ConfigError",
    "ControlResult",
    "GateResult",
    "render_text",
    "run_control",
    "run_gate",
    "write_result",
]
