#!/usr/bin/env python3
"""YAML Registry Broken Reference Sweeper.

Scans all YAML files in cortex-registry/ for references to non-existent
Python files and either:
  --dry-run  (default): Reports all broken refs with proposed fixes
  --fix:     Comments out broken path lines with '[STALE-REF]' marker

Safe for completed/deferred phase YAMLs — these are historical records
and broken refs point to code that existed at the time of that phase.

CORE-002 compliant: all output inline, no report files created.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from typing import Dict, List, Tuple


def find_broken_refs(registry_root: str = "cortex-registry") -> Dict[str, List[Tuple[int, str, str]]]:
    """Find all broken .py path references in YAML files.

    Args:
        registry_root: Root directory of the YAML registry.

    Returns:
        Dict mapping YAML file path to list of (line_num, line_content, broken_path).
    """
    results: Dict[str, List[Tuple[int, str, str]]] = {}
    pattern = re.compile(r"(cortex/[^\s'\"\n,\]\}]+\.py)")

    for yf in sorted(glob.glob(f"{registry_root}/**/*.yaml", recursive=True)):
        try:
            with open(yf) as f:
                lines = f.readlines()
        except Exception:
            continue

        broken: List[Tuple[int, str, str]] = []
        for i, line in enumerate(lines, 1):
            # Skip already-marked stale refs and comment-only lines
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            for match in pattern.finditer(line):
                path = match.group(1)
                if not os.path.exists(path):
                    broken.append((i, line.rstrip(), path))
        if broken:
            results[yf] = broken

    return results


def classify_yaml(filepath: str) -> str:
    """Classify a YAML file by its phase status.

    Args:
        filepath: Path to the YAML file.

    Returns:
        Status string: COMPLETED, DEFERRED, PLANNED, or ACTIVE.
    """
    if "/completed/" in filepath:
        return "COMPLETED"
    if "/deferred/" in filepath:
        return "DEFERRED"
    if "/planned/" in filepath:
        return "PLANNED"
    return "ACTIVE"


def fix_broken_refs(broken_refs: Dict[str, List[Tuple[int, str, str]]]) -> int:
    """Comment out lines with broken refs using [STALE-REF] marker.

    Args:
        broken_refs: Output from find_broken_refs.

    Returns:
        Total number of lines fixed.
    """
    total_fixed = 0
    for yf, entries in broken_refs.items():
        broken_lines = {line_num for line_num, _, _ in entries}
        with open(yf) as f:
            lines = f.readlines()
        with open(yf, "w") as f:
            for i, line in enumerate(lines, 1):
                if i in broken_lines:
                    # Comment out with marker
                    indent = len(line) - len(line.lstrip())
                    f.write(f"{' ' * indent}# [STALE-REF] {line.lstrip()}")
                    total_fixed += 1
                else:
                    f.write(line)
    return total_fixed


def main() -> int:
    """Run the YAML broken reference sweeper.

    Returns:
        0 if clean or fixes applied, 1 if broken refs found in dry-run.
    """
    parser = argparse.ArgumentParser(description="YAML Registry Broken Reference Sweeper")
    parser.add_argument("--fix", action="store_true", help="Comment out broken ref lines")
    parser.add_argument("--active-only", action="store_true", help="Only check ACTIVE YAML files")
    args = parser.parse_args()

    broken = find_broken_refs()

    if args.active_only:
        broken = {k: v for k, v in broken.items() if classify_yaml(k) == "ACTIVE"}

    if not broken:
        print("✅ No broken YAML registry references found.")
        return 0

    total_refs = sum(len(v) for v in broken.values())

    # Group by status
    by_status: Dict[str, int] = {}
    for yf in broken:
        status = classify_yaml(yf)
        by_status[status] = by_status.get(status, 0) + len(broken[yf])

    print(f"{'=' * 60}")
    print(f"YAML Registry Broken Reference Report")
    print(f"{'=' * 60}")
    print(f"Total broken refs: {total_refs} across {len(broken)} files\n")
    print("By status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status:10s}: {count:4d} refs")
    print()

    if args.fix:
        fixed = fix_broken_refs(broken)
        print(f"✅ Fixed {fixed} lines (commented out with [STALE-REF] marker)")
        return 0

    # Dry run — show top offenders
    print("Top 15 files by broken ref count:")
    for yf, entries in sorted(broken.items(), key=lambda x: -len(x[1]))[:15]:
        status = classify_yaml(yf)
        print(f"  {len(entries):4d} [{status:9s}] {yf}")

    print(f"\nRun with --fix to comment out all {total_refs} broken references.")
    print("Run with --active-only to limit to ACTIVE files only.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
