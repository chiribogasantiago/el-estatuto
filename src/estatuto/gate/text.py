"""Text heuristics shared by the controls: prose extraction, language and machine paths."""

from __future__ import annotations

import fnmatch
import re
from collections.abc import Iterable
from pathlib import Path

SPANISH_MARKERS = re.compile(
    r"[¿¡]|\b(el|la|los|las|una|para|con|que|del|según|también|porque|cómo|sólo|además|"
    r"desde|hasta|sobre|entre|cuando|donde|mediante|cada|este|esta|estos|estas|ese|esa)\b",
    re.IGNORECASE,
)
MACHINE_PATH = re.compile(r"(/Users/|/home/|[A-Za-z]:\\)")
CLAUSE_ID = re.compile(r"\bE-(\d+)\.(\d+)\b")


def prose_lines(text: str) -> list[str]:
    """Lines that are prose: no tables, no fenced or indented code, no inline-code-only lines."""
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fenced = not fenced
            continue
        if fenced or stripped.startswith(("|", "`", "    ", "\t", "<!--")):
            continue
        # Drop inline code, links' targets and HTML so identifiers never count as prose.
        cleaned = re.sub(r"`[^`]*`", " ", line)
        cleaned = re.sub(r"\]\([^)]*\)", "]", cleaned)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        lines.append(cleaned)
    return lines


def spanish_hits(text: str, proper_nouns: Iterable[str]) -> list[str]:
    """Spanish function words found in the prose of ``text``, after removing proper nouns."""
    prose = re.sub(r"\s+", " ", " ".join(prose_lines(text)))
    for noun in proper_nouns:
        prose = prose.replace(noun, " ")
    hits: list[str] = []
    for match in SPANISH_MARKERS.finditer(prose):
        word = match.group(0)
        # "El"/"La" starting a capitalised name ("La Paz") is a name, not prose.
        tail = prose[match.end() : match.end() + 2]
        if word.lower() in {"el", "la"} and tail[:1] == " " and tail[1:2].isupper():
            continue
        hits.append(word)
    return hits


def machine_paths(text: str) -> list[str]:
    """Absolute, machine-specific paths found anywhere in ``text``."""
    return [match.group(0) for match in MACHINE_PATH.finditer(text)]


def is_archived(relative: str, patterns: Iterable[str]) -> bool:
    """Whether a repository-relative path falls under one of the archive globs."""
    for pattern in patterns:
        if fnmatch.fnmatch(relative, pattern):
            return True
        if pattern.endswith("/**") and relative.startswith(pattern[:-2]):
            return True
    return False


def live_markdown(root: Path, archive: Iterable[str]) -> list[Path]:
    """Root Markdown files and ``docs/**/*.md`` that are not archived."""
    candidates = sorted(root.glob("*.md")) + sorted((root / "docs").rglob("*.md"))
    patterns = tuple(archive)
    return [
        path
        for path in candidates
        if path.is_file() and not is_archived(path.relative_to(root).as_posix(), patterns)
    ]


def clause_ids(text: str) -> set[str]:
    """Every ``E-n.m`` clause identifier in ``text``."""
    return {f"E-{major}.{minor}" for major, minor in CLAUSE_ID.findall(text)}


__all__ = [
    "CLAUSE_ID",
    "MACHINE_PATH",
    "SPANISH_MARKERS",
    "clause_ids",
    "is_archived",
    "live_markdown",
    "machine_paths",
    "prose_lines",
    "spanish_hits",
]
