"""ADLC orchestrator enforcing bounded convergence cycles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ADLCCycleResult:
    """Result for a single ADLC execution cycle.

    Args:
        cycle: Current cycle number.
        converged: Whether execution converged.
    """

    cycle: int
    converged: bool


class MaxCyclesExceeded(RuntimeError):
    """Raised when ADLC max cycle limit is exceeded."""


class ADLCOrchestrator:
    """Execute ADLC cycles with a strict max-cycles convergence cap.

    Args:
        max_cycles: Maximum number of convergence cycles.
    """

    def __init__(self, max_cycles: int = 3) -> None:
        self.max_cycles = max_cycles

    def execute_cycle(self, cycle: int, converged: bool) -> ADLCCycleResult:
        """Execute one ADLC cycle.

        Args:
            cycle: 1-based cycle number.
            converged: Whether convergence has been reached.

        Returns:
            ADLCCycleResult: Cycle result payload.

        Raises:
            MaxCyclesExceeded: If cycle exceeds configured max_cycles.
        """
        if cycle > self.max_cycles:
            raise MaxCyclesExceeded(
                f"ADLC max_cycles exceeded: cycle={cycle}, max_cycles={self.max_cycles}"
            )
        return ADLCCycleResult(cycle=cycle, converged=converged)
