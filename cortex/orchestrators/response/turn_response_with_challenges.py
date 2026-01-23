"""Turn Response with Challenges - Handles responses with challenge integration.

Generates responses that include challenge questions, recommendations, and
holistic context information, with proper segment ordering.

Author: CORTEX Framework
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


class ChallengeResponseGenerator:
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


class TurnResponseWithChallenges:
    """Wrapper for generating turn responses with challenge integration.
    
    Integrates base response generation with challenge orchestrator and
    holistic context builder to produce responses with embedded challenges,
    recommendations, and context information in proper order.
    
    Attributes:
        base_generator: Base response generator.
        challenge_generator: Challenge orchestrator/generator.
        context_builder: Holistic context builder.
    """
    
    def __init__(
        self,
        base_generator: Any,
        challenge_generator: Any,
        context_builder: Any
    ) -> None:
        """Initialize turn response with challenges wrapper.
        
        Args:
            base_generator: Base response generator.
            challenge_generator: Challenge orchestrator.
            context_builder: Holistic context builder.
        """
        self.base_generator = base_generator
        self.challenge_generator = challenge_generator
        self.context_builder = context_builder
    
    def generate_response_with_challenges(
        self,
        context: Dict[str, Any]
    ) -> str:
        """Generate response with challenges, recommendations, and context.
        
        Generates a complete response by:
        1. Calling base generator to get base response
        2. Processing challenges and adding challenge segment
        3. Adding recommendations segment if present
        4. Building holistic context
        
        Segment order: base → challenges → recommendations → context
        
        Args:
            context: Context dictionary for generation
                
        Returns:
            Formatted response string with all segments
        """
        # Get base response from generator
        base_response = self.base_generator.generate_response(context)
        
        # Start with base response
        segments = [base_response] if base_response else []
        
        # Process challenges through challenge generator
        processed_challenges = self.challenge_generator.process_challenges(context)
        if processed_challenges:
            challenge_text = self._format_challenges(processed_challenges)
            segments.append(challenge_text)
        
        # Add recommendations if present in context
        recommendations = context.get("recommendations", [])
        if recommendations:
            recommendations_text = self._format_recommendations(recommendations)
            segments.append(recommendations_text)
        
        # Build holistic context
        holistic_context = self.context_builder.build_holistic_context(context)
        # Context is built but not added as a separate segment
        
        # Join all segments
        return "\n\n".join(segments)
    
    def _format_challenges(self, challenges: List[Dict[str, Any]]) -> str:
        """Format challenges as markdown segment.
        
        Args:
            challenges: List of challenge dictionaries.
            
        Returns:
            Formatted challenge markdown text.
        """
        lines = ["## Challenges Identified"]
        lines.append("")
        for i, challenge in enumerate(challenges, 1):
            desc = challenge.get("description", challenge.get("desc", "Unknown challenge"))
            severity = challenge.get("severity", "")
            confidence = challenge.get("confidence", None)
            mitigation = challenge.get("mitigation", "")
            
            lines.append(f"{i}. {desc}")
            if severity:
                lines.append(f"   - Severity: {severity}")
            if confidence is not None:
                lines.append(f"   - Confidence: {int(confidence * 100)}%")
            if mitigation:
                lines.append(f"   - Mitigation: {mitigation}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as markdown segment.
        
        Args:
            recommendations: List of recommendation dictionaries.
            
        Returns:
            Formatted recommendation markdown text.
        """
        lines = ["## Recommendations"]
        lines.append("")
        for i, rec in enumerate(recommendations, 1):
            action = rec.get("action", rec.get("description", "Unknown action"))
            priority = rec.get("priority", None)
            rationale = rec.get("rationale", "")
            
            lines.append(f"{i}. {action}")
            if priority is not None:
                lines.append(f"   - Priority: {priority}")
            if rationale:
                lines.append(f"   - Rationale: {rationale}")
            lines.append("")
        
        return "\n".join(lines)


__all__ = [
    "ChallengeType",
    "Challenge",
    "TurnResponseSegment",
    "ResponseWithChallenges",
    "ChallengeResponseGenerator",
    "TurnResponseWithChallenges",
]
