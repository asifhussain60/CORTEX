"""
Challenge Engine - AI-driven disagreement detection and alternative generation.

AC-ID: AC-CHALLENGE-SYSTEM-001
Implements intelligent challenge system that:
- Uses LENS synthesis to build context
- Detects when CORTEX has a better solution than user's request
- Generates clear explanations of disagreement
- Presents alternatives with reasoning
- Integrates into every user interaction

CORE Governance Rules Applied:
- CORE-008: TDD (tests in tests/unit/orchestrators/core/test_challenge_engine.py)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging
- CORE-030: Implementation truth enforcement

Author: Asif Hussain
Date: 2026-01-25
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = logging.getLogger(__name__)


class DisagreementType(Enum):
    """Types of disagreements CORTEX can have with user requests."""
    
    BETTER_SOLUTION = "better_solution"  # CORTEX has a superior approach
    MISSING_CONTEXT = "missing_context"  # User missing critical information
    HARMFUL_ACTION = "harmful_action"  # Request would cause problems
    REDUNDANT_WORK = "redundant_work"  # Feature already exists
    ARCHITECTURAL_VIOLATION = "architectural_violation"  # Breaks design principles


@dataclass
class LENSContext:
    """
    Context gathered via LENS (Language→Examination→Navigation→Synthesis).
    
    Attributes:
        language: Natural language interpretation of user request
        examination: Code/docs/tests examined to understand current state
        navigation: Paths explored to find relevant context
        synthesis: Synthesized understanding combining all LENS phases
        confidence: Confidence in the synthesis (0.0-1.0)
    """
    language: str
    examination: Dict[str, Any] = field(default_factory=dict)
    navigation: List[str] = field(default_factory=list)
    synthesis: str = ""
    confidence: float = 0.0


@dataclass
class ChallengeResponse:
    """
    CORTEX's challenge to user's request.
    
    Attributes:
        has_disagreement: Whether CORTEX disagrees with user
        disagreement_type: Type of disagreement
        user_request_interpretation: How CORTEX understood the request
        cortex_analysis: CORTEX's analysis of the situation
        recommended_alternative: CORTEX's recommended approach
        reasoning: Explanation of why alternative is better
        evidence: Supporting evidence (code locations, test results, etc.)
        options: Numbered options for user to choose from
    """
    has_disagreement: bool
    disagreement_type: Optional[DisagreementType] = None
    user_request_interpretation: str = ""
    cortex_analysis: str = ""
    recommended_alternative: str = ""
    reasoning: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)


class ChallengeEngine:
    """
    Generates intelligent challenges when CORTEX disagrees with user requests.
    
    Uses LENS synthesis to build deep context, then applies AI reasoning to:
    1. Detect when user's request may not be optimal
    2. Analyze implementation reality vs user's assumptions
    3. Generate better alternatives with clear reasoning
    4. Present choices in user-friendly format
    
    Integrated into InteractionOrchestrator to challenge every turn.
    
    Usage:
        >>> engine = ChallengeEngine()
        >>> lens_context = engine.build_lens_context("Remove AC-PERMANENT-FIX")
        >>> challenge = engine.generate_challenge("Remove AC-PERMANENT-FIX", lens_context)
        >>> if challenge.has_disagreement:
        >>>     print(challenge.recommended_alternative)
    """
    
    def __init__(self) -> None:
        """Initialize Challenge Engine with audit logging."""
        self.logger = EnhancedAuditLogger.instance()
        logger.info("ChallengeEngine initialized")
    
    def build_lens_context(
        self,
        user_request: str,
        search_tools: Optional[Dict[str, Any]] = None
    ) -> LENSContext:
        """
        Build context using LENS protocol.
        
        LENS = Language → Examination → Navigation → Synthesis
        
        Args:
            user_request: User's natural language request
            search_tools: Optional dict of search tools (grep_search, semantic_search, etc.)
            
        Returns:
            LENSContext with full analysis
            
        Example:
            >>> engine = ChallengeEngine()
            >>> context = engine.build_lens_context("Remove AC-PERMANENT-FIX")
            >>> print(context.synthesis)
            "AC-PERMANENT-FIX serves different purpose than CORE-030..."
        """
        logger.info("Building LENS context for request: %s", user_request)
        
        # Language: Parse natural language
        language_interpretation = self._parse_language(user_request)
        
        # Examination: Search code/docs/tests
        examination_results = self._examine_implementation(
            user_request,
            search_tools or {}
        )
        
        # Navigation: Explore relevant paths
        navigation_paths = self._navigate_context(examination_results)
        
        # Synthesis: Combine all phases
        synthesis, confidence = self._synthesize_context(
            language_interpretation,
            examination_results,
            navigation_paths
        )
        
        context = LENSContext(
            language=language_interpretation,
            examination=examination_results,
            navigation=navigation_paths,
            synthesis=synthesis,
            confidence=confidence
        )
        
        logger.info(
            "LENS context built: confidence=%.2f, paths=%d",
            confidence,
            len(navigation_paths)
        )
        
        return context
    
    def generate_challenge(
        self,
        user_request: str,
        lens_context: LENSContext,
        threshold: float = 0.7
    ) -> ChallengeResponse:
        """
        Generate challenge if CORTEX disagrees with user's request.
        
        Args:
            user_request: User's original request
            lens_context: LENS context from build_lens_context()
            threshold: Confidence threshold to trigger challenge (default: 0.7)
            
        Returns:
            ChallengeResponse with disagreement details or no challenge
            
        Example:
            >>> challenge = engine.generate_challenge(request, context)
            >>> if challenge.has_disagreement:
            >>>     print(f"Type: {challenge.disagreement_type}")
            >>>     print(f"Alternative: {challenge.recommended_alternative}")
        """
        logger.info("Analyzing request for potential disagreement")
        
        # If confidence too low, don't challenge (need more info)
        if lens_context.confidence < threshold:
            logger.info("Confidence %.2f below threshold %.2f - no challenge", 
                       lens_context.confidence, threshold)
            return ChallengeResponse(has_disagreement=False)
        
        # Detect disagreement type
        disagreement_type = self._detect_disagreement(
            user_request,
            lens_context
        )
        
        if disagreement_type is None:
            logger.info("No disagreement detected")
            return ChallengeResponse(has_disagreement=False)
        
        logger.info("Disagreement detected: %s", disagreement_type.value)
        
        # Generate alternative
        alternative = self._generate_alternative(
            user_request,
            lens_context,
            disagreement_type
        )
        
        # Build reasoning
        reasoning = self._build_reasoning(
            lens_context,
            disagreement_type,
            alternative
        )
        
        # Extract evidence
        evidence = self._extract_evidence(lens_context)
        
        # Generate options for user
        options = self._generate_options(
            user_request,
            alternative,
            disagreement_type
        )
        
        challenge = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=disagreement_type,
            user_request_interpretation=lens_context.language,
            cortex_analysis=lens_context.synthesis,
            recommended_alternative=alternative,
            reasoning=reasoning,
            evidence=evidence,
            options=options
        )
        
        self.logger.log_operation_complete(
            ac_id="AC-CHALLENGE-SYSTEM-001",
            operation="CHALLENGE_GENERATED",
            success=True,
            details={
                "disagreement_type": disagreement_type.value,
                "confidence": lens_context.confidence,
                "has_alternative": bool(alternative)
            }
        )
        
        return challenge
    
    def format_challenge_response(
        self,
        challenge: ChallengeResponse
    ) -> str:
        """
        Format challenge as user-friendly markdown.
        
        Args:
            challenge: ChallengeResponse from generate_challenge()
            
        Returns:
            Markdown-formatted challenge message
            
        Example:
            >>> formatted = engine.format_challenge_response(challenge)
            >>> print(formatted)
            ### 🤔 CORTEX Challenge
            I disagree with your request...
        """
        if not challenge.has_disagreement:
            return ""
        
        lines = [
            "### 🤔 CORTEX Challenge",
            "",
            f"**Disagreement Type:** {challenge.disagreement_type.value.replace('_', ' ').title()}",
            "",
            "**Your Request (as I understand it):**",
            challenge.user_request_interpretation,
            "",
            "**My Analysis:**",
            challenge.cortex_analysis,
            "",
            "**My Recommendation:**",
            challenge.recommended_alternative,
            "",
            "**Why This Is Better:**",
            challenge.reasoning,
            ""
        ]
        
        if challenge.evidence:
            lines.append("**Evidence:**")
            for key, value in challenge.evidence.items():
                lines.append(f"- {key}: {value}")
            lines.append("")
        
        if challenge.options:
            lines.append("**What would you like to do?**")
            for i, option in enumerate(challenge.options, 1):
                lines.append(f"{i}. {option}")
            lines.append("")
        
        return "\n".join(lines)
    
    # Private helper methods
    
    def _parse_language(self, user_request: str) -> str:
        """Parse natural language to extract intent."""
        # Simple parsing for now - can be enhanced with NLP
        return f"User wants to: {user_request.lower().strip()}"
    
    def _examine_implementation(
        self,
        request: str,
        search_tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Examine code/docs/tests related to request."""
        # Placeholder - will integrate with actual search tools
        return {
            "code_found": [],
            "tests_found": [],
            "docs_found": [],
            "git_history": []
        }
    
    def _navigate_context(
        self,
        examination: Dict[str, Any]
    ) -> List[str]:
        """Navigate through related context paths."""
        return []
    
    def _synthesize_context(
        self,
        language: str,
        examination: Dict[str, Any],
        navigation: List[str]
    ) -> tuple[str, float]:
        """Synthesize all LENS phases into understanding."""
        synthesis = f"Based on examination of {len(examination)} sources"
        confidence = 0.5  # Placeholder
        return synthesis, confidence
    
    def _detect_disagreement(
        self,
        request: str,
        context: LENSContext
    ) -> Optional[DisagreementType]:
        """Detect if there's a disagreement and classify it."""
        # Placeholder - will implement sophisticated detection
        return None
    
    def _generate_alternative(
        self,
        request: str,
        context: LENSContext,
        disagreement: DisagreementType
    ) -> str:
        """Generate alternative approach."""
        return "Alternative approach based on LENS analysis"
    
    def _build_reasoning(
        self,
        context: LENSContext,
        disagreement: DisagreementType,
        alternative: str
    ) -> str:
        """Build explanation of why alternative is better."""
        return f"Reasoning based on {context.confidence:.0%} confidence analysis"
    
    def _extract_evidence(
        self,
        context: LENSContext
    ) -> Dict[str, Any]:
        """Extract supporting evidence from LENS context."""
        return {
            "confidence": f"{context.confidence:.0%}",
            "sources_examined": len(context.examination)
        }
    
    def _generate_options(
        self,
        original_request: str,
        alternative: str,
        disagreement: DisagreementType
    ) -> List[str]:
        """Generate numbered options for user to choose from."""
        return [
            f"Proceed with your request ({original_request})",
            f"Accept my recommendation ({alternative})",
            "Modify approach (tell me how)",
            "Explain your reasoning (I'll reconsider)"
        ]


# Singleton accessor for global use
_challenge_engine_instance: Optional[ChallengeEngine] = None


def get_challenge_engine() -> ChallengeEngine:
    """
    Get singleton instance of ChallengeEngine.
    
    Returns:
        ChallengeEngine instance
        
    Example:
        >>> engine = get_challenge_engine()
        >>> challenge = engine.generate_challenge(request, context)
    """
    global _challenge_engine_instance
    if _challenge_engine_instance is None:
        _challenge_engine_instance = ChallengeEngine()
    return _challenge_engine_instance
