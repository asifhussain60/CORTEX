"""
Master Orchestrator Stage 2 (Routing) Implementation

AC-PROD-001-03: Intent Router + Master Orchestrator Integration
Resolves ISSUE-001: Intent Router MISSING (final 50%)

This module provides the Stage 2 (Routing) implementation for the Master Orchestrator
4-stage workflow:

Stage 1: Comprehension (language analysis, intent extraction)
  Input: User query/request
  Output: Comprehension context with user intent, domain, keywords
  
Stage 2: Routing (THIS STAGE)
  Input: Comprehension context from Stage 1
  Output: Routing decision with target handler and confidence
  
Stage 3: Knowledge (domain-specific knowledge retrieval)
  Input: Routing decision from Stage 2
  Output: Domain knowledge and execution context
  
Stage 4: Approval (user-facing validation gates)
  Input: Proposed execution from Stage 3
  Output: Approved/rejected with feedback

CORE Governance Rules:
  - CORE-008: TDD (tests created first)
  - CORE-011: Type hints on all functions
  - CORE-012: Google-style docstrings
  - CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.orchestrators.core.intent_router import IntentRouter, IntentType, RoutingDecision
from src.core.result import Result, Ok, Err
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class Stage2RoutingContext:
    """
    Context for Stage 2 routing operation.
    
    Attributes:
        stage1_comprehension: Output from Stage 1 (comprehension)
        routing_decision: Generated routing decision (output)
        timestamp: When routing was performed
        turn_number: Multi-turn conversation tracking
    """
    stage1_comprehension: Dict[str, Any]
    routing_decision: Optional[RoutingDecision] = None
    timestamp: str = ""
    turn_number: int = 0
    
    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MasterOrchestrationStage2:
    """
    Stage 2 (Routing) of Master Orchestrator 4-stage workflow.
    
    Analyzes comprehension context from Stage 1 and determines the appropriate
    execution path via IntentRouter.
    
    Responsibilities:
    1. Accept Stage 1 comprehension output
    2. Route based on intent type and domain
    3. Generate routing decision with confidence
    4. Log all routing decisions to audit trail
    5. Pass routing decision to Stage 3
    
    CORE Governance:
      - CORE-008: TDD - tests provided first
      - CORE-011: Type hints on all methods
      - CORE-012: Docstrings (Google style)
      - CORE-027: Audit trail logging
    
    Example:
        stage2 = MasterOrchestrationStage2()
        stage1_output = {...comprehension context...}
        result = stage2.route(stage1_output)
        routing_decision = result.unwrap()
    """
    
    def __init__(self) -> None:
        """
        Initialize Stage 2 routing.
        
        Sets up:
        - IntentRouter for routing logic
        - Audit logger for compliance
        - Routing history tracking
        """
        self.router: IntentRouter = IntentRouter()
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self.routing_history: list[Dict[str, Any]] = []
        
        self.logger.log_operation_complete(
            ac_id="AC-PROD-001-03",
            operation="STAGE_2_INIT",
            success=True,
            details={"status": "initialized"}
        )
    
    def route(
        self,
        stage1_comprehension: Dict[str, Any],
        turn_number: int = 0
    ) -> Result[RoutingDecision]:
        """
        Execute Stage 2 routing based on Stage 1 comprehension.
        
        Takes the comprehension context from Stage 1 and routes the operation
        to the appropriate handler based on intent type and domain.
        
        Algorithm:
        1. Log routing start (AC_START)
        2. Validate Stage 1 output
        3. Call IntentRouter.route()
        4. Log routing decision (AC_EXECUTE)
        5. Store in history
        6. Log routing complete (AC_COMPLETE)
        
        Args:
            stage1_comprehension: Comprehension output from Stage 1:
                - operation: Operation name
                - description: Human-readable description
                - domain: Target domain (optional)
                - keywords: Keywords from description (optional)
                - urgency: Urgency level (optional)
                - user_intent: User's stated intent (optional)
            turn_number: Multi-turn conversation turn number (default 0)
        
        Returns:
            Result[RoutingDecision]: Ok with routing decision, or Err with error message
        
        Raises:
            ValueError: If Stage 1 output is invalid
            Exception: If routing fails
        """
        try:
            # Stage 2.1: Log operation start (AC_START)
            self.logger.log_operation_start(
                ac_id="AC-PROD-001-03",
                operation="STAGE_2_ROUTING",
                details={
                    "operation": stage1_comprehension.get("operation"),
                    "domain": stage1_comprehension.get("domain"),
                    "turn_number": turn_number
                }
            )
            
            # Stage 2.2: Validate Stage 1 output
            validation_result = self._validate_stage1_output(stage1_comprehension)
            if validation_result.is_err():
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-001-03",
                    operation="STAGE_2_ROUTING",
                    success=False,
                    details={"error": validation_result.unwrap_err()}
                )
                return validation_result
            
            # Stage 2.3: Perform routing (AC_EXECUTE)
            routing_decision = self.router.route(stage1_comprehension)
            
            # Stage 2.4: Store in history
            routing_record: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "turn_number": turn_number,
                "operation": stage1_comprehension.get("operation"),
                "target_handler": routing_decision.target_handler,
                "intent_type": routing_decision.intent_type.value,
                "confidence": routing_decision.confidence_score,
                "reasoning": routing_decision.reasoning
            }
            self.routing_history.append(routing_record)
            
            # Stage 2.5: Log operation complete (AC_COMPLETE)
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-03",
                operation="STAGE_2_ROUTING",
                success=True,
                details={
                    "target_handler": routing_decision.target_handler,
                    "intent_type": routing_decision.intent_type.value,
                    "confidence": routing_decision.confidence_score,
                    "turn_number": turn_number
                }
            )
            
            return Ok(routing_decision)
        
        except ValueError as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-03",
                operation="STAGE_2_ROUTING",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Routing validation error: {str(e)}")
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-03",
                operation="STAGE_2_ROUTING",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Stage 2 routing failed: {str(e)}")
    
    def _validate_stage1_output(
        self,
        stage1_output: Dict[str, Any]
    ) -> Result[bool]:
        """
        Validate Stage 1 comprehension output format.
        
        Checks that:
        - Output is a non-empty dictionary
        - Required fields are present or can be inferred
        - Field values are of correct types
        
        Args:
            stage1_output: Stage 1 output to validate
        
        Returns:
            Result[bool]: Ok(True) if valid, Err(message) if invalid
        """
        try:
            if not isinstance(stage1_output, dict):
                return Err("Stage 1 output must be a dictionary")
            
            if not stage1_output:
                return Err("Stage 1 output cannot be empty")
            
            # Check for at least operation or description
            if "operation" not in stage1_output and "description" not in stage1_output:
                return Err("Stage 1 output must include 'operation' or 'description'")
            
            # Validate field types
            if "keywords" in stage1_output and not isinstance(stage1_output["keywords"], list):
                return Err("Keywords must be a list")
            
            return Ok(True)
        
        except Exception as e:
            return Err(f"Validation error: {str(e)}")
    
    def get_routing_decision_for_stage3(
        self,
        routing_decision: RoutingDecision
    ) -> Dict[str, Any]:
        """
        Transform Stage 2 routing decision into Stage 3 input format.
        
        Stage 3 (Knowledge retrieval) needs:
        - target_handler: Which orchestrator to use
        - intent_type: Type of operation (IMPLEMENT, FIX, REFACTOR)
        - confidence: Confidence in routing (for approval gates)
        - reasoning: Human-readable explanation
        - metadata: Additional context
        
        Args:
            routing_decision: Routing decision from Stage 2
        
        Returns:
            Dict with Stage 3 input format
        """
        return {
            "target_handler": routing_decision.target_handler,
            "intent_type": routing_decision.intent_type.value,
            "confidence": routing_decision.confidence_score,
            "reasoning": routing_decision.reasoning,
            "metadata": routing_decision.metadata,
            "timestamp": routing_decision.timestamp
        }
    
    def get_routing_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get recent routing decisions.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of recent routing records
        """
        return self.routing_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get routing statistics.
        
        Returns statistics about routing decisions made during this session.
        
        Returns:
            Dict with routing statistics
        """
        if not self.routing_history:
            return {
                "total_routings": 0,
                "average_confidence": 0.0,
                "intent_distribution": {}
            }
        
        intent_counts: Dict[str, int] = {}
        total_confidence = 0.0
        
        for record in self.routing_history:
            intent = record.get("intent_type", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            total_confidence += record.get("confidence", 0.0)
        
        return {
            "total_routings": len(self.routing_history),
            "average_confidence": total_confidence / len(self.routing_history),
            "intent_distribution": intent_counts,
            "most_common_intent": max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        }


# Module exports
__all__ = [
    "MasterOrchestrationStage2",
    "Stage2RoutingContext",
]
