"""Tutorial mode post-execution renderer for optional teaching output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TutorialRenderRequest:
    """Input payload for tutorial rendering.

    Args:
        mode: Tutorial mode state (on|auto|off).
        is_expert_user: Whether the active user is expert-profile.
        explicit_teach_intent: Whether request explicitly asks for explanation.
        operational_summary: Operational output summary to annotate.
    """

    mode: str
    is_expert_user: bool
    explicit_teach_intent: bool
    operational_summary: str


class TutorialModeRenderer:
    """Render optional tutorial block after operational execution.

    Notes:
        This renderer is post-execution only and does not mutate operational
        decision paths.
    """

    VALID_STATES = {"on", "auto", "off"}

    def render(self, request: TutorialRenderRequest) -> Optional[str]:
        """Render tutorial content based on mode and user context.

        Args:
            request: Tutorial render request payload.

        Returns:
            Optional[str]: Tutorial block text or ``None`` when suppressed.
        """
        if request.mode not in self.VALID_STATES:
            return None

        if request.mode == "off":
            return None

        if request.is_expert_user and request.mode == "auto":
            return None

        if request.mode == "auto" and not request.explicit_teach_intent:
            return None

        return (
            "Tutorial: Completed operational flow successfully. "
            f"Summary: {request.operational_summary}"
        )
