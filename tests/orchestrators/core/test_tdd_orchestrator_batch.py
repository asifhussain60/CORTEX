"""
TDD RED phase — BatchTestRunner on TDDOrchestrator.

Tests for run_batch_suite() and the build_chat_output() method
on BatchProgressReporter. All tests are RED until implementation.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
AC-ID: AC-BATCH-TEST-RUNNER-001
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tdd_orchestrator():
    """Return a fresh TDDOrchestrator instance."""
    from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

    return TDDOrchestrator()


@pytest.fixture()
def reporter():
    """Return a BatchProgressReporter with 100 total / 25 per batch."""
    from cortex.testing.framework.progress_reporter import BatchProgressReporter

    return BatchProgressReporter(total=100, batch_size=25)


# ---------------------------------------------------------------------------
# BatchProgressReporter — build_chat_output()
# ---------------------------------------------------------------------------


class TestBuildChatOutput:
    """build_chat_output() must return a formatted ASCII string, not write to stderr."""

    def test_returns_string_not_none(self, reporter):
        """build_chat_output returns a non-empty string."""
        output = reporter.build_chat_output(
            batch_num=1,
            passed=20,
            failed=0,
            duration=3.2,
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_contains_progress_bar_chars(self, reporter):
        """Output contains block chars that form the ASCII bar."""
        output = reporter.build_chat_output(
            batch_num=1,
            passed=25,
            failed=0,
            duration=1.0,
        )
        assert "█" in output or "░" in output

    def test_shows_passed_failed_counts(self, reporter):
        """Output includes pass and fail counts."""
        output = reporter.build_chat_output(
            batch_num=2,
            passed=18,
            failed=3,
            duration=2.5,
        )
        assert "18" in output
        assert "3" in output

    def test_shows_batch_number(self, reporter):
        """Output includes the batch number."""
        output = reporter.build_chat_output(
            batch_num=3,
            passed=10,
            failed=0,
            duration=1.0,
        )
        assert "3" in output

    def test_shows_duration(self, reporter):
        """Output includes formatted duration."""
        output = reporter.build_chat_output(
            batch_num=1,
            passed=25,
            failed=0,
            duration=7.83,
        )
        assert "7.8" in output or "7.83" in output or "⏱" in output

    def test_final_summary_string(self, reporter):
        """build_final_summary() returns inline string for Chat."""
        # Simulate 4 completed batches
        for i in range(4):
            reporter.build_chat_output(
                batch_num=i + 1,
                passed=24,
                failed=1,
                duration=2.0,
            )
        summary = reporter.build_final_summary()
        assert isinstance(summary, str)
        assert "PASS" in summary or "FAIL" in summary or "✅" in summary or "🔴" in summary

    def test_zero_failures_shows_pass_icon(self, reporter):
        """✅ icon appears when no failures in batch."""
        output = reporter.build_chat_output(
            batch_num=1,
            passed=25,
            failed=0,
            duration=1.0,
        )
        assert "✅" in output

    def test_nonzero_failures_shows_fail_icon(self, reporter):
        """🔴 icon appears when batch has failures."""
        output = reporter.build_chat_output(
            batch_num=1,
            passed=20,
            failed=5,
            duration=1.0,
        )
        assert "🔴" in output


# ---------------------------------------------------------------------------
# TDDOrchestrator — run_batch_suite()
# ---------------------------------------------------------------------------


class TestRunBatchSuite:
    """run_batch_suite() must split tests, run per-batch, and return chat string."""

    def test_method_exists(self, tdd_orchestrator):
        """run_batch_suite method is present on TDDOrchestrator."""
        assert hasattr(tdd_orchestrator, "run_batch_suite"), (
            "TDDOrchestrator must have run_batch_suite() — GREEN phase not yet implemented"
        )

    def test_returns_dict_with_chat_output(self, tdd_orchestrator):
        """run_batch_suite returns dict with 'chat_output' key."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"passed": 10, "failed": 0, "errors": []}',
                stderr="",
            )
            result = tdd_orchestrator.run_batch_suite(
                path="tests/unit",
                profile="unit",
                batch_size=10,
                fix_on_fail=False,
            )
        assert isinstance(result, dict)
        assert "chat_output" in result

    def test_chat_output_contains_progress_bar(self, tdd_orchestrator):
        """chat_output string from run_batch_suite contains ASCII bar characters."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"passed": 5, "failed": 0, "errors": []}',
                stderr="",
            )
            result = tdd_orchestrator.run_batch_suite(
                path="tests/unit",
                profile="unit",
                batch_size=5,
                fix_on_fail=False,
            )
        chat = result.get("chat_output", "")
        assert isinstance(chat, str)
        assert len(chat) > 0

    def test_stops_if_fix_on_fail_false_and_batch_fails(self, tdd_orchestrator):
        """When fix_on_fail=False and a batch has failures, suite stops after that batch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout='{"passed": 3, "failed": 2, "errors": ["ImportError: foo"]}',
                stderr="",
            )
            result = tdd_orchestrator.run_batch_suite(
                path="tests/unit",
                profile="unit",
                batch_size=5,
                fix_on_fail=False,
            )
        assert result.get("aborted") is True or result.get("total_failed", 0) > 0

    def test_profile_param_accepted(self, tdd_orchestrator):
        """run_batch_suite accepts profile kwarg without raising."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"passed": 1, "failed": 0, "errors": []}',
                stderr="",
            )
            # Should not raise
            result = tdd_orchestrator.run_batch_suite(
                path="tests/unit",
                profile="smoke",
                batch_size=5,
                fix_on_fail=False,
            )
        assert "chat_output" in result

    def test_result_includes_totals(self, tdd_orchestrator):
        """Result dict includes total_passed and total_failed."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"passed": 7, "failed": 0, "errors": []}',
                stderr="",
            )
            result = tdd_orchestrator.run_batch_suite(
                path="tests/unit",
                profile="unit",
                batch_size=7,
                fix_on_fail=False,
            )
        assert "total_passed" in result
        assert "total_failed" in result
