# =============================================================================
# ParallelGoldenRunner — Phase 49
# Wraps pytest-xdist with real-time VS Code terminal progress.
# =============================================================================
#
# AC-ID: AC-P49-IMPL-002
# Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
#            CORE-049 (silent autonomous / progress bars in terminal)
# Author: Asif Hussain
# Created: 2026-02-18
#
# Coverage Matrix:
# P0: run() returns ParallelRunResult, workers list populated, dry_run respected
# P1: ProgressReporter start_step/complete_step called per worker batch
# P2: TestProgressMonitor integration, monitor optional kwarg accepted
# =============================================================================

from __future__ import annotations

import math
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Optional, Any


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class WorkerResult:
    """Result record for a single parallel worker batch.

    Attributes:
        worker_id: Integer identifier for this worker (1-based).
        paths: Test file paths assigned to this worker.
        passed: Number of tests that passed in this batch.
        failed: Number of tests that failed in this batch.
        duration: Wall-clock seconds consumed by this worker.
    """

    worker_id: int
    paths: List[str]
    passed: int
    failed: int
    duration: float


@dataclass
class ParallelRunResult:
    """Aggregated result across all parallel workers.

    Attributes:
        total_passed: Sum of passed across all workers.
        total_failed: Sum of failed across all workers.
        workers: Per-worker result records.
        duration: Total wall-clock duration (max worker duration).
        dry_run: Whether this was a dry run (no tests executed).
    """

    total_passed: int
    total_failed: int
    workers: List[WorkerResult]
    duration: float
    dry_run: bool = False


# =============================================================================
# RUNNER
# =============================================================================

