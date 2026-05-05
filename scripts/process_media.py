"""
process_media.py — Repeatable flat-file pipeline for any music/video folder.

Subcommands
-----------
  scan     Find files in --src not yet curated in --titles JSON.
           Outputs a numbered list of raw stems for Copilot to title.

  preview  Show the dedup + rename plan (50 random sample).
           Saves full plan to --cache file.

  execute  Execute the moves from --cache (dry-run unless --live).

Typical workflow
----------------
  1. python scripts/process_media.py scan   --src "Z:/MUSIC/YouTube"
  2. Copilot curates titles -> appended to scripts/_titles_youtube.json
  3. python scripts/process_media.py preview --src "Z:/MUSIC/YouTube"
  4. python scripts/process_media.py execute --live

Profile defaults (--profile)
-----------------------------
  bollywood   src=Z:/MUSIC/Bollywood    dest=Z:/MUSIC/Flattened files
              titles=scripts/_titles_bollywood.json
  youtube     src=Z:/MUSIC/YouTube      dest=Z:/MUSIC/Flattened files
              titles=scripts/_titles_youtube.json
  music       src=Z:/MUSIC              dest=Z:/MUSIC/Flattened files
              titles=scripts/_titles_music.json

All defaults can be overridden with explicit flags.
"""

import argparse
import json
import os
import random
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Built-in profiles — override any value with explicit CLI flags
# ---------------------------------------------------------------------------
PROFILES: dict[str, dict] = {
    "bollywood": {
        "src":    "Z:/MUSIC/Bollywood",
        "dest":   "Z:/MUSIC/Flattened files",
        "titles": "scripts/_titles_bollywood.json",
    },
    "youtube": {
        "src":    "Z:/MUSIC/YouTube",
        "dest":   "Z:/MUSIC/Flattened files",
        "titles": "scripts/_titles_youtube.json",
    },
    "music": {
        "src":    "Z:/MUSIC",
        "dest":   "Z:/MUSIC/Flattened files",
        "titles": "scripts/_titles_music.json",
    },
}

DEFAULT_MAX_LEN = 25
DEFAULT_SEED    = 42
DEFAULT_CACHE   = "scripts/_media_plan.json"
VIDEO_EXTS      = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}
AUDIO_EXTS      = {".mp3", ".flac", ".m4a", ".wav", ".ogg", ".aac"}
ALL_EXTS        = VIDEO_EXTS | AUDIO_EXTS


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def resolve_args(args: argparse.Namespace) -> argparse.Namespace:
    """Fill in profile defaults for any unset values."""
    profile = PROFILES.get(getattr(args, "profile", None) or "bollywood", {})
    if getattr(args, "src", None) is None:
        args.src = profile.get("src")
    if getattr(args, "dest", None) is None:
        args.dest = profile.get("dest")
    if getattr(args, "titles", None) is None:
        args.titles = profile.get("titles")
    return args


def load_titles(titles_path: Path) -> dict[str, list[str]]:
    """Load titles JSON: stem -> [title, ...].  Returns empty dict if missing."""
    if not titles_path.exists():
        return {}
    entries = json.loads(titles_path.read_text(encoding="utf-8"))
    mapping: dict[str, list[str]] = {}
    for entry in entries:
        stem = entry["stem"]
        mapping.setdefault(stem, []).append(entry["title"])
    return mapping


def save_titles(titles_path: Path, entries: list[dict]) -> None:
    titles_path.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def enforce_max_len(title: str, max_len: int) -> str:
    if len(title) <= max_len:
        return title
    truncated = title[: max_len + 1]
    sp = truncated.rfind(" ")
    return (title[:sp] if sp > 0 else title[:max_len]).strip()


def get_title(stem: str, mapping: dict[str, list[str]],
              usage: dict[str, int], max_len: int) -> str:
    titles = mapping.get(stem)
    if titles:
        idx = usage.get(stem, 0)
        t = titles[idx] if idx < len(titles) else titles[-1]
        usage[stem] = idx + 1
    else:
        t = stem.title()
    return enforce_max_len(t, max_len)


def collect_files(src: Path) -> list[Path]:
    files = [
        f for f in sorted(src.rglob("*"), key=lambda p: p.stem.lower())
        if f.is_file() and f.suffix.lower() in ALL_EXTS
    ]
    return files


