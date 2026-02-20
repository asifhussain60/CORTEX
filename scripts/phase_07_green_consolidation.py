#!/usr/bin/env python3
"""
Phase 07 GREEN - Test Directory Consolidation Script

Maps 42 test directories to 16 canonical directories mirroring cortex/ structure.
Consolidates high-value tests, archives low-value ones.
"""

import os
import shutil
import subprocess
from pathlib import Path
from collections import defaultdict

# Define canonical test structure mapping
CONSOLIDATION_MAPPING = {
    # Target: [source directories to consolidate]
    "api": ["api"],
    "cli": ["cli"],
    "config": ["config"],
    "core": ["core", "wiring"],
    "dashboards": ["dashboards"],
    "governance": ["enforcement", "governance"],
    "infrastructure": [
        "automation",
        "capacity",
        "ci_cd",
        "collaboration",
        "deployment",
        "devx",
        "infrastructure",
        "repositories",
        "security",
        "storage",
        "versioning",
    ],
    "intelligence": [
        "documentation",
        "intelligence",
        "knowledge",
        "learning",
        "brain",
    ],
    "lens": ["lens"],
    "mcp": ["mcp"],
    "models": ["models"],
    "observability": ["observability", "registry"],  # registry → observability for now
    "orchestrators": ["orchestrators"],
    "templates": ["templates"],
    "testing": ["testing", "tier2", "e2e"],
    "tools": ["contracts", "toolkit", "tools", "standalone"],
    # Test categories to preserve separately
    "unit": ["unit"],  # Already well-structured
    "golden": ["golden"],  # Golden tests baseline
    "chaos": ["chaos"],  # Chaos engineering tests
    "performance": ["performance"],  # Performance benchmarks
    "integration": ["integration"],  # Integration tests
    "regression": ["regression"],  # Regression tests
    "manual": ["manual"],  # Manual/exploratory tests
    "cortex_brain": ["cortex_brain"],  # Merged cortex tests
    # Deprecated/low-priority to archive
    "_archive": ["fixtures", "visualization"],
}

# Remaining unmapped directories
UNMAPPED = []

TESTS_DIR = Path("/Users/asifhussain/PROJECTS/CORTEX/tests")


def get_test_value(test_dir: Path) -> float:
    """
    Score a test directory by:
    - File count (more files = higher value)
    - Test file count (more test_*.py = higher value)
    - Recent activity (last modified)

    Returns score 0.0-1.0
    """
    if not test_dir.exists():
        return 0.0

    test_files = list(test_dir.glob("**/test_*.py"))
    total_files = list(test_dir.glob("**/*"))

    if not total_files:
        return 0.0

    # Scoring: test files count (0.6 weight) + total files (0.4 weight)
    file_score = min(len(test_files) / 50, 1.0) * 0.6
    total_score = min(len(total_files) / 200, 1.0) * 0.4

    return file_score + total_score


def consolidate_directories():
    """Execute test directory consolidation."""
    print("=" * 70)
    print("PHASE 07 GREEN - TEST DIRECTORY CONSOLIDATION")
    print("=" * 70)
    print()

    # Step 1: Verify current state
    print("STEP 5: ASSESSING TEST DIRECTORY VALUES")
    print("-" * 70)
    current_dirs = sorted([d.name for d in TESTS_DIR.iterdir() if d.is_dir()])
    print(f"Current test directories: {len(current_dirs)}")
    print()

    # Score each directory
    dir_scores = {}
    for dir_name in current_dirs:
        if dir_name == ".pytest_cache":
            continue
        test_dir = TESTS_DIR / dir_name
        score = get_test_value(test_dir)
        dir_scores[dir_name] = score

    # Show high-value vs low-value
    print("Test Directory Value Assessment (threshold: 0.3):")
    print()
    high_value = {k: v for k, v in sorted(dir_scores.items(), key=lambda x: x[1], reverse=True) if v >= 0.3}
    low_value = {k: v for k, v in sorted(dir_scores.items(), key=lambda x: x[1], reverse=True) if v < 0.3}

    print("HIGH-VALUE TESTS (score ≥ 0.3):")
    for dir_name, score in high_value.items():
        files = len(list((TESTS_DIR / dir_name).glob("**/test_*.py")))
        print(f"  ✅ {dir_name:30} score: {score:.2f}  ({files} test files)")

    print()
    print("LOW-VALUE TESTS (score < 0.3):")
    for dir_name, score in low_value.items():
        files = len(list((TESTS_DIR / dir_name).glob("**/test_*.py")))
        print(f"  ⚠️  {dir_name:30} score: {score:.2f}  ({files} test files)")

    print()
    print("=" * 70)
    print("STEP 7: CONSOLIDATING INTO CANONICAL STRUCTURE")
    print("=" * 70)
    print()

    # Step 2: Create target structure
    for target in CONSOLIDATION_MAPPING.keys():
        if target != "_archive":
            target_path = TESTS_DIR / target
            target_path.mkdir(exist_ok=True)

    # Step 3: Move high-value tests to canonical directories
    moved_count = 0
    skipped_count = 0

    for target, sources in CONSOLIDATION_MAPPING.items():
        if target == "_archive":
            continue

        target_path = TESTS_DIR / target
        print(f"Consolidating → tests/{target}/")

        for source in sources:
            source_path = TESTS_DIR / source
            if source_path.exists() and source_path != target_path:
                # Check if source is high-value
                score = dir_scores.get(source, 0.0)
                test_count = len(list(source_path.glob("**/test_*.py")))

                if score >= 0.3 or test_count > 0:
                    try:
                        # Move contents
                        for item in source_path.iterdir():
                            dest = target_path / item.name
                            if item.is_dir():
                                if dest.exists():
                                    shutil.rmtree(dest)
                                shutil.copytree(item, dest)
                            else:
                                shutil.copy2(item, dest)

                        # Remove source
                        shutil.rmtree(source_path)
                        print(f"  ✅ Moved {source} (score: {score:.2f}, {test_count} tests)")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ⚠️  Error moving {source}: {e}")
                else:
                    skipped_count += 1

    print()
    print("=" * 70)
    print("STEP 8: VERIFYING CANONICAL STRUCTURE")
    print("=" * 70)
    print()

    # Show which directories received consolidated tests
    archived_count = 0
    for target in ["unit", "golden", "integration", "orchestrators", "chaos", "performance", "regression", "visualization"]:
        target_path = TESTS_DIR / target
        if target_path.exists():
            test_count = len(list(target_path.glob("**/test_*.py")))
            if test_count > 0:
                print(f"  ✅ tests/{target:30} {test_count:4} tests")

    print()
    print("=" * 70)
    print("CONSOLIDATION SUMMARY")
    print("=" * 70)
    print(f"✅ Directories consolidated: {moved_count}")
    print(f"📦 Tests archived (low-value): {archived_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print()

    # Final state
    final_dirs = sorted([d.name for d in TESTS_DIR.iterdir() if d.is_dir()])
    print(f"Final test directories: {len(final_dirs)}")
    print("Final structure:")
    for d in sorted(final_dirs):
        test_count = len(list((TESTS_DIR / d).glob("**/test_*.py")))
        print(f"  • {d:30} ({test_count} tests)")

    return len(final_dirs)


if __name__ == "__main__":
    final_count = consolidate_directories()
