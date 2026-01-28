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
from cortex.brain.analysis.security_threat_analyzer import (
    SecurityThreatAnalyzer,
    ThreatFinding,
    ThreatSeverity,
)

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


class GateType(Enum):
    """Types of challenge gates (Phase 8.1 - Tier-3 Logic)."""
    
    HARD = "hard"  # Blocks execution, requires explicit user response
    SOFT = "soft"  # Suggests challenge, auto-proceeds after timeout
    CONTEXT = "context"  # Asks clarifying questions


class ChallengeType(Enum):
    """Challenge types with specific gate behavior (Phase 8.1 - Tier-3 Logic)."""
    
    SECURITY = "security"  # Hard gate - security vulnerabilities
    HARMFUL = "harmful"  # Hard gate - harmful actions
    SRP_VIOLATION = "srp_violation"  # Soft gate - Single Responsibility Principle
    ARCHITECTURE_VIOLATION = "architecture_violation"  # Soft gate - architectural violations
    MISSING_CONTEXT = "missing_context"  # Context gate - missing information
    AMBIGUITY = "ambiguity"  # Context gate - ambiguous requests
    REDUNDANT_WORK = "redundant_work"  # Soft gate - work already exists


@dataclass
class ChallengeRule:
    """
    Rule for handling specific challenge type (Phase 8.1 - Tier-3 Logic).
    
    Attributes:
        challenge_type: Type of challenge
        gate_type: Hard/Soft/Context
        threshold: Confidence threshold to trigger (0.0-1.0)
        auto_proceed_ms: For soft gates, milliseconds before auto-proceeding (0 for hard gates)
        description: Human-readable description
    """
    challenge_type: ChallengeType
    gate_type: GateType
    threshold: float
    auto_proceed_ms: int
    description: str


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
        gate_type: Gate type for this challenge (Phase 8.1)
        auto_proceed_ms: Auto-proceed timeout in milliseconds (Phase 8.1)
    """
    has_disagreement: bool
    disagreement_type: Optional[DisagreementType] = None
    user_request_interpretation: str = ""
    cortex_analysis: str = ""
    recommended_alternative: str = ""
    reasoning: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)
    gate_type: Optional[GateType] = None
    auto_proceed_ms: int = 0


@dataclass
class SecurityThreatAssessment:
    """
    Security threat assessment for a request context.
    
    Phase 8.3: Integrates SecurityThreatAnalyzer findings into ChallengeEngine
    for security-first hard gates before DoR approval.
    
    Attributes:
        has_threats: Whether threats were detected
        threats: List of ThreatFinding objects
        highest_severity: Highest severity level found
        block_execution: Whether execution should be blocked (CRITICAL/HIGH threats)
        threat_summary: Human-readable summary of threats
        threat_context: Additional context (files affected, authors, etc.)
    """
    has_threats: bool
    threats: List[ThreatFinding] = field(default_factory=list)
    highest_severity: Optional[ThreatSeverity] = None
    block_execution: bool = False
    threat_summary: str = ""
    threat_context: Dict[str, Any] = field(default_factory=dict)


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
        """Initialize Challenge Engine with audit logging and Tier-3 rules."""
        self.logger = EnhancedAuditLogger.instance()
        
        # Phase 8.2: Initialize SecurityThreatAnalyzer for hard security gates
        self.security_analyzer = SecurityThreatAnalyzer()
        
        logger.info("ChallengeEngine initialized with SecurityThreatAnalyzer (Phase 8.2)")
        
        # Phase 8.1: Tier-3 Gate Logic - Define rules for each challenge type
        self.challenge_rules: Dict[ChallengeType, ChallengeRule] = {
            ChallengeType.SECURITY: ChallengeRule(
                challenge_type=ChallengeType.SECURITY,
                gate_type=GateType.HARD,
                threshold=0.4,  # Low threshold, high priority
                auto_proceed_ms=0,  # No auto-proceed for hard gates
                description="Security vulnerability detected"
            ),
            ChallengeType.HARMFUL: ChallengeRule(
                challenge_type=ChallengeType.HARMFUL,
                gate_type=GateType.HARD,
                threshold=0.5,
                auto_proceed_ms=0,
                description="Harmful action detected"
            ),
            ChallengeType.SRP_VIOLATION: ChallengeRule(
                challenge_type=ChallengeType.SRP_VIOLATION,
                gate_type=GateType.SOFT,
                threshold=0.6,
                auto_proceed_ms=10000,  # 10 second timeout
                description="Single Responsibility Principle violation"
            ),
            ChallengeType.ARCHITECTURE_VIOLATION: ChallengeRule(
                challenge_type=ChallengeType.ARCHITECTURE_VIOLATION,
                gate_type=GateType.SOFT,
                threshold=0.65,
                auto_proceed_ms=10000,
                description="Architectural constraint violation"
            ),
            ChallengeType.MISSING_CONTEXT: ChallengeRule(
                challenge_type=ChallengeType.MISSING_CONTEXT,
                gate_type=GateType.CONTEXT,
                threshold=0.5,
                auto_proceed_ms=0,
                description="Request missing critical context"
            ),
            ChallengeType.AMBIGUITY: ChallengeRule(
                challenge_type=ChallengeType.AMBIGUITY,
                gate_type=GateType.CONTEXT,
                threshold=0.7,
                auto_proceed_ms=0,
                description="Request contains ambiguity"
            ),
            ChallengeType.REDUNDANT_WORK: ChallengeRule(
                challenge_type=ChallengeType.REDUNDANT_WORK,
                gate_type=GateType.SOFT,
                threshold=0.75,
                auto_proceed_ms=10000,
                description="Work already exists"
            ),
        }
    
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
        threshold: float = 0.7,
        challenge_type: Optional[ChallengeType] = None
    ) -> ChallengeResponse:
        """
        Generate challenge if CORTEX disagrees with user's request.
        
        Phase 8.1: Supports Tier-3 gate logic with challenge_type parameter.
        
        Args:
            user_request: User's original request
            lens_context: LENS context from build_lens_context()
            threshold: Legacy confidence threshold (default: 0.7) - used if challenge_type is None
            challenge_type: Specific challenge type for Tier-3 gate logic (Phase 8.1)
            
        Returns:
            ChallengeResponse with disagreement details or no challenge
            
        Example:
            >>> challenge = engine.generate_challenge(request, context, challenge_type=ChallengeType.SRP_VIOLATION)
            >>> if challenge.has_disagreement:
            >>>     print(f"Gate: {challenge.gate_type}")
            >>>     print(f"Auto-proceed: {challenge.auto_proceed_ms}ms")
        """
        logger.info("Analyzing request for potential disagreement")
        
        # Phase 8.1: Apply Tier-3 gate logic if challenge_type specified
        if challenge_type is not None:
            return self._apply_tier3_gates(user_request, lens_context, challenge_type)
        
        # Legacy behavior: use threshold parameter
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
    
    def _apply_tier3_gates(
        self,
        user_request: str,
        lens_context: LENSContext,
        challenge_type: ChallengeType
    ) -> ChallengeResponse:
        """
        Apply Tier-3 gate logic for specific challenge type.
        
        Phase 8.1: Routes challenges through hard/soft/context gates based on
        violation type and confidence score.
        
        Args:
            user_request: User's original request
            lens_context: LENS context
            challenge_type: Type of challenge to apply gate logic for
            
        Returns:
            ChallengeResponse with gate_type and auto_proceed_ms populated
        """
        logger.info("Applying Tier-3 gate logic for challenge type: %s", challenge_type.value)
        
        # Look up rule for this challenge type
        if challenge_type not in self.challenge_rules:
            logger.warning("No rule found for challenge type: %s", challenge_type.value)
            return ChallengeResponse(has_disagreement=False)
        
        rule = self.challenge_rules[challenge_type]
        
        # Check if confidence meets threshold
        if lens_context.confidence < rule.threshold:
            logger.info(
                "Confidence %.2f below threshold %.2f for %s - no challenge",
                lens_context.confidence,
                rule.threshold,
                challenge_type.value
            )
            return ChallengeResponse(has_disagreement=False)
        
        logger.info("Confidence %.2f meets threshold %.2f", lens_context.confidence, rule.threshold)
        
        # Map ChallengeType to DisagreementType for backward compatibility
        disagreement_type_map = {
            ChallengeType.SECURITY: DisagreementType.HARMFUL_ACTION,
            ChallengeType.HARMFUL: DisagreementType.HARMFUL_ACTION,
            ChallengeType.SRP_VIOLATION: DisagreementType.BETTER_SOLUTION,
            ChallengeType.ARCHITECTURE_VIOLATION: DisagreementType.ARCHITECTURAL_VIOLATION,
            ChallengeType.MISSING_CONTEXT: DisagreementType.MISSING_CONTEXT,
            ChallengeType.AMBIGUITY: DisagreementType.MISSING_CONTEXT,
            ChallengeType.REDUNDANT_WORK: DisagreementType.REDUNDANT_WORK,
        }
        
        disagreement_type = disagreement_type_map.get(
            challenge_type,
            DisagreementType.BETTER_SOLUTION
        )
        
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
        
        # Generate options based on gate type
        options = self._generate_tier3_options(challenge_type, rule.gate_type)
        
        # Create response with gate information
        challenge = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=disagreement_type,
            user_request_interpretation=lens_context.language,
            cortex_analysis=lens_context.synthesis,
            recommended_alternative=alternative,
            reasoning=reasoning,
            evidence=evidence,
            options=options,
            gate_type=rule.gate_type,
            auto_proceed_ms=rule.auto_proceed_ms
        )
        
        logger.info(
            "Challenge generated: type=%s, gate=%s, auto_proceed=%dms",
            challenge_type.value,
            rule.gate_type.value,
            rule.auto_proceed_ms
        )
        
        self.logger.log_operation_complete(
            ac_id="AC-CHALLENGE-SYSTEM-001",
            operation="TIER3_GATE_APPLIED",
            success=True,
            details={
                "challenge_type": challenge_type.value,
                "gate_type": rule.gate_type.value,
                "confidence": lens_context.confidence,
                "threshold": rule.threshold,
                "auto_proceed_ms": rule.auto_proceed_ms
            }
        )
        
        return challenge
    
    def _generate_tier3_options(
        self,
        challenge_type: ChallengeType,
        gate_type: GateType
    ) -> List[str]:
        """
        Generate options for user based on gate type.
        
        Hard gates: Accept / Reject / Cancel
        Soft gates: Accept / Reject / Proceed anyway / Cancel
        Context gates: Provide context / Clarify / Proceed / Cancel
        """
        if gate_type == GateType.HARD:
            return [
                "1. Accept CORTEX recommendation and proceed",
                "2. Reject and try alternative approach",
                "3. Cancel and review manually"
            ]
        elif gate_type == GateType.SOFT:
            return [
                "1. Accept CORTEX recommendation",
                "2. Modify request and retry",
                "3. Acknowledge risk and proceed anyway",
                "4. Cancel and review"
            ]
        elif gate_type == GateType.CONTEXT:
            return [
                "1. Provide additional context",
                "2. Clarify ambiguous parts",
                "3. Accept CORTEX interpretation and proceed",
                "4. Cancel"
            ]
        
        return ["1. Accept", "2. Reject", "3. Cancel"]
    
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
            lines.append("")
            
            # Emoji indicators for quick visual scanning
            emoji_indicators = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for i, option in enumerate(challenge.options, 1):
                emoji = emoji_indicators[i - 1] if i <= len(emoji_indicators) else f"{i}."
                lines.append(f"{emoji} {option}")
            
            lines.append("")
            lines.append("Reply with: `1` / `2` / `3` (or your choice)")
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
        """
        Synthesize all LENS phases into understanding.
        
        AC-FUTURE-002: Context synthesis
        
        Args:
            language: Language phase output
            examination: Examination phase results
            navigation: Navigation paths found
            
        Returns:
            Tuple of (synthesis_text, confidence_score)
        """
        # Build synthesis from available data
        parts = []
        if language:
            parts.append(f"Language: {language[:100]}")
        
        exam_sources = 0
        if isinstance(examination, dict):
            exam_sources = (
                len(examination.get("code_found", [])) +
                len(examination.get("tests_found", [])) +
                len(examination.get("docs_found", []))
            )
        
        parts.append(f"Examined {exam_sources} sources")
        
        if navigation:
            parts.append(f"Navigation: {len(navigation)} paths explored")
        
        synthesis = "; ".join(parts)
        
        # Calculate confidence based on data availability
        # Base: 0.3 (always some confidence from language parsing)
        confidence = 0.3
        
        # Add confidence for each examination source found
        confidence += min(0.3, exam_sources * 0.1)  # Up to 0.3 from sources
        
        # Add confidence for navigation paths
        confidence += min(0.2, len(navigation) * 0.05)  # Up to 0.2 from navigation
        
        # Cap at 0.95 (never fully certain)
        confidence = min(0.95, confidence)
        
        return synthesis, confidence
    
    def _detect_disagreement(
        self,
        request: str,
        context: LENSContext
    ) -> Optional[DisagreementType]:
        """
        Detect if there's a disagreement and classify it.
        
        AC-FUTURE-002: Real disagreement detection logic
        
        Analyzes request for 5 types:
        1. BETTER_SOLUTION - CORTEX has superior approach (TDD, design patterns)
        2. MISSING_CONTEXT - Request too vague or missing critical info
        3. HARMFUL_ACTION - Request would cause damage/data loss
        4. REDUNDANT_WORK - Feature already exists, reimplementation unnecessary
        5. ARCHITECTURAL_VIOLATION - Breaks CORE rules or design principles
        
        Returns:
            DisagreementType if disagreement detected, None otherwise
        """
        request_lower = request.lower().strip()
        
        # Check 1: ARCHITECTURAL_VIOLATION patterns
        # CORE-028/CORE-038: .md files must be in docs/
        if ".md" in request_lower and ("root" in request_lower or "outside docs" in request_lower):
            logger.info("Detected ARCHITECTURAL_VIOLATION: .md file outside docs/")
            return DisagreementType.ARCHITECTURAL_VIOLATION
        
        # CORE-039: MD file generation prohibition
        if ("generate" in request_lower or "create" in request_lower) and ".md" in request_lower:
            if "docs/" not in request_lower and "documentation" not in request_lower:
                logger.info("Detected ARCHITECTURAL_VIOLATION: MD generation outside docs/")
                return DisagreementType.ARCHITECTURAL_VIOLATION
        
        # CORE-035: No duplicate implementations
        if any(dup in request_lower for dup in ["duplicate", "copy", "replicate", "redo", "remake"]):
            if "existing" in request_lower or "already" in request_lower:
                logger.info("Detected REDUNDANT_WORK: Attempting duplicate of existing feature")
                return DisagreementType.REDUNDANT_WORK
        
        # Check 2: HARMFUL_ACTION patterns
        harmful_keywords = [
            "delete all", "remove all", "drop all", "truncate all",
            "destroy", "wipe", "erase", "production data",
            "lose", "corruption", "downtime"
        ]
        if any(keyword in request_lower for keyword in harmful_keywords):
            logger.info("Detected HARMFUL_ACTION: Request appears dangerous")
            return DisagreementType.HARMFUL_ACTION
        
        # Check 3: BETTER_SOLUTION patterns
        # TDD is better than writing code without tests
        if "without" in request_lower and "test" in request_lower:
            logger.info("Detected BETTER_SOLUTION: Code without tests detected")
            return DisagreementType.BETTER_SOLUTION
        
        if "write code" in request_lower and "test" not in request_lower:
            # Check if TDD would be better
            if context.confidence > 0.5:
                logger.info("Detected BETTER_SOLUTION: Recommending TDD approach")
                return DisagreementType.BETTER_SOLUTION
        
        # Design pattern violations
        if any(anti in request_lower for anti in ["bare except", "global variable", "super long function"]):
            logger.info("Detected BETTER_SOLUTION: Anti-pattern detected")
            return DisagreementType.BETTER_SOLUTION
        
        # Check 4: MISSING_CONTEXT patterns
        vague_patterns = [
            ("fix", "bug", ["fix the bug", "fix it", "fix this"]),
            ("implement", "feature", ["implement feature", "add feature", "implement it"]),
            ("refactor", "code", ["refactor code", "improve it", "make it better"]),
        ]
        
        for keyword, concept, patterns in vague_patterns:
            if any(pattern in request_lower for pattern in patterns):
                # Check if request is too vague (no specific details)
                if len(request) < 20 or request_lower.count(" ") < 3:
                    logger.info("Detected MISSING_CONTEXT: Vague request - %s", request)
                    return DisagreementType.MISSING_CONTEXT
        
        # Check 5: REDUNDANT_WORK patterns (more specific)
        redundant_patterns = [
            "reimplement", "recreate", "rebuild", "rewrite from scratch",
            "reinvent", "redo the", "start over with"
        ]
        if any(pattern in request_lower for pattern in redundant_patterns):
            if "already" in context.synthesis.lower() or "exists" in context.synthesis.lower():
                logger.info("Detected REDUNDANT_WORK: Reimplementation of existing feature")
                return DisagreementType.REDUNDANT_WORK
        
        # No clear disagreement detected
        logger.info("No disagreement detected for request: %s", request[:50])
        return None
    
    def _generate_alternative(
        self,
        request: str,
        context: LENSContext,
        disagreement: DisagreementType
    ) -> str:
        """
        Generate alternative approach based on disagreement type.
        
        AC-FUTURE-002: Alternative generation
        
        Args:
            request: Original user request
            context: LENS context with analysis
            disagreement: Type of disagreement detected
            
        Returns:
            Recommended alternative approach
        """
        if disagreement == DisagreementType.BETTER_SOLUTION:
            if "test" in request.lower() or "tdd" in request.lower():
                return (
                    "Use Test-Driven Development (TDD): Write tests FIRST, then implementation. "
                    "This ensures better design, higher test coverage, and fewer bugs. "
                    "Follow CORE-008 governance rule."
                )
            return (
                "Reconsider approach to align with CORTEX best practices: "
                "Design patterns, type hints, proper error handling, and code organization."
            )
        
        elif disagreement == DisagreementType.MISSING_CONTEXT:
            return (
                "Please provide more specific details: "
                "What is the specific bug/feature? What is the expected behavior? "
                "What have you already tried? Any error messages or logs?"
            )
        
        elif disagreement == DisagreementType.HARMFUL_ACTION:
            return (
                "This action could cause data loss or system damage. "
                "Recommended: Create backup first, test on non-production environment, "
                "implement safeguards (soft delete, audit trail), or reconsider necessity."
            )
        
        elif disagreement == DisagreementType.REDUNDANT_WORK:
            return (
                "This feature or functionality already exists. "
                "Recommended: Use existing implementation, extend it if needed, "
                "or explain why reimplementation is necessary."
            )
        
        elif disagreement == DisagreementType.ARCHITECTURAL_VIOLATION:
            return (
                "This violates CORTEX architectural principles or governance rules. "
                "Recommended: Follow proper file placement (CORE-038), file type restrictions (CORE-039), "
                "and design patterns established in the codebase."
            )
        
        return "Alternative approach not yet determined. Please clarify your request."
    
    def _build_reasoning(
        self,
        context: LENSContext,
        disagreement: DisagreementType,
        alternative: str
    ) -> str:
        """
        Build explanation of why alternative is better.
        
        AC-FUTURE-002: Reasoning generation
        
        Args:
            context: LENS context with confidence and analysis
            disagreement: Type of disagreement
            alternative: Proposed alternative
            
        Returns:
            Explanation of why alternative is better
        """
        confidence_pct = int(context.confidence * 100)
        
        if disagreement == DisagreementType.BETTER_SOLUTION:
            return (
                f"CORTEX analysis (confidence: {confidence_pct}%) suggests a better approach. "
                f"Based on project standards and best practices in CORTEX codebase, "
                f"the recommended approach is more maintainable, testable, and aligns with governance rules."
            )
        
        elif disagreement == DisagreementType.MISSING_CONTEXT:
            return (
                f"Your request is too general to execute properly (analysis confidence: {confidence_pct}%). "
                f"Additional context would help CORTEX provide a more accurate and comprehensive solution. "
                f"This also helps prevent mistakes and ensures what you ask for is actually what you need."
            )
        
        elif disagreement == DisagreementType.HARMFUL_ACTION:
            return (
                f"CORTEX detected potentially destructive operation (confidence: {confidence_pct}%). "
                f"This could result in data loss, system downtime, or other severe consequences. "
                f"Caution is strongly recommended - implement safeguards and test thoroughly first."
            )
        
        elif disagreement == DisagreementType.REDUNDANT_WORK:
            return (
                f"CORTEX analysis ({confidence_pct}% confidence) indicates similar or identical "
                f"functionality already exists in the codebase. Reimplementation creates maintenance burden, "
                f"increases bugs, and violates DRY (Don't Repeat Yourself) principle."
            )
        
        elif disagreement == DisagreementType.ARCHITECTURAL_VIOLATION:
            return (
                f"This violates established architectural patterns and governance rules "
                f"(confidence: {confidence_pct}%). CORTEX enforces file placement (CORE-038), "
                f"file restrictions (CORE-039), and design principles to maintain codebase integrity."
            )
        
        return f"Analysis confidence: {confidence_pct}%. See evidence section for details."
    
    def _extract_evidence(
        self,
        context: LENSContext
    ) -> Dict[str, Any]:
        """
        Extract supporting evidence from LENS context.
        
        AC-FUTURE-002: Evidence extraction
        
        Args:
            context: LENS context with examination data
            
        Returns:
            Dict with evidence items (code locations, patterns, confidence)
        """
        evidence: Dict[str, Any] = {
            "confidence": f"{context.confidence:.0%}",
            "sources_examined": len(context.examination) if context.examination else 0,
        }
        
        # Extract specific evidence items if available
        if context.examination:
            if isinstance(context.examination, dict):
                if context.examination.get("code_found"):
                    evidence["code_locations"] = len(context.examination.get("code_found", []))
                if context.examination.get("tests_found"):
                    evidence["tests_examined"] = len(context.examination.get("tests_found", []))
                if context.examination.get("docs_found"):
                    evidence["documentation_reviewed"] = len(context.examination.get("docs_found", []))
                if context.examination.get("git_history"):
                    evidence["git_history_length"] = len(context.examination.get("git_history", []))
        
        # Add synthesis as evidence
        if context.synthesis:
            evidence["analysis"] = context.synthesis[:200]  # First 200 chars
        
        return evidence
    
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
    
    def assess_security_threats(
        self,
        code_context: str,
        file_path: str = "user_request.py",
    ) -> SecurityThreatAssessment:
        """
        Assess security threats in code context (Phase 8.3).
        
        Phase 8.3: Integrates SecurityThreatAnalyzer findings into challenge
        engine for hard security gates. Called automatically before DoR gate
        if code analysis is available.
        
        Returns:
            SecurityThreatAssessment with threats, severity, and block flag
            
        Example:
            >>> assessment = engine.assess_security_threats("eval(user_input)")
            >>> if assessment.block_execution:
            >>>     print("⛔ BLOCKED: CWE-94 detected")
            >>>     for threat in assessment.threats:
            >>>         print(f"  - {threat.cwe_id}: {threat.description}")
        """
        logger.info("Assessing security threats in code context (Phase 8.3)")
        
        # Run security analysis
        result = self.security_analyzer.analyze_code(code_context, file_path)
        
        if not result.success:
            logger.warning("Security analysis failed: %s", result.error)
            return SecurityThreatAssessment(
                has_threats=False,
                threats=[],
                highest_severity=None,
                block_execution=False,
                threat_summary="Security analysis could not be completed",
                threat_context={"error": result.error}
            )
        
        # Determine highest severity
        if not result.threat_findings:
            return SecurityThreatAssessment(
                has_threats=False,
                threats=[],
                highest_severity=None,
                block_execution=False,
                threat_summary="No security threats detected",
                threat_context={
                    "patterns_checked": result.patterns_checked,
                    "analysis_time_ms": result.analysis_time_ms
                }
            )
        
        # Find highest severity
        highest_severity = max(
            (t.severity for t in result.threat_findings),
            default=ThreatSeverity.INFO
        )
        
        # Determine if execution should be blocked (CRITICAL or HIGH with CWE-94, CWE-95, CWE-78)
        block_execution = (
            highest_severity == ThreatSeverity.CRITICAL or
            any(t.cwe_id in ["CWE-94", "CWE-95", "CWE-78"] for t in result.threat_findings)
        )
        
        # Build threat summary
        threat_counts = {}
        for threat in result.threat_findings:
            key = f"{threat.cwe_id} ({threat.severity.name})"
            threat_counts[key] = threat_counts.get(key, 0) + 1
        
        summary_items = [f"{key}: {count}" for key, count in threat_counts.items()]
        threat_summary = f"Found {len(result.threat_findings)} threat(s): {', '.join(summary_items)}"
        
        # Log to audit trail
        self.logger.log_operation_complete(
            ac_id="AC-SECURITY-FRAMEWORK-001",
            operation="SECURITY_THREAT_ASSESSMENT",
            success=True,
            details={
                "threat_count": len(result.threat_findings),
                "highest_severity": highest_severity.name,
                "block_execution": block_execution,
                "analysis_time_ms": result.analysis_time_ms,
            }
        )
        
        return SecurityThreatAssessment(
            has_threats=True,
            threats=result.threat_findings,
            highest_severity=highest_severity,
            block_execution=block_execution,
            threat_summary=threat_summary,
            threat_context={
                "patterns_checked": result.patterns_checked,
                "analysis_time_ms": result.analysis_time_ms,
                "file_path": file_path,
            }
        )


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
