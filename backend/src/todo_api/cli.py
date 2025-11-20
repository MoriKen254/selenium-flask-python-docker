"""Command Line Interface for Todo API.

This module provides CLI commands for running and managing the Todo API application.
"""

import argparse
import sys
from typing import Optional

from .app import create_app


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Todo API - A modern Flask REST API for Todo List management"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"todo-api {get_version()}"
    )

    args = parser.parse_args()

    try:
        app = create_app()
        print(f"Starting Todo API server on {args.host}:{args.port}")
        if args.debug:
            print("Debug mode enabled")
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down Todo API server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def get_version() -> str:
    """Get the current version of the package."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


if __name__ == "__main__":
    main()
