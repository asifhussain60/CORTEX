"""
Master Orchestrator Stage 1 (Comprehension) Implementation - AC-PROD-003-01

Stage 1 represents the Comprehension phase of the Master Orchestrator 4-stage workflow.
It analyzes operation context using LENS Protocol Phase 1 (Language Analysis) to understand
intent and produce Stage 1 output that feeds into Stage 2 (Routing).

The comprehension stage:
1. Accepts raw operation input (description, keywords, intent)
2. Runs LENS Protocol Phase 1 (Language Analysis) automatically
3. Extracts intent (IMPLEMENT, FIX, REFACTOR) and confidence
4. Produces Stage 1 output for Stage 2 routing
5. Logs all operations to audit trail

AC-PROD-003-01: Master Orchestrator Stage 1 (Comprehension) - Resolves ISSUE-003 (partial)

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class Stage1ComprehensionContext:
    """
    Input context for Stage 1 Comprehension phase.
    
    Attributes:
        operation: Operation name/identifier
        description: Human-readable operation description
        keywords: List of keywords describing operation
        domain: Target domain (api, persistence, core, etc.)
        user_intent: Optional user-stated intent
        urgency: Operation urgency (low, medium, high, critical)
        metadata: Additional context metadata
        timestamp: When context was created
        turn_number: Multi-turn conversation tracking
    """
    operation: str
    description: str
    keywords: List[str]
    domain: Optional[str] = None
    user_intent: Optional[str] = None
    urgency: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    turn_number: int = 0


@dataclass
class Stage1Output:
    """
    Output from Stage 1 Comprehension phase - ready for Stage 2 Routing.
    
    Attributes:
        operation: Original operation name
        language_analysis: Phase 1 language analysis results
        extracted_intent: Detected intent (implement, fix, refactor)
        confidence_score: Confidence in intent detection (0-1)
        domain: Target domain
        keywords: Operation keywords
        metadata: Additional analysis metadata
        timestamp: When comprehension was completed
        turn_number: Multi-turn tracking
    """
    operation: str
    language_analysis: Dict[str, Any]
    extracted_intent: str
    confidence_score: float
    domain: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    turn_number: int = 0


class MasterOrchestrationStage1:
    """
    Stage 1 (Comprehension) of Master Orchestrator 4-stage workflow.
    
    Executes LENS Protocol Phase 1 (Language Analysis) to understand operation intent.
    Transforms raw operation input into structured comprehension output ready for
    Stage 2 (Routing) decision-making.
    
    The comprehension stage:
    1. Analyzes operation description and keywords
    2. Detects intent type (IMPLEMENT, FIX, REFACTOR)
    3. Calculates confidence score
    4. Produces Stage 1 output for routing
    5. Maintains audit trail
    
    Usage:
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="implement_oauth2",
            description="Implement OAuth2 authentication",
            keywords=["oauth2", "authentication", "implement"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        if result.is_ok():
            output = result.unwrap()
            # Pass to Stage 2 routing
    
    CORE Governance:
      - CORE-008: TDD - tests created first
      - CORE-011: Type hints - all methods typed
      - CORE-012: Docstrings - Google style
      - CORE-027: Audit trail - AC_START/EXECUTE/COMPLETE
    """
    
    # Intent detection keywords by type
    IMPLEMENT_KEYWORDS = {
        "create", "add", "new", "feature", "implement", "build",
        "setup", "initialize", "construct", "develop", "design"
    }
    
    FIX_KEYWORDS = {
        "fix", "bug", "error", "repair", "issue", "problem",
        "debug", "resolve", "patch", "correct", "broken"
    }
    
    REFACTOR_KEYWORDS = {
        "refactor", "clean", "improve", "optimize", "enhance",
        "reorganize", "restructure", "streamline", "simplify",
        "modernize", "maintainability"
    }
    
    def __init__(self) -> None:
        """
        Initialize Stage 1 Comprehension.
        
        Sets up:
        - Audit logger
        - Comprehension history
        - Intent detection keywords
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self.comprehension_history: List[Dict[str, Any]] = []
        self.lens_phase_1: Optional[Any] = None
        
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-01",
            operation="STAGE_1_INIT",
            success=True,
            details={"stage": "comprehension", "intent_types": 3}
        )
    
    def comprehend(
        self,
        context: Optional[Stage1ComprehensionContext]
    ) -> Result[Stage1Output]:
        """
        Comprehend operation intent from context.
        
        Executes LENS Protocol Phase 1 (Language Analysis) to:
        1. Analyze operation description and keywords
        2. Detect intent type (IMPLEMENT, FIX, REFACTOR)
        3. Calculate confidence score
        4. Produce Stage 1 output
        
        Args:
            context: Stage1ComprehensionContext with operation details
        
        Returns:
            Result[Stage1Output]: Ok with comprehension output, or Err with message
        
        Raises:
            ValueError: If context invalid
            Exception: If comprehension fails
        """
        try:
            # Log comprehension start (AC_START)
            self.logger.log_operation_start(
                ac_id="AC-PROD-003-01",
                operation="COMPREHEND",
                details={
                    "operation": str(context.operation)[:50] if context else "None",
                    "has_keywords": bool(context and context.keywords) if context else False
                }
            )
            
            # Validate context
            validation = self._validate_context(context)
            if validation.is_err():
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-003-01",
                    operation="COMPREHEND",
                    success=False,
                    details={"error": validation.unwrap_err()}
                )
                return validation
            
            # Perform language analysis (LENS Phase 1)
            intent, confidence = self._analyze_language(context)
            
            # Build language analysis results
            language_analysis: Dict[str, Any] = {
                "intent": intent,
                "confidence": confidence,
                "keywords": context.keywords,
                "description_length": len(context.description),
                "domain": context.domain
            }
            
            # Create Stage 1 output (AC_EXECUTE)
            output = Stage1Output(
                operation=context.operation,
                language_analysis=language_analysis,
                extracted_intent=intent,
                confidence_score=confidence,
                domain=context.domain,
                keywords=context.keywords,
                metadata=context.metadata,
                turn_number=context.turn_number
            )
            
            # Store in history
            self.comprehension_history.append({
                "operation": context.operation,
                "intent": intent,
                "confidence": confidence,
                "timestamp": output.timestamp,
                "turn": context.turn_number
            })
            
            # Log comprehension complete (AC_COMPLETE)
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-01",
                operation="COMPREHEND",
                success=True,
                details={
                    "operation": context.operation,
                    "intent": intent,
                    "confidence": confidence,
                    "domain": context.domain,
                    "turn_number": context.turn_number
                }
            )
            
            return Ok(output)
        
        except ValueError as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-01",
                operation="COMPREHEND",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Comprehension validation error: {str(e)}")
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-01",
                operation="COMPREHEND",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Comprehension failed: {str(e)}")
    
    def _validate_context(
        self,
        context: Optional[Stage1ComprehensionContext]
    ) -> Result[bool]:
        """
        Validate Stage 1 context.
        
        Args:
            context: Context to validate
        
        Returns:
            Result[bool]: Ok(True) if valid, Err(message) if invalid
        """
        try:
            if context is None:
                return Err("Context cannot be None")
            
            if not isinstance(context, Stage1ComprehensionContext):
                return Err("Context must be Stage1ComprehensionContext instance")
            
            if not context.operation:
                return Err("Operation cannot be empty")
            
            if not context.description:
                return Err("Description cannot be empty")
            
            if not context.keywords or len(context.keywords) == 0:
                return Err("Keywords cannot be empty")
            
            return Ok(True)
        
        except Exception as e:
            return Err(f"Validation error: {str(e)}")
    
    def _analyze_language(
        self,
        context: Stage1ComprehensionContext
    ) -> tuple:
        """
        Analyze language to detect intent (LENS Phase 1).
        
        Examines keywords and description to detect operation intent.
        Returns intent type and confidence score.
        
        Args:
            context: Operation context
        
        Returns:
            Tuple of (intent: str, confidence: float)
        """
        # Combine keywords for analysis
        all_keywords = set(context.keywords)
        description_words = set(context.description.lower().split())
        
        # Count keyword matches
        implement_matches = len(all_keywords & self.IMPLEMENT_KEYWORDS)
        fix_matches = len(all_keywords & self.FIX_KEYWORDS)
        refactor_matches = len(all_keywords & self.REFACTOR_KEYWORDS)
        
        # Also check description
        implement_matches += len(description_words & self.IMPLEMENT_KEYWORDS)
        fix_matches += len(description_words & self.FIX_KEYWORDS)
        refactor_matches += len(description_words & self.REFACTOR_KEYWORDS)
        
        # Determine intent and confidence
        matches = [
            ("implement", implement_matches),
            ("fix", fix_matches),
            ("refactor", refactor_matches)
        ]
        
        # Sort by match count
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Get winning intent
        if matches[0][1] == 0:
            # No clear matches - default to implement with low confidence
            intent = "implement"
            confidence = 0.5
        else:
            intent, match_count = matches[0]
            
            # Calculate confidence based on match ratio
            total_keywords = len(all_keywords) + len(description_words)
            if total_keywords > 0:
                confidence = min(1.0, match_count / (total_keywords / 2))
            else:
                confidence = 0.6
            
            # Boost confidence if user intent provided
            if context.user_intent:
                confidence = min(1.0, confidence * 1.1)
        
        # Ensure confidence is in valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return intent, confidence
    
    def get_comprehension_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent comprehension results.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of recent comprehension operations
        """
        return self.comprehension_history[-limit:]


# Module exports
__all__ = [
    "MasterOrchestrationStage1",
    "Stage1ComprehensionContext",
    "Stage1Output",
]
