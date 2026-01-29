"""
structured-decision: Structured Decision Formatter

Provides StructuredDecisionFormatter for formatting execution decisions
as structured JSON (never markdown), per CORE-040.

CORE Rules Applied:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings
    - CORE-040: Execution Specification Mandate (NO MARKDOWN in execution paths)
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of execution decisions."""
    APPROVAL = "approval"
    ROUTING = "routing"
    GOVERNANCE = "governance"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class StructuredDecision:
    """Represents a structured decision in JSON format."""
    decision_type: DecisionType
    decision_code: str
    description: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (JSON-serializable)."""
        return {
            "decision_type": self.decision_type.value,
            "decision_code": self.decision_code,
            "description": self.description,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {},
            "recommendations": self.recommendations or []
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class StructuredDecisionFormatter:
    """
    Formats execution decisions as structured JSON.
    
    CRITICAL: Never returns markdown in execution paths.
    Markdown is for UI/display layer only.
    
    Execution layer MUST use JSON (dict) for all decisions.
    """
    
    @staticmethod
    def format_approval_decision(
        intent_reflection: Any
    ) -> Dict[str, Any]:
        """
        Convert approval decision to structured JSON dict.
        
        This is CRITICAL for CORE-040 compliance:
        - IntentReflection.to_markdown() is for UI display ONLY
        - Execution layer must use StructuredDecisionFormatter
        - Output is PURE DICT (JSON), NEVER markdown
        
        Args:
            intent_reflection: IntentReflection object from DoRApprovalGate
        
        Returns:
            Dictionary representation (JSON-serializable)
        
        Example:
            >>> formatter = StructuredDecisionFormatter()
            >>> intent_ref = IntentReflection(...)  # from DoRApprovalGate
            >>> decision_dict = formatter.format_approval_decision(intent_ref)
            >>> # decision_dict is pure dict, no markdown
            >>> assert isinstance(decision_dict, dict)
        """
        # Extract fields from IntentReflection (SAFELY)
        approval_dict = {
            "decision_type": "approval",
            "intent_type": getattr(intent_reflection, "intent_type", "unknown"),
            "intent_code": getattr(intent_reflection, "intent_code", ""),
            "confidence": getattr(intent_reflection, "confidence", 0.0),
            "handler": getattr(intent_reflection, "handler", None),
            "governance_rules": getattr(
                intent_reflection,
                "governance_rules",
                []
            ),
            "required_fields": getattr(
                intent_reflection,
                "required_fields",
                {}
            ),
            "optional_fields": getattr(
                intent_reflection,
                "optional_fields",
                {}
            ),
            "modifications": getattr(
                intent_reflection,
                "modifications",
                []
            )
        }
        
        logger.debug(
            f"Formatted approval decision: {approval_dict['intent_type']} "
            f"(confidence: {approval_dict['confidence']})"
        )
        
        return approval_dict
    
    @staticmethod
    def format_routing_decision(
        decision: Any
    ) -> Dict[str, Any]:
        """
        Format routing decision as structured JSON dict.
        
        Args:
            decision: RoutingDecision object
        
        Returns:
            Dictionary representation (JSON-serializable)
        
        Example:
            >>> formatter = StructuredDecisionFormatter()
            >>> routing_dict = formatter.format_routing_decision(decision)
            >>> assert isinstance(routing_dict, dict)
        """
        routing_dict = {
            "decision_type": "routing",
            "intent": getattr(decision, "intent", "unknown"),
            "handler": getattr(decision, "handler", None),
            "confidence": getattr(decision, "confidence", 0.0),
            "reasoning": getattr(decision, "reasoning", ""),
            "alternative_handlers": getattr(
                decision,
                "alternative_handlers",
                []
            ),
            "metadata": getattr(decision, "metadata", {})
        }
        
        logger.debug(
            f"Formatted routing decision: {routing_dict['intent']} "
            f"→ {routing_dict['handler']}"
        )
        
        return routing_dict
    
    @staticmethod
    def format_governance_violation(
        violation: Any
    ) -> Dict[str, Any]:
        """
        Format governance violation as structured JSON.
        
        CRITICAL: Use violation codes (GOVE_NNN), NOT English text.
        
        Args:
            violation: Governance violation object
        
        Returns:
            Dictionary with structured violation (JSON-serializable)
        """
        violation_dict = {
            "decision_type": "governance_violation",
            "violation_code": getattr(violation, "code", "UNKNOWN"),
            "violation_id": getattr(violation, "id", ""),
            "rule": getattr(violation, "rule", ""),
            "severity": getattr(violation, "severity", "error"),
            "description": getattr(violation, "description", ""),
            "details": getattr(violation, "details", {}),
            "remediation": getattr(violation, "remediation", "")
        }
        
        logger.warning(
            f"Formatted governance violation: "
            f"{violation_dict['violation_code']} "
            f"({violation_dict['severity']})"
        )
        
        return violation_dict
    
    @staticmethod
    def format_error_result(
        error_code: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error result as structured JSON.
        
        Args:
            error_code: Machine-readable error code (e.g., GOVE_001)
            error_message: Error message (can be English, but should be clear)
            context: Optional error context
        
        Returns:
            Dictionary with structured error (JSON-serializable)
        """
        error_dict = {
            "decision_type": "error",
            "error_code": error_code,
            "error_message": error_message,
            "context": context or {}
        }
        
        logger.error(
            f"Formatted error: {error_code} - {error_message}"
        )
        
        return error_dict
    
    @staticmethod
    def format_success_result(
        operation: str,
        handler: str,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format successful execution as structured JSON.
        
        Args:
            operation: Operation name
            handler: Handler orchestrator used
            output: Operation output
            metadata: Additional metadata
        
        Returns:
            Dictionary with structured success (JSON-serializable)
        """
        success_dict = {
            "decision_type": "success",
            "operation": operation,
            "handler": handler,
            "output": output or {},
            "metadata": metadata or {}
        }
        
        logger.info(
            f"Formatted success: {operation} via {handler}"
        )
        
        return success_dict
    
    @staticmethod
    def ensure_json_serializable(obj: Any) -> Dict[str, Any]:
        """
        Ensure object is JSON-serializable dict.
        
        CRITICAL: This is final validation before returning to caller.
        MUST NOT contain: markdown strings, complex objects, functions
        
        Args:
            obj: Object to validate
        
        Returns:
            JSON-serializable dict
        
        Raises:
            TypeError: If object cannot be serialized to JSON
        """
        try:
            # Try to serialize to JSON and back
            json_str = json.dumps(obj, default=str)
            return json.loads(json_str)
        except (TypeError, ValueError) as e:
            logger.error(f"Object not JSON-serializable: {e}")
            return {
                "error": "Object not JSON-serializable",
                "original_type": str(type(obj))
            }


__all__ = [
    "StructuredDecisionFormatter",
    "StructuredDecision",
    "DecisionType",
]
