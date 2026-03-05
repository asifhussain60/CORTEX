#!/usr/bin/env python3
"""
CORTEX Environment Setup — Fast, Cross-Platform Initializer

Sets up `.cortex-runtime/` with all 7 SQLite databases and required directories.
Runs in < 3 seconds on any modern machine. Pure Python stdlib — no pip install required.

Usage:
    python scripts/setup_env.py                  # First-time setup (idempotent)
    python scripts/setup_env.py --clean          # Delete and recreate all databases
    python scripts/setup_env.py --verify         # Check without modifying
    python scripts/setup_env.py --quiet          # Suppress progress output

Authority: CORTEX audit-fix pipeline Stage -2
Phase: 109 (Environment Readiness Fast-Init)
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Ensure cortex package is importable when run from repo root
_repo_root = Path(__file__).parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from cortex.infrastructure.env_initializer import (
    DB_REGISTRY,
    RUNTIME_DIRS,
    initialize_runtime_environment,
    verify_runtime_environment,
)


def _configure_logging(quiet: bool, verbose: bool) -> None:
    level = logging.WARNING if quiet else (logging.DEBUG if verbose else logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        level=level,
        stream=sys.stdout,
    )


def _banner(quiet: bool) -> None:
    if not quiet:
        print()
        print("🧠 CORTEX Environment Setup")
        print("═" * 60)


def _print_result(result, quiet: bool) -> None:
    if quiet:
        return

    print()
    for db in result.databases:
        icon = "✅" if db.ok else "❌"
        status_parts = []
        if not db.existed:
            status_parts.append("NEW")
        if db.was_rebuilt:
            label = "REBUILT (was corrupt)" if db.was_corrupt else "REBUILT (clean mode)"
            status_parts.append(label)
        if db.tables_created:
            status_parts.append(f"{db.tables_created} tables created")
        if db.columns_added:
            status_parts.append(f"{db.columns_added} columns added")
        if not status_parts:
            status_parts.append("up-to-date")
        if db.error:
            status_parts.append(f"ERROR: {db.error}")

        print(f"  {icon}  {db.name:<25} {', '.join(status_parts)}")

    print()
    print("─" * 60)
    if result.ok:
        print(f"✅  {result.summary()}")
    else:
        failed = ", ".join(db.name for db in result.failed_dbs)
        print(f"❌  Setup failed for: {failed}")
        print(f"    Run with --verbose for details or --clean to rebuild.")
    print()


def _print_verify_result(ok: bool, issues: list, quiet: bool) -> None:
    if quiet:
        return
    print()
    if ok:
        print("✅  Environment is healthy — all databases and directories present.")
    else:
        print(f"❌  {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"    • {issue}")
        print()
        print("    Run:  python scripts/setup_env.py         to fix (idempotent)")
        print("    Run:  python scripts/setup_env.py --clean to force rebuild")
    print()


def _print_inventory(quiet: bool) -> None:
    if quiet:
        return
    print()
    print("  Databases to initialize:")
    for name, spec in DB_REGISTRY.items():
        print(f"    • {name:<25} → .cortex-runtime/{spec['path']}")
    print()
    print("  Directories to create:")
    for d in RUNTIME_DIRS:
        print(f"    • .cortex-runtime/{d}/")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CORTEX Environment Setup — Initialize all databases and directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup_env.py              First-time setup (idempotent — safe to re-run)
  python scripts/setup_env.py --clean      Rebuild all databases from scratch
  python scripts/setup_env.py --verify     Check environment without modifications
  python scripts/setup_env.py --quiet      Silent mode for CI/CD pipelines
  python scripts/setup_env.py --verbose    Debug output for troubleshooting

Exit codes:
  0  Success
  1  One or more databases failed to initialize
  2  Verify found issues (--verify mode only)
        """,
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete and recreate all databases (removes existing data!)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify environment without modifying anything",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output (exit code only)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose debug output",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=None,
        help="Custom .cortex-runtime/ path (default: .cortex-runtime/ in cwd)",
    )
    args = parser.parse_args()

    _configure_logging(args.quiet, args.verbose)
    _banner(args.quiet)

    if args.verify:
        if not args.quiet:
            print("  Mode: VERIFY (no changes)")
            print()
        ok, issues = verify_runtime_environment(runtime_root=args.runtime_root)
        _print_verify_result(ok, issues, args.quiet)
        return 0 if ok else 2

    # Setup mode
    mode_label = "CLEAN (delete & rebuild)" if args.clean else "SETUP (idempotent)"
    if not args.quiet:
        print(f"  Mode: {mode_label}")
        print(f"  Root: .cortex-runtime/")
        _print_inventory(args.quiet)

    if args.clean and not args.quiet:
        print("  ⚠️  --clean: all existing database data will be erased")
        print()

    t0 = time.monotonic()
    result = initialize_runtime_environment(
        runtime_root=args.runtime_root,
        clean=args.clean,
        verbose=args.verbose,
    )
    elapsed = (time.monotonic() - t0) * 1000

    _print_result(result, args.quiet)

    if not args.quiet:
        print(f"  Total time: {elapsed:.0f}ms")
        print()
        if result.ok:
            print("  → Run 'python scripts/setup-mcp.py' to configure MCP server")
            print("  → Run 'make test-preflight' to verify the full stack")
        print()

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
