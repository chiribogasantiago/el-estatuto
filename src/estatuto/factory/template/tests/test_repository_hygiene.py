"""The repository stays free of the clutter that misleads the next agent."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_SURFACE = [
    *ROOT.glob("*.md"),
    *(path for path in (ROOT / "docs").rglob("*.md") if "baseline" not in path.parts),
]
SPANISH = re.compile(r"[¿¡]|\b(los|las|una|para|con|que|del|también|porque)\b", re.I)


def _prose(text: str) -> str:
    lines, fenced = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and not line.strip().startswith(("|", "`", "    ")):
            lines.append(re.sub(r"`[^`]*`", " ", line))
    return "\n".join(lines)


def test_live_documents_are_english() -> None:
    for path in LIVE_SURFACE:
        hits = SPANISH.findall(_prose(path.read_text(encoding="utf-8")))
        assert not hits, f"{path.relative_to(ROOT)} contains Spanish prose: {sorted(set(hits))[:6]}"


def test_no_machine_specific_paths_in_documentation() -> None:
    offenders = [
        path.name
        for path in LIVE_SURFACE
        if re.search(r"(/Users/|/home/|[A-Za-z]:\\)", path.read_text())
    ]
    assert offenders == []


def test_protocol_schemas_are_vendored() -> None:
    names = {path.name for path in (ROOT / "contracts" / "peg").glob("*.json")}
    assert {
        "manifest-v1.0.0.json",
        "assignment-v1.0.0.json",
        "result-v1.0.0.json",
        "refusal-v1.0.0.json",
    } <= names
