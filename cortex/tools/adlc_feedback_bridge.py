"""ADLC feedback bridge handling Stage 7 to Stage 2 remediation loops."""

from __future__ import annotations

from dataclasses import dataclass

from cortex.tools.adlc_orchestrator import MaxCyclesExceeded


@dataclass(frozen=True)
class ADLCFeedbackAction:
    """Represents a feedback bridge action.

    Args:
        from_stage: Current stage name.
        to_stage: Next stage name.
        cycle: Current cycle number.
    """

    from_stage: str
    to_stage: str
    cycle: int


class ADLCFeedbackBridge:
    """Bridge feedback from stage 7 to stage 2 with max-cycle enforcement.

    Args:
        max_cycles: Maximum allowed feedback loop cycles.
    """

    def __init__(self, max_cycles: int = 3) -> None:
        self.max_cycles = max_cycles

    def route_feedback(self, cycle: int) -> ADLCFeedbackAction:
        """Route stage-7 feedback to stage-2 for remediation.

        Args:
            cycle: 1-based cycle number.

        Returns:
            ADLCFeedbackAction: Action descriptor.

        Raises:
            MaxCyclesExceeded: If cycle exceeds max_cycles.
        """
        if cycle > self.max_cycles:
            raise MaxCyclesExceeded(
                f"Feedback loop exceeded max_cycles: cycle={cycle}, max_cycles={self.max_cycles}"
            )
        return ADLCFeedbackAction(
            from_stage="feedback_and_learning",
            to_stage="scope_and_risk",
            cycle=cycle,
        )
