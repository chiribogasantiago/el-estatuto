"""El Estatuto obeys its own standard, and its two editions carry the same clauses."""

from __future__ import annotations

from pathlib import Path

from estatuto.gate.runner import render_text, run_gate
from estatuto.gate.text import clause_ids

ROOT = Path(__file__).resolve().parents[1]


def test_the_standard_passes_its_own_gate() -> None:
    result = run_gate(ROOT)
    assert result.passed, render_text(result)
    assert result.role == "standard"


def test_the_spanish_edition_and_the_english_standard_share_every_clause() -> None:
    spanish = clause_ids((ROOT / "ESTATUTO.md").read_text())
    english = clause_ids((ROOT / "docs" / "standard" / "STANDARD.md").read_text())
    assert spanish and spanish == english


def test_every_control_enforces_a_clause_that_exists_in_the_standard() -> None:
    from estatuto.gate.runner import CONTROL_IDS

    english = clause_ids((ROOT / "docs" / "standard" / "STANDARD.md").read_text())
    assert english >= CONTROL_IDS
