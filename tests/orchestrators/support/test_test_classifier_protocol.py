"""
Phase 57-b RED — OrchestratorProtocolMixin compliance tests.

Covers GAP-57-02 (TestClassifierOrchestrator) and
       GAP-57-03 (ReviewOrchestrator).

AC-ID: AC-PHASE57-B-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import pytest

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


# ---------------------------------------------------------------------------
# GAP-57-02: TestClassifierOrchestrator
# ---------------------------------------------------------------------------


class TestTestClassifierProtocol:
    """Verify TestClassifierOrchestrator satisfies OrchestratorProtocolMixin."""

    def _make(self):
        from cortex.orchestrators.support.test_classifier_orchestrator import (  # noqa: PLC0415
            TestClassifierOrchestrator,
        )
        return TestClassifierOrchestrator()

    def test_test_classifier_inherits_protocol_mixin(self) -> None:
        """TestClassifierOrchestrator must be an instance of OrchestratorProtocolMixin."""
        inst = self._make()
        assert isinstance(inst, OrchestratorProtocolMixin), (
            "TestClassifierOrchestrator does not inherit OrchestratorProtocolMixin."
        )

    def test_test_classifier_get_name_returns_string(self) -> None:
        """get_name() must return a non-empty string."""
        inst = self._make()
        name = inst.get_name()
        assert isinstance(name, str) and len(name) > 0, (
            f"get_name() returned {name!r} — must be a non-empty string."
        )

    def test_test_classifier_health_check_returns_dict(self) -> None:
        """health_check() must return a dict with at least 'status' and 'orchestrator' keys."""
        inst = self._make()
        result = inst.health_check()
        assert isinstance(result, dict), f"health_check() must return dict, got {type(result)}"
        assert "status" in result, "health_check() dict missing 'status' key"
        assert "orchestrator" in result, "health_check() dict missing 'orchestrator' key"

    def test_test_classifier_classify_still_works(self) -> None:
        """Existing classify() behaviour must be unaffected by mixin addition."""
        inst = self._make()
        decision = inst.classify("cortex/orchestrators/support/health_orchestrator.py")
        assert decision is not None, "classify() returned None"
        assert hasattr(decision, "tier"), "TestDecision missing 'tier' attribute"


# ---------------------------------------------------------------------------
# GAP-57-03: ReviewOrchestrator
# ---------------------------------------------------------------------------


class TestReviewOrchestratorProtocol:
    """Verify ReviewOrchestrator satisfies OrchestratorProtocolMixin."""

    def _make(self):
        from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator  # noqa: PLC0415
        return ReviewOrchestrator()

    def test_review_orchestrator_inherits_protocol_mixin(self) -> None:
        """ReviewOrchestrator must be an instance of OrchestratorProtocolMixin."""
        inst = self._make()
        assert isinstance(inst, OrchestratorProtocolMixin), (
            "ReviewOrchestrator does not inherit OrchestratorProtocolMixin."
        )

    def test_review_orchestrator_get_name_returns_string(self) -> None:
        """get_name() must return a non-empty string."""
        inst = self._make()
        name = inst.get_name()
        assert isinstance(name, str) and len(name) > 0, (
            f"get_name() returned {name!r} — must be a non-empty string."
        )

    def test_review_orchestrator_health_check_via_mixin(self) -> None:
        """health_check() must return a dict with 'status' and 'orchestrator' keys."""
        inst = self._make()
        result = inst.health_check()
        assert isinstance(result, dict), f"health_check() must return dict, got {type(result)}"
        assert "status" in result, "health_check() dict missing 'status' key"
        assert "orchestrator" in result, "health_check() dict missing 'orchestrator' key"

    def test_review_orchestrator_execute_final_review_still_works(self) -> None:
        """execute_final_review() must continue to function after mixin addition."""
        inst = self._make()
        result = inst.execute_final_review(
            plan={"phases": [{"files": ["f.py"]}]},
            commits=["abc123"],
            complexity_level="SIMPLE",
        )
        assert isinstance(result, dict), "execute_final_review() must return dict"
        assert "ready_for_next_phase" in result, "result missing 'ready_for_next_phase'"
