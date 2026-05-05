"""Consolidate Bollywood folder sprawl into a compact hierarchy.

Default mode is dry-run. Use --apply to execute moves.

Target layout:
- Artists/<A-F|G-L|M-R|S-Z|Other>/<ArtistFolder>/<Filename>
- Collections/<Compilations|Party-Dance|Romantic|Arabic-Style>/<SourceFolder>/<Filename>
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple

MEDIA_EXTENSIONS = {".mp4", ".m4a", ".mp3", ".flac", ".ogg", ".wav"}

COLLECTION_RULES: Dict[str, Tuple[str, ...]] = {
    "Compilations": ("mashup", "compilation", "nonstop", "megamix", "playlist"),
    "Party-Dance": ("party", "dance", "edm", "afro", "reggaeton"),
    "Romantic": ("romantic", "love", "ishq", "dil"),
    "Arabic-Style": ("arabic", "habibi"),
}


@dataclass
class ConsolidationStats:
    total_files: int = 0
    moves_planned: int = 0
    moves_applied: int = 0
    already_in_place: int = 0
    skipped_collisions: int = 0
    source_missing: int = 0
    errors: List[str] = field(default_factory=list)


def _is_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS


def _bucket_for_artist(artist_folder: str) -> str:
    if not artist_folder:
        return "Other"
    ch = artist_folder[0].upper()
    if "A" <= ch <= "F":
        return "A-F"
    if "G" <= ch <= "L":
        return "G-L"
    if "M" <= ch <= "R":
        return "M-R"
    if "S" <= ch <= "Z":
        return "S-Z"
    return "Other"


def _classify_collection(folder_name: str, file_name: str) -> Optional[str]:
    text = f"{folder_name} {file_name}".lower()
    for collection, keywords in COLLECTION_RULES.items():
        if any(keyword in text for keyword in keywords):
            return collection
    return None


def _build_target(root: Path, source_file: Path) -> Path:
    folder_name = source_file.parent.name
    file_name = source_file.name

    collection = _classify_collection(folder_name, file_name)
    if collection is not None:
        return root / "Collections" / collection / folder_name / file_name

    bucket = _bucket_for_artist(folder_name)
    return root / "Artists" / bucket / folder_name / file_name


def consolidate(root: Path, apply_changes: bool) -> ConsolidationStats:
    stats = ConsolidationStats()

    files = sorted([p for p in root.rglob("*") if _is_media_file(p)])
    stats.total_files = len(files)

    for source in files:
        # Skip files that are already under final hierarchy.
        rel_parts = source.relative_to(root).parts
        if rel_parts and rel_parts[0] in {"Artists", "Collections"}:
            stats.already_in_place += 1
            continue

        target = _build_target(root, source)

        if source == target:
            stats.already_in_place += 1
            continue

        stats.moves_planned += 1

        if not apply_changes:
            continue

        if not source.exists():
            stats.source_missing += 1
            continue

        try:
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists() and target != source:
                stats.skipped_collisions += 1
                continue

            shutil.move(str(source), str(target))
            stats.moves_applied += 1
        except Exception as exc:  # noqa: BLE001
            stats.errors.append(f"{source} -> {target}: {exc}")

    return stats


def remove_empty_dirs(root: Path) -> int:
    removed = 0
    # Deepest paths first.
    for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda x: len(x.parts), reverse=True):
        if d == root:
            continue
        try:
            if not any(d.iterdir()):
                d.rmdir()
                removed += 1
        except OSError:
            continue
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolidate Bollywood folders into compact hierarchy")
    parser.add_argument("--root", type=str, default=r"Z:\MUSIC\Bollywood", help="Library root")
    parser.add_argument("--apply", action="store_true", help="Apply file moves")
    parser.add_argument("--remove-empty", action="store_true", help="Remove empty directories after apply")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"ERROR: Root not found: {root}")
        return 1

    dry_run = not args.apply
    print(f"MODE={'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"ROOT={root}")

    stats = consolidate(root=root, apply_changes=args.apply)

    print(f"TOTAL_FILES={stats.total_files}")
    print(f"MOVES_PLANNED={stats.moves_planned}")
    print(f"MOVES_APPLIED={stats.moves_applied}")
    print(f"ALREADY_IN_PLACE={stats.already_in_place}")
    print(f"SKIPPED_COLLISIONS={stats.skipped_collisions}")
    print(f"SOURCE_MISSING={stats.source_missing}")
    print(f"ERRORS={len(stats.errors)}")

    removed_empty = 0
    if args.apply and args.remove_empty:
        removed_empty = remove_empty_dirs(root)
        print(f"EMPTY_DIRS_REMOVED={removed_empty}")

    if stats.errors:
        print("ERROR_SAMPLES=")
        for err in stats.errors[:20]:
            print(err)

    return 0 if not stats.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
