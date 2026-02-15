"""
CORTEX Pytest Progress Plugin — Real-time terminal feedback.

Solves the "hanging test" perception by showing progress during:
1. Test collection (16K+ tests = 15s+ of silence without this)
2. Long test execution (shows elapsed time per test)
3. Slow test detection (warns when tests exceed threshold)

Usage:
    Automatically loaded via conftest.py or pytest plugin system.
    Set CORTEX_TEST_PROGRESS=1 to enable verbose progress.

Author: Asif Hussain
AC-ID: AC-TEST-PERF-002
"""

from __future__ import annotations

import os
import time
import sys
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


# Only activate when running in terminal (not in CI capture mode)
_INTERACTIVE = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
_VERBOSE_PROGRESS = os.getenv("CORTEX_TEST_PROGRESS", "0") == "1"
_SLOW_THRESHOLD = float(os.getenv("CORTEX_SLOW_THRESHOLD", "5.0"))  # seconds


class CortexProgressPlugin:
    """Provides real-time feedback during test collection and execution.

    Prevents the "tests are hanging" perception by:
    - Printing collection progress every 1000 items
    - Showing per-test elapsed time when > slow threshold
    - Printing a summary of slow tests at the end
    """

    def __init__(self) -> None:
        """Initialize progress tracking state."""
        self._collect_count: int = 0
        self._collect_start: float = 0.0
        self._test_starts: Dict[str, float] = {}
        self._slow_tests: List[Tuple[str, float]] = []
        self._total_start: float = 0.0

    def pytest_collection_modifyitems(
        self, config: pytest.Config, items: list[pytest.Item]
    ) -> None:
        """Report collection completion with count and time."""
        elapsed = time.monotonic() - self._collect_start if self._collect_start else 0
        if _INTERACTIVE and len(items) > 500:
            sys.stderr.write(
                f"\r\033[K✓ Collected {len(items)} tests in {elapsed:.1f}s\n"
            )
            sys.stderr.flush()

    def pytest_collectstart(self, collector: pytest.Collector) -> None:
        """Track collection start time."""
        if self._collect_start == 0.0:
            self._collect_start = time.monotonic()
            self._total_start = self._collect_start

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        """Show collection progress for large test suites."""
        if report.result:
            self._collect_count += len(report.result)
            if _INTERACTIVE and self._collect_count % 1000 == 0:
                elapsed = time.monotonic() - self._collect_start
                sys.stderr.write(
                    f"\r\033[K⏳ Collecting tests... {self._collect_count} found ({elapsed:.1f}s)"
                )
                sys.stderr.flush()

    def pytest_runtest_setup(self, item: pytest.Item) -> None:
        """Record test start time."""
        self._test_starts[item.nodeid] = time.monotonic()

    def pytest_runtest_teardown(self, item: pytest.Item) -> None:
        """Check if test was slow and record it."""
        start = self._test_starts.pop(item.nodeid, None)
        if start is not None:
            elapsed = time.monotonic() - start
            if elapsed > _SLOW_THRESHOLD:
                self._slow_tests.append((item.nodeid, elapsed))
                if _INTERACTIVE and _VERBOSE_PROGRESS:
                    sys.stderr.write(
                        f"\n⚠️  SLOW ({elapsed:.1f}s): {item.nodeid}\n"
                    )
                    sys.stderr.flush()

    def pytest_terminal_summary(
        self, terminalreporter: "TerminalReporter", exitstatus: int
    ) -> None:
        """Print slow test summary at the end of the run."""
        if self._slow_tests:
            terminalreporter.section("Slow Tests (>{:.0f}s)".format(_SLOW_THRESHOLD))
            # Sort by duration descending
            for nodeid, duration in sorted(
                self._slow_tests, key=lambda x: x[1], reverse=True
            )[:20]:  # Top 20 slowest
                terminalreporter.line(f"  {duration:6.1f}s  {nodeid}")
            terminalreporter.line(
                f"\n  Total slow tests: {len(self._slow_tests)}"
            )

        total_elapsed = time.monotonic() - self._total_start if self._total_start else 0
        if total_elapsed > 0:
            terminalreporter.line(
                f"  Total wall time: {total_elapsed:.1f}s"
            )


def pytest_configure(config: pytest.Config) -> None:
    """Register the progress plugin."""
    config.pluginmanager.register(CortexProgressPlugin(), "cortex-progress")
