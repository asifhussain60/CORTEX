"""Phase 143 — Knowledge Guidance Decision Traceability (TDD tests).

Verifies that KnowledgeGuidanceEngine emits a DecisionTraceabilityLogger.log_decision()
call with RESOLUTION type for every guidance resolution.

CORE-008: TDD mandatory — RED  before GREEN
QW-006: Knowledge guidance auditability
AC-ID: AC-P143-KGT-001
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch, call
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = ROOT / "cortex" / "knowledge"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1 — DecisionTraceabilityLogger is wired into KnowledgeGuidanceEngine
# ════════════════════════════════════════════════════════════════════════════

class TestKnowledgeGuidanceDecisionLogger:
    """KnowledgeGuidanceEngine must have _decision_logger after phase-143 wiring."""

    def test_decision_logger_attribute_exists(self) -> None:
        """After init, KnowledgeGuidanceEngine must have a _decision_logger attribute."""
        from cortex.core.knowledge_guidance_engine import KnowledgeGuidanceEngine

        if not KNOWLEDGE_ROOT.exists():
            pytest.skip("Knowledge root not available in this environment")

        engine = KnowledgeGuidanceEngine(knowledge_root=KNOWLEDGE_ROOT)
        assert hasattr(engine, "_decision_logger"), (
            "KnowledgeGuidanceEngine must have _decision_logger attribute after phase-143 wiring"
        )

    def test_decision_logger_has_log_decision(self) -> None:
        """_decision_logger must expose log_decision() method."""
        from cortex.core.knowledge_guidance_engine import KnowledgeGuidanceEngine

        if not KNOWLEDGE_ROOT.exists():
            pytest.skip("Knowledge root not available in this environment")

        engine = KnowledgeGuidanceEngine(knowledge_root=KNOWLEDGE_ROOT)
        assert hasattr(engine._decision_logger, "log_decision"), (
            "_decision_logger must have log_decision() method"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2 — log_decision() is called on every guidance resolution
# ════════════════════════════════════════════════════════════════════════════

class TestKnowledgeGuidanceEmitsTrace:
    """get_guidance_for_module() must emit a decision trace every time it resolves."""

    @pytest.fixture
    def engine(self) -> Any:
        """Return a KnowledgeGuidanceEngine with a real knowledge root."""
        from cortex.core.knowledge_guidance_engine import KnowledgeGuidanceEngine

        if not KNOWLEDGE_ROOT.exists():
            pytest.skip("Knowledge root not available in this environment")
        return KnowledgeGuidanceEngine(knowledge_root=KNOWLEDGE_ROOT)

    def test_knowledge_guidance_emits_decision_trace(self, engine: Any) -> None:
        """get_guidance_for_module() must call _decision_logger.log_decision() once."""
        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            mock_logger.log_decision.assert_called_once()

    def test_decision_trace_contains_module_path(self, engine: Any) -> None:
        """Decision trace context must contain the module_path key."""
        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            call_kwargs = mock_logger.log_decision.call_args.kwargs
            if not call_kwargs:
                # Fall back to positional args inspection via call_args[1]
                call_kwargs = mock_logger.log_decision.call_args[1] or {}
            context = call_kwargs.get("context", {})
            assert "module_path" in context, (
                "Decision trace context must include 'module_path'"
            )
            assert context["module_path"] == "cortex.core.rollback_manager"

    def test_decision_trace_contains_domain(self, engine: Any) -> None:
        """Decision trace context must contain the domain key."""
        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            call_kwargs = mock_logger.log_decision.call_args.kwargs or {}
            context = call_kwargs.get("context", {})
            assert "domain" in context, (
                "Decision trace context must include 'domain'"
            )

    def test_decision_trace_contains_confidence(self, engine: Any) -> None:
        """Decision trace must include the resolved confidence score."""
        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            call_kwargs = mock_logger.log_decision.call_args.kwargs or {}
            assert "confidence" in call_kwargs, (
                "log_decision() must be called with 'confidence' kwarg"
            )
            confidence = call_kwargs["confidence"]
            assert 0.0 <= confidence <= 1.0, (
                f"confidence must be in [0, 1], got {confidence}"
            )

    def test_decision_trace_type_is_resolution(self, engine: Any) -> None:
        """Decision trace must use DecisionType.RESOLUTION."""
        from cortex.intelligence.explainability.decision_logger import DecisionType

        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            call_kwargs = mock_logger.log_decision.call_args.kwargs or {}
            assert call_kwargs.get("decision_type") == DecisionType.RESOLUTION, (
                "Decision trace must be of type DecisionType.RESOLUTION"
            )

    def test_decision_trace_outcome_is_approved(self, engine: Any) -> None:
        """Decision trace must use DecisionOutcome.APPROVED."""
        from cortex.intelligence.explainability.decision_logger import DecisionOutcome

        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            call_kwargs = mock_logger.log_decision.call_args.kwargs or {}
            assert call_kwargs.get("outcome") == DecisionOutcome.APPROVED, (
                "Decision outcome must be DecisionOutcome.APPROVED"
            )

    def test_cached_results_do_not_emit_duplicate_traces(self, engine: Any) -> None:
        """Cached guidance hits must NOT re-emit a decision trace (cache bypasses resolution)."""
        with patch.object(engine, "_decision_logger") as mock_logger:
            engine.get_guidance_for_module("cortex.core.rollback_manager")
            engine.get_guidance_for_module("cortex.core.rollback_manager")  # cache hit
            # Only the first call should trigger the logger
            assert mock_logger.log_decision.call_count == 1, (
                "Cached guidance must not emit duplicate decision traces"
            )
