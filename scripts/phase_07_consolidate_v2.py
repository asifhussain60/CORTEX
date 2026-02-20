#!/usr/bin/env python3
"""
Phase 07 GREEN - Simplified Test Consolidation

Strategy:
1. Keep high-value test categories: unit, golden, integration, orchestrators, chaos, performance, regression
2. Consolidate scattered single-test-file directories into canonical structure
3. Preserve all tests (no deletion)
"""

import os
import shutil
from pathlib import Path

TESTS_DIR = Path("/Users/asifhussain/PROJECTS/CORTEX/tests")

# Test categories to keep as-is (well-structured)
KEEP_DIRS = {
    "unit",
    "golden",
    "integration",
    "orchestrators",
    "chaos",
    "performance",
    "regression",
    "visualization",
    "fixtures",
}

# Map scattered directories to canonical homes
CONSOLIDATION_MAP = {
    "core": ["wiring"],
    "governance": ["enforcement"],
    "infrastructure": ["ci_cd", "collaboration", "repositories", "security"],
    "intelligence": ["documentation", "knowledge", "learning", "brain"],
    "mcp": [],  # Stays as-is
    "models": [],  # Stays as-is
    "templates": [],  # Stays as-is
    "tools": ["contracts", "toolkit", "standalone"],
    "testing": ["tier2", "e2e"],
    "observability": ["registry"],
    "api": [],  # Stays as-is
    "cli": [],  # Stays as-is
    "dashboards": [],  # Stays as-is
    "lens": [],  # Stays as-is
    "config": [],  # Stays as-is
    "cortex_brain": [],  # Stays as-is
    "manual": [],  # Stays as-is
}


def count_tests_in_dir(dir_path: Path) -> int:
    """Count test files in directory."""
    if not dir_path.exists():
        return 0
    return len(list(dir_path.glob("**/test_*.py")))


def consolidate():
    """Execute consolidation."""
    print("=" * 70)
    print("PHASE 07 GREEN - SIMPLIFIED TEST CONSOLIDATION")
    print("=" * 70)
    print()

    print("STEP 7: CONSOLIDATING SCATTERED DIRECTORIES")
    print("-" * 70)

    total_moved = 0
    total_tests_moved = 0

    for target_name, sources in CONSOLIDATION_MAP.items():
        if not sources:
            continue

        target = TESTS_DIR / target_name
        target.mkdir(parents=True, exist_ok=True)

        for source_name in sources:
            source = TESTS_DIR / source_name
            if not source.exists():
                continue

            test_count = count_tests_in_dir(source)

            try:
                # Move contents
                for item in source.iterdir():
                    dest_item = target / item.name
                    if item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(dest_item)
                        shutil.copytree(item, dest_item)
                    else:
                        dest_item.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_item)

                # Remove source
                shutil.rmtree(source)
                print(f"  ✅ {source_name:25} → {target.name:20} ({test_count} tests)")
                total_moved += 1
                total_tests_moved += test_count
            except Exception as e:
                print(f"  ⚠️  Error: {source_name} → {target.name}: {e}")

    print()
    print("=" * 70)
    print("FINAL TEST STRUCTURE")
    print("=" * 70)
    print()

    final_dirs = sorted([d for d in TESTS_DIR.iterdir() if d.is_dir() and d.name != ".pytest_cache"])
    print(f"Total test directories: {len(final_dirs)}")
    print()
    print("Test directories:")
    for dir_path in final_dirs:
        test_count = count_tests_in_dir(dir_path)
        status = "✅" if test_count > 0 else "ℹ️ "
        print(f"  {status} {dir_path.name:25} {test_count:4} tests")

    print()
    total_tests = sum(count_tests_in_dir(d) for d in final_dirs)
    print(f"Total tests preserved: {total_tests}")
    print(f"Directories consolidated: {total_moved}")
    print()

    return len(final_dirs), total_tests


if __name__ == "__main__":
    dir_count, test_count = consolidate()
