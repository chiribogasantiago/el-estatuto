"""The changelog gate: a normative change records itself under ``## Unreleased``.

The files changed between a base ref and ``HEAD`` are listed with ``git diff``. When any of them
is normative — as ``estatuto.toml`` declares under ``[changelog]`` — ``CHANGELOG.md`` must be
among them. Tooling files may change alone. An unknown base (empty or all zeros, as a first
push reports) is not a failure: there is nothing to compare.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from estatuto.gate.config import FrameworkConfig

CHANGELOG = "CHANGELOG.md"


def is_normative(path: str, config: FrameworkConfig) -> bool:
    """Whether a changed path carries behaviour the changelog must record."""
    return path in config.normative_files or path.startswith(tuple(config.normative_prefixes))


def changed_files(base: str, root: Path) -> list[str]:
    """Paths changed between ``base`` and ``HEAD``, as git reports them."""
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        completed = subprocess.run(
            ["git", "diff", "--name-only", base, "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def verdict(changed: list[str], config: FrameworkConfig) -> tuple[bool, str]:
    """``(passed, message)`` for a list of changed paths."""
    normative = sorted(path for path in changed if is_normative(path, config))
    if not normative:
        return True, "changelog gate: no normative change"
    if CHANGELOG in changed:
        return True, f"changelog gate: {len(normative)} normative change(s) recorded"
    listing = "\n".join(f"  {path}" for path in normative)
    return False, (
        "changelog gate: normative content changed without a CHANGELOG.md entry:\n"
        f"{listing}\nRecord the change under '## Unreleased'."
    )


__all__ = ["CHANGELOG", "changed_files", "is_normative", "verdict"]
