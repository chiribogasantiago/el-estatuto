"""``estatuto``: render the protocol schemas, measure a repository, create an employee."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from estatuto.changelog import changed_files, verdict
from estatuto.gate.config import ConfigError, load_config
from estatuto.gate.runner import render_text, run_gate, write_result
from estatuto.render import render_all
from estatuto.version import STANDARD_VERSION

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = PACKAGE_ROOT / "schemas" / "peg"


def _render(args: argparse.Namespace) -> int:
    changed = render_all(SCHEMAS, check=args.check)
    print(json.dumps({"would change" if args.check else "rendered": changed}))
    return 1 if (args.check and changed) else 0


def _gate(args: argparse.Namespace) -> int:
    try:
        result = run_gate(Path(args.repository))
    except ConfigError as error:
        print(f"estatuto gate: {error}", file=sys.stderr)
        return 2
    print(render_text(result))
    if args.output:
        write_result(result, Path(args.output))
    return 0 if result.passed else 1


def _changelog_gate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not args.base or set(args.base) == {"0"}:
        print("changelog gate: no base to compare against; skipped")
        return 0
    try:
        config = load_config(root)
    except ConfigError as error:
        print(f"changelog gate: {error}", file=sys.stderr)
        return 2
    passed, message = verdict(changed_files(args.base, root), config)
    print(message)
    return 0 if passed else 1


def _sync_peg(args: argparse.Namespace) -> int:
    from estatuto.factory.scaffold import sync_peg_schemas

    written = sync_peg_schemas(Path(args.repository))
    print(json.dumps({"vendored": [path.name for path in written]}))
    return 0


def _new_employee(args: argparse.Namespace) -> int:
    from estatuto.factory.scaffold import ScaffoldError, scaffold_employee

    try:
        written = scaffold_employee(
            Path(args.destination),
            name=args.name,
            slug=args.slug,
            package=args.package or args.slug,
            lock=not args.no_lock,
        )
    except ScaffoldError as error:
        print(f"estatuto new-employee: {error}", file=sys.stderr)
        return 2
    print(f"created {args.name} at {args.destination} ({len(written)} files)")
    print("next: cd there, `uv sync`, `uv run pytest`, `estatuto gate .`, then write the charter.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The command-line surface."""
    parser = argparse.ArgumentParser(prog="estatuto", description=__doc__)
    parser.add_argument("--version", action="version", version=f"estatuto {STANDARD_VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)

    render = commands.add_parser("render", help="render schemas/peg from the protocol models")
    render.add_argument("--check", action="store_true", help="exit 1 if any schema is stale")
    render.set_defaults(handler=_render)

    gate = commands.add_parser("gate", help="measure a repository against the standard")
    gate.add_argument("repository", nargs="?", default=".")
    gate.add_argument("--output", help="write the result document to this path")
    gate.set_defaults(handler=_gate)

    changelog = commands.add_parser("changelog-gate", help="a normative change must record itself")
    changelog.add_argument("--base", required=True, help="git ref to compare HEAD against")
    changelog.add_argument("--root", default=".")
    changelog.set_defaults(handler=_changelog_gate)

    sync = commands.add_parser("sync-peg", help="vendor the protocol schemas under contracts/peg")
    sync.add_argument("repository", nargs="?", default=".")
    sync.set_defaults(handler=_sync_peg)

    new = commands.add_parser("new-employee", help="create a conforming employee framework")
    new.add_argument("destination")
    new.add_argument("--name", required=True, help='the persona, e.g. "El Archivero"')
    new.add_argument("--slug", required=True, help="lowercase identifier, e.g. archivero")
    new.add_argument("--package", help="Python package name; defaults to the slug")
    new.add_argument("--no-lock", action="store_true", help="do not run `uv lock` afterwards")
    new.set_defaults(handler=_new_employee)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    args = build_parser().parse_args(argv)
    handler = args.handler
    result: int = handler(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
