"""``__SLUG__``: render the publication, serve the protocol, run conformance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from __PACKAGE__.capabilities import render_publication
from __PACKAGE__.version import EMPLOYEE_VERSION

ROOT = Path(__file__).resolve().parents[2]


def _render(args: argparse.Namespace) -> int:
    changed = render_publication(ROOT, check=args.check)
    print(json.dumps({"would change" if args.check else "rendered": changed}))
    return 1 if (args.check and changed) else 0


def _serve(args: argparse.Namespace) -> int:
    from __PACKAGE__.peg import PegEmployee
    from __PACKAGE__.transports import HttpServer

    server = HttpServer(PegEmployee(), host=args.host, port=args.port)
    print(f"__NAME__ {EMPLOYEE_VERSION} serving PEG/1 at {server.base_url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The command-line surface."""
    parser = argparse.ArgumentParser(prog="__SLUG__", description=__doc__)
    parser.add_argument("--version", action="version", version=f"__SLUG__ {EMPLOYEE_VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    render = commands.add_parser(
        "render", help="render manifest.json and contracts/ from the declarations"
    )
    render.add_argument("--check", action="store_true", help="exit 1 if anything is stale")
    render.set_defaults(handler=_render)
    serve = commands.add_parser("serve", help="serve PEG/1 over HTTP")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.set_defaults(handler=_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    args = build_parser().parse_args(argv)
    result: int = args.handler(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
