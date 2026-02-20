"""
Tests for ConvergenceNeuron — Phase 83 Stage 1.

Neuron nomenclature: Aligns with CORTEX brain metaphor.
- ConvergenceNeuron: sensory neuron that fires when convergence detected
- ConvergenceSignal: action potential carrying convergence state

AC_START: AC-P83-S1-T1-001
Phase: 83 | Stage: 1 | Priority: P0
Description: TDD RED phase for ConvergenceNeuron and enhanced SuccessCriteria
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock


# =============================================================================
# Import targets (expected to fail in RED phase)
# =============================================================================
try:
    from cortex.orchestrators.core.convergence_neuron import (
        ConvergenceNeuron,
        ConvergenceSignal,
    )
except ImportError:
    ConvergenceNeuron = None
    ConvergenceSignal = None

try:
    from cortex.orchestrators.core.tdd_orchestrator import (
        SuccessCriteria,
        CycleMetrics,
        GateResult,
        TDDOrchestrator,
    )
except ImportError:
    SuccessCriteria = None
    CycleMetrics = None
    GateResult = None
    TDDOrchestrator = None


# =============================================================================
# CONVERGENCE SIGNAL DATACLASS TESTS
# =============================================================================
class TestConvergenceSignal:
    """Test ConvergenceSignal dataclass structure."""

    @pytest.mark.skipif(ConvergenceSignal is None, reason="ConvergenceSignal not yet implemented")
    def test_convergence_signal_has_required_fields(self):
        """ConvergenceSignal has converged, current_value, target_value, improvement_rate."""
        signal = ConvergenceSignal(
            converged=False,
            current_value=50,
            target_value=0,
            improvement_rate=0.0,
        )
        assert signal.converged is False
        assert signal.current_value == 50
        assert signal.target_value == 0
        assert signal.improvement_rate == 0.0

    @pytest.mark.skipif(ConvergenceSignal is None, reason="ConvergenceSignal not yet implemented")
    def test_convergence_signal_with_error(self):
        """ConvergenceSignal can carry error information."""
        signal = ConvergenceSignal(
            converged=False,
            current_value=-1,
            target_value=0,
            improvement_rate=0.0,
            error="Scan function raised ValueError",
        )
        assert signal.error == "Scan function raised ValueError"

    @pytest.mark.skipif(ConvergenceSignal is None, reason="ConvergenceSignal not yet implemented")
    def test_convergence_signal_converged_state(self):
        """ConvergenceSignal reflects convergence when target met."""
        signal = ConvergenceSignal(
            converged=True,
            current_value=0,
            target_value=0,
            improvement_rate=1.0,
        )
        assert signal.converged is True
        assert signal.improvement_rate == 1.0


# =============================================================================
# CONVERGENCE NEURON INIT TESTS
# =============================================================================
class TestConvergenceNeuronInit:
    """Test ConvergenceNeuron initialization."""

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_convergence_neuron_accepts_scan_and_predicate(self):
        """AC-P83-S1-T1-001: ConvergenceNeuron.__init__ takes scan_function and target_predicate."""
        def scan() -> int:
            return 50

        def predicate(value: int) -> bool:
            return value <= 5

        neuron = ConvergenceNeuron(
            scan_function=scan,
            target_predicate=predicate,
        )
        assert neuron is not None

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_convergence_neuron_accepts_optional_baseline(self):
        """ConvergenceNeuron can accept an explicit baseline value."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 50,
            target_predicate=lambda v: v <= 5,
            baseline=100,
        )
        assert neuron._baseline == 100


