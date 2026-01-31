"""
Phase 8.3: Disambiguation UI for Ambiguous Routing

Interactive component to resolve routing ambiguity when multiple
orchestrators match a user request with similar confidence.

AC-ID: AC-PHASE-8.3-02 (Task SEMANTIC-002)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from cortex.orchestrators.core.semantic_ranking import RankedCandidate
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class DisambiguationResult:
    """
    Result of disambiguation interaction.
    
    Attributes:
        selected_candidate: User-selected orchestrator
        selection_method: How selection was made (interactive/auto/fallback)
        user_feedback: Optional feedback on why this selection
        timestamp: When disambiguation occurred
    """
    selected_candidate: RankedCandidate
    selection_method: str
    user_feedback: Optional[str] = None
    timestamp: Optional[str] = None


class DisambiguationUI:
    """
    Interactive UI for resolving routing ambiguity.
    
    Shows top 3-5 candidates with confidence scores and match reasons,
    allows user to select correct orchestrator.
    
    Example:
        ui = DisambiguationUI()
        result = ui.prompt_selection(candidates, context)
        
        # Returns DisambiguationResult with selected orchestrator
        selected_orch = result.selected_candidate.orchestrator_instance
    """
    
    def __init__(self, auto_select_threshold: float = 0.9) -> None:
        """
        Initialize disambiguation UI.
        
        Args:
            auto_select_threshold: Auto-select if top candidate > threshold
        """
        self.logger = EnhancedAuditLogger.instance()
        self.auto_select_threshold = auto_select_threshold
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.3-02",
            operation="DISAMBIGUATION_UI_INIT",
            success=True,
            details={"auto_select_threshold": auto_select_threshold},
        )
    
    def prompt_selection(
        self,
        candidates: List[RankedCandidate],
        context: Dict[str, Any],
    ) -> DisambiguationResult:
        """
        Prompt user to select from multiple candidates.
        
        AC-PHASE-8.3-02: Interactive disambiguation with confidence display
        
        Args:
            candidates: List of ranked candidates (2-5)
            context: Original request context
        
        Returns:
            DisambiguationResult: User selection result
        
        Raises:
            ValueError: If no candidates provided
        """
        if not candidates:
            raise ValueError("No candidates provided for disambiguation")
        
        try:
            # Auto-select if top candidate confidence is very high
            if candidates[0].total_confidence >= self.auto_select_threshold:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-8.3-02",
                    operation="DISAMBIGUATION_AUTO_SELECT",
                    success=True,
                    details={
                        "selected": candidates[0].orchestrator_name,
                        "confidence": candidates[0].total_confidence,
                    },
                )
                
                return DisambiguationResult(
                    selected_candidate=candidates[0],
                    selection_method="auto",
                    user_feedback="Auto-selected due to high confidence",
                )
            
            # Build disambiguation message
            message = self._build_disambiguation_message(candidates, context)
            
            # In production, this would integrate with user interface
            # For now, return top candidate with metadata
            selected = candidates[0]
            
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.3-02",
                operation="DISAMBIGUATION_FALLBACK",
                success=True,
                details={
                    "selected": selected.orchestrator_name,
                    "confidence": selected.total_confidence,
                    "candidates_shown": len(candidates),
                },
            )
            
            return DisambiguationResult(
                selected_candidate=selected,
                selection_method="fallback",
                user_feedback=message,
            )
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.3-02",
                operation="DISAMBIGUATION_ERROR",
                success=False,
                details={"error": str(e)},
            )
            raise
    
    def _build_disambiguation_message(
        self,
        candidates: List[RankedCandidate],
        context: Dict[str, Any],
    ) -> str:
        """
        Build user-friendly disambiguation message.
        
        Args:
            candidates: Candidates to display
            context: Original request context
        
        Returns:
            str: Formatted disambiguation message
        """
        description = context.get("description", "your request")
        
        lines = [
            f"Multiple orchestrators can handle {description!r}:",
            "",
        ]
        
        for i, candidate in enumerate(candidates, 1):
            conf_pct = int(candidate.total_confidence * 100)
            lines.append(f"{i}. {candidate.orchestrator_name} ({conf_pct}% confidence)")
            
            # Show top 2 match reasons
            for reason in candidate.match_reasons[:2]:
                lines.append(f"   - {reason}")
            
            lines.append("")
        
        lines.append("Defaulting to top candidate (highest confidence).")
        
        return "\n".join(lines)
    
    def format_candidate_details(self, candidate: RankedCandidate) -> str:
        """
        Format candidate details for display.
        
        AC-PHASE-8.3-02: Human-readable candidate information
        
        Args:
            candidate: Candidate to format
        
        Returns:
            str: Formatted candidate details
        """
        lines = [
            f"Orchestrator: {candidate.orchestrator_name}",
            f"Confidence: {candidate.total_confidence:.2%}",
            f"  - Keyword match: {candidate.base_confidence:.2%}",
            f"  - Semantic analysis: {candidate.semantic_score:.2%}",
            "",
            "Match Reasons:",
        ]
        
        for reason in candidate.match_reasons:
            lines.append(f"  • {reason}")
        
        return "\n".join(lines)
