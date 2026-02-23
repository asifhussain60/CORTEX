#!/usr/bin/env python3
"""
scripts/fix_media_tags.py

CLI entry point for the CORTEX Media Tag Cleaner.

Recursively scans a music library root, parses filenames into clean metadata,
and writes corrected tags (Title, Artist, Album, Genre, Year, Track) so Plex
and other media servers display the correct information.

Usage examples
--------------
Dry-run (preview changes, write nothing)::

    python scripts/fix_media_tags.py --root "Z:\\MUSIC\\Bollywood" --dry-run

Live run on default Bollywood library::

    python scripts/fix_media_tags.py --root "Z:\\MUSIC\\Bollywood" \\
        --genre Bollywood --year 2024

Only process MP4 files::

    python scripts/fix_media_tags.py --root "Z:\\MUSIC" \\
        --extensions .mp4 --dry-run

Keep folder name as album (default ``True``)::

    python scripts/fix_media_tags.py --root "Z:\\MUSIC\\Bollywood" \\
        --no-album-from-folder

Show verbose per-file detail::

    python scripts/fix_media_tags.py --root "Z:\\MUSIC\\Bollywood" \\
        --dry-run --verbose

Exit codes
----------
0 — success (all files processed, no errors)
1 — one or more files failed (partial success)
2 — fatal error (root not found, import error, etc.)

AC_START: AC-MEDIA-2026-02-23-005
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Bootstrap logging before importing cortex modules
# ---------------------------------------------------------------------------


def _configure_logging(verbose: bool) -> None:
    """Configure root logger based on verbosity flag."""
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(levelname)-8s %(message)s"
    logging.basicConfig(level=level, format=fmt, stream=sys.stderr)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="fix_media_tags",
        description=(
            "CORTEX Media Tag Cleaner — sync Plex-visible tags from filenames.\n"
            "Reads every media file under ROOT, parses the filename, and writes\n"
            "clean Title / Artist / Album / Genre / Year / Track tags."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path("Z:/MUSIC/Bollywood"),
        metavar="DIR",
        help=(
            "Root directory to scan recursively. "
            "Default: Z:/MUSIC/Bollywood"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing any tags.",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=None,
        metavar="EXT",
        help=(
            "Limit processing to these file extensions "
            "(dot-prefixed, e.g. '.mp4 .mp3'). "
            "Default: all supported media types."
        ),
    )
    parser.add_argument(
        "--genre",
        default=None,
        metavar="GENRE",
        help="Override genre tag on every file (e.g. 'Bollywood').",
    )
    parser.add_argument(
        "--year",
        default=None,
        metavar="YEAR",
        help="Override year/date tag on every file (e.g. '2024').",
    )
    parser.add_argument(
        "--comment",
        default=None,
        metavar="TEXT",
        help="Set the comment tag on every file.",
    )
    parser.add_argument(
        "--no-album-from-folder",
        action="store_true",
        default=False,
        dest="no_album_from_folder",
        help=(
            "Disable the default behaviour of using the parent folder name "
            "as the Album tag."
        ),
    )
    parser.add_argument(
        "--keep-stale-tags",
        action="store_true",
        default=False,
        dest="keep_stale_tags",
        help=(
            "Do NOT remove stale legacy atoms (e.g. tvsh, tvnn) before "
            "writing. By default they are cleared to avoid Plex confusion."
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Show per-file debug output.",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        default=False,
        dest="errors_only",
        help="Only print files that failed.",
    )
    return parser


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _colour(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour code if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"{code}{text}{_RESET}"
    return text


def _print_result(result: "CleanResult", errors_only: bool) -> None:  # noqa: F821
    """Print a formatted line for one file result."""
    from cortex.tools.media.tag_cleaner import CleanResult  # noqa: PLC0415

    dr_label = _colour("[DRY-RUN] ", _CYAN) if result.dry_run else ""

    if not result.success:
        print(
            f"  {dr_label}{_colour('❌', _RED)} "
            f"{result.path.name!r}  — {result.error}"
        )
        return

    if errors_only:
        return

    if result.changes:
        change_parts = []
        for field_name, (old, new) in result.changes.items():
            change_parts.append(
                f"  {_colour(field_name, _CYAN)}: "
                f"{_colour(repr(old), _DIM)} → {_colour(repr(new), _YELLOW)}"
            )
        print(
            f"  {dr_label}{_colour('✅', _GREEN)} "
            f"{_colour(result.path.name, _BOLD)}"
        )
        for part in change_parts:
            print(f"    {part}")
    else:
        print(
            f"  {dr_label}{_colour('⏭', _DIM)}  "
            f"{_colour(result.path.name, _DIM)}  (no changes)"
        )


def _print_summary(results: list, dry_run: bool) -> None:
    """Print a final summary table."""
    total = len(results)
    updated = sum(1 for r in results if r.success and r.changes)
    skipped = sum(1 for r in results if r.success and not r.changes)
    failed = sum(1 for r in results if not r.success)

    dr = "  [DRY-RUN — no files written]" if dry_run else ""
    print()
    print(_colour("─" * 60, _DIM))
    print(
        f"  {_colour('Total', _BOLD)}: {total}   "
        f"{_colour('Updated', _GREEN)}: {updated}   "
        f"{_colour('Skipped', _DIM)}: {skipped}   "
        f"{_colour('Failed', _RED)}: {failed}"
        f"{_colour(dr, _CYAN)}"
    )
    print(_colour("─" * 60, _DIM))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    """
    Entry point for the fix_media_tags CLI.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code: 0 success, 1 partial failure, 2 fatal.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)
    log = logging.getLogger(__name__)

    # Validate root
    if not args.root.exists():
        print(
            f"{_colour('ERROR', _RED)}: Root directory not found: {args.root}",
            file=sys.stderr,
        )
        return 2

    # Build extension set
    extensions = None
    if args.extensions:
        extensions = {
            ext if ext.startswith(".") else f".{ext}"
            for ext in args.extensions
        }

    # Import cleaner (late import so arg validation runs first)
    try:
        from cortex.tools.media.tag_cleaner import MediaTagCleaner  # noqa: PLC0415
    except ImportError as exc:
        print(
            f"{_colour('ERROR', _RED)}: Cannot import MediaTagCleaner: {exc}",
            file=sys.stderr,
        )
        return 2

    cleaner = MediaTagCleaner(
        root=args.root,
        dry_run=args.dry_run,
        use_folder_as_album=not args.no_album_from_folder,
        clear_stale_tags=not args.keep_stale_tags,
        extensions=extensions,
        genre=args.genre,
        year=args.year,
        comment=args.comment,
    )

    mode = _colour("DRY-RUN", _CYAN) if args.dry_run else _colour("LIVE", _GREEN)
    print(
        f"\n{_colour('CORTEX Media Tag Cleaner', _BOLD)}  "
        f"[{mode}]\n"
        f"  root  : {args.root}\n"
        f"  album : {'folder name' if not args.no_album_from_folder else 'keep existing'}\n"
        f"  genre : {args.genre or '(keep existing)'}\n"
        f"  year  : {args.year or '(keep existing)'}\n"
        f"  exts  : {', '.join(sorted(extensions)) if extensions else 'all supported'}\n"
    )

    try:
        results = cleaner.run()
    except Exception as exc:
        log.exception("Fatal error during scan: %s", exc)
        return 2

    if not results:
        print("  No media files found.")
        return 0

    for result in results:
        _print_result(result, errors_only=args.errors_only)

    _print_summary(results, dry_run=args.dry_run)

    # Exit 1 if any file failed
    if any(not r.success for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

# AC_COMPLETE: AC-MEDIA-2026-02-23-005 ✅
