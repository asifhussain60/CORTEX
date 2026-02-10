"""
Orchestrator Base Protocol - Mandatory 6-phase execution for ALL orchestrators.

AC-ID: ARCH-012
Purpose: Enforce LENS → Security → Challenge → DoR → Execute → Learn pattern

This base class provides:
1. LENS Context Building (automatic on every turn)
2. Security Threat Assessment (hard gate for code context)
3. Challenge Generation (automatic when CORTEX disagrees)
4. DoR Confidence Gate (blocks execution if <60%)
5. Domain-specific execution (subclass implements)
6. Learning Capture (automatic pattern extraction - Phase 71)

All orchestrators MUST inherit from this class to ensure:
- Consistent intelligence layer (LENS synthesis)
- Security-first hard gates (Phase 8.3)
- Intelligent disagreement detection (Challenge Engine)
- Quality gates (DoR confidence threshold)
- Automatic learning capture (Universal Learning Loop)
- Audit trail compliance (CORE-027)

Governance:
- ARCH-012: Orchestrator base protocol mandatory
- CORE-008: TDD (tests in tests/unit/orchestrators/test_orchestrator_base_protocol.py)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging
- CORE-029: LENS + Challenge automatic
- AC-PERMANENT-FIX-006: Challenge system cannot be disabled
- PHASE-71-S2: Automatic learning capture

Author: Asif Hussain
Date: 2026-01-31
Updated: 2026-02-09 (Phase 71 S2 - Learning Capture)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import logging
import functools

from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


# Decorator to skip learning capture for specific orchestrators
def skip_learning(cls_or_method):
    """
    Decorator to skip automatic learning capture.
    
    Use on orchestrator class or _execute_learning_phase method
    to disable automatic learning capture for that orchestrator.
    
    Example:
        @skip_learning
        class DebugOrchestrator(OrchestratorBaseProtocol):
            pass
    
    AC-ID: PHASE-71-S2
    """
    if isinstance(cls_or_method, type):
        # Class decorator
        cls_or_method._skip_learning = True
        return cls_or_method
    else:
        # Method decorator
        @functools.wraps(cls_or_method)
        def wrapper(*args, **kwargs):
            return None  # Skip learning
        wrapper._skip_learning = True
        return wrapper

# Import Universal Learning Loop for Phase 6 (Learning Capture)
try:
    from cortex.learning import get_learning_loop, UniversalLearningLoop
except ImportError:
    get_learning_loop = None
    UniversalLearningLoop = None

# Import LENS, Challenge, DoR, Security components
try:
    from cortex.lens import LENSOrchestrator
except ImportError:
    LENSOrchestrator = None

try:
    from cortex.orchestrators.core.challenge_engine import (
        ChallengeEngine,
        LENSContext,
        ChallengeResponse,
        GateType,
    )
except ImportError:
    ChallengeEngine = None
    LENSContext = None
    ChallengeResponse = None
    GateType = None

try:
    from cortex.orchestrators.core.dor_approval_gate import (
        DoRApprovalGate,
        IntentReflection,
        DOR_CONFIDENCE_THRESHOLD,
    )
except ImportError:
    DoRApprovalGate = None
    IntentReflection = None
    DOR_CONFIDENCE_THRESHOLD = 0.6

try:
    from cortex.brain.analysis.security_threat_analyzer import (
        SecurityThreatAnalyzer,
        SecurityThreatAssessment,
    )
except ImportError:
    SecurityThreatAnalyzer = None
    SecurityThreatAssessment = None


logger = logging.getLogger(__name__)


@dataclass
class ProtocolExecutionResult:
    """
    Result of protocol execution phases.
    
    Attributes:
        phase: Phase that produced result (lens, security, challenge, dor, domain)
        success: Whether phase succeeded
        output: Phase output data
        blocked: Whether execution was blocked
        block_reason: Reason for blocking (if blocked)
        lens_context: LENS context from Phase 1
        security_assessment: Security assessment from Phase 2 (if applicable)
        challenge: Challenge from Phase 3 (if disagreement)
        dor_reflection: DoR reflection from Phase 4
    """
    phase: str
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    block_reason: str = ""
    lens_context: Optional[Any] = None
    security_assessment: Optional[Any] = None
    challenge: Optional[Any] = None
    dor_reflection: Optional[Any] = None


class OrchestratorBaseProtocol(ABC):
    """
    Mandatory base class for ALL CORTEX orchestrators.
    
    Enforces 4-phase execution protocol:
    
    Phase 1: LENS Context Building
        - Language: Parse natural language request
        - Examination: Analyze relevant code/docs/tests
        - Navigation: Explore codebase paths
        - Synthesis: Build unified understanding
    
    Phase 2: Security Threat Assessment (if code context present)
        - HARD GATE: Blocks CRITICAL/HIGH security threats
        - Analyzes code for vulnerabilities
        - Integrated with ChallengeEngine
    
    Phase 3: Challenge Generation
        - Automatic when CORTEX has better solution
        - HARD GATE: Security/harmful actions block
        - SOFT GATE: Architectural violations suggest with auto-proceed
        - CONTEXT GATE: Requests clarification
    
    Phase 4: DoR Confidence Gate
        - Blocks execution if confidence <60%
        - Requires clarification before proceeding
        - Validates intent classification
    
    Phase 5: Domain Execution
        - Subclass-specific logic
        - TDD, Refactoring, Planning, etc.
    
    Subclasses MUST implement:
    - _execute_domain_logic(): Domain-specific orchestration
    
    Subclasses CANNOT override:
    - execute_with_protocol(): Enforced 4-phase flow
    
    Usage:
        class MyOrchestrator(OrchestratorBaseProtocol):
            def _execute_domain_logic(self, user_request, lens_context, context):
                # Domain-specific logic here
                return Ok({"result": "success"})
    """
    
    def __init__(
        self,
        enable_lens: bool = True,
        enable_security: bool = True,
        enable_challenges: bool = True,
        enable_dor_gate: bool = True,
    ) -> None:
        """
        Initialize orchestrator with protocol components.
        
        Args:
            enable_lens: Enable LENS context building (MANDATORY, cannot be False)
            enable_security: Enable security threat assessment (MANDATORY for code)
            enable_challenges: Enable challenge generation (MANDATORY per CORE-029)
            enable_dor_gate: Enable DoR confidence gate (MANDATORY)
        
        Note: All enable_* flags are MANDATORY (True). Parameters kept for
        backward compatibility but forced to True per ARCH-012.
        """
        # ARCH-012: Force ALL protocol phases to be enabled
        self._enable_lens = True  # Override any False
        self._enable_security = True  # Override any False
        self._enable_challenges = True  # CORE-029: Cannot be disabled
        self._enable_dor_gate = True  # Override any False
        
        self.logger = EnhancedAuditLogger.instance()
        
        # Initialize protocol components (gracefully handle missing imports)
        self.lens_orchestrator: Optional[Any] = None
        self.challenge_engine: Optional[Any] = None
        self.dor_gate: Optional[Any] = None
        self.security_analyzer: Optional[Any] = None
        
        if LENSOrchestrator:
            try:
                self.lens_orchestrator = LENSOrchestrator()
                logger.info("LENS Orchestrator initialized (Phase 1)")
            except Exception as e:
                logger.warning(f"LENS Orchestrator init failed: {e}")
        
        if ChallengeEngine:
            try:
                self.challenge_engine = ChallengeEngine()
                logger.info("Challenge Engine initialized (Phase 3)")
            except Exception as e:
                logger.warning(f"Challenge Engine init failed: {e}")
        
        if DoRApprovalGate:
            try:
                self.dor_gate = DoRApprovalGate()
                logger.info("DoR Approval Gate initialized (Phase 4)")
            except Exception as e:
                logger.warning(f"DoR Approval Gate init failed: {e}")
        
        if SecurityThreatAnalyzer:
            try:
                self.security_analyzer = SecurityThreatAnalyzer()
                logger.info("Security Threat Analyzer initialized (Phase 2)")
            except Exception as e:
                logger.warning(f"Security Threat Analyzer init failed: {e}")
        
        logger.info(
            f"OrchestratorBaseProtocol initialized: "
            f"LENS={self.lens_orchestrator is not None}, "
            f"Challenge={self.challenge_engine is not None}, "
            f"DoR={self.dor_gate is not None}, "
            f"Security={self.security_analyzer is not None}"
        )
    
    def execute_with_protocol(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[Any]:
        """
        Execute orchestrator with MANDATORY 4-phase protocol.
        
        CANNOT BE OVERRIDDEN by subclasses (enforced by not marking as @abstractmethod).
        
        Phases:
        1. LENS Context Building (automatic)
        2. Security Threat Assessment (if code context)
        3. Challenge Generation (if disagreement)
        4. DoR Confidence Gate (blocks <60%)
        5. Domain Execution (subclass-specific)
        
        Args:
            user_request: Natural language user request
            context: Optional context dictionary (may contain code, files, etc.)
        
        Returns:
            Result[Any]: Success with output or Error with reason
        
        AC-ID: ARCH-012
        """
        if context is None:
            context = {}
        
        self.logger.log_operation_start(
            ac_id="ARCH-012",
            operation="ORCHESTRATOR_PROTOCOL_EXECUTION",
            details={
                "orchestrator": self.__class__.__name__,
                "request": user_request[:100],
            }
        )
        
        # =====================================================================
        # PHASE 1: LENS Context Building
        # =====================================================================
        lens_context = None
        if self.lens_orchestrator:
            try:
                logger.info("Phase 1: Building LENS context...")
                lens_result = self._execute_lens_phase(user_request, context)
                
                if lens_result.is_err():
                    return lens_result
                
                lens_context = lens_result.unwrap()
                logger.info("Phase 1: LENS context built successfully")
                
            except Exception as e:
                logger.error(f"Phase 1: LENS context building failed: {e}")
                # Continue without LENS context (degraded mode)
        
        # =====================================================================
        # PHASE 2: Security Threat Assessment (HARD GATE)
        # =====================================================================
        if self.security_analyzer and ("code" in context or "file_path" in context):
            try:
                logger.info("Phase 2: Assessing security threats...")
                security_result = self._execute_security_phase(context)
                
                if security_result.is_err():
                    # HARD GATE: Security threats block execution
                    return security_result
                
                security_assessment = security_result.unwrap()
                
                if security_assessment and security_assessment.get("block_execution"):
                    # CRITICAL/HIGH threats detected - HARD BLOCK
                    return Err(
                        f"SECURITY BLOCK: {security_assessment.get('threat_summary', 'Critical security threats detected')}"
                    )
                
                logger.info("Phase 2: Security assessment passed")
                
            except Exception as e:
                logger.error(f"Phase 2: Security assessment failed: {e}")
                # Continue (security check failure doesn't block non-code operations)
        
        # =====================================================================
        # PHASE 3: Challenge Generation
        # =====================================================================
        if self.challenge_engine and lens_context:
            try:
                logger.info("Phase 3: Generating challenge...")
                challenge_result = self._execute_challenge_phase(
                    user_request,
                    lens_context,
                    context
                )
                
                if challenge_result.is_ok():
                    challenge = challenge_result.unwrap()
                    
                    if challenge and challenge.get("has_disagreement"):
                        gate_type = challenge.get("gate_type")
                        
                        # HARD GATE: Block and require user choice
                        if gate_type == "hard" or challenge.get("block_execution"):
                            logger.info("Phase 3: HARD GATE challenge - blocking execution")
                            return Ok({
                                "type": "challenge",
                                "phase": "challenge",
                                "challenge": challenge,
                                "requires_user_choice": True,
                                "blocked": True,
                            })
                        
                        # SOFT GATE: Suggest but allow auto-proceed
                        elif gate_type == "soft":
                            logger.info("Phase 3: SOFT GATE challenge - suggesting alternative")
                            # Return challenge but don't block execution
                            # Client can choose to show challenge or proceed
                            context["challenge_suggestion"] = challenge
                
                logger.info("Phase 3: Challenge phase complete")
                
            except Exception as e:
                logger.error(f"Phase 3: Challenge generation failed: {e}")
                # Continue without challenge (degraded mode)
        
        # =====================================================================
        # PHASE 4: DoR Confidence Gate
        # =====================================================================
        dor_reflection = None
        if self.dor_gate:
            try:
                logger.info("Phase 4: Evaluating DoR confidence...")
                dor_result = self._execute_dor_phase(user_request, context)
                
                if dor_result.is_err():
                    return dor_result
                
                dor_reflection = dor_result.unwrap()
                
                # Check confidence threshold (default 60%)
                confidence = dor_reflection.get("dor_confidence", 0.0)
                threshold = DOR_CONFIDENCE_THRESHOLD
                
                if confidence < threshold:
                    # DoR NOT MET - block execution
                    logger.warning(
                        f"Phase 4: DoR NOT MET ({confidence:.0%} < {threshold:.0%})"
                    )
                    return Err(
                        f"DoR NOT MET: Confidence {confidence:.0%} below threshold {threshold:.0%}. "
                        f"Please provide more specific details about: {', '.join(dor_reflection.get('key_entities', ['the request']))}"
                    )
                
                logger.info(f"Phase 4: DoR MET ({confidence:.0%} >= {threshold:.0%})")
                
            except Exception as e:
                logger.error(f"Phase 4: DoR evaluation failed: {e}")
                # Continue without DoR gate (degraded mode)
        
        # =====================================================================
        # PHASE 5: Domain Execution (Subclass-specific)
        # =====================================================================
        try:
            logger.info("Phase 5: Executing domain logic...")
            
            domain_result = self._execute_domain_logic(
                user_request=user_request,
                lens_context=lens_context,
                context=context,
            )
            
            # =====================================================================
            # PHASE 6: Learning Capture (Automatic - Phase 71)
            # =====================================================================
            if domain_result.is_ok():
                try:
                    logger.info("Phase 6: Capturing learnings...")
                    self._execute_learning_phase(
                        user_request=user_request,
                        context=context,
                        result=domain_result.unwrap(),
                        lens_context=lens_context,
                    )
                    logger.info("Phase 6: Learnings captured successfully")
                except Exception as e:
                    # Learning capture failure should NOT block execution
                    logger.warning(f"Phase 6: Learning capture failed: {e}")
            
            self.logger.log_operation_complete(
                ac_id="ARCH-012",
                operation="ORCHESTRATOR_PROTOCOL_EXECUTION",
                success=domain_result.is_ok(),
                details={
                    "orchestrator": self.__class__.__name__,
                    "phases_completed": [
                        "lens" if lens_context else None,
                        "security",
                        "challenge",
                        "dor" if dor_reflection else None,
                        "domain",
                        "learning" if domain_result.is_ok() else None,
                    ],
                }
            )
            
            return domain_result
            
        except Exception as e:
            logger.error(f"Phase 5: Domain execution failed: {e}")
            self.logger.log_operation_complete(
                ac_id="ARCH-012",
                operation="ORCHESTRATOR_PROTOCOL_EXECUTION",
                success=False,
                details={"error": str(e)},
            )
            return Err(f"Domain execution failed: {e}")
    
    def _execute_lens_phase(
        self,
        user_request: str,
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute Phase 1: LENS Context Building.
        
        Args:
            user_request: User request text
            context: Request context
        
        Returns:
            Result with LENS context or error
        """
        try:
            # Build LENS context using LENSOrchestrator
            lens_result = self.lens_orchestrator.analyze(
                user_request=user_request,
                context=context,
            )
            
            return lens_result
            
        except Exception as e:
            return Err(f"LENS context building failed: {e}")
    
    def _execute_security_phase(
        self,
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute Phase 2: Security Threat Assessment.
        
        HARD GATE: Blocks CRITICAL/HIGH threats.
        
        Args:
            context: Request context with code/file_path
        
        Returns:
            Result with security assessment or error
        """
        try:
            code_content = context.get("code", "")
            file_path = context.get("file_path", "user_code.py")
            
            if not code_content:
                # No code to analyze
                return Ok(None)
            
            # Assess security threats
            assessment = self.security_analyzer.assess_threats(
                code=code_content,
                file_path=file_path,
            )
            
            return Ok({
                "has_threats": assessment.has_threats if assessment else False,
                "block_execution": assessment.block_execution if assessment else False,
                "threat_summary": assessment.threat_summary if assessment else "",
                "threats": assessment.threats if assessment else [],
            })
            
        except Exception as e:
            return Err(f"Security assessment failed: {e}")
    
    def _execute_challenge_phase(
        self,
        user_request: str,
        lens_context: Any,
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute Phase 3: Challenge Generation.
        
        Args:
            user_request: User request text
            lens_context: LENS context from Phase 1
            context: Request context
        
        Returns:
            Result with challenge or None if no disagreement
        """
        try:
            # Generate challenge if CORTEX disagrees
            challenge = self.challenge_engine.generate_challenge(
                user_request=user_request,
                lens_context=lens_context,
            )
            
            if challenge and hasattr(challenge, "has_disagreement"):
                return Ok({
                    "has_disagreement": challenge.has_disagreement,
                    "disagreement_type": challenge.disagreement_type.value if challenge.disagreement_type else None,
                    "recommended_alternative": challenge.recommended_alternative,
                    "reasoning": challenge.reasoning,
                    "gate_type": challenge.gate_type.value if challenge.gate_type else "soft",
                    "block_execution": challenge.gate_type and challenge.gate_type.value == "hard",
                })
            
            return Ok(None)
            
        except Exception as e:
            return Err(f"Challenge generation failed: {e}")
    
    def _execute_dor_phase(
        self,
        user_request: str,
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute Phase 4: DoR Confidence Gate.
        
        Args:
            user_request: User request text
            context: Request context
        
        Returns:
            Result with DoR reflection or error
        """
        try:
            # Classify and reflect on intent
            reflection = self.dor_gate.classify_and_reflect(
                text=user_request,
                context=context,
            )
            
            if reflection and hasattr(reflection, "dor_confidence"):
                return Ok({
                    "dor_confidence": reflection.dor_confidence,
                    "intent_type": reflection.intent_type,
                    "target_handler": reflection.target_handler,
                    "key_entities": reflection.key_entities,
                    "governance_rules": reflection.governance_rules,
                })
            
            return Ok({"dor_confidence": 0.5})  # Default medium confidence
            
        except Exception as e:
            return Err(f"DoR evaluation failed: {e}")
    
    def _execute_learning_phase(
        self,
        user_request: str,
        context: Dict[str, Any],
        result: Any,
        lens_context: Optional[Any] = None,
    ) -> None:
        """
        Execute Phase 6: Learning Capture (Phase 71).
        
        Automatically captures patterns from orchestrator execution results
        and merges them into CORTEX knowledge repositories.
        
        This is a NON-BLOCKING phase - failures do not stop execution.
        Subclasses can override to customize learning capture.
        
        Args:
            user_request: Original user request
            context: Request context
            result: Domain execution result
            lens_context: LENS context from Phase 1 (may be None)
        
        AC-ID: PHASE-71-S2
        """
        # Check if learning is skipped for this orchestrator
        if getattr(self.__class__, '_skip_learning', False):
            logger.debug(f"Phase 6: Learning skipped for {self.__class__.__name__} (decorator)")
            return
        
        if get_learning_loop is None:
            logger.debug("Phase 6: Learning loop not available (optional)")
            return
        
        try:
            learning_loop = get_learning_loop()
            
            # Build result dict for learning capture
            result_dict = result if isinstance(result, dict) else {"result": result}
            
            # Build context dict for learning capture
            context_dict = {
                "request": user_request,
                "lens_context": lens_context,
                **context,
            }
            
            # Capture learnings from this operation
            captures = learning_loop.capture_from_operation(
                orchestrator=self.__class__.__name__,
                operation=self._get_learning_operation_type(),
                context=context_dict,
                result=result_dict,
            )
            
            if captures:
                logger.info(
                    f"Phase 6: Captured {len(captures)} learnings "
                    f"from {self.__class__.__name__}"
                )
            
        except Exception as e:
            # Learning failure should never block execution
            logger.warning(f"Phase 6: Learning capture failed: {e}")
    
    def _get_learning_operation_type(self) -> str:
        """
        Get the operation type for learning capture.
        
        Subclasses should override to provide specific operation types:
        - TDDOrchestrator -> "tdd"
        - RefactoringOrchestrator -> "refactoring"
        - InteractionOrchestrator -> "interaction"
        - etc.
        
        Returns:
            Operation type string for pattern extraction
        """
        # Default: derive from class name
        class_name = self.__class__.__name__.lower()
        
        if "tdd" in class_name:
            return "tdd"
        elif "refactor" in class_name:
            return "refactoring"
        elif "interaction" in class_name:
            return "interaction"
        elif "governance" in class_name or "enforcement" in class_name:
            return "governance"
        elif "coordination" in class_name or "master" in class_name:
            return "coordination"
        else:
            return "generic"
    
    @abstractmethod
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute Phase 5: Domain-specific orchestration logic.
        
        MUST BE IMPLEMENTED by subclasses.
        
        This is where orchestrator-specific logic lives:
        - TDDOrchestrator: RED → GREEN → REFACTOR
        - RefactoringOrchestrator: Analyze → Plan → Refactor
        - PlanningOrchestrator: Estimate → Plan → Schedule
        
        Args:
            user_request: Original user request
            lens_context: LENS context from Phase 1 (may be None)
            context: Request context with additional data
        
        Returns:
            Result[Any]: Success with domain output or Error
        
        Raises:
            NotImplementedError: If subclass doesn't implement
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _execute_domain_logic()"
        )
    
    def get_protocol_status(self) -> Dict[str, Any]:
        """
        Get status of protocol components.
        
        Returns:
            Dictionary with component availability and configuration
        """
        return {
            "orchestrator": self.__class__.__name__,
            "protocol_version": "2.0",  # Updated for Phase 71
            "components": {
                "lens": self.lens_orchestrator is not None,
                "challenge": self.challenge_engine is not None,
                "dor_gate": self.dor_gate is not None,
                "security": self.security_analyzer is not None,
                "learning": get_learning_loop is not None,
            },
            "enforcement": {
                "lens_enabled": self._enable_lens,
                "security_enabled": self._enable_security,
                "challenges_enabled": self._enable_challenges,
                "dor_gate_enabled": self._enable_dor_gate,
                "learning_enabled": not getattr(self.__class__, '_skip_learning', False),
            },
            "governance": [
                "ARCH-012",  # Orchestrator base protocol
                "CORE-029",  # LENS + Challenge automatic
                "AC-PERMANENT-FIX-006",  # Challenge system mandatory
                "PHASE-71-S2",  # Automatic learning capture
            ],
        }


__all__ = [
    "OrchestratorBaseProtocol",
    "ProtocolExecutionResult",
    "skip_learning",
]
