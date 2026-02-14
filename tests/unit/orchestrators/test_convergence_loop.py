"""
Tests for execute_convergence_loop — Phase 83 Stage 2.

Neuron nomenclature: ConvergenceNeuron + ConvergenceSignal (brain metaphor).

AC_START: AC-P83-S2-T1-001
Phase: 83 | Stage: 2 | Priority: P0
Description: TDD RED phase for convergence-aware multi-cycle execution
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch


# =============================================================================
# Import targets
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
        TDDOrchestrator,
    )
except ImportError:
    TDDOrchestrator = None


# =============================================================================
# CONVERGENCE LOOP EXECUTION TESTS
# =============================================================================
class TestConvergenceLoopExecution:
    """Test TDDOrchestrator.execute_convergence_loop() method."""

    @pytest.mark.skipif(TDDOrchestrator is None, reason="TDDOrchestrator not available")
    def test_convergence_loop_method_exists(self):
        """execute_convergence_loop method exists on TDDOrchestrator."""
        orchestrator = TDDOrchestrator()
        assert hasattr(orchestrator, 'execute_convergence_loop')
        assert callable(orchestrator.execute_convergence_loop)

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_converges_in_3_cycles(self):
        """AC-P83-S2-T1-001: Simulated scan that improves each cycle converges."""
        orchestrator = TDDOrchestrator()

        # Simulate: starts at 50 issues, each fix removes ~20
        remaining = [50]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            remaining[0] = max(remaining[0] - 20, 0)

        def target(value: int) -> bool:
            return value <= 5

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=target,
            max_cycles=10,
        )

        assert result["success"] is True
        assert result["cycles_executed"] <= 3
        assert len(result["progress_history"]) > 0

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_respects_max_cycles(self):
        """AC-P83-S2-T1-002: Loop exits at max_cycles with partial progress."""
        orchestrator = TDDOrchestrator()

        # Simulate: scan always returns 100, fix only removes 1 per cycle
        remaining = [100]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            remaining[0] -= 1

        def target(value: int) -> bool:
            return value <= 0

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=target,
            max_cycles=3,
        )

        assert result["success"] is False
        assert result["cycles_executed"] == 3
        assert result["progress_history"][-1].current_value < 100  # Some progress made

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_emits_events(self):
        """AC-P83-S2-T1-003: EventBus receives convergence events."""
        orchestrator = TDDOrchestrator()

        emitted_events: List[str] = []
        original_emit = orchestrator._emit_event

        def capture_emit(event_name: str, data: Dict[str, Any]) -> None:
            emitted_events.append(event_name)
            original_emit(event_name, data)

        orchestrator._emit_event = capture_emit

        remaining = [10]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            remaining[0] = 0

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=5,
        )

        assert "CONVERGENCE_CHECK" in emitted_events
        assert "PHASE_CONVERGED" in emitted_events

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_tracks_progress_history(self):
        """AC-P83-S2-T1-004: Result includes list of ConvergenceSignal per cycle."""
        orchestrator = TDDOrchestrator()
        remaining = [30]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            remaining[0] = max(remaining[0] - 15, 0)

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=5,
        )

        history = result["progress_history"]
        assert len(history) >= 2
        assert all(isinstance(r, ConvergenceSignal) for r in history)

        # Progress should be decreasing
        values = [r.current_value for r in history]
        assert values[-1] <= values[0]

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_handles_fix_function_error(self):
        """AC-P83-S2-T1-005: Fix function error logged, loop continues."""
        orchestrator = TDDOrchestrator()
        call_count = [0]

        def scan() -> int:
            return max(20 - (call_count[0] * 10), 0)

        def fix() -> None:
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Fix failed on first attempt")

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=5,
        )

        # Should still converge despite first fix failing
        assert result["cycles_executed"] >= 2

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_immediate_convergence(self):
        """AC-P83-S2-T1-006: If already converged on first scan, exits with 0 fix cycles."""
        orchestrator = TDDOrchestrator()

        result = orchestrator.execute_convergence_loop(
            scan_function=lambda: 0,
            fix_function=lambda: None,
            target_predicate=lambda v: v <= 5,
            max_cycles=10,
        )

        assert result["success"] is True
        assert result["cycles_executed"] == 0
        assert result.get("already_converged", False) is True

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_convergence_loop_stagnation_detection(self):
        """AC-P83-S2-T1-007: If improvement_rate < 1% for 2 consecutive cycles, exit early."""
        orchestrator = TDDOrchestrator()

        # Simulate: drops to 50 then stalls
        remaining = [100]
        call_count = [0]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            call_count[0] += 1
            if call_count[0] == 1:
                remaining[0] = 50  # Big improvement first time
            # After that, no improvement (stagnation)

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=10,
        )

        assert result["success"] is False
        assert result.get("stagnation_detected", False) is True
        assert result["cycles_executed"] < 10  # Should exit early


# =============================================================================
# AC_COMPLETE: AC-P83-S2-T1-001 (RED phase — tests expected to fail/skip)
# =============================================================================
