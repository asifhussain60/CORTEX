"""
Turn Response With Challenges - Wraps TurnResponseGenerator with challenge injection.

Automatically injects challenges, recommendations, and holistic context into every turn response.
Enables INT-RULE-009 enforcement (mandatory intelligent challenges).

Type hints: CORE-011 compliant
Docstrings: Google style, CORE-012 compliant
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TurnResponseSegment:
    """Response segment (challenges, recommendations, context).
    
    Attributes:
        name: Segment name (e.g., "challenges", "recommendations")
        content: Segment content as string or list
        order: Insertion order (lower = earlier)
    """
    name: str
    content: Any
    order: int = 0


class TurnResponseWithChallenges:
    """Wraps TurnResponseGenerator to inject challenges automatically.
    
    Responsibilities:
    - Call base response generator
    - Inject challenges segment after header
    - Inject recommendations segment
    - Build and inject holistic context segment
    - Maintain response validity
    
    Example:
        wrapper = TurnResponseWithChallenges(
            base_generator,
            challenge_orchestrator,
            context_builder,
        )
        response = wrapper.generate_response_with_challenges(context)
    """
    
    def __init__(
        self,
        base_response_generator,
        challenge_orchestrator,
        context_builder,
    ) -> None:
        """Initialize response wrapper.
        
        Args:
            base_response_generator: Base response generator instance.
            challenge_orchestrator: Challenge orchestrator for generating challenges.
            context_builder: Holistic context builder.
        """
        self.base_generator = base_response_generator
        self.challenge_orchestrator = challenge_orchestrator
        self.context_builder = context_builder
    
    def generate_response_with_challenges(
        self,
        context: Dict[str, Any],
    ) -> str:
        """Generate response with automatic challenge injection.
        
        Execution flow:
        1. Generate base response from base_generator
        2. Generate challenges using challenge_orchestrator
        3. Build holistic context using context_builder
        4. Inject challenge segment after header
        5. Inject recommendations segment
        6. Inject holistic context segment
        7. Return combined response
        
        Args:
            context: Context dictionary containing base_response, challenges, etc.
        
        Returns:
            String response with injected challenge and recommendation segments.
        """
        # Step 1: Generate base response
        base_response = self.base_generator.generate_response(context)
        
        # Step 2: Generate challenges
        challenges = self.challenge_orchestrator.process_challenges(context)
        
        # Step 3: Build holistic context
        holistic_context = self.context_builder.build_holistic_context(context)
        
        # Step 4-6: Build segments
        segments = []
        
        # Base response (order 0)
        segments.append(TurnResponseSegment("base", base_response, order=0))
        
        # Challenges segment (order 1)
        if challenges:
            segments.append(
                TurnResponseSegment(
                    "challenges",
                    self._format_challenges(challenges),
                    order=1
                )
            )
        
        # Recommendations segment (order 2)
        if context.get("recommendations"):
            segments.append(
                TurnResponseSegment(
                    "recommendations",
                    self._format_recommendations(context.get("recommendations", [])),
                    order=2
                )
            )
        
        # Holistic context segment (order 3)
        if holistic_context:
            segments.append(
                TurnResponseSegment(
                    "context",
                    holistic_context,
                    order=3
                )
            )
        
        # Step 7: Combine segments in order
        segments.sort(key=lambda s: s.order)
        combined = "\n\n".join(str(s.content) for s in segments)
        
        return combined
    
    def _format_challenges(self, challenges: List[Dict[str, Any]]) -> str:
        """Format challenges for inclusion in response.
        
        Args:
            challenges: List of challenge dictionaries.
        
        Returns:
            Formatted challenges string.
        """
        if not challenges:
            return ""
        
        lines = ["## Challenges Identified"]
        for i, challenge in enumerate(challenges, 1):
            lines.append(f"\n{i}. {challenge.get('description', 'Unknown challenge')}")
            if challenge.get('severity'):
                lines.append(f"   Severity: {challenge['severity']}")
            if challenge.get('confidence'):
                lines.append(f"   Confidence: {challenge['confidence']:.0%}")
            if challenge.get('mitigation'):
                lines.append(f"   Mitigation: {challenge['mitigation']}")
        
        return "\n".join(lines)
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for inclusion in response.
        
        Args:
            recommendations: List of recommendation dictionaries.
        
        Returns:
            Formatted recommendations string.
        """
        if not recommendations:
            return ""
        
        lines = ["## Recommendations"]
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"\n{i}. {rec.get('action', 'Unknown action')}")
            if rec.get('priority'):
                lines.append(f"   Priority: {rec['priority']}")
            if rec.get('rationale'):
                lines.append(f"   Rationale: {rec['rationale']}")
        
        return "\n".join(lines)
