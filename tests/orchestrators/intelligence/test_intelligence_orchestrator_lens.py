"""
Phase 57-c RED — LENS wiring tests for IntelligenceOrchestrator and domain tier.

GAP-57-04: IntelligenceOrchestrator must inherit OrchestratorProtocolMixin
           and expose analyze_with_context(request, lens_context=None).
GAP-57-05: Domain orchestrators must consume lens_context from orchestrator_context.

AC-ID: AC-PHASE57-C-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import pytest
from pathlib import Path

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


# ---------------------------------------------------------------------------
# GAP-57-04: IntelligenceOrchestrator
# ---------------------------------------------------------------------------


class TestIntelligenceOrchestratorLens:
    """Verify IntelligenceOrchestrator satisfies mixin and LENS contract."""

    def _make(self, tmp_path: Path):
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (  # noqa: PLC0415
            IntelligenceOrchestrator,
        )
        return IntelligenceOrchestrator(audit_db_path=tmp_path / "test_audit.db")

    def test_intelligence_orchestrator_inherits_protocol_mixin(self, tmp_path: Path) -> None:
        """IntelligenceOrchestrator must inherit OrchestratorProtocolMixin."""
        inst = self._make(tmp_path)
        assert isinstance(inst, OrchestratorProtocolMixin), (
            "IntelligenceOrchestrator does not inherit OrchestratorProtocolMixin."
        )

    def test_intelligence_orchestrator_accepts_lens_context(self, tmp_path: Path) -> None:
        """analyze_with_context() must accept optional lens_context kwarg without error."""
        inst = self._make(tmp_path)
        assert hasattr(inst, "analyze_with_context"), (
            "IntelligenceOrchestrator missing analyze_with_context() method."
        )
        result = inst.analyze_with_context("IMPLEMENT", lens_context=None)
        assert isinstance(result, dict), (
            f"analyze_with_context() must return dict, got {type(result)}"
        )

    def test_intelligence_orchestrator_enriches_result_with_lens(self, tmp_path: Path) -> None:
        """When lens_context provided, result must include lens_enriched key."""
        inst = self._make(tmp_path)
        fake_lens = {"git_analysis": {"commits": 5}, "ast_analysis": {}}
        result = inst.analyze_with_context("IMPLEMENT", lens_context=fake_lens)
        assert isinstance(result, dict), "analyze_with_context must return dict"
        # When lens_context is supplied, result should acknowledge it
        assert result.get("lens_enriched") is True or "lens_context" in result, (
            "Result does not indicate LENS enrichment when lens_context was provided."
        )


# ---------------------------------------------------------------------------
# GAP-57-05: Domain orchestrator LENS context consumption
# ---------------------------------------------------------------------------


class TestDomainLensConsumption:
    """Verify domain orchestrators extract and use lens_context."""

    def test_refactoring_orchestrator_consumes_lens_context(self) -> None:
        """RefactoringOrchestrator._extract_lens_context must exist and extract context."""
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator  # noqa: PLC0415
        inst = RefactoringOrchestrator()
        fake_ctx = {"lens_context": {"git_analysis": {}}}
        result = inst._extract_lens_context(fake_ctx)
        assert result is not None, "_extract_lens_context returned None for a valid context dict"
        assert "git_analysis" in result, (
            "_extract_lens_context must return the lens_context sub-dict"
        )

    def test_planning_orchestrator_consumes_lens_context(self) -> None:
        """PlanningOrchestrator._extract_lens_context must exist and extract context."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator  # noqa: PLC0415
        inst = PlanningOrchestrator()
        fake_ctx = {"lens_context": {"ast_analysis": {"classes": 3}}}
        result = inst._extract_lens_context(fake_ctx)
        assert result is not None
        assert "ast_analysis" in result
