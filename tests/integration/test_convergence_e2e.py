"""
Integration tests for E2E convergence loop — Phase 83 Stage 3.

Neuron nomenclature: ConvergenceNeuron + ConvergenceSignal (brain metaphor).

AC_START: AC-P83-S3-T2-001
Phase: 83 | Stage: 3 | Priority: P0
Description: E2E integration tests proving full convergence loop works
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
import re
from typing import Any, Dict, List

try:
    from cortex.orchestrators.core.convergence_neuron import (
        ConvergenceNeuron,
        ConvergenceSignal,
    )
except ImportError:
    ConvergenceNeuron = None
    ConvergenceSignal = None

try:
    from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
except ImportError:
    TDDOrchestrator = None


# =============================================================================
# SIMULATED CODEBASES FOR E2E SCENARIOS
# =============================================================================

def _create_simulated_codebase(bad_references: int, bad_pattern: str = "wave") -> Dict[str, List[str]]:
    """Create a simulated codebase with N bad references for testing.

    Args:
        bad_references: Number of bad pattern occurrences to inject.
        bad_pattern: The pattern to inject (default: "wave").

    Returns:
        Dictionary mapping file paths to list of lines.
    """
    files: Dict[str, List[str]] = {}
    refs_placed = 0
    file_num = 0

    while refs_placed < bad_references:
        file_num += 1
        lines = []
        refs_in_file = min(bad_references - refs_placed, 5)
        for i in range(10):
            if i < refs_in_file:
                lines.append(f"# This references {bad_pattern}-{i} terminology")
                refs_placed += 1
            else:
                lines.append(f"# Clean line {i}")
        files[f"file_{file_num}.py"] = lines

    return files


def _count_pattern_in_codebase(codebase: Dict[str, List[str]], pattern: str) -> int:
    """Count occurrences of pattern across all files.

    Args:
        codebase: Dictionary of files to lines.
        pattern: Pattern to search for.

    Returns:
        Total count of pattern matches.
    """
    count = 0
    for lines in codebase.values():
        for line in lines:
            if pattern in line:
                count += 1
    return count


def _fix_pattern_in_codebase(
    codebase: Dict[str, List[str]],
    old_pattern: str,
    new_pattern: str,
    max_fixes_per_call: int = 10,
) -> int:
    """Replace old_pattern with new_pattern in codebase (simulated fix).

    Args:
        codebase: Dictionary of files to lines.
        old_pattern: Pattern to replace.
        new_pattern: Replacement text.
        max_fixes_per_call: Maximum replacements per invocation.

    Returns:
        Number of replacements made.
    """
    fixes = 0
    for filename, lines in codebase.items():
        for i, line in enumerate(lines):
            if old_pattern in line and fixes < max_fixes_per_call:
                codebase[filename][i] = line.replace(old_pattern, new_pattern)
                fixes += 1
        if fixes >= max_fixes_per_call:
            break
    return fixes


# =============================================================================
# E2E CONVERGENCE INTEGRATION TESTS
# =============================================================================
class TestE2ENomenclatureConvergence:
    """Simulate the exact chat01 scenario: nomenclature cleanup to convergence."""

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_e2e_nomenclature_convergence(self):
        """AC-P83-S3-T2-001: Simulated cleanup converges from 50 → 0 in ≤5 cycles."""
        orchestrator = TDDOrchestrator()
        codebase = _create_simulated_codebase(50, "wave")

        def scan() -> int:
            return _count_pattern_in_codebase(codebase, "wave")

        def fix() -> None:
            _fix_pattern_in_codebase(codebase, "wave", "phase", max_fixes_per_call=15)

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=10,
        )

        assert result["success"] is True
        assert result["cycles_executed"] <= 5
        assert _count_pattern_in_codebase(codebase, "wave") == 0


class TestE2ESecuritySweepConvergence:
    """Simulate security vulnerability remediation."""

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_e2e_security_sweep_convergence(self):
        """AC-P83-S3-T2-002: Security fix converges from 10 → 0 in ≤3 cycles."""
        orchestrator = TDDOrchestrator()
        codebase = _create_simulated_codebase(10, "sql_raw_query")

        def scan() -> int:
            return _count_pattern_in_codebase(codebase, "sql_raw_query")

        def fix() -> None:
            _fix_pattern_in_codebase(codebase, "sql_raw_query", "sql_parameterized", max_fixes_per_call=5)

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=5,
        )

        assert result["success"] is True
        assert result["cycles_executed"] <= 3


class TestE2EStagnationExit:
    """Simulate stagnation where progress plateaus."""

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_e2e_stagnation_exit(self):
        """AC-P83-S3-T2-003: Stagnating progress exits with warning after 2 flat cycles."""
        orchestrator = TDDOrchestrator()

        # Fix only works once, then stagnates
        remaining = [50]
        fixed_once = [False]

        def scan() -> int:
            return remaining[0]

        def fix() -> None:
            if not fixed_once[0]:
                remaining[0] = 25
                fixed_once[0] = True
            # After first fix, no more progress

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=10,
        )

        assert result["success"] is False
        assert result.get("stagnation_detected", False) is True
        # Should exit well before max_cycles due to stagnation
        assert result["cycles_executed"] < 10


class TestE2EAlreadyClean:
    """Simulate scenario where codebase is already clean."""

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_e2e_already_clean(self):
        """AC-P83-S3-T2-004: Zero-issue scan exits immediately with success."""
        orchestrator = TDDOrchestrator()

        result = orchestrator.execute_convergence_loop(
            scan_function=lambda: 0,
            fix_function=lambda: None,
            target_predicate=lambda v: v <= 0,
            max_cycles=10,
        )

        assert result["success"] is True
        assert result["cycles_executed"] == 0
        assert result.get("already_converged", False) is True


class TestE2EMaxCyclesPartialProgress:
    """Simulate partial progress when max_cycles is hit."""

    @pytest.mark.skipif(
        TDDOrchestrator is None or ConvergenceNeuron is None,
        reason="Dependencies not available"
    )
    def test_e2e_max_cycles_partial_progress(self):
        """AC-P83-S3-T2-005: Partial progress reported when max_cycles hit."""
        orchestrator = TDDOrchestrator()
        codebase = _create_simulated_codebase(100, "bad_pattern")

        def scan() -> int:
            return _count_pattern_in_codebase(codebase, "bad_pattern")

        def fix() -> None:
            _fix_pattern_in_codebase(codebase, "bad_pattern", "good_pattern", max_fixes_per_call=5)

        result = orchestrator.execute_convergence_loop(
            scan_function=scan,
            fix_function=fix,
            target_predicate=lambda v: v <= 0,
            max_cycles=3,
        )

        assert result["success"] is False
        assert result["cycles_executed"] == 3

        # Should show partial progress (some fixed, but not all)
        history = result["progress_history"]
        assert len(history) >= 2
        assert history[-1].current_value < 100  # Some progress made
        assert history[-1].current_value > 0    # But not complete


# =============================================================================
# AC_COMPLETE: AC-P83-S3-T2-001 (RED phase — tests expected to fail/skip)
# =============================================================================
