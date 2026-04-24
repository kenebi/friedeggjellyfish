"""
friedegg.cli — Command-line entry point.

Exposes the `friedegg` command after `pip install friedegg`:

    friedegg dashboard             # launch the dashboard server
    friedegg dashboard --port 9000 # on a different port
    friedegg --version
"""

from __future__ import annotations

import argparse
import logging
import sys
import threading
import time
import webbrowser

from friedegg import __version__

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def _open_browser_delayed(url: str, delay: float = 1.0) -> None:
    """Open the dashboard in the default browser after a short delay
    so uvicorn has time to bind the port."""
    def _open() -> None:
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()


def _cmd_dashboard(args: argparse.Namespace) -> int:
    import uvicorn  # imported lazily so `friedegg --version` stays fast

    url = f"http://{args.host}:{args.port}"
    print(f"FEJ dashboard starting on {url}")
    print("Press Ctrl+C to stop.")

    if not args.no_browser:
        _open_browser_delayed(url)

    uvicorn.run(
        "friedegg.server:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        access_log=False,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="friedegg",
        description="Fried Egg Jellyfish — real-time visual monitoring for code-built automations.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"friedegg {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    dash = sub.add_parser("dashboard", help="Launch the local FEJ dashboard.")
    dash.add_argument("--host", default=DEFAULT_HOST, help="Bind address (default: 127.0.0.1)")
    dash.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (default: 8765)")
    dash.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")
    dash.add_argument(
        "--log-level",
        default="warning",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Server log level (default: warning)",
    )
    dash.set_defaults(func=_cmd_dashboard)

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
