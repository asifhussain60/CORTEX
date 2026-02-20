"""
CORTEX Parallel Test Runner — Batch-aware pytest-xdist wrapper.

Provides tiered execution profiles that map each test category to
appropriate parallelism, distribution strategy, and batch size.

Profiles:
  smoke       — -n auto, loadfile, batch=500 (fastest feedback)
  unit        — -n auto, loadscope, batch=500 (class isolation)
  integration — -n 4, loadfile, batch=200 (limited concurrency)
  golden      — serial (no -n), batch=100 (deterministic order)

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional


# ============================================================================
# Execution profiles — single source of truth for parallelism config
# ============================================================================

EXECUTION_PROFILES: Dict[str, Dict[str, Any]] = {
    "smoke": {
        "workers": "auto",
        "dist": "loadfile",
        "markers": ["smoke"],
        "batch_size": 500,
        "description": "Fastest feedback — smoke tests only",
    },
    "unit": {
        "workers": "auto",
        "dist": "loadscope",          # keeps test class on same worker
        "markers": ["unit"],
        "batch_size": 500,
        "description": "Parallel unit tests with class isolation",
    },
    "integration": {
        "workers": 4,
        "dist": "loadfile",
        "markers": ["integration"],
        "batch_size": 200,
        "description": "Limited concurrency for external-dependency tests",
    },
    "golden": {
        "workers": 0,                 # 0 = serial, no xdist
        "dist": "no",
        "markers": ["golden", "e2e"],
        "batch_size": 100,
        "description": "Deterministic serial execution for golden/e2e",
    },
    "auto": {
        "workers": "auto",
        "dist": "loadscope",
        "markers": [],
        "batch_size": 500,
        "description": "Auto-detect workers, run all tests",
    },
}


class ParallelRunner:
    """Batch-aware pytest-xdist configuration builder.

    Wraps pytest-xdist configuration with CORTEX-specific batch sizing,
    distribution strategies, and profile-driven worker counts.

    Example::

        runner = ParallelRunner(profile="unit")
        args = runner.build_pytest_args(paths=["tests/unit"])
        # -> ["-n", "auto", "--dist", "loadscope", "-v", "tests/unit"]

    """

    def __init__(
        self,
        profile: str = "auto",
        workers: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> None:
        """Initialise runner with execution profile.

        Args:
            profile: One of smoke | unit | integration | golden | auto.
            workers: Explicit worker count (overrides profile default).
            batch_size: Tests per batch (overrides profile default).
        """
        if profile not in EXECUTION_PROFILES:
            raise ValueError(
                f"Unknown profile '{profile}'. "
                f"Valid profiles: {list(EXECUTION_PROFILES.keys())}"
            )
        self.profile = profile
        self._profile_cfg = EXECUTION_PROFILES[profile]
        self._explicit_workers = workers
        self.batch_size: int = batch_size or self._profile_cfg["batch_size"]

    # ------------------------------------------------------------------ #
    # Worker count
    # ------------------------------------------------------------------ #

    def worker_count(self) -> int:
        """Resolve actual worker count.

        Returns:
            Number of parallel workers (≥1, ≤2× CPU count).
        """
        if self._explicit_workers is not None:
            return max(1, self._explicit_workers)

        raw = self._profile_cfg["workers"]

        if raw == "auto" or raw == 0:
            # Profile "golden" uses 0 = serial — return 1 for the count
            if raw == 0:
                return 1
            cpu = os.cpu_count() or 4
            return min(cpu, cpu)        # same as cpu_count, cap at 2x if needed

        return max(1, int(raw))

    # ------------------------------------------------------------------ #
    # Arg builder
    # ------------------------------------------------------------------ #

    def build_pytest_args(self, paths: List[str]) -> List[str]:
        """Build pytest CLI argument list for this profile.

        Args:
            paths: Test paths to include.

        Returns:
            List of strings to pass to pytest.main().
        """
        cfg = self._profile_cfg
        args: List[str] = ["-v", "--tb=short"]

        if cfg["workers"] != 0:          # 0 = serial, skip xdist flags
            worker_val = (
                "auto" if cfg["workers"] == "auto"
                else str(self._explicit_workers or cfg["workers"])
            )
            args += ["-n", worker_val, "--dist", cfg["dist"]]

        # Marker filter
        if cfg["markers"]:
            marker_expr = " or ".join(cfg["markers"])
            args += ["-m", marker_expr]

        args += paths
        return args

    # ------------------------------------------------------------------ #
    # Batch splitting
    # ------------------------------------------------------------------ #

    def split_into_batches(self, items: List[str]) -> List[List[str]]:
        """Divide test node IDs into fixed-size batches.

        Args:
            items: List of test node ID strings.

        Returns:
            List of sublists, each of length ≤ batch_size.
        """
        if not items:
            return []

        size = self.batch_size
        return [items[i : i + size] for i in range(0, len(items), size)]
