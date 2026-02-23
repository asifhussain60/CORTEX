"""
Phase 57-b RED — ReviewOrchestrator protocol compliance test (standalone).

GAP-57-03: ReviewOrchestrator bare class must inherit OrchestratorProtocolMixin.

AC-ID: AC-PHASE57-B-002
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import pytest

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class TestReviewOrchestratorProtocolCompliance:
    """Standalone protocol compliance suite for ReviewOrchestrator (GAP-57-03)."""

    def _make(self):
        from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator  # noqa: PLC0415
        return ReviewOrchestrator()

    def test_review_orchestrator_inherits_protocol_mixin(self) -> None:
        """ReviewOrchestrator must inherit OrchestratorProtocolMixin."""
        inst = self._make()
        assert isinstance(inst, OrchestratorProtocolMixin)

    def test_review_orchestrator_get_name_returns_string(self) -> None:
        """get_name() must return a non-empty str."""
        name = self._make().get_name()
        assert isinstance(name, str) and len(name) > 0

    def test_review_orchestrator_health_check_via_mixin(self) -> None:
        """health_check() must return {status, orchestrator} dict."""
        result = self._make().health_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert "orchestrator" in result
