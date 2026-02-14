"""
ConvergenceNeuron — Phase 83 Stage 1.

Sensory neuron that fires when convergence is detected. Part of
CORTEX brain metaphor: neurons process signals, axons (EventBus)
carry them between orchestrators.

AC_START: AC-P83-S1-T3-001
Phase: 83 | Stage: 1 | Priority: P0
Description: GREEN phase — ConvergenceNeuron + ConvergenceSignal
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConvergenceSignal:
    """Action potential carrying convergence state between neurons.

    Represents the result of a single convergence check — whether the
    target has been met, current measurement, and improvement rate.

    Attributes:
        converged: Whether the target predicate is satisfied.
        current_value: Current measurement from the scan function.
        target_value: Target value (for display/logging purposes).
        improvement_rate: Progress ratio (baseline - current) / baseline.
            0.0 means no improvement, 1.0 means fully converged from baseline.
        error: Optional error message if the scan function failed.

    Example:
        >>> signal = ConvergenceSignal(
        ...     converged=False,
        ...     current_value=25,
        ...     target_value=0,
        ...     improvement_rate=0.5,
        ... )
    """

    converged: bool
    current_value: Any
    target_value: Any
    improvement_rate: float
    error: Optional[str] = None


class ConvergenceNeuron:
    """Sensory neuron that fires when convergence is detected.

    Accepts a scan_function (measures the current state) and a
    target_predicate (defines when convergence is achieved). Each
    call to check() runs the scan, evaluates the predicate, calculates
    improvement rate, and returns a ConvergenceSignal.

    Tracks history of all signals for progress analysis.

    Args:
        scan_function: Callable that returns a numeric measurement.
        target_predicate: Callable that returns True when converged.
        baseline: Optional explicit baseline value. If None, the first
            check() result becomes the baseline automatically.
        target_value: Optional target value for display in signals.

    Example:
        >>> neuron = ConvergenceNeuron(
        ...     scan_function=lambda: count_bad_refs(),
        ...     target_predicate=lambda v: v <= 5,
        ...     baseline=550,
        ... )
        >>> signal = neuron.check()
        >>> signal.converged
        False
    """

    def __init__(
        self,
        scan_function: Callable[[], Any],
        target_predicate: Callable[[Any], bool],
        baseline: Optional[Any] = None,
        target_value: Any = None,
    ) -> None:
        """Initialize ConvergenceNeuron with scan and predicate functions.

        Args:
            scan_function: Callable returning current measurement.
            target_predicate: Callable returning True when target met.
            baseline: Optional explicit baseline for improvement calculation.
            target_value: Optional target value for display purposes.
        """
        self._scan_function = scan_function
        self._target_predicate = target_predicate
        self._baseline: Optional[Any] = baseline
        self._target_value = target_value
        self._history: List[ConvergenceSignal] = []

    def check(self) -> ConvergenceSignal:
        """Run scan function, evaluate predicate, return signal.

        Executes the scan function to get the current value, evaluates
        the target predicate, calculates improvement rate from baseline,
        and appends the result to history.

        Returns:
            ConvergenceSignal with convergence state and metrics.

        Raises:
            No exceptions — scan errors are captured in the signal.
        """
        try:
            current_value = self._scan_function()
        except Exception as e:
            logger.warning(f"ConvergenceNeuron scan failed: {e}")
            signal = ConvergenceSignal(
                converged=False,
                current_value=-1,
                target_value=self._target_value,
                improvement_rate=0.0,
                error=str(e),
            )
            self._history.append(signal)
            return signal

        # Auto-set baseline from first check if not explicitly provided
        if self._baseline is None:
            self._baseline = current_value

        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(current_value)

        # Evaluate target predicate
        converged = self._target_predicate(current_value)

        signal = ConvergenceSignal(
            converged=converged,
            current_value=current_value,
            target_value=self._target_value,
            improvement_rate=improvement_rate,
        )
        self._history.append(signal)
        return signal

    def get_history(self) -> List[ConvergenceSignal]:
        """Return all signals from prior checks.

        Returns:
            List of ConvergenceSignal in chronological order.
        """
        return list(self._history)

    def _calculate_improvement_rate(self, current_value: Any) -> float:
        """Calculate improvement rate from baseline to current.

        Args:
            current_value: Current measurement from scan.

        Returns:
            Float between 0.0 (no improvement) and 1.0 (fully improved).
            Returns 0.0 if baseline is zero or not numeric.
        """
        try:
            baseline = float(self._baseline)
            current = float(current_value)

            if baseline == 0:
                return 0.0

            # If this is the first check (current == baseline), no improvement yet
            if len(self._history) == 0 and current == baseline:
                return 0.0

            rate = (baseline - current) / baseline
            # Clamp to [0.0, 1.0] — negative improvement (regression) shows as 0.0
            return max(0.0, min(1.0, rate))
        except (TypeError, ValueError):
            return 0.0


__all__ = [
    "ConvergenceNeuron",
    "ConvergenceSignal",
]
# AC_COMPLETE: AC-P83-S1-T3-001 ✅ ConvergenceNeuron + ConvergenceSignal implemented
