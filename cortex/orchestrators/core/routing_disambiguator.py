"""
Routing Disambiguator - ROUTE-005

Handles ambiguous routing scenarios where multiple orchestrators match with similar confidence.
Provides user interface for selecting between top candidates.

Features:
- Ambiguity detection based on confidence gap threshold
- Formatted disambiguation prompts with top 3 candidates
- User selection application
- Audit trail logging for CORE-027 compliance

AC-IDs: ROUTE-005-AC01, ROUTE-005-AC02

CORE Governance:
  - CORE-008: TDD (tests written first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Date: 2026-01-30
"""

from typing import List, Tuple, Optional, Any
from dataclasses import dataclass, field

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.models.canonical_enums import IntentType


@dataclass
class DisambiguationResult:
    """
    Result of routing disambiguation analysis.
    
    Attributes:
        is_ambiguous: Whether routing is ambiguous
        top_candidates: Top orchestrator candidates with confidence scores
        confidence_gap: Gap between top two candidates (0.0-1.0)
        selected_orchestrator: User-selected orchestrator (after apply_user_selection)
        prompt: Formatted disambiguation prompt
    """
    is_ambiguous: bool
    top_candidates: List[Tuple[Any, float]]
    confidence_gap: float
    selected_orchestrator: Optional[Any] = None
    prompt: str = ""


