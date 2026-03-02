"""
CORTEX xdist Plugin — Parallel-aware batch progress for pytest.

Integrates with pytest-xdist to display real-time batch progress in
the terminal. Every CORTEX_BATCH_SIZE tests triggers a batch boundary:
  - Batch header printed before first test of each batch
  - Live pass/fail counts updated after each test
  - Batch summary printed at each batch boundary
  - Final aggregated summary at session end

Environment variables::

    CORTEX_BATCH_SIZE   — Tests per batch (default: 500)
    CORTEX_TEST_WORKERS — Worker count override (default: auto)

Usage (automatic via conftest.py)::

    pytest_plugins = ["cortex.testing.plugins.cortex_xdist_plugin"]

Authority: CORE-008 | CORE-011 | CORE-012
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import os
import time
from typing import Optional

import pytest

from cortex.testing.framework.progress_reporter import BatchProgressReporter


def _env_int(key: str, default: int) -> int:
    """Read an integer environment variable with a default."""
    try:
        return int(os.environ[key])
    except (KeyError, ValueError):
        return default


class CortexXdistPlugin:
    """Pytest plugin that renders batch-aware progress for xdist parallel runs.

    Hooks into pytest's runtest lifecycle to:
    - Open a new batch every ``batch_size`` tests
    - Emit live pass/fail counters to stderr
    - Print a final summary table at session end

    Args:
        batch_size: Number of tests per batch.
    """

    def __init__(self, batch_size: Optional[int] = None) -> None:
        """Initialise plugin with batch size from arg or env."""
        self.batch_size: int = (
            batch_size
            if batch_size is not None
            else _env_int("CORTEX_BATCH_SIZE", 500)
        )
        # Will be wired up in pytest_collection_finish once we know total
        self.reporter: Optional[BatchProgressReporter] = None
        self.current_batch: int = 1
        self._batch_passed: int = 0
        self._batch_failed: int = 0
        self._batch_start: float = 0.0
        self._test_index: int = 0
        self._total: int = 0
        # Initialise reporter with a placeholder total (updated at collection)
        self.reporter = BatchProgressReporter(total=0, batch_size=self.batch_size)

    # ------------------------------------------------------------------ #
    # Pytest hooks
    # ------------------------------------------------------------------ #

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Re-initialise reporter with actual total after collection.

        Only fires on the main controller process (not xdist workers),
        so this is the correct place to set up batch reporting.
        """
        self._total = len(session.items)
        if self._total == 0:
            return  # nothing to report
        self.reporter = BatchProgressReporter(
            total=self._total,
            batch_size=self.batch_size,
        )
        self._batch_start = time.monotonic()
        # Print batch 1 header now that we know total
        batch_items = min(self.batch_size, self._total)
        self.reporter.on_batch_start(batch_num=1, count=batch_items)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Track each test result and emit batch boundary output."""
        # Only count the final call phase (not setup/teardown separately)
        if report.when != "call":
            return

        self._test_index += 1

        if report.passed:
            self._batch_passed += 1
        elif report.failed:
            self._batch_failed += 1

        # Check if we've hit the batch boundary
        if self._test_index % self.batch_size == 0 and self._test_index < self._total:
            duration = time.monotonic() - self._batch_start
            self.reporter.on_batch_complete(
                batch_num=self.current_batch,
                passed=self._batch_passed,
                failed=self._batch_failed,
                duration=duration,
            )
            # Advance to next batch
            self.current_batch += 1
            self._batch_passed = 0
            self._batch_failed = 0
            self._batch_start = time.monotonic()
            remaining = self._total - self._test_index
            batch_items = min(self.batch_size, remaining)
            if batch_items > 0:
                self.reporter.on_batch_start(
                    batch_num=self.current_batch,
                    count=batch_items,
                )

    def pytest_sessionfinish(
        self, session: pytest.Session, exitstatus: int
    ) -> None:
        """Complete the final partial batch and print overall summary."""
        if self._batch_passed + self._batch_failed > 0:
            duration = time.monotonic() - self._batch_start
            self.reporter.on_batch_complete(
                batch_num=self.current_batch,
                passed=self._batch_passed,
                failed=self._batch_failed,
                duration=duration,
            )
        self.reporter.print_final_summary()

    # ------------------------------------------------------------------ #
    # Internal helper (used by tests)
    # ------------------------------------------------------------------ #

    def _on_test_complete(self, nodeid: str, passed: bool) -> None:
        """Simulate a test completion (used in unit tests only).

        Args:
            nodeid: Test node identifier string.
            passed: Whether the simulated test passed.
        """
        self._test_index += 1
        if passed:
            self._batch_passed += 1
        else:
            self._batch_failed += 1

        if self._test_index % self.batch_size == 0:
            self.current_batch += 1
            self._batch_passed = 0
            self._batch_failed = 0


# ============================================================================
# Module-level pytest hook — called by pytest plugin system
# ============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Register CortexXdistPlugin if not already registered.

    Args:
        config: Pytest configuration object.
    """
    if not config.pluginmanager.is_registered("cortex-xdist"):
        plugin = CortexXdistPlugin()
        config.pluginmanager.register(plugin, "cortex-xdist")
