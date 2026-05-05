"""
LLM-curated Bollywood filename cleaner.

Uses a pre-curated title mapping (scripts/_flatten_titles.json) generated
by GitHub Copilot's built-in LLM with Bollywood music domain knowledge.
No external API key required.

Usage:
    python scripts/flatten_llm_preview.py

Optional env vars:
    FLATTEN_PREVIEW_SEED  — integer seed for the random 50 sample (default: 42)
    FLATTEN_MAX_LEN       — max characters per title (default: 25)
"""

import json
import os
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SRC_DIR = Path("Z:/MUSIC/Bollywood")
DEST_DIR = Path("Z:/MUSIC/Flattened files")
MAX_LEN = int(os.environ.get("FLATTEN_MAX_LEN", "25"))
SEED = int(os.environ.get("FLATTEN_PREVIEW_SEED", "42"))
TITLES_JSON = Path(__file__).parent / "_flatten_titles.json"


def load_title_mapping() -> dict[str, list[str]]:
    """
    Load the LLM-curated title list.
    Returns dict: stem -> list of curated titles (list because same stem
    can appear multiple times for true duplicates, preserving order).
    """
    entries = json.loads(TITLES_JSON.read_text(encoding="utf-8"))
    # Build ordered list; for duplicate stems, each occurrence gets its own slot
    mapping: dict[str, list[str]] = {}
    for entry in entries:
        stem = entry["stem"]
        mapping.setdefault(stem, []).append(entry["title"])
    return mapping


def get_title_for_file(
    stem: str,
    mapping: dict[str, list[str]],
    usage_counter: dict[str, int],
) -> str:
    """Return the next curated title for this stem, consuming one slot."""
    titles = mapping.get(stem)
    if titles:
        idx = usage_counter.get(stem, 0)
        if idx < len(titles):
            usage_counter[stem] = idx + 1
            t = titles[idx]
        else:
            # Fallback: reuse last known title
            t = titles[-1]
    else:
        # Stem not in mapping: apply basic title-case as fallback
        t = stem.title()

    # Enforce max length at word boundary
    if len(t) > MAX_LEN:
        truncated = t[: MAX_LEN + 1]
        sp = truncated.rfind(" ")
        t = t[:sp] if sp > 0 else t[:MAX_LEN]
    return t.strip()


def build_flat_name_map(
    files: list[Path], mapping: dict[str, list[str]]
) -> tuple[dict[Path, str], dict[Path, str]]:
    """
    Returns:
        winners : Path → flat title stem  (these files will be moved)
        skipped : Path → reason string    (these files are dropped as smaller dupes)

    Strategy: group all files that share the same curated title, then keep only
    the one with the largest file size. In a tie, keep the first encountered.
    """
    usage_counter: dict[str, int] = {}

    # 1. Resolve a raw curated title for every file (no suffix yet)
    raw_titles: dict[Path, str] = {}
    for f in files:
        raw_titles[f] = get_title_for_file(f.stem, mapping, usage_counter)

    # 2. Group by normalised title → pick largest file per group
    groups: dict[str, list[Path]] = {}
    for f, title in raw_titles.items():
        groups.setdefault(title.lower(), []).append(f)

    winners: dict[Path, str] = {}
    skipped: dict[Path, str] = {}

    for norm_title, group in groups.items():
        title = raw_titles[group[0]]  # display-case title from first member
        if len(group) == 1:
            winners[group[0]] = title
        else:
            # Sort descending by size; ties broken by path (deterministic)
            group.sort(key=lambda p: (-p.stat().st_size, str(p)))
            winner = group[0]
            winners[winner] = title
            for loser in group[1:]:
                size_diff = winner.stat().st_size - loser.stat().st_size
                skipped[loser] = (
                    f"duplicate of '{winner.name}' "
                    f"(smaller by {size_diff:,} bytes)"
                )

    return winners, skipped


def print_preview(
    files: list[Path],
    winners: dict[Path, str],
    skipped: dict[Path, str],
    n: int = 50,
):
    all_files = list(files)
    rng = random.Random(SEED)
    sample = rng.sample(all_files, min(n, len(all_files)))
    sample.sort(key=lambda f: f.stem.lower())

    print(f"\n{'#':<3} {'ORIGINAL FILENAME':<52} | {'TITLE / STATUS':<30} | LEN")
    print("-" * 95)
    for i, f in enumerate(sample, 1):
        orig = f.stem[:51]
        if f in winners:
            title = winners[f]
            size_kb = f.stat().st_size // 1024
            flag = "  *** OVER" if len(title) > MAX_LEN else ""
            print(f"{i:<3} {orig:<52} | {title:<30} | {len(title)}{flag}  ({size_kb:,} KB)")
        else:
            reason = skipped.get(f, "unknown")
            print(f"{i:<3} {orig:<52} | SKIP — {reason[:38]}")

    print(f"\n  Sample: {len(sample)} shown")
    over = sum(1 for t in winners.values() if len(t) > MAX_LEN)
    print(f"  Full corpus: {len(winners)} will be moved | "
          f"{len(skipped)} skipped (smaller dupes) | "
          f"{over} over {MAX_LEN}-char limit")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not TITLES_JSON.exists():
        print(f"ERROR: title mapping not found at {TITLES_JSON}")
        return

    files = sorted(SRC_DIR.rglob("*.mp4"), key=lambda f: f.stem.lower())
    print(f"Found {len(files)} .mp4 files in {SRC_DIR}")
    print(f"Loading LLM-curated title mapping from {TITLES_JSON.name} ...")

    mapping = load_title_mapping()
    winners, skipped = build_flat_name_map(files, mapping)

    print_preview(files, winners, skipped)

    # Save full mapping for the move script
    out = Path("scripts/_flatten_title_cache.json")
    cache = []
    for f in files:
        if f in winners:
            cache.append({
                "action": "move",
                "original": str(f),
                "flat_title": winners[f],
                "size_bytes": f.stat().st_size,
            })
        else:
            cache.append({
                "action": "skip",
                "original": str(f),
                "reason": skipped.get(f, "unknown"),
                "size_bytes": f.stat().st_size,
            })
    out.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Full mapping saved → {out}")


if __name__ == "__main__":
    main()