class RoutingDisambiguator:
    """
    Handles disambiguation when multiple orchestrators match with similar confidence.
    
    Detects ambiguous routing scenarios and provides formatted prompts for user selection.
    
    Example:
        disambiguator = RoutingDisambiguator(ambiguity_threshold=0.1)
        
        candidates = [
            (tdd_orchestrator, 0.75),
            (intent_router, 0.72),  # Gap of 0.03 < 0.1 → ambiguous
            (master_orchestrator, 0.68),
        ]
        
        if disambiguator.detect_ambiguous_routing(candidates):
            prompt = disambiguator.format_disambiguation_prompt(candidates)
            print(prompt)
            selection = int(input("Select orchestrator: "))
            orchestrator = disambiguator.apply_user_selection(selection, candidates)
    
    CORE Governance:
      - CORE-008: TDD (tests first)
      - CORE-011: Type hints on all methods
      - CORE-012: Docstrings (Google style)
      - CORE-027: Audit trail for all disambiguation events
    """
    
    DEFAULT_AMBIGUITY_THRESHOLD = 0.1
    MAX_CANDIDATES_TO_DISPLAY = 3
    
    def __init__(
        self,
        ambiguity_threshold: float = DEFAULT_AMBIGUITY_THRESHOLD,
        max_candidates: int = MAX_CANDIDATES_TO_DISPLAY
    ) -> None:
        """
        Initialize RoutingDisambiguator.
        
        Args:
            ambiguity_threshold: Minimum confidence gap to avoid ambiguity (default: 0.1)
            max_candidates: Maximum candidates to display in prompt (default: 3)
        
        Raises:
            RuntimeError: If audit logger cannot be initialized
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self.ambiguity_threshold = ambiguity_threshold
        self.max_candidates = max_candidates
        
        self.logger.log_operation_complete(
            ac_id="AC-ROUTE-005",
            operation="DISAMBIGUATOR_INIT",
            success=True,
            details={
                "ambiguity_threshold": ambiguity_threshold,
                "max_candidates": max_candidates
            }
        )
    
    def detect_ambiguous_routing(
        self,
        candidates: List[Tuple[Any, float]]
    ) -> bool:
        """
        Detect if routing is ambiguous based on confidence gap.
        
        Ambiguous conditions:
        - Less than 2 candidates → not ambiguous
        - Confidence gap < threshold → ambiguous
        - Single clear winner → not ambiguous
        
        Args:
            candidates: List of (orchestrator, confidence) tuples, sorted by confidence desc
        
        Returns:
            bool: True if ambiguous, False otherwise
        
        Example:
            candidates = [(orch1, 0.75), (orch2, 0.72)]  # Gap 0.03
            is_ambiguous = disambiguator.detect_ambiguous_routing(candidates)
            # Returns True if threshold is 0.1 (0.03 < 0.1)
        """
        # Edge cases
        if len(candidates) == 0:
            return False
        
        if len(candidates) == 1:
            return False
        
        # Check confidence gap between top two
        top_confidence = candidates[0][1]
        second_confidence = candidates[1][1]
        gap = abs(top_confidence - second_confidence)
        
        is_ambiguous = gap < self.ambiguity_threshold
        
        # Log detection
        self.logger.log_operation_complete(
            ac_id="AC-ROUTE-005-AC01",
            operation="AMBIGUITY_DETECTION",
            success=True,
            details={
                "is_ambiguous": is_ambiguous,
                "confidence_gap": gap,
                "threshold": self.ambiguity_threshold,
                "num_candidates": len(candidates)
            }
        )
        
        return is_ambiguous
    
    def format_disambiguation_prompt(
        self,
        candidates: List[Tuple[Any, float]],
        intent_type: Optional[IntentType] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Format disambiguation prompt for user selection.
        
        Displays top N candidates with:
        - Numbered options (0, 1, 2, ...)
        - Orchestrator name
        - Description (if available)
        - Confidence score (percentage)
        
        Args:
            candidates: List of (orchestrator, confidence) tuples
            intent_type: Optional intent type for context
            description: Optional operation description
        
        Returns:
            str: Formatted prompt text
        
        Example:
            prompt = disambiguator.format_disambiguation_prompt(
                candidates,
                intent_type=IntentType.IMPLEMENT,
                description="Implement user authentication"
            )
            
            Output:
            '''
            🔀 Ambiguous Routing Detected for IMPLEMENT operation:
            "Implement user authentication"
            
            Select orchestrator:
            [0] TDDOrchestrator (75% confidence)
                Test-Driven Development orchestrator
            [1] IntentRouter (72% confidence)
                Intent routing and classification
            [2] MasterOrchestrator (68% confidence)
                Master coordination
            
            Enter selection (0-2):
            '''
        """
        # Handle empty candidates
        if len(candidates) == 0:
            return "❌ No orchestrator candidates available"
        
        # Limit to max_candidates
        display_candidates = candidates[:self.max_candidates]
        
        # Build prompt header
        lines = ["🔀 Ambiguous Routing Detected"]
        
        if intent_type:
            lines.append(f"Operation type: {intent_type.value}")
        
        if description:
            lines.append(f'Description: "{description}"')
        
        lines.append("")
        lines.append("Select orchestrator:")
        
        # Add candidates
        for idx, (orchestrator, confidence) in enumerate(display_candidates):
            # Get orchestrator info
            orch_name = getattr(orchestrator, 'name', str(orchestrator))
            orch_desc = getattr(orchestrator, 'description', '')
            
            # Format confidence as percentage
            confidence_pct = int(confidence * 100)
            
            lines.append(f"[{idx}] {orch_name} ({confidence_pct}% confidence)")
            
            if orch_desc:
                lines.append(f"    {orch_desc}")
        
        lines.append("")
        lines.append(f"Enter selection (0-{len(display_candidates) - 1}):")
        
        prompt = "\n".join(lines)
        
        # Log prompt generation
        self.logger.log_operation_complete(
            ac_id="AC-ROUTE-005-AC02",
            operation="PROMPT_FORMAT",
            success=True,
            details={
                "num_candidates": len(display_candidates),
                "intent_type": intent_type.value if intent_type else None,
                "has_description": description is not None
            }
        )
        
        return prompt
    
    def apply_user_selection(
        self,
        selection: int,
        candidates: List[Tuple[Any, float]]
    ) -> Any:
        """
        Apply user selection to return selected orchestrator.
        
        Args:
            selection: Index of selected candidate (0-based)
            candidates: List of (orchestrator, confidence) tuples
        
        Returns:
            Any: Selected orchestrator instance
        
        Raises:
            IndexError: If selection is out of bounds
            ValueError: If candidates list is empty
        
        Example:
            selected = disambiguator.apply_user_selection(1, candidates)
            # Returns candidates[1][0] (the orchestrator at index 1)
        """
        if len(candidates) == 0:
            raise ValueError("Cannot apply selection to empty candidates list")
        
        if selection < 0 or selection >= len(candidates):
            raise IndexError(
                f"Selection {selection} out of bounds for {len(candidates)} candidates. "
                f"Valid range: 0-{len(candidates) - 1}"
            )
        
        selected_orchestrator = candidates[selection][0]
        selected_confidence = candidates[selection][1]
        
        # Log selection
        self.logger.log_operation_complete(
            ac_id="AC-ROUTE-005-AC02",
            operation="USER_SELECTION_APPLIED",
            success=True,
            details={
                "selection_index": selection,
                "selected_orchestrator": getattr(selected_orchestrator, 'name', str(selected_orchestrator)),
                "confidence": selected_confidence,
                "total_candidates": len(candidates)
            }
        )
        
        return selected_orchestrator
    
    def disambiguate(
        self,
        candidates: List[Tuple[Any, float]],
        intent_type: Optional[IntentType] = None,
        description: Optional[str] = None
    ) -> DisambiguationResult:
        """
        Perform complete disambiguation analysis.
        
        Detects ambiguity, formats prompt, and returns structured result.
        Does NOT apply user selection (that requires interactive input).
        
        Args:
            candidates: List of (orchestrator, confidence) tuples
            intent_type: Optional intent type for context
            description: Optional operation description
        
        Returns:
            DisambiguationResult: Structured disambiguation result
        
        Example:
            result = disambiguator.disambiguate(candidates, IntentType.IMPLEMENT)
            
            if result.is_ambiguous:
                print(result.prompt)
                selection = int(input())
                orchestrator = disambiguator.apply_user_selection(selection, candidates)
        """
        is_ambiguous = self.detect_ambiguous_routing(candidates)
        
        # Calculate confidence gap
        if len(candidates) >= 2:
            gap = abs(candidates[0][1] - candidates[1][1])
        else:
            gap = 1.0  # Single candidate, perfect clarity
        
        # Format prompt
        prompt = ""
        if is_ambiguous:
            prompt = self.format_disambiguation_prompt(candidates, intent_type, description)
        
        # Top candidates (limit to max_candidates)
        top_candidates = candidates[:self.max_candidates]
        
        result = DisambiguationResult(
            is_ambiguous=is_ambiguous,
            top_candidates=top_candidates,
            confidence_gap=gap,
            prompt=prompt
        )
        
        # Log complete disambiguation
        self.logger.log_operation_complete(
            ac_id="AC-ROUTE-005",
            operation="DISAMBIGUATION_COMPLETE",
            success=True,
            details={
                "is_ambiguous": is_ambiguous,
                "confidence_gap": gap,
                "num_candidates": len(candidates)
            }
        )
        
        return result


# Module-level exports
__all__ = [
    "RoutingDisambiguator",
    "DisambiguationResult",
]
