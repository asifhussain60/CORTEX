"""Phase 107 Sub-Phase D — Directory Flattening + Stub Pruning.

RED→GREEN→REFACTOR tests for GAP-107-07, GAP-107-08, GAP-107-09.

Authority: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Tier: T1 (unit)
"""
from __future__ import annotations

import pathlib
from typing import List

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[3]
INTELLIGENCE_DIR = CORTEX_ROOT / "cortex" / "intelligence"


# ════════════════════════════════════════════════════════════════════════════
# GAP-107-07: No double-nested directories (intelligence/X/X/)
# ════════════════════════════════════════════════════════════════════════════

class TestNoDoubleNestedDirs:
    """GAP-107-07: Eliminate redundant parent/child same-name nesting."""

    def _find_double_nested(self) -> List[str]:
        """Return list of dirs where parent and child share the same name."""
        violations: List[str] = []
        for d in INTELLIGENCE_DIR.rglob("*"):
            if not d.is_dir():
                continue
            if d.name == d.parent.name and d.parent != INTELLIGENCE_DIR:
                violations.append(str(d.relative_to(CORTEX_ROOT)))
        return violations

    def test_no_double_nested_directories(self) -> None:
        """No directory pattern intelligence/X/X/ should exist.

        Known violations at RED time:
          - domain_brain/domain_brain/ (15 KG files)
          - lens/lens/ (lens_pipeline.py)
          - state/state/ (user-personas.yaml only — no Python)
        """
        violations = self._find_double_nested()
        assert not violations, (
            f"GAP-107-07: {len(violations)} double-nested dir(s) found. "
            f"Flatten inner content into parent:\n  " + "\n  ".join(violations)
        )

    def test_domain_brain_kg_files_at_outer_level(self) -> None:
        """After flattening, KG files must be directly in domain_brain/, not domain_brain/domain_brain/."""
        kg_files = [
            "kg_indexer.py",
            "kg_querier.py",
            "kg_inference.py",
            "kg_deduplicator.py",
            "kg_validation.py",
            "kg_sync_orchestrator.py",
        ]
        for fname in kg_files:
            flat_path = INTELLIGENCE_DIR / "domain_brain" / fname
            assert flat_path.exists(), (
                f"GAP-107-07: {fname} not found at domain_brain/ level. "
                f"Expected: {flat_path.relative_to(CORTEX_ROOT)}"
            )

    def test_lens_pipeline_at_outer_level(self) -> None:
        """After flattening, lens_pipeline.py must be directly in lens/, not lens/lens/."""
        flat_path = INTELLIGENCE_DIR / "lens" / "lens_pipeline.py"
        assert flat_path.exists(), (
            f"GAP-107-07: lens_pipeline.py not found at lens/ level. "
            f"Expected: {flat_path.relative_to(CORTEX_ROOT)}"
        )


# ════════════════════════════════════════════════════════════════════════════
# GAP-107-08: Single-file subdirectories should be modules, not packages
# ════════════════════════════════════════════════════════════════════════════

class TestSingleFileDirsCollapsed:
    """GAP-107-08: Directories with only 1-2 Python files → collapse into parent.

    Candidates (non-__init__ file count):
      - perception/ (1 file: chat_file_detector.py) → removed, module at parent
      - sensory/ (1 file) → removed, module at parent
      - reasoning/ (1 file: strategy_selector.py) → removed, module at parent
      - nlp/ (1 file: embedding_cache.py) → removed, module at parent
    """

    # Directories that should NOT exist after flattening
    # Phase 1 (Sub-Phase D): only dirs with zero external imports
    # Phase 2 (Sub-Phase C): perception, reasoning, nlp consolidated during LENS merge
    COLLAPSED_DIRS = [
        "sensory",
        "releases",
    ]

    def test_collapsed_dirs_no_longer_exist(self) -> None:
        """Single-file directories should be removed after collapsing."""
        still_exist = []
        for dirname in self.COLLAPSED_DIRS:
            d = INTELLIGENCE_DIR / dirname
            if d.is_dir():
                still_exist.append(str(d.relative_to(CORTEX_ROOT)))
        assert not still_exist, (
            f"GAP-107-08: {len(still_exist)} single-file dir(s) still exist. "
            f"Collapse to modules:\n  " + "\n  ".join(still_exist)
        )

    def test_collapsed_modules_importable(self) -> None:
        """Collapsed directories should no longer exist as package dirs."""
        for dirname in self.COLLAPSED_DIRS:
            d = INTELLIGENCE_DIR / dirname
            assert not d.is_dir(), (
                f"GAP-107-08: {dirname}/ is still a directory package. "
                f"Should be removed (zero external imports)."
            )


# ════════════════════════════════════════════════════════════════════════════
# GAP-107-09: Empty directories pruned
# ════════════════════════════════════════════════════════════════════════════

class TestEmptyDirsPruned:
    """GAP-107-09: Remove empty directories (no Python files at any depth)."""

    # Known empty dirs that should be pruned
    # Note: governance/ retained — has precedence.yaml referenced by runtime tests
    EXPECTED_PRUNED = [
        "cortex/intelligence/releases",
        "cortex/intelligence/releases/v1.0.0",
        "cortex/intelligence/audit/migrations",
        "cortex/intelligence/state/state",
    ]

    def test_empty_dirs_removed(self) -> None:
        """Directories with zero Python files should be removed."""
        still_exist = []
        for rel_path in self.EXPECTED_PRUNED:
            d = CORTEX_ROOT / rel_path
            if d.is_dir():
                # Check if it has ANY Python files
                py_files = list(d.rglob("*.py"))
                if not py_files:
                    still_exist.append(rel_path)
        assert not still_exist, (
            f"GAP-107-09: {len(still_exist)} empty dir(s) still exist:\n  "
            + "\n  ".join(still_exist)
        )


# ════════════════════════════════════════════════════════════════════════════
# Convergence: Overall directory health
# ════════════════════════════════════════════════════════════════════════════

class TestDirectoryConvergence:
    """Convergence gate tests for Sub-Phase D completion."""

    def test_intelligence_subdir_count(self) -> None:
        """Top-level intelligence subdirectories must be ≤25.

        Starting point: 28 subdirs.
        Target after D: ≤25 (removed releases/, sensory/, state/).
        Final target after full Phase 107: ≤15 (Sub-Phase C merges remaining).
        """
        subdirs = [
            d for d in INTELLIGENCE_DIR.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ]
        assert len(subdirs) <= 25, (
            f"Convergence: {len(subdirs)} top-level intelligence subdirs "
            f"(target ≤25 after Sub-Phase D). Current:\n  "
            + "\n  ".join(sorted(d.name for d in subdirs))
        )

    def test_max_directory_depth(self) -> None:
        """No directory chain deeper than 5 levels from cortex/intelligence/.

        Prevents re-growth of deep nesting.
        """
        max_depth = 0
        deepest = ""
        for d in INTELLIGENCE_DIR.rglob("*"):
            if not d.is_dir() or "__pycache__" in str(d):
                continue
            depth = len(d.relative_to(INTELLIGENCE_DIR).parts)
            if depth > max_depth:
                max_depth = depth
                deepest = str(d.relative_to(CORTEX_ROOT))
        assert max_depth <= 5, (
            f"Convergence: max depth is {max_depth} levels "
            f"(target ≤5). Deepest: {deepest}"
        )
