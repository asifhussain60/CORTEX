"""Turn Response with Challenges - Handles responses with challenges.

Generates responses that include challenge questions and follow-ups.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum


class ChallengeType(Enum):
    """Types of challenges."""

    CLARIFICATION = "clarification"
    VALIDATION = "validation"
    EXTENSION = "extension"
    CONTRADICTION = "contradiction"
    EXPLORATION = "exploration"


@dataclass
class Challenge:
    """Challenge question or prompt.

    Attributes:
        challenge_type: Type of challenge.
        question: Challenge question.
        context: Context for the challenge.
        severity: Severity level (low/medium/high).
    """

    challenge_type: ChallengeType
    question: str
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"


@dataclass
class TurnResponseSegment:
    """Segment of a turn response.

    Attributes:
        segment_id: Unique segment identifier.
        content: Segment content.
        segment_type: Type of segment.
        position: Position in response.
    """

    segment_id: str
    content: str
    segment_type: str = "text"
    position: int = 0


@dataclass
class ResponseWithChallenges:
    """Response content with embedded challenges.

    Attributes:
        primary_response: Main response text.
        challenges: List of challenge questions.
        metadata: Optional metadata.
        follow_up_required: Whether follow-up is required.
    """

    primary_response: str
    challenges: List[Challenge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    follow_up_required: bool = False


class TurnResponseWithChallenges:
    """Generates responses with embedded challenges."""

    def __init__(self) -> None:
        """Initialize challenge response generator."""
        self.responses: List[ResponseWithChallenges] = []

    def create_response(
        self,
        primary_response: str,
        challenges: Optional[List[Challenge]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        follow_up_required: bool = False,
    ) -> ResponseWithChallenges:
        """Create a response with challenges.

        Args:
            primary_response: Main response.
            challenges: List of challenges.
            metadata: Optional metadata.
            follow_up_required: If follow-up needed.

        Returns:
            ResponseWithChallenges.
        """
        response = ResponseWithChallenges(
            primary_response=primary_response,
            challenges=challenges or [],
            metadata=metadata or {},
            follow_up_required=follow_up_required,
        )
        self.responses.append(response)
        return response

    def add_challenge(
        self,
        response: ResponseWithChallenges,
        challenge_type: ChallengeType,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "medium",
    ) -> Challenge:
        """Add a challenge to a response.

        Args:
            response: Target response.
            challenge_type: Type of challenge.
            question: Challenge question.
            context: Optional context.
            severity: Severity level.

        Returns:
            Challenge.
        """
        challenge = Challenge(
            challenge_type=challenge_type,
            question=question,
            context=context or {},
            severity=severity,
        )
        response.challenges.append(challenge)
        return challenge

    def get_challenging_responses(self) -> List[ResponseWithChallenges]:
        """Get all responses with challenges.

        Returns:
            List of ResponseWithChallenges with challenges.
        """
        return [r for r in self.responses if r.challenges]

    def get_responses_requiring_followup(self) -> List[ResponseWithChallenges]:
        """Get responses requiring follow-up.

        Returns:
            List of ResponseWithChallenges.
        """
        return [r for r in self.responses if r.follow_up_required]


# Alias for backward compatibility
ChallengeResponseGenerator = TurnResponseWithChallenges

__all__ = [
    "TurnResponseWithChallenges",
    "ChallengeResponseGenerator",
    "ResponseWithChallenges",
    "TurnResponseSegment",
    "Challenge",
    "ChallengeType",
]
