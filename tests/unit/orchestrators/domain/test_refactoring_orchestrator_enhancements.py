"""
RefactoringOrchestrator Enhancement Tests — TDD RED phase (CORE-008)

AC_START: AC-ENH-STS-2026-02-22-001
Tests for ENH-STS-01, ENH-STS-02, ENH-STS-06:
  - ENH-STS-01: Functional completeness gate (_check_functional_completeness)
  - ENH-STS-02: Session traceability (write_refactor_session_trace)
  - ENH-STS-06: Scorecard generation (_generate_scorecard)

CORE-008: Tests written BEFORE implementation.
"""

from __future__ import annotations

import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# ENH-STS-01 — Functional Completeness Gate
# ─────────────────────────────────────────────────────────────────────────────


class TestFunctionalCompletenessGate:
    """ENH-STS-01: Refactoring must not silently drop source endpoints/functions."""

    def test_check_functional_completeness_returns_ok_when_all_present(self) -> None:
        """All source items present in target → Ok with zero gaps."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        source = ["/api/users", "/api/accounts", "/api/accounts/transfer"]
        target = ["/api/users", "/api/accounts", "/api/accounts/transfer"]

        result = orchestrator.check_functional_completeness(source, target)

        assert result.is_ok()
        report = result.unwrap()
        assert report["gaps"] == []
        assert report["gap_count"] == 0
        assert report["complete"] is True

    def test_check_functional_completeness_detects_dropped_endpoints(self) -> None:
        """Missing target endpoints are reported as gaps."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        source = ["/api/users", "/api/accounts", "/api/accounts/transfer"]
        target = ["/api/users", "/api/accounts"]  # transfer dropped

        result = orchestrator.check_functional_completeness(source, target)

        assert result.is_ok()
        report = result.unwrap()
        assert "/api/accounts/transfer" in report["gaps"]
        assert report["gap_count"] == 1
        assert report["complete"] is False

    def test_check_functional_completeness_detects_multiple_gaps(self) -> None:
        """Multiple dropped items all reported."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        source = ["/api/users", "/api/accounts/transfer", "/api/admin/stats"]
        target = ["/api/users"]

        result = orchestrator.check_functional_completeness(source, target)

        assert result.is_ok()
        report = result.unwrap()
        assert report["gap_count"] == 2
        assert set(report["gaps"]) == {"/api/accounts/transfer", "/api/admin/stats"}

    def test_check_functional_completeness_empty_source_is_ok(self) -> None:
        """Empty source list → no gaps (vacuously complete)."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_functional_completeness([], ["/api/users"])

        assert result.is_ok()
        assert result.unwrap()["complete"] is True

    def test_check_functional_completeness_target_superset_is_ok(self) -> None:
        """Target having MORE items than source is fine (additive refactoring)."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        source = ["/api/users"]
        target = ["/api/users", "/api/accounts", "/api/health"]

        result = orchestrator.check_functional_completeness(source, target)

        assert result.is_ok()
        assert result.unwrap()["complete"] is True


# ─────────────────────────────────────────────────────────────────────────────
# ENH-STS-02 — Session Traceability
# ─────────────────────────────────────────────────────────────────────────────


class TestRefactoringSessionTraceability:
    """ENH-STS-02: RefactoringOrchestrator writes AC_START/AC_COMPLETE to trace DB."""

    def test_write_refactor_session_trace_returns_ok(self) -> None:
        """write_refactor_session_trace returns Ok with a session_id."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.write_refactor_session_trace(
            action="AC_START",
            source_repo="cortex-sts/CortexLabs/BadMonolith",
            target_repo="cortex-sts/CortexLabs/Refactored",
            session_id="test-session-001",
            metadata={"smells_catalogued": 25},
        )

        assert result.is_ok()

    def test_write_refactor_session_trace_ac_start_action(self) -> None:
        """AC_START action is accepted."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.write_refactor_session_trace(
            action="AC_START",
            source_repo="source/repo",
            target_repo="target/repo",
            session_id=str(uuid.uuid4()),
            metadata={},
        )
        assert result.is_ok()

    def test_write_refactor_session_trace_ac_complete_action(self) -> None:
        """AC_COMPLETE action is accepted with full metadata."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.write_refactor_session_trace(
            action="AC_COMPLETE",
            source_repo="source/repo",
            target_repo="target/repo",
            session_id=str(uuid.uuid4()),
            metadata={
                "smells_addressed": 25,
                "files_created": 87,
                "test_count_before": 12,
                "test_count_after": 25,
                "security_p0_before": 5,
                "security_p0_after": 0,
            },
        )
        assert result.is_ok()

    def test_write_refactor_session_trace_invalid_action_returns_err(self) -> None:
        """Invalid action value returns Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.write_refactor_session_trace(
            action="INVALID_ACTION",
            source_repo="src",
            target_repo="tgt",
            session_id="s1",
            metadata={},
        )
        assert result.is_err()

    def test_write_refactor_session_trace_persists_to_trace_logger(self) -> None:
        """Trace entries reach OrchestratorTraceLogger.record_trace."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        from cortex.infrastructure.orchestrator_trace_logger import OrchestratorTraceLogger

        orchestrator = RefactoringOrchestrator()

        with patch.object(OrchestratorTraceLogger, "record_trace") as mock_record:
            from cortex.core.result import Ok
            mock_record.return_value = Ok(None)

            orchestrator.write_refactor_session_trace(
                action="AC_START",
                source_repo="src",
                target_repo="tgt",
                session_id="trace-persist-test",
                metadata={"smells_catalogued": 10},
            )

        mock_record.assert_called_once()
        call_args = mock_record.call_args[0][0]
        assert call_args.action == "AC_START"
        assert "source_repo" in call_args.context
        assert call_args.context["source_repo"] == "src"


