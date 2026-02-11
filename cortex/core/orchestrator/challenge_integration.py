"""Challenge Integration Orchestrator - Production Implementation

Integrates challenge detection and processing with:
- Confidence threshold filtering
- Severity-based sorting
- Challenge composition
- Integration with generator

Author: Asif Hussain
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ChallengeSeverity(Enum):
    """Challenge severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def sort_order(self) -> int:
        """Return sort order (lower = earlier in sorted list)."""
        order = {
            ChallengeSeverity.CRITICAL: 0,
            ChallengeSeverity.HIGH: 1,
            ChallengeSeverity.MEDIUM: 2,
            ChallengeSeverity.LOW: 3,
        }
        return order[self]


@dataclass
class Challenge:
    """Represents a challenge with description, severity, and confidence."""
    description: str
    severity: ChallengeSeverity
    confidence: float
    challenge_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    mitigation: Optional[str] = None
    code_context: Optional[str] = None

    def __post_init__(self):
        """Post-initialization setup."""
        if self.parameters is None:
            self.parameters = {}
        if self.challenge_id is None:
            self.challenge_id = f"challenge_{id(self)}"


class ChallengeIntegrationOrchestrator:
    """Orchestrate challenge integration with filtering and sorting."""

    def __init__(
        self,
        generator: Optional[Any] = None,
        confidence_threshold: float = 0.30,
    ):
        """
        Initialize orchestrator.

        Args:
            generator: Challenge generator (optional for testing)
            confidence_threshold: Minimum confidence to include challenge
        """
        self.generator = generator
        self.confidence_threshold = confidence_threshold

    def process_challenges(
        self,
        context: Dict[str, Any],
    ) -> List[Challenge]:
        """
        Process challenges from generator with filtering and sorting.

        Args:
            context: Context dict for challenge generation

        Returns:
            Sorted list of challenges above confidence threshold
        """
        # Generate challenges if generator available
        if self.generator:
            challenges = self.generator.generate_challenges(context)
        else:
            challenges = []

        # Filter by confidence threshold
        filtered = [
            c for c in challenges
            if c.confidence >= self.confidence_threshold
        ]

        # Sort by severity (CRITICAL first)
        sorted_challenges = sorted(
            filtered,
            key=lambda c: c.severity.sort_order()
        )

        return sorted_challenges

    def process_challenge(self, challenge: Challenge) -> bool:
        """
        Process single challenge.

        Args:
            challenge: Challenge to process

        Returns:
            True if processed successfully
        """
        return challenge.confidence >= self.confidence_threshold


__all__ = [
    "Challenge",
    "ChallengeSeverity",
    "ChallengeIntegrationOrchestrator",
]
