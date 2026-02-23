"""
Phase 57-c RED — Domain tier LENS context consumption tests.

GAP-57-05: RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
           DashboardOrchestrator must all extract lens_context from
           orchestrator_context kwarg.

AC-ID: AC-PHASE57-C-002
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import pytest


FAKE_LENS_CTX = {"git_analysis": {"commits": 10}, "ast_analysis": {"classes": 2}}
FAKE_ORCH_CTX = {"lens_context": FAKE_LENS_CTX, "intent": "IMPLEMENT"}


class TestDomainLensConsumptionFull:
    """All four domain orchestrators must expose _extract_lens_context."""

    def _assert_extraction(self, orchestrator_instance: object, ctx: dict) -> None:
        assert hasattr(orchestrator_instance, "_extract_lens_context"), (
            f"{type(orchestrator_instance).__name__} is missing _extract_lens_context()"
        )
        result = orchestrator_instance._extract_lens_context(ctx)  # type: ignore[attr-defined]
        assert result is not None, "_extract_lens_context returned None"
        assert "git_analysis" in result, (
            "_extract_lens_context must return the inner lens_context sub-dict"
        )

    def test_refactoring_orchestrator_consumes_lens_context(self) -> None:
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator  # noqa: PLC0415
        self._assert_extraction(RefactoringOrchestrator(), FAKE_ORCH_CTX)

    def test_planning_orchestrator_consumes_lens_context(self) -> None:
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator  # noqa: PLC0415
        self._assert_extraction(PlanningOrchestrator(), FAKE_ORCH_CTX)

    def test_domain_orchestrator_consumes_lens_context(self) -> None:
        from cortex.orchestrators.domain.domain_orchestrator import DomainOrchestrator  # noqa: PLC0415
        self._assert_extraction(DomainOrchestrator(), FAKE_ORCH_CTX)

    def test_none_context_returns_none_gracefully(self) -> None:
        """Passing None must not raise — graceful degradation."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator  # noqa: PLC0415
        inst = PlanningOrchestrator()
        result = inst._extract_lens_context(None)  # type: ignore[arg-type]
        assert result is None, "None context should return None gracefully"

    def test_missing_lens_key_returns_none(self) -> None:
        """Context without 'lens_context' key must return None."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator  # noqa: PLC0415
        inst = PlanningOrchestrator()
        result = inst._extract_lens_context({"intent": "IMPLEMENT"})
        assert result is None, "Context without lens_context key should return None"