def build_plan(
    files: list[Path],
    mapping: dict[str, list[str]],
    max_len: int,
) -> tuple[dict[Path, str], dict[Path, str]]:
    """
    Returns (winners, skipped).
    winners : Path -> flat title stem (file will be moved)
    skipped : Path -> reason string   (smaller duplicate, dropped)
    """
    usage: dict[str, int] = {}
    raw: dict[Path, str] = {f: get_title(f.stem, mapping, usage, max_len) for f in files}

    groups: dict[str, list[Path]] = {}
    for f, title in raw.items():
        groups.setdefault(title.lower(), []).append(f)

    winners: dict[Path, str] = {}
    skipped: dict[Path, str] = {}

    for norm, group in groups.items():
        title = raw[group[0]]
        if len(group) == 1:
            winners[group[0]] = title
        else:
            group.sort(key=lambda p: (-p.stat().st_size, str(p)))
            winners[group[0]] = title
            for loser in group[1:]:
                diff = group[0].stat().st_size - loser.stat().st_size
                skipped[loser] = (
                    f"duplicate of '{group[0].name}' (smaller by {diff:,} bytes)"
                )

    return winners, skipped


# ---------------------------------------------------------------------------
# SCAN subcommand
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> None:
    src = Path(args.src)
    titles_path = Path(args.titles)

    if not src.exists():
        print(f"ERROR: source folder not found: {src}", file=sys.stderr)
        sys.exit(1)

    files = collect_files(src)
    mapping = load_titles(titles_path)
    curated_stems = set(mapping.keys())

    uncurated = [f for f in files if f.stem not in curated_stems]

    print(f"Source      : {src}")
    print(f"Total files : {len(files)}")
    print(f"Curated     : {len(files) - len(uncurated)}")
    print(f"Uncurated   : {len(uncurated)}\n")

    if not uncurated:
        print("All files are already curated. Run 'preview' next.")
        return

    print("--- Files needing titles ---")
    print("(Paste this list to Copilot and ask it to clean the titles)")
    print()
    for i, f in enumerate(uncurated, 1):
        print(f"  {i:>4}. {f.stem}")

    # Save uncurated stems to a staging file for Copilot to work with
    staging = titles_path.parent / (titles_path.stem + "_staging.json")
    staging.write_text(
        json.dumps(
            [{"stem": f.stem, "title": ""} for f in uncurated],
            indent=2, ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nStaging file saved -> {staging}")
    print("Fill in 'title' for each entry, then merge into the main titles JSON.")


# ---------------------------------------------------------------------------
# PREVIEW subcommand
# ---------------------------------------------------------------------------

def cmd_preview(args: argparse.Namespace) -> None:
    src = Path(args.src)
    dest = Path(args.dest)
    titles_path = Path(args.titles)
    cache_path = Path(args.cache)
    max_len = args.max_len
    seed = args.seed

    if not src.exists():
        print(f"ERROR: source folder not found: {src}", file=sys.stderr)
        sys.exit(1)

    files = collect_files(src)
    mapping = load_titles(titles_path)

    print(f"Source       : {src}")
    print(f"Destination  : {dest}")
    print(f"Titles map   : {titles_path} ({len(mapping)} entries)")
    print(f"Total files  : {len(files)}\n")

    winners, skipped = build_plan(files, mapping, max_len)

    # Print 50-sample
    rng = random.Random(seed)
    sample = rng.sample(files, min(50, len(files)))
    sample.sort(key=lambda f: f.stem.lower())

    print(f"{'#':<4} {'ORIGINAL STEM':<52} | {'TITLE':<28} | LEN")
    print("-" * 95)
    for i, f in enumerate(sample, 1):
        orig = f.stem[:51]
        if f in winners:
            title = winners[f]
            size_kb = f.stat().st_size // 1024
            over = "  ***" if len(title) > max_len else ""
            print(f"{i:<4} {orig:<52} | {title:<28} | {len(title)}{over}  ({size_kb:,} KB)")
        else:
            reason = skipped.get(f, "unknown")[:55]
            print(f"{i:<4} {orig:<52} | SKIP -- {reason}")

    over_total = sum(1 for t in winners.values() if len(t) > max_len)
    print(f"\n  Files to move : {len(winners)}")
    print(f"  Dupes dropped : {len(skipped)}")
    print(f"  Over {max_len}-char limit : {over_total}")

    # Save plan cache
    plan = []
    for f in files:
        if f in winners:
            plan.append({
                "action": "move",
                "original": str(f),
                "flat_title": winners[f],
                "ext": f.suffix.lower(),
                "size_bytes": f.stat().st_size,
            })
        else:
            plan.append({
                "action": "skip",
                "original": str(f),
                "reason": skipped.get(f, "unknown"),
                "size_bytes": f.stat().st_size,
            })
    cache_path.write_text(
        json.dumps({"dest": str(dest), "plan": plan}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  Plan saved -> {cache_path}")
    print("  Run 'execute' (add --live) when ready.")


# ---------------------------------------------------------------------------
# EXECUTE subcommand
# ---------------------------------------------------------------------------

def cmd_execute(args: argparse.Namespace) -> None:
    cache_path = Path(args.cache)
    live = args.live

    if not cache_path.exists():
        print(
            f"ERROR: plan cache not found: {cache_path}\n"
            "Run 'preview' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    dest = Path(payload["dest"])
    plan = payload["plan"]

    moves = [e for e in plan if e["action"] == "move"]
    skips = [e for e in plan if e["action"] == "skip"]

    mode = "LIVE" if live else "DRY RUN"
    print(f"\n=== process_media execute [{mode}] ===")
    print(f"  Destination : {dest}")
    print(f"  Move : {len(moves)}  |  Skip (dupes) : {len(skips)}\n")

    if live:
        dest.mkdir(parents=True, exist_ok=True)

    moved = already = errors = 0
    for entry in moves:
        src_file = Path(entry["original"])
        flat = entry["flat_title"] + entry["ext"]
        dest_file = dest / flat
        size_kb = entry["size_bytes"] // 1024

        if not src_file.exists():
            print(f"  MISSING  {src_file.name}")
            errors += 1
            continue
        if dest_file.exists():
            print(f"  EXISTS   {flat}  <- already in dest, skipping")
            already += 1
            continue

        print(f"  MOVE  {src_file.name[:55]:<56} -> {flat}  ({size_kb:,} KB)")
        if live:
            try:
                shutil.move(str(src_file), str(dest_file))
                moved += 1
            except Exception as exc:
                print(f"         ERROR: {exc}")
                errors += 1
        else:
            moved += 1

    print(f"\n--- Skipped duplicates ({len(skips)}) ---")
    for entry in skips:
        size_kb = entry["size_bytes"] // 1024
        reason = entry.get("reason", "")[:70]
        print(f"  SKIP  {Path(entry['original']).name[:55]:<56}  ({size_kb:,} KB)  {reason}")

    print(f"\n{'=' * 60}")
    action = "Moved" if live else "Would move"
    print(f"  {action:<10} : {moved}")
    print(f"  Dupes skipped : {len(skips)}")
    if already:
        print(f"  Already exist : {already}")
    if errors:
        print(f"  Errors        : {errors}")
    if not live:
        print("\n  Re-run with --live to apply.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="process_media",
        description="Flat-file pipeline: scan → curate → preview → execute",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--profile", "-p",
        choices=list(PROFILES.keys()),
        default="bollywood",
        help="Named profile (sets default src/dest/titles). Default: bollywood",
    )

    subs = parser.add_subparsers(dest="cmd", required=True)

    # ---- scan ----
    p_scan = subs.add_parser("scan", help="Find uncurated files in --src")
    p_scan.add_argument("--src",    default=None, help="Source folder")
    p_scan.add_argument("--titles", default=None, help="Titles JSON path")

    # ---- preview ----
    p_prev = subs.add_parser("preview", help="Show rename/dedup plan")
    p_prev.add_argument("--src",     default=None)
    p_prev.add_argument("--dest",    default=None)
    p_prev.add_argument("--titles",  default=None)
    p_prev.add_argument("--cache",   default=DEFAULT_CACHE)
    p_prev.add_argument("--max-len", type=int, default=DEFAULT_MAX_LEN, dest="max_len")
    p_prev.add_argument("--seed",    type=int, default=DEFAULT_SEED)

    # ---- execute ----
    p_exec = subs.add_parser("execute", help="Move files per saved plan")
    p_exec.add_argument("--cache", default=DEFAULT_CACHE)
    p_exec.add_argument("--live",  action="store_true",
                        help="Actually move files (default is dry run)")

    args = parser.parse_args()
    args = resolve_args(args)

    if args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "preview":
        cmd_preview(args)
    elif args.cmd == "execute":
        cmd_execute(args)


if __name__ == "__main__":
    main()