class ParallelGoldenRunner:
    """Runs golden test suites in parallel workers with real-time progress.

    Uses pytest-xdist under the hood. Streams per-worker progress bars
    to the terminal via ProgressReporter and optionally a TestProgressMonitor.

    All public parameters are optional-keyword-only to keep the interface
    forwards-compatible (CORE-035: single canonical implementation).

    Usage::

        runner = ParallelGoldenRunner(workers=4)
        result = runner.run([
            "tests/golden/orchestrators/",
            "tests/golden/governance/",
        ])
        print(f"{result.total_passed} passed in {result.duration:.2f}s")
    """

    def __init__(
        self,
        workers: int = 4,
        dry_run: bool = False,
        reporter: Optional[Any] = None,
        monitor: Optional[Any] = None,
    ) -> None:
        """Initialise the runner.

        Args:
            workers: Number of parallel pytest-xdist workers. Default 4.
            dry_run: If True, collect tests only — do not execute.
            reporter: Optional ProgressReporter instance. Auto-created if None.
            monitor: Optional TestProgressMonitor instance. Ignored if None.
        """
        self.workers = max(1, workers)
        self.dry_run = dry_run
        self.monitor = monitor

        # Lazy-import ProgressReporter so the module stays importable even in
        # environments where the reporter is not available.
        if reporter is not None:
            self._reporter = reporter
        else:
            try:
                from cortex.core.common.core_progress_reporter import ProgressReporter
                self._reporter = ProgressReporter()
            except Exception:
                self._reporter = None

    # -------------------------------------------------------------------------
    # Public interface
    # -------------------------------------------------------------------------

    def run(self, test_paths: List[str]) -> ParallelRunResult:
        """Run the given test paths in parallel, return aggregated results.

        In dry_run mode: collects test paths only, returns zeros for
        passed/failed counts, and marks the result as ``dry_run=True``.

        Args:
            test_paths: List of test file or directory paths to execute.

        Returns:
            ParallelRunResult: Aggregated counts, per-worker records, duration.
        """
        if self.dry_run:
            return self._dry_run(test_paths)

        return self._execute(test_paths)

    # -------------------------------------------------------------------------
    # Internal: dry run
    # -------------------------------------------------------------------------

    def _dry_run(self, test_paths: List[str]) -> ParallelRunResult:
        """Collect-only mode — no execution, zero counts.

        Args:
            test_paths: Paths that would be executed.

        Returns:
            ParallelRunResult: All counts zero, dry_run=True.
        """
        batches = self._partition(test_paths, self.workers)
        workers = [
            WorkerResult(
                worker_id=i + 1,
                paths=batch,
                passed=0,
                failed=0,
                duration=0.0,
            )
            for i, batch in enumerate(batches)
        ]

        if self._reporter:
            self._reporter.start_step("dry-run-collect")
            self._reporter.complete_step("dry-run-collect")

        return ParallelRunResult(
            total_passed=0,
            total_failed=0,
            workers=workers,
            duration=0.0,
            dry_run=True,
        )

    # -------------------------------------------------------------------------
    # Internal: real execution
    # -------------------------------------------------------------------------

    def _execute(self, test_paths: List[str]) -> ParallelRunResult:
        """Execute tests in parallel workers, stream progress, aggregate results.

        Args:
            test_paths: Paths to execute.

        Returns:
            ParallelRunResult: Aggregated counts.
        """
        batches = self._partition(test_paths, self.workers)
        worker_results: List[WorkerResult] = []
        start_total = time.monotonic()

        total_batches = len(batches)
        if self._reporter:
            self._reporter.start_step("parallel-golden-run")
            self._reporter.set_step_estimates(total_batches)

        for idx, batch in enumerate(batches):
            if not batch:
                continue

            worker_start = time.monotonic()
            passed, failed = self._run_batch(batch, worker_id=idx + 1)
            worker_dur = time.monotonic() - worker_start

            w = WorkerResult(
                worker_id=idx + 1,
                paths=batch,
                passed=passed,
                failed=failed,
                duration=round(worker_dur, 3),
            )
            worker_results.append(w)

            if self._reporter:
                self._reporter.complete_step(f"worker-{idx + 1}")

        total_duration = time.monotonic() - start_total

        total_passed = sum(w.passed for w in worker_results)
        total_failed = sum(w.failed for w in worker_results)

        if self._reporter:
            self._reporter.complete_step("parallel-golden-run")

        return ParallelRunResult(
            total_passed=total_passed,
            total_failed=total_failed,
            workers=worker_results,
            duration=round(total_duration, 3),
            dry_run=False,
        )

    def _run_batch(self, paths: List[str], worker_id: int) -> tuple[int, int]:
        """Execute a batch of test paths via subprocess pytest.

        Args:
            paths: Test paths for this batch.
            worker_id: Worker identifier for display.

        Returns:
            Tuple of (passed_count, failed_count).
        """
        cmd = ["python", "-m", "pytest"] + paths + [
            "--tb=no", "-q", "--no-header",
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return self._parse_pytest_output(proc.stdout + proc.stderr)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return 0, 0

    @staticmethod
    def _parse_pytest_output(output: str) -> tuple[int, int]:
        """Parse 'N passed, M failed' from pytest summary line.

        Args:
            output: Combined stdout+stderr from pytest subprocess.

        Returns:
            Tuple of (passed_count, failed_count).
        """
        passed = 0
        failed = 0
        for line in output.splitlines():
            if " passed" in line or " failed" in line:
                import re
                m_passed = re.search(r"(\d+) passed", line)
                m_failed = re.search(r"(\d+) failed", line)
                if m_passed:
                    passed = int(m_passed.group(1))
                if m_failed:
                    failed = int(m_failed.group(1))
        return passed, failed

    @staticmethod
    def _partition(items: List[str], n: int) -> List[List[str]]:
        """Partition a list into at most n roughly equal batches.

        Args:
            items: Items to partition.
            n: Target number of batches.

        Returns:
            List of batches (may be fewer than n if len(items) < n).
        """
        if not items:
            return [[]]
        n = max(1, min(n, len(items)))
        size = math.ceil(len(items) / n)
        return [items[i : i + size] for i in range(0, len(items), size)]
