"""
Tests for Unified Reinforcement Signal (URS) — Phase 83 Sub-Phase A.

Authority: phase-83-unified-reinforcement-signal.yaml GAP-83-01, GAP-83-02
AC-ID: AC-83-URS-20260226

RED Phase: All tests must FAIL before implementation begins.

Test Coverage:
- ReinforcementSignal dataclass + SignalType enum (GAP-83-01)
- ReinforcementEngine emit/apply/history (GAP-83-01)
- UniversalLearningLoop.reinforcement_signal() method (GAP-83-01)
- EffectivenessAnalyzer decay/promote/quarantine (GAP-83-02)
- Cross-cutting boost for multi-orchestrator validation

CORE Rules:
- CORE-008: TDD mandatory (tests BEFORE implementation) ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import patch


# ─────────────────────────────────────────────────────────────────────────────
# 1. ReinforcementSignal Dataclass + SignalType Enum
# ─────────────────────────────────────────────────────────────────────────────


class TestReinforcementSignalDataclass:
    """GAP-83-01: ReinforcementSignal dataclass with all required fields."""

    def test_signal_type_enum_has_five_values(self) -> None:
        """SignalType enum must have exactly 5 values."""
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        values = list(SignalType)
        assert len(values) == 5, f"Expected 5 SignalType values, got {len(values)}"
        names = {v.name for v in values}
        assert names == {
            "STRONG_REWARD",
            "MILD_REWARD",
            "NEUTRAL",
            "MILD_PUNISHMENT",
            "STRONG_PUNISHMENT",
        }

    def test_signal_type_scores(self) -> None:
        """Each SignalType must map to its canonical score."""
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        assert SignalType.STRONG_REWARD.score == 1.0
        assert SignalType.MILD_REWARD.score == 0.5
        assert SignalType.NEUTRAL.score == 0.0
        assert SignalType.MILD_PUNISHMENT.score == -0.5
        assert SignalType.STRONG_PUNISHMENT.score == -1.0

    def test_reinforcement_signal_dataclass_fields(self) -> None:
        """ReinforcementSignal must have all required fields."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementSignal,
            SignalType,
        )

        signal = ReinforcementSignal(
            signal_type=SignalType.STRONG_REWARD,
            pattern_id="test-pattern-001",
            source_orchestrator="TDDOrchestrator",
            context={"operation": "tdd_cycle"},
        )

        assert signal.signal_type == SignalType.STRONG_REWARD
        assert signal.pattern_id == "test-pattern-001"
        assert signal.source_orchestrator == "TDDOrchestrator"
        assert signal.context == {"operation": "tdd_cycle"}
        assert isinstance(signal.timestamp, datetime)
        assert isinstance(signal.signal_id, str)
        assert len(signal.signal_id) > 0

    def test_reinforcement_signal_to_dict(self) -> None:
        """ReinforcementSignal.to_dict() must produce serializable dict."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementSignal,
            SignalType,
        )

        signal = ReinforcementSignal(
            signal_type=SignalType.MILD_PUNISHMENT,
            pattern_id="bad-pattern",
            source_orchestrator="EnforcementOrchestrator",
        )
        d = signal.to_dict()

        assert d["signal_type"] == "MILD_PUNISHMENT"
        assert d["pattern_id"] == "bad-pattern"
        assert d["source_orchestrator"] == "EnforcementOrchestrator"
        assert d["score"] == -0.5
        assert "timestamp" in d
        assert "signal_id" in d


# ─────────────────────────────────────────────────────────────────────────────
# 2. ReinforcementEngine — emit, apply, history
# ─────────────────────────────────────────────────────────────────────────────


class TestReinforcementEngine:
    """GAP-83-01: ReinforcementEngine emit_signal, apply_to_learning, history."""

    def test_emit_signal_stores_and_returns_id(self) -> None:
        """emit_signal() must store signal and return signal_id."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )

        engine = ReinforcementEngine()
        signal_id = engine.emit_signal(
            signal_type=SignalType.STRONG_REWARD,
            pattern_id="pattern-abc",
            source_orchestrator="TrainerOrchestrator",
        )

        assert isinstance(signal_id, str)
        assert len(signal_id) > 0

    def test_emit_signal_increments_history(self) -> None:
        """Each emit_signal() call must add to signal history."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )

        engine = ReinforcementEngine()
        engine.emit_signal(SignalType.STRONG_REWARD, "p1", "Orch1")
        engine.emit_signal(SignalType.MILD_PUNISHMENT, "p2", "Orch2")

        history = engine.get_signal_history()
        assert len(history) == 2

    def test_get_signal_history_filterable_by_pattern(self) -> None:
        """get_signal_history(pattern_id=X) must filter by pattern."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )

        engine = ReinforcementEngine()
        engine.emit_signal(SignalType.STRONG_REWARD, "p1", "Orch1")
        engine.emit_signal(SignalType.MILD_PUNISHMENT, "p2", "Orch2")
        engine.emit_signal(SignalType.MILD_REWARD, "p1", "Orch3")

        p1_history = engine.get_signal_history(pattern_id="p1")
        assert len(p1_history) == 2
        assert all(s.pattern_id == "p1" for s in p1_history)

    def test_apply_to_learning_updates_confidence(self) -> None:
        """apply_to_learning() must update confidence on cached learning patterns."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )
        from cortex.intelligence.learning.universal_learning_loop import (
            LearningCapture,
            PatternType,
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)
        capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="test pattern",
            pattern_data={"id": "p-apply-test"},
            confidence=0.5,
        )
        loop.capture_pattern(capture)

        engine = ReinforcementEngine()
        engine.apply_to_learning(
            learning_loop=loop,
            pattern_id="p-apply-test",
            signal_type=SignalType.STRONG_REWARD,
        )

        # Find the pattern in cache and verify confidence increased
        found = False
        for captures in loop._learning_cache.values():
            for c in captures:
                if c.pattern_data.get("id") == "p-apply-test":
                    assert c.confidence > 0.5, (
                        f"Confidence should have increased from 0.5, got {c.confidence}"
                    )
                    found = True
        assert found, "Pattern 'p-apply-test' not found in learning cache"

    def test_strong_reward_increases_confidence(self) -> None:
        """STRONG_REWARD (+1.0) must increase confidence proportionally."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )
        from cortex.intelligence.learning.universal_learning_loop import (
            LearningCapture,
            PatternType,
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)
        capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="reward test",
            pattern_data={"id": "reward-test"},
            confidence=0.6,
        )
        loop.capture_pattern(capture)

        engine = ReinforcementEngine()
        engine.apply_to_learning(loop, "reward-test", SignalType.STRONG_REWARD)

        for captures in loop._learning_cache.values():
            for c in captures:
                if c.pattern_data.get("id") == "reward-test":
                    assert c.confidence > 0.6

    def test_strong_punishment_decreases_confidence(self) -> None:
        """STRONG_PUNISHMENT (-1.0) must decrease confidence proportionally."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )
        from cortex.intelligence.learning.universal_learning_loop import (
            LearningCapture,
            PatternType,
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)
        capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="punish test",
            pattern_data={"id": "punish-test"},
            confidence=0.6,
        )
        loop.capture_pattern(capture)

        engine = ReinforcementEngine()
        engine.apply_to_learning(loop, "punish-test", SignalType.STRONG_PUNISHMENT)

        for captures in loop._learning_cache.values():
            for c in captures:
                if c.pattern_data.get("id") == "punish-test":
                    assert c.confidence < 0.6

    def test_confidence_clamped_0_to_1(self) -> None:
        """Confidence must never go below 0.0 or above 1.0."""
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )
        from cortex.intelligence.learning.universal_learning_loop import (
            LearningCapture,
            PatternType,
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)

        # Pattern near ceiling
        high_capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="high",
            pattern_data={"id": "clamp-high"},
            confidence=0.95,
        )
        loop.capture_pattern(high_capture)

        # Pattern near floor
        low_capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="low",
            pattern_data={"id": "clamp-low"},
            confidence=0.05,
        )
        loop.capture_pattern(low_capture)

        engine = ReinforcementEngine()

        # Reward the high one — should clamp at 1.0
        engine.apply_to_learning(loop, "clamp-high", SignalType.STRONG_REWARD)
        # Punish the low one — should clamp at 0.0
        engine.apply_to_learning(loop, "clamp-low", SignalType.STRONG_PUNISHMENT)

        for captures in loop._learning_cache.values():
            for c in captures:
                if c.pattern_data.get("id") == "clamp-high":
                    assert c.confidence <= 1.0
                if c.pattern_data.get("id") == "clamp-low":
                    assert c.confidence >= 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 3. UniversalLearningLoop.reinforcement_signal() integration
# ─────────────────────────────────────────────────────────────────────────────


class TestLearningLoopReinforcementIntegration:
    """GAP-83-01: UniversalLearningLoop.reinforcement_signal() method."""

    def test_learning_loop_has_reinforcement_signal_method(self) -> None:
        """UniversalLearningLoop must expose reinforcement_signal()."""
        from cortex.intelligence.learning.universal_learning_loop import (
            UniversalLearningLoop,
        )

        loop = UniversalLearningLoop(enable_logging=False)
        assert hasattr(loop, "reinforcement_signal")
        assert callable(loop.reinforcement_signal)

    def test_reinforcement_signal_delegates_to_engine(self) -> None:
        """reinforcement_signal() must delegate to ReinforcementEngine."""
        from cortex.intelligence.learning.universal_learning_loop import (
            LearningCapture,
            PatternType,
            UniversalLearningLoop,
        )
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        loop = UniversalLearningLoop(enable_logging=False)
        capture = LearningCapture(
            orchestrator="TestOrch",
            operation="test",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="delegate test",
            pattern_data={"id": "delegate-test"},
            confidence=0.5,
        )
        loop.capture_pattern(capture)

        signal_id = loop.reinforcement_signal(
            pattern_id="delegate-test",
            signal_type=SignalType.MILD_REWARD,
            source_orchestrator="TestOrch",
        )

        assert isinstance(signal_id, str)
        assert len(signal_id) > 0

    def test_reinforcement_history_accessible_from_loop(self) -> None:
        """get_reinforcement_history() must return signal history."""
        from cortex.intelligence.learning.universal_learning_loop import (
            UniversalLearningLoop,
        )
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        loop = UniversalLearningLoop(enable_logging=False)
        loop.reinforcement_signal("p1", SignalType.STRONG_REWARD, "Orch1")

        history = loop.get_reinforcement_history()
        assert len(history) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 4. EffectivenessAnalyzer — decay, promote, quarantine
# ─────────────────────────────────────────────────────────────────────────────


class TestEffectivenessAnalyzerDecayPromote:
    """GAP-83-02: EffectivenessAnalyzer decay/promote/quarantine methods."""

    def test_decay_stale_patterns(self) -> None:
        """decay_stale_patterns() must reduce confidence of idle patterns."""
        from cortex.intelligence.learning.effectiveness_analyzer import (
            EffectivenessAnalyzer,
            PatternApplication,
        )

        analyzer = EffectivenessAnalyzer()

        # Record an old application (40 days ago)
        old_app = PatternApplication(
            pattern_id="stale-pattern",
            orchestrator="TestOrch",
            timestamp=datetime.now() - timedelta(days=40),
            success=True,
            time_taken_seconds=1.0,
            quality_before=0.5,
            quality_after=0.7,
        )
        analyzer.record_application(old_app)

        decayed = analyzer.decay_stale_patterns(max_age_days=30, decay_amount=0.1)
        assert "stale-pattern" in decayed

    def test_decay_does_not_affect_recent_patterns(self) -> None:
        """decay_stale_patterns() must NOT touch recently-used patterns."""
        from cortex.intelligence.learning.effectiveness_analyzer import (
            EffectivenessAnalyzer,
            PatternApplication,
        )

        analyzer = EffectivenessAnalyzer()

        recent_app = PatternApplication(
            pattern_id="fresh-pattern",
            orchestrator="TestOrch",
            timestamp=datetime.now() - timedelta(days=5),
            success=True,
            time_taken_seconds=1.0,
            quality_before=0.5,
            quality_after=0.7,
        )
        analyzer.record_application(recent_app)

        decayed = analyzer.decay_stale_patterns(max_age_days=30, decay_amount=0.1)
        assert "fresh-pattern" not in decayed

    def test_promote_high_confidence(self) -> None:
        """promote_high_confidence() must flag patterns above threshold with sufficient applications."""
        from cortex.intelligence.learning.effectiveness_analyzer import (
            EffectivenessAnalyzer,
            PatternApplication,
        )

        analyzer = EffectivenessAnalyzer()

        # Record 4 successful applications (above min_apps=3)
        for i in range(4):
            app = PatternApplication(
                pattern_id="high-conf-pattern",
                orchestrator="TestOrch",
                timestamp=datetime.now() - timedelta(hours=i),
                success=True,
                time_taken_seconds=1.0,
                quality_before=0.5,
                quality_after=0.9,
            )
            analyzer.record_application(app)

        promoted = analyzer.promote_high_confidence(threshold=0.9, min_apps=3)
        assert "high-conf-pattern" in promoted

    def test_quarantine_low_confidence(self) -> None:
        """quarantine_low_confidence() must flag patterns below threshold with punishment history."""
        from cortex.intelligence.learning.effectiveness_analyzer import (
            EffectivenessAnalyzer,
            PatternApplication,
        )

        analyzer = EffectivenessAnalyzer()

        # Record 3 failed applications
        for i in range(3):
            app = PatternApplication(
                pattern_id="bad-pattern",
                orchestrator="TestOrch",
                timestamp=datetime.now() - timedelta(hours=i),
                success=False,
                time_taken_seconds=5.0,
                quality_before=0.5,
                quality_after=0.3,
            )
            analyzer.record_application(app)

        quarantined = analyzer.quarantine_low_confidence(
            threshold=0.3, min_punishments=2
        )
        assert "bad-pattern" in quarantined

    def test_cross_cutting_boost(self) -> None:
        """Patterns validated across 3+ orchestrators must get confidence boost."""
        from cortex.intelligence.learning.effectiveness_analyzer import (
            EffectivenessAnalyzer,
            PatternApplication,
        )

        analyzer = EffectivenessAnalyzer()

        # Record from 3 different orchestrators
        for orch in ["Orch1", "Orch2", "Orch3"]:
            app = PatternApplication(
                pattern_id="cross-cutting-pattern",
                orchestrator=orch,
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=1.0,
                quality_before=0.5,
                quality_after=0.7,
            )
            analyzer.record_application(app)

        boosted = analyzer.get_cross_cutting_boost(
            pattern_id="cross-cutting-pattern", min_orchestrators=3, boost=0.15
        )
        assert boosted is True


# ─────────────────────────────────────────────────────────────────────────────
# 5. Module exports
# ─────────────────────────────────────────────────────────────────────────────


class TestModuleExports:
    """Verify reinforcement_signal module is importable from cortex.intelligence.learning."""

    def test_reinforcement_signal_importable(self) -> None:
        """ReinforcementSignal importable from cortex.intelligence.learning."""
        from cortex.intelligence.learning import ReinforcementSignal

        assert ReinforcementSignal is not None

    def test_reinforcement_engine_importable(self) -> None:
        """ReinforcementEngine importable from cortex.intelligence.learning."""
        from cortex.intelligence.learning import ReinforcementEngine

        assert ReinforcementEngine is not None

    def test_signal_type_importable(self) -> None:
        """SignalType importable from cortex.intelligence.learning."""
        from cortex.intelligence.learning import SignalType

        assert SignalType is not None
