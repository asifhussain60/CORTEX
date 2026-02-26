"""
Phase 83-d: URS Orchestrator Wiring Tests.

Tests that OPJMixin, TDDOrchestrator, and EnforcementOrchestrator
emit reinforcement signals on record/cycle/validation events.

10 tests per phase plan tdd_sequence.red:
  1. test_opj_mixin_emits_signal_on_record
  2. test_opj_success_maps_to_reward
  3. test_opj_failure_maps_to_punishment
  4. test_tdd_green_first_try_strong_reward
  5. test_tdd_green_with_retries_mild_reward
  6. test_tdd_cycle_failure_mild_punishment
  7. test_enforcement_zero_violations_reward
  8. test_enforcement_p2_only_mild_reward
  9. test_enforcement_p0_present_punishment
  10. test_signal_emission_resilient

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from cortex.intelligence.learning.opj_mixin import OPJMixin
from cortex.intelligence.learning.reinforcement_signal import (
    ReinforcementEngine,
    SignalType,
)


# ── Test Helper: Concrete OPJMixin subclass ────────────────────────────────

class _TestOrchestrator(OPJMixin):
    """Minimal concrete subclass to test OPJMixin signal emission."""

    def __init__(self, tmp_path: Path) -> None:
        self.name = "TestOrchestrator"
        self._opj_init(registry_root=tmp_path)


# ═══════════════════════════════════════════════════════════════════════════
# OPJMixin URS wiring (3 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestOPJMixinURS:
    """Tests for OPJMixin emitting reinforcement signals."""

    def test_opj_mixin_emits_signal_on_record(self, tmp_path: Path) -> None:
        """OPJMixin._opj_record_success/failure emits reinforcement signal."""
        orch = _TestOrchestrator(tmp_path)

        # After _opj_record_success, engine should have a signal
        orch._opj_record_success(
            operation="test_op",
            context={"key": "value"},
            resolution="worked",
            confidence=0.8,
        )

        # The mixin should have created a reinforcement engine and emitted
        assert hasattr(orch, "_urs_engine"), (
            "OPJMixin should lazy-init _urs_engine on record"
        )
        engine: ReinforcementEngine = orch._urs_engine
        history = engine.get_signal_history()
        assert len(history) >= 1, "At least one signal should be emitted on record_success"

    def test_opj_success_maps_to_reward(self, tmp_path: Path) -> None:
        """OPJ success=True maps to MILD_REWARD signal."""
        orch = _TestOrchestrator(tmp_path)

        orch._opj_record_success(
            operation="compile",
            context={},
            resolution="compiled cleanly",
            confidence=0.9,
        )

        engine: ReinforcementEngine = orch._urs_engine
        history = engine.get_signal_history()
        assert len(history) == 1
        signal = history[0]
        assert signal.signal_type == SignalType.MILD_REWARD, (
            f"OPJ success should map to MILD_REWARD, got {signal.signal_type}"
        )
        assert signal.source_orchestrator == "TestOrchestrator"
        assert signal.pattern_id == "compile"

    def test_opj_failure_maps_to_punishment(self, tmp_path: Path) -> None:
        """OPJ failure maps to MILD_PUNISHMENT signal."""
        orch = _TestOrchestrator(tmp_path)

        orch._opj_record_failure(
            operation="deploy",
            error="timeout",
            attempted_fix="retry",
            confidence=0.7,
        )

        engine: ReinforcementEngine = orch._urs_engine
        history = engine.get_signal_history()
        assert len(history) == 1
        signal = history[0]
        assert signal.signal_type == SignalType.MILD_PUNISHMENT, (
            f"OPJ failure should map to MILD_PUNISHMENT, got {signal.signal_type}"
        )
        assert signal.source_orchestrator == "TestOrchestrator"
        assert signal.pattern_id == "deploy"


# ═══════════════════════════════════════════════════════════════════════════
# TDDOrchestrator URS wiring (3 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestTDDOrchestratorURS:
    """Tests for TDDOrchestrator emitting reinforcement signals on TDD cycles."""

    def test_tdd_green_first_try_strong_reward(self) -> None:
        """TDD GREEN on first attempt emits STRONG_REWARD."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

        orch = TDDOrchestrator.__new__(TDDOrchestrator)
        # Minimal init for URS — engine only
        orch._urs_engine = ReinforcementEngine()
        orch.name = "TDDOrchestrator"

        # Simulate: emit TDD cycle signal — green on first try
        orch._emit_tdd_cycle_signal(
            operation="tdd_execute",
            success=True,
            retries=0,
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.STRONG_REWARD, (
            "GREEN on first try should emit STRONG_REWARD"
        )
        assert history[0].source_orchestrator == "TDDOrchestrator"

    def test_tdd_green_with_retries_mild_reward(self) -> None:
        """TDD GREEN after retries emits MILD_REWARD."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

        orch = TDDOrchestrator.__new__(TDDOrchestrator)
        orch._urs_engine = ReinforcementEngine()
        orch.name = "TDDOrchestrator"

        orch._emit_tdd_cycle_signal(
            operation="tdd_execute",
            success=True,
            retries=3,
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_REWARD, (
            "GREEN with retries should emit MILD_REWARD"
        )

    def test_tdd_cycle_failure_mild_punishment(self) -> None:
        """TDD cycle failure emits MILD_PUNISHMENT."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

        orch = TDDOrchestrator.__new__(TDDOrchestrator)
        orch._urs_engine = ReinforcementEngine()
        orch.name = "TDDOrchestrator"

        orch._emit_tdd_cycle_signal(
            operation="tdd_execute",
            success=False,
            retries=5,
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_PUNISHMENT, (
            "TDD failure should emit MILD_PUNISHMENT"
        )


# ═══════════════════════════════════════════════════════════════════════════
# EnforcementOrchestrator URS wiring (3 tests)
# ═══════════════════════════════════════════════════════════════════════════


class TestEnforcementOrchestratorURS:
    """Tests for EnforcementOrchestrator emitting signals on validation."""

    def test_enforcement_zero_violations_reward(self) -> None:
        """Zero violations emits STRONG_REWARD."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )

        orch = EnforcementOrchestrator.__new__(EnforcementOrchestrator)
        orch._urs_engine = ReinforcementEngine()
        orch.name = "EnforcementOrchestrator"

        orch._emit_enforcement_signal(
            operation="validate_operation",
            violations=[],
            warnings=[],
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.STRONG_REWARD, (
            "Zero violations should emit STRONG_REWARD"
        )
        assert history[0].source_orchestrator == "EnforcementOrchestrator"

    def test_enforcement_p2_only_mild_reward(self) -> None:
        """P2-only warnings (no violations) emits MILD_REWARD."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )

        orch = EnforcementOrchestrator.__new__(EnforcementOrchestrator)
        orch._urs_engine = ReinforcementEngine()
        orch.name = "EnforcementOrchestrator"

        orch._emit_enforcement_signal(
            operation="validate_operation",
            violations=[],
            warnings=["P2: Minor style issue"],
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_REWARD, (
            "P2-only warnings (no violations) should emit MILD_REWARD"
        )

    def test_enforcement_p0_present_punishment(self) -> None:
        """P0 violation present emits MILD_PUNISHMENT."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )

        orch = EnforcementOrchestrator.__new__(EnforcementOrchestrator)
        orch._urs_engine = ReinforcementEngine()
        orch.name = "EnforcementOrchestrator"

        orch._emit_enforcement_signal(
            operation="validate_operation",
            violations=["CORE-008 violation: no test file"],
            warnings=[],
        )

        history = orch._urs_engine.get_signal_history()
        assert len(history) == 1
        assert history[0].signal_type == SignalType.MILD_PUNISHMENT, (
            "P0/P1 violations should emit MILD_PUNISHMENT"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Resilience (1 test)
# ═══════════════════════════════════════════════════════════════════════════


class TestSignalEmissionResilience:
    """Tests that signal emission errors don't break orchestrator flow."""

    def test_signal_emission_resilient(self, tmp_path: Path) -> None:
        """Exception in signal emission doesn't break OPJMixin record_success."""
        orch = _TestOrchestrator(tmp_path)

        # Inject a broken engine that raises on emit
        broken_engine = MagicMock(spec=ReinforcementEngine)
        broken_engine.emit_signal.side_effect = RuntimeError("engine exploded")
        orch._urs_engine = broken_engine

        # This should NOT raise — signal emission is resilient
        orch._opj_record_success(
            operation="resilient_op",
            context={},
            resolution="should not crash",
            confidence=0.8,
        )

        # Verify the emit was attempted
        broken_engine.emit_signal.assert_called_once()