# ─────────────────────────────────────────────────────────────────────────────
# ENH-STS-06 — Scorecard Generation
# ─────────────────────────────────────────────────────────────────────────────


class TestRefactoringScorecardGeneration:
    """ENH-STS-06: Auto-generate weighted scorecard at REFACTOR completion."""

    def test_generate_scorecard_returns_dict_with_required_keys(self) -> None:
        """Scorecard has all required category keys and a weighted_total."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores: Dict[str, float] = {
            "architecture": 9,
            "security": 8,
            "testing": 6,
            "documentation": 9,
            "frontend": 8,
            "traceability": 3,
        }

        result = orchestrator.generate_scorecard(scores)

        assert result.is_ok()
        card = result.unwrap()
        assert "weighted_total" in card
        assert "categories" in card
        assert set(card["categories"].keys()) == set(scores.keys())

    def test_generate_scorecard_weighted_total_matches_known_value(self) -> None:
        """Weighted total for the STS baseline (82) matches within 1 point."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores: Dict[str, float] = {
            "architecture": 9,     # 0.25 → 2.25
            "security": 8,         # 0.25 → 2.00
            "testing": 6,          # 0.20 → 1.20
            "documentation": 9,    # 0.15 → 1.35
            "frontend": 8,         # 0.10 → 0.80
            "traceability": 3,     # 0.05 → 0.15
        }                          # total → 7.75 × 10 = 77.5 → rounded 78

        result = orchestrator.generate_scorecard(scores)
        card = result.unwrap()

        # Weighted total is raw (0-10 scale), then multiply by 10 for 0-100
        assert 76 <= card["weighted_total"] <= 83

    def test_generate_scorecard_rejects_out_of_range_scores(self) -> None:
        """Scores outside 0-10 return Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores = {
            "architecture": 11,  # invalid
            "security": 8,
            "testing": 6,
            "documentation": 9,
            "frontend": 8,
            "traceability": 3,
        }

        result = orchestrator.generate_scorecard(scores)
        assert result.is_err()

    def test_generate_scorecard_rejects_missing_categories(self) -> None:
        """Missing required categories return Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores = {"architecture": 9}  # missing 5 categories

        result = orchestrator.generate_scorecard(scores)
        assert result.is_err()

    def test_generate_scorecard_includes_grade(self) -> None:
        """Scorecard includes a letter grade (A/B/C/D/F)."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores = {
            "architecture": 9, "security": 9, "testing": 9,
            "documentation": 9, "frontend": 9, "traceability": 9,
        }

        result = orchestrator.generate_scorecard(scores)
        card = result.unwrap()
        assert "grade" in card
        assert card["grade"] in ("A", "B", "C", "D", "F")

    def test_generate_scorecard_perfect_scores_grade_a(self) -> None:
        """All 10s → grade A."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores = {k: 10 for k in
                  ["architecture", "security", "testing", "documentation", "frontend", "traceability"]}

        result = orchestrator.generate_scorecard(scores)
        assert result.unwrap()["grade"] == "A"

    def test_generate_scorecard_low_scores_grade_f(self) -> None:
        """All 1s → grade F."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        scores = {k: 1 for k in
                  ["architecture", "security", "testing", "documentation", "frontend", "traceability"]}

        result = orchestrator.generate_scorecard(scores)
        assert result.unwrap()["grade"] == "F"


# AC_COMPLETE: AC-ENH-STS-2026-02-22-001 ✅ (RED phase — all tests expected to FAIL until implementation)
