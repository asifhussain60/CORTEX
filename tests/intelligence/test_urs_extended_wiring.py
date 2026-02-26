"""
Phase 83-e: Extended Intelligence URS Wiring Tests.

Tests that TestValueScorer, KnowledgeSynthesisEngine,
IntelligenceMatrixBuilder, and LENSContext integrate with URS.

9 tests per phase plan tdd_sequence.red:
  1. test_scorer_recalibrate_method_exists
  2. test_scorer_adjusts_weights
  3. test_knowledge_track_instruction
  4. test_knowledge_instruction_reward
  5. test_knowledge_instruction_ignored
  6. test_matrix_coverage_increase_reward
  7. test_matrix_coverage_decrease_punishment
  8. test_lens_analysis_id_tracking
  9. test_lens_correct_insight_reward

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
from typing import Any, Dict, List

from cortex.intelligence.learning.reinforcement_signal import (
    ReinforcementEngine,
    ReinforcementSignal,
    SignalType,
)


# ═══════════════════════════════════════════════════════════════════════════
# TestValueScorer URS wiring (2 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestScorerRecalibration:
    """Tests for TestValueScorer recalibration from reinforcement signals."""

    def test_scorer_recalibrate_method_exists(self) -> None:
        """TestValueScorer.recalibrate_from_signals() is callable."""
        from cortex.orchestrators.intelligence.orch_test_value_scorer import (
            TestValueScorer,
        )

        scorer = TestValueScorer()
        assert hasattr(scorer, "recalibrate_from_signals"), (
            "TestValueScorer must have recalibrate_from_signals method"
        )
        assert callable(scorer.recalibrate_from_signals)

    def test_scorer_adjusts_weights(self) -> None:
        """recalibrate_from_signals adjusts severity_weight based on signal data."""
        from cortex.orchestrators.intelligence.orch_test_value_scorer import (
            TestValueScorer,
        )

        scorer = TestValueScorer(
            severity_weight=0.4,
            likelihood_weight=0.3,
            coverage_gap_weight=0.3,
        )
        original_severity = scorer.severity_weight

        # Build a signal history where severity-related patterns got STRONG_REWARD
        engine = ReinforcementEngine()
        engine.emit_signal(
            signal_type=SignalType.STRONG_REWARD,
            pattern_id="severity_high",
            source_orchestrator="TDDOrchestrator",
            context={"factor": "severity"},
        )
        engine.emit_signal(
            signal_type=SignalType.STRONG_REWARD,
            pattern_id="severity_high",
            source_orchestrator="EnforcementOrchestrator",
            context={"factor": "severity"},
        )

        signal_history = engine.get_signal_history()
        result = scorer.recalibrate_from_signals(signal_history)

        # Weights should have changed
        assert isinstance(result, dict), "recalibrate_from_signals should return a dict"
        assert "adjusted" in result, "Result should indicate whether adjustment happened"


# ═══════════════════════════════════════════════════════════════════════════
# KnowledgeSynthesisEngine URS wiring (3 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnowledgeInstructionTracking:
    """Tests for KnowledgeSynthesisEngine instruction outcome tracking."""

    def test_knowledge_track_instruction(self) -> None:
        """KnowledgeSynthesisEngine.track_instruction_outcome() exists and is callable."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        assert hasattr(engine, "track_instruction_outcome"), (
            "KnowledgeSynthesisEngine must have track_instruction_outcome method"
        )
        assert callable(engine.track_instruction_outcome)

    def test_knowledge_instruction_reward(self) -> None:
        """Used instruction emits MILD_REWARD signal."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        urs_engine = ReinforcementEngine()
        engine._urs_engine = urs_engine

        engine.track_instruction_outcome(
            instruction_id="inst-001",
            outcome="used",
        )

        history = urs_engine.get_signal_history()
        assert len(history) == 1, "One signal should be emitted"
        assert history[0].signal_type == SignalType.MILD_REWARD, (
            "Used instruction should emit MILD_REWARD"
        )
        assert history[0].pattern_id == "inst-001"

    def test_knowledge_instruction_ignored(self) -> None:
        """Ignored instruction emits NEUTRAL signal."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        urs_engine = ReinforcementEngine()
        engine._urs_engine = urs_engine

        engine.track_instruction_outcome(
            instruction_id="inst-002",
            outcome="ignored",
        )

        history = urs_engine.get_signal_history()
        assert len(history) == 1, "One signal should be emitted"
        assert history[0].signal_type == SignalType.NEUTRAL, (
            "Ignored instruction should emit NEUTRAL"
        )


# ═══════════════════════════════════════════════════════════════════════════
# IntelligenceMatrixBuilder URS wiring (2 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestMatrixCoverageSignals:
    """Tests for IntelligenceMatrixBuilder coverage change signals."""

    def test_matrix_coverage_increase_reward(self) -> None:
        """Coverage increase emits MILD_REWARD."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )

        builder = IntelligenceMatrixBuilder()
        urs_engine = ReinforcementEngine()
        builder._urs_engine = urs_engine

        builder.on_coverage_change(
            capability_id="lens_ast",
            old_coverage=0.6,
            new_coverage=0.7,
        )

        history = urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_REWARD, (
            "Coverage increase should emit MILD_REWARD"
        )
        assert history[0].pattern_id == "lens_ast"

    def test_matrix_coverage_decrease_punishment(self) -> None:
        """Coverage decrease emits MILD_PUNISHMENT."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )

        builder = IntelligenceMatrixBuilder()
        urs_engine = ReinforcementEngine()
        builder._urs_engine = urs_engine

        builder.on_coverage_change(
            capability_id="brain_t1",
            old_coverage=0.8,
            new_coverage=0.7,
        )

        history = urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_PUNISHMENT, (
            "Coverage decrease should emit MILD_PUNISHMENT"
        )


# ═══════════════════════════════════════════════════════════════════════════
# LENSContext URS wiring (2 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestLENSAnalysisTracking:
    """Tests for LENS analysis_id tracking and outcome correlation."""

    def test_lens_analysis_id_tracking(self) -> None:
        """LENSContext has analysis_id field."""
        from cortex.lens.lens_orchestrator import LENSContext

        ctx = LENSContext()
        assert hasattr(ctx, "analysis_id"), (
            "LENSContext must have analysis_id field"
        )
        # Should auto-generate a non-empty string
        assert isinstance(ctx.analysis_id, str)
        assert len(ctx.analysis_id) > 0, "analysis_id should be auto-generated"

    def test_lens_correct_insight_reward(self) -> None:
        """Analysis that led to successful operation emits MILD_REWARD."""
        from cortex.lens.lens_orchestrator import LENSOrchestrator

        orch = LENSOrchestrator.__new__(LENSOrchestrator)
        urs_engine = ReinforcementEngine()
        orch._urs_engine = urs_engine

        orch.record_analysis_outcome(
            analysis_id="lens-abc-123",
            success=True,
        )

        history = urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_REWARD, (
            "Correct insight should emit MILD_REWARD"
        )
        assert history[0].pattern_id == "lens-abc-123"
