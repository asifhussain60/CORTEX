"""
Challenge Integration Orchestrator - Wraps ChallengeGenerator with confidence filtering.

Generates challenges from code context and sorts by severity level.
Filters out low-confidence challenges (< 0.30 by default).

Type hints: CORE-011 compliant
Docstrings: Google style, CORE-012 compliant
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class ChallengeSeverity(Enum):
    """Challenge severity levels ranked by priority.
    
    Used for sorting challenges in output. CRITICAL challenges appear first,
    LOW challenges appear last.
    """
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Challenge:
    """Challenge data structure for risk identification.
    
    Attributes:
        description: Human-readable challenge description.
        severity: ChallengeSeverity enum value (CRITICAL | HIGH | MEDIUM | LOW).
        confidence: Float 0.0-1.0 indicating confidence in challenge validity.
        mitigation: Optional mitigation strategy or workaround.
        code_context: Optional code snippet relevant to challenge.
    """
    description: str
    severity: ChallengeSeverity
    confidence: float
    mitigation: str = ""
    code_context: str = ""


class ChallengeIntegrationOrchestrator:
    """Wraps ChallengeGenerator with filtering and sorting.
    
    Responsibilities:
    - Calls underlying ChallengeGenerator to produce challenges
    - Filters challenges by confidence threshold (INT-RULE-009)
    - Sorts challenges by severity (CRITICAL → LOW)
    - Handles edge cases (empty lists, all low-confidence)
    
    Example:
        generator = ChallengeGenerator()
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.30
        )
        challenges = orchestrator.process_challenges(context)
    """
    
    def __init__(
        self,
        challenge_generator,
        confidence_threshold: float = 0.30,
    ) -> None:
        """Initialize orchestrator.
        
        Args:
            challenge_generator: Underlying challenge generator instance.
            confidence_threshold: Minimum confidence (0.0-1.0) to include challenge.
                Defaults to 0.30 per INT-RULE-009.
        
        Raises:
            ValueError: If confidence_threshold not in [0.0, 1.0].
        """
        if not (0.0 <= confidence_threshold <= 1.0):
            raise ValueError(
                f"confidence_threshold must be in [0.0, 1.0], got {confidence_threshold}"
            )
        
        self.challenge_generator = challenge_generator
        self.confidence_threshold = confidence_threshold
    
    def process_challenges(self, context: dict) -> List[Challenge]:
        """Process challenges: generate, filter, and sort.
        
        Execution flow:
        1. Call challenge_generator.generate_challenges(context)
        2. Filter by confidence >= self.confidence_threshold
        3. Sort by severity (CRITICAL first, LOW last)
        4. Return sorted, filtered list
        
        Args:
            context: Dictionary containing code context, intent, changes, etc.
        
        Returns:
            List of Challenge objects sorted by severity, filtered by confidence.
            Empty list if no challenges pass filter.
        """
        # Step 1: Generate challenges from context
        challenges = self.challenge_generator.generate_challenges(context)
        
        # Step 2: Filter by confidence threshold
        filtered = [
            c for c in challenges
            if c.confidence >= self.confidence_threshold
        ]
        
        # Step 3: Sort by severity (CRITICAL=1 first, LOW=4 last)
        sorted_challenges = sorted(
            filtered,
            key=lambda c: c.severity.value
        )
        
        return sorted_challenges
