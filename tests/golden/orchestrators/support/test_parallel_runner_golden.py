# =============================================================================
# Phase 49 — ParallelGoldenRunner Golden Tests
# GP-001 through GP-008: Parallel Execution & Progress Integration Scenarios
# =============================================================================
#
# AC-ID: AC-P49-GP-001
# Authority: CORE-008 (TDD), CORE-049 (Silent Autonomous), CORE-055 (Golden Test Tier)
# Author: Asif Hussain
# Created: 2026-02-18
#
# Coverage Matrix:
# P0 (Critical): GP-001..GP-004 — core parallel execution behaviour
# P1 (High):     GP-005..GP-007 — ProgressReporter integration
# P2 (Medium):   GP-008 — TestProgressMonitor real-time streaming
#
# AC_START: ParallelGoldenRunner golden test suite
# =============================================================================

import pytest
from unittest.mock import MagicMock, patch, call
from cortex.orchestrators.support.parallel_golden_runner import (
    ParallelGoldenRunner,
    WorkerResult,
    ParallelRunResult,
)
from cortex.common.progress_reporter import ProgressReporter


# =============================================================================
# P0 SCENARIOS — Core Parallel Execution
# =============================================================================

class TestParallelRunnerCore:
    """GP-001 through GP-004: core parallel execution behaviour."""

    def test_runner_accepts_list_of_test_paths(self):
        """GP-001: parallel runner accepts list of test paths and returns ParallelRunResult."""
        runner = ParallelGoldenRunner(workers=2, dry_run=True)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
            "tests/golden/orchestrators/support/test_classifier_golden.py",
        ]
        result = runner.run(paths)
        assert isinstance(result, ParallelRunResult)

    def test_output_includes_per_worker_progress(self):
        """GP-002: output includes per-worker progress stream (WorkerResult objects)."""
        runner = ParallelGoldenRunner(workers=2, dry_run=True)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
            "tests/golden/orchestrators/support/test_classifier_golden.py",
        ]
        result = runner.run(paths)
        assert isinstance(result.workers, list)
        assert len(result.workers) >= 1
        for w in result.workers:
            assert isinstance(w, WorkerResult)
            assert hasattr(w, "worker_id")
            assert hasattr(w, "passed")
            assert hasattr(w, "failed")
            assert hasattr(w, "duration")

    def test_final_summary_aggregates_across_workers(self):
        """GP-003: final summary aggregates passed/failed across all workers."""
        runner = ParallelGoldenRunner(workers=2, dry_run=True)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
        ]
        result = runner.run(paths)
        assert hasattr(result, "total_passed")
        assert hasattr(result, "total_failed")
        assert hasattr(result, "duration")
        total = result.total_passed + result.total_failed
        worker_total = sum(w.passed + w.failed for w in result.workers)
        assert total == worker_total

    def test_dry_run_collects_without_executing(self):
        """GP-005: dry_run=True collects test paths without executing tests."""
        runner = ParallelGoldenRunner(workers=2, dry_run=True)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
        ]
        result = runner.run(paths)
        # In dry_run mode: total_passed = 0, total_failed = 0 (no execution)
        assert result.total_passed == 0
        assert result.total_failed == 0
        assert result.dry_run is True


# =============================================================================
# P1 SCENARIOS — ProgressReporter Integration
# =============================================================================

class TestProgressReporterIntegration:
    """GP-006 through GP-007: ProgressReporter called correctly."""

    def test_progress_reporter_start_step_called_per_worker(self):
        """GP-006: ProgressReporter.start_step called for each worker group."""
        mock_reporter = MagicMock(spec=ProgressReporter)
        runner = ParallelGoldenRunner(workers=2, dry_run=True, reporter=mock_reporter)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
            "tests/golden/orchestrators/support/test_classifier_golden.py",
        ]
        runner.run(paths)
        assert mock_reporter.start_step.called

    def test_progress_reporter_complete_step_called_on_worker_finish(self):
        """GP-007: ProgressReporter.complete_step called when worker finishes."""
        mock_reporter = MagicMock(spec=ProgressReporter)
        runner = ParallelGoldenRunner(workers=2, dry_run=True, reporter=mock_reporter)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
        ]
        runner.run(paths)
        assert mock_reporter.complete_step.called


# =============================================================================
# P2 SCENARIOS — TestProgressMonitor Integration
# =============================================================================

class TestProgressMonitorIntegration:
    """GP-008: TestProgressMonitor real-time streaming."""

    def test_test_progress_monitor_integration(self):
        """GP-008: TestProgressMonitor integration — output format has expected structure."""
        from cortex.devx.test_progress_monitor import TestProgressMonitor
        # TestProgressMonitor requires a command list to initialise
        monitor = TestProgressMonitor(command=["python", "-m", "pytest", "--co", "-q"])
        assert hasattr(monitor, "run") or hasattr(monitor, "get_metrics_summary")
        runner = ParallelGoldenRunner(workers=2, dry_run=True, monitor=monitor)
        paths = [
            "tests/golden/orchestrators/health_vacuum/test_health_orchestrator_golden.py",
        ]
        result = runner.run(paths)
        assert isinstance(result, ParallelRunResult)