# =============================================================================
# CONVERGENCE NEURON check() TESTS
# =============================================================================
class TestConvergenceNeuronCheck:
    """Test ConvergenceNeuron.check() method."""

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_check_returns_convergence_signal(self):
        """AC-P83-S1-T1-002: check() returns ConvergenceSignal."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 30,
            target_predicate=lambda v: v <= 5,
            target_value=5,
        )
        signal = neuron.check()
        assert isinstance(signal, ConvergenceSignal)
        assert signal.current_value == 30
        assert signal.target_value == 5

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_check_detects_convergence_when_target_met(self):
        """AC-P83-S1-T1-003: check() returns converged=True when predicate satisfied."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 0,
            target_predicate=lambda v: v <= 5,
        )
        signal = neuron.check()
        assert signal.converged is True

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_check_detects_non_convergence(self):
        """AC-P83-S1-T1-004: check() returns converged=False when predicate not satisfied."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 50,
            target_predicate=lambda v: v <= 5,
        )
        signal = neuron.check()
        assert signal.converged is False

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_check_handles_scan_exception_gracefully(self):
        """AC-P83-S1-T1-005: check() returns converged=False with error info on scan failure."""
        def failing_scan() -> int:
            raise ValueError("Scan failed: file not found")

        neuron = ConvergenceNeuron(
            scan_function=failing_scan,
            target_predicate=lambda v: v <= 5,
        )
        signal = neuron.check()
        assert signal.converged is False
        assert signal.error is not None
        assert "Scan failed" in signal.error

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_check_tracks_history(self):
        """AC-P83-S1-T1-006: get_history() returns list of all ConvergenceSignal."""
        call_count = 0

        def decreasing_scan() -> int:
            nonlocal call_count
            call_count += 1
            return max(50 - (call_count * 15), 0)

        neuron = ConvergenceNeuron(
            scan_function=decreasing_scan,
            target_predicate=lambda v: v <= 5,
        )
        neuron.check()
        neuron.check()
        neuron.check()

        history = neuron.get_history()
        assert len(history) == 3
        assert all(isinstance(s, ConvergenceSignal) for s in history)

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_improvement_rate_calculated(self):
        """AC-P83-S1-T1-007: improvement_rate = (baseline - current) / baseline."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 25,
            target_predicate=lambda v: v <= 5,
            baseline=50,
        )
        signal = neuron.check()
        # improvement_rate = (50 - 25) / 50 = 0.5
        assert abs(signal.improvement_rate - 0.5) < 0.01

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_improvement_rate_auto_baseline_from_first_check(self):
        """If no explicit baseline, first check() sets the baseline automatically."""
        call_count = 0

        def decreasing_scan() -> int:
            nonlocal call_count
            call_count += 1
            return 100 if call_count == 1 else 50

        neuron = ConvergenceNeuron(
            scan_function=decreasing_scan,
            target_predicate=lambda v: v <= 5,
        )
        signal1 = neuron.check()
        assert signal1.improvement_rate == 0.0  # First check = baseline, no improvement yet

        signal2 = neuron.check()
        # improvement_rate = (100 - 50) / 100 = 0.5
        assert abs(signal2.improvement_rate - 0.5) < 0.01

    @pytest.mark.skipif(ConvergenceNeuron is None, reason="ConvergenceNeuron not yet implemented")
    def test_improvement_rate_zero_baseline_handled(self):
        """If baseline is 0, improvement_rate is 0.0 (no division by zero)."""
        neuron = ConvergenceNeuron(
            scan_function=lambda: 0,
            target_predicate=lambda v: v <= 5,
            baseline=0,
        )
        signal = neuron.check()
        assert signal.improvement_rate == 0.0  # No division by zero
        assert signal.converged is True


# =============================================================================
# ENHANCED SUCCESS CRITERIA TESTS
# =============================================================================
class TestEnhancedSuccessCriteria:
    """Test SuccessCriteria enhanced with goal_predicate."""

    @pytest.mark.skipif(SuccessCriteria is None, reason="SuccessCriteria not yet available")
    def test_success_criteria_accepts_goal_predicate(self):
        """AC-P83-S1-T2-001: SuccessCriteria has optional goal_predicate field."""
        criteria = SuccessCriteria(
            min_coverage=0.85,
            max_latency_ms=200,
            extensibility_required=False,
            goal_predicate=lambda metrics: metrics.tests_failed == 0,
        )
        assert criteria.goal_predicate is not None

    @pytest.mark.skipif(SuccessCriteria is None, reason="SuccessCriteria not yet available")
    def test_backward_compatible_without_goal_predicate(self):
        """AC-P83-S1-T2-003: Existing tests pass without goal_predicate."""
        criteria = SuccessCriteria(
            min_coverage=0.85,
            max_latency_ms=200,
            extensibility_required=False,
        )
        # goal_predicate should default to None
        assert not hasattr(criteria, 'goal_predicate') or criteria.goal_predicate is None

    @pytest.mark.skipif(
        TDDOrchestrator is None or SuccessCriteria is None,
        reason="TDDOrchestrator or SuccessCriteria not yet available"
    )
    def test_holistic_refactor_gate_evaluates_goal_predicate(self):
        """AC-P83-S1-T2-002: holistic_refactor_gate checks goal_predicate when present."""
        orchestrator = TDDOrchestrator()

        # Goal predicate: tests_failed must be 0
        criteria = SuccessCriteria(
            min_coverage=0.0,  # Intentionally low so only goal_predicate matters
            max_latency_ms=9999,
            extensibility_required=False,
            goal_predicate=lambda metrics: metrics.tests_failed == 0,
        )

        # Metrics with 2 failures — should fail the goal
        metrics_failing = CycleMetrics(
            cycle_number=1,
            tests_passed=10,
            tests_failed=2,
            coverage_percent=0.90,
            avg_latency_ms=100.0,
            extensibility_score=0.0,
        )
        result = orchestrator.holistic_refactor_gate(criteria=criteria, metrics=metrics_failing)
        assert result.passed is False
        assert any("goal" in gap.lower() or "predicate" in gap.lower() for gap in result.gaps)

        # Metrics with 0 failures — should pass
        metrics_passing = CycleMetrics(
            cycle_number=2,
            tests_passed=12,
            tests_failed=0,
            coverage_percent=0.90,
            avg_latency_ms=100.0,
            extensibility_score=0.0,
        )
        result = orchestrator.holistic_refactor_gate(criteria=criteria, metrics=metrics_passing)
        assert result.passed is True


# =============================================================================
# AC_COMPLETE: AC-P83-S1-T1-001 (RED phase — all tests expected to fail)
# =============================================================================
