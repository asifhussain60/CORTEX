"""
CORTEX Test Categorizer — Auto-assigns execution tier markers by path.

Eliminates the need for developers to manually add @pytest.mark.unit,
@pytest.mark.golden, etc. by inferring the correct tier from directory
path conventions established in Phase 07.

Tier mapping (authoritative):
  tests/golden/      → golden
  tests/unit/        → unit
  tests/integration/ → integration
  tests/chaos/       → e2e
  tests/performance/ → slow
  tests/regression/  → unit  (fast regression checks)
  tests/mcp/         → integration
  tests/observability/ → integration
  tests/lens/        → unit
  *                  → unit  (safe default)

Authority: CORE-008 | CORE-011 | CORE-012
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


# Ordered mapping: first match wins
_TIER_RULES: List[tuple[str, str]] = [
    ("tests/golden",          "golden"),
    ("tests/chaos",           "e2e"),
    ("tests/performance",     "slow"),
    ("tests/integration",     "integration"),
    ("tests/mcp",             "integration"),
    ("tests/observability",   "integration"),
    ("tests/infrastructure",  "integration"),
    ("tests/regression",      "unit"),
    ("tests/lens",            "unit"),
    ("tests/unit",            "unit"),
    ("tests/core",            "unit"),
    ("tests/governance",      "unit"),
]


class TestCategorizer:
    """Infers execution tier for test files from their filesystem path.

    Used by the parallel runner to route tests to the correct execution
    profile (workers, distribution strategy, batch size).

    Example::

        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/golden/test_x.py"))
        # → "golden"
    """

    def __init__(self, custom_rules: Optional[List[tuple[str, str]]] = None) -> None:
        """Initialise with optional custom path→tier rules.

        Args:
            custom_rules: Additional (path_prefix, tier) pairs prepended
                          before built-in rules (first match wins).
        """
        self._rules: List[tuple[str, str]] = (custom_rules or []) + _TIER_RULES

    def categorize_by_path(self, path: Path) -> str:
        """Return the execution tier for a single test path.

        Args:
            path: Filesystem path to the test file.

        Returns:
            Tier string: golden | unit | integration | e2e | slow.
        """
        path_str = str(path).replace("\\", "/")   # normalise Windows paths
        for prefix, tier in self._rules:
            if path_str.startswith(prefix) or f"/{prefix.lstrip('tests/')}" in path_str:
                return tier
        return "unit"   # safe default

    def assign_tiers(self, paths: List[Path]) -> Dict[Path, str]:
        """Return path→tier mapping for a list of test paths.

        Args:
            paths: List of test file paths.

        Returns:
            Dictionary mapping each path to its tier string.
        """
        return {p: self.categorize_by_path(p) for p in paths}

    def group_by_tier(self, paths: List[Path]) -> Dict[str, List[Path]]:
        """Group paths by execution tier.

        Args:
            paths: List of test file paths.

        Returns:
            Dictionary keyed by tier with lists of paths as values.
        """
        groups: Dict[str, List[Path]] = {}
        for path, tier in self.assign_tiers(paths).items():
            groups.setdefault(tier, []).append(path)
        return groups
