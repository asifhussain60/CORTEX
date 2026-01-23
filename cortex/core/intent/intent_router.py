"""Intent Router - Routes canonicalized intents to appropriate orchestrators.

This module provides intelligent routing of user intents to the correct orchestration
layer based on intent type, confidence, and context.

Author: CORTEX Framework
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from cortex.core.intent.intent_canonicalizer import IntentType


class OrchestrationTarget(str, Enum):
    """Target orchestrator for routing decisions."""
    TDD = "TDD"  # Test-Driven Development Orchestrator
    DIRECT_RESPONSE = "DIRECT_RESPONSE"  # Direct answer without delegation
    INTERACTION = "INTERACTION"  # Return to interaction for clarification
    PLANNING = "PLANNING"  # Planning orchestrator
    ANALYSIS = "ANALYSIS"  # Analysis orchestrator


@dataclass
class RoutingDecision:
    """Routing decision with orchestrator target and metadata."""
    target_orchestrator: OrchestrationTarget
    routing_reason: str
    canonical_intent: Any
    confidence: float
    caution_flag: bool = False
    requires_delegation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentRouter:
    """Routes canonicalized intents to appropriate orchestrators.
    
    The router uses a decision tree based on:
    - Intent type (IMPLEMENT, FIX, REFACTOR, QUERY, etc.)
    - Confidence level (high >= 0.85, medium >= 0.70, low < 0.70)
    - Context and metadata
    
    Routing Rules:
    - IMPLEMENT/FIX/REFACTOR/VALIDATE/MIGRATE → TDD Orchestrator (requires delegation)
    - QUERY/ANALYZE → Direct Response (no delegation needed)
    - UNKNOWN or low confidence → Interaction Orchestrator for clarification
    """
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.85
    MEDIUM_CONFIDENCE = 0.70
    
    def __init__(self):
        """Initialize the intent router with routing rules."""
        self._routing_map = {
            IntentType.IMPLEMENT: OrchestrationTarget.TDD,
            IntentType.FIX: OrchestrationTarget.TDD,
            IntentType.REFACTOR: OrchestrationTarget.TDD,
            IntentType.VALIDATE: OrchestrationTarget.TDD,
            IntentType.MIGRATE: OrchestrationTarget.TDD,
            IntentType.QUERY: OrchestrationTarget.DIRECT_RESPONSE,
            IntentType.ANALYZE: OrchestrationTarget.DIRECT_RESPONSE,
            IntentType.UNKNOWN: OrchestrationTarget.INTERACTION,
        }
        
        # Delegation requirements by target
        self._requires_delegation = {
            OrchestrationTarget.TDD: True,
            OrchestrationTarget.PLANNING: True,
            OrchestrationTarget.DIRECT_RESPONSE: False,
            OrchestrationTarget.INTERACTION: False,
            OrchestrationTarget.ANALYSIS: False,
        }
    
    def route(self, canonical_intent: Any) -> RoutingDecision:
        """Route a canonicalized intent to the appropriate orchestrator.
        
        Args:
            canonical_intent: Canonicalized intent with type and confidence
            
        Returns:
            RoutingDecision: Decision with target orchestrator and reasoning
        """
        # Extract intent type and confidence
        if hasattr(canonical_intent, 'intent_type'):
            intent_type_str = canonical_intent.intent_type
            # Convert string to IntentType enum
            try:
                intent_type = IntentType(intent_type_str)
            except (ValueError, KeyError):
                intent_type = IntentType.UNKNOWN
        else:
            intent_type = IntentType.UNKNOWN
        
        confidence = getattr(canonical_intent, 'confidence', 0.0)
        
        # Check for low confidence (except for safe queries)
        if confidence < self.MEDIUM_CONFIDENCE:
            # Queries are safe to handle even with low confidence
            if intent_type not in [IntentType.QUERY, IntentType.ANALYZE]:
                return self._create_interaction_decision(
                    canonical_intent,
                    confidence,
                    "Low confidence - returning for clarification"
                )
        
        # Get target from routing map
        target = self._routing_map.get(intent_type, OrchestrationTarget.INTERACTION)
        
        # Determine caution flag
        caution_flag = self._should_set_caution(confidence, intent_type)
        
        # Build routing reason
        reason = self._build_routing_reason(intent_type, confidence, target)
        
        # Determine if delegation is required
        requires_delegation = self._requires_delegation.get(target, False)
        
        return RoutingDecision(
            target_orchestrator=target,
            routing_reason=reason,
            canonical_intent=canonical_intent,
            confidence=confidence,
            caution_flag=caution_flag,
            requires_delegation=requires_delegation,
        )
    
    def _should_set_caution(self, confidence: float, intent_type: IntentType) -> bool:
        """Determine if caution flag should be set.
        
        Args:
            confidence: Confidence score
            intent_type: Type of intent
            
        Returns:
            bool: True if caution should be flagged
        """
        # High confidence = no caution
        if confidence >= self.HIGH_CONFIDENCE:
            return False
        
        # Medium confidence = caution for action intents
        if confidence >= self.MEDIUM_CONFIDENCE:
            # Action intents get caution flag at medium confidence
            action_intents = {
                IntentType.IMPLEMENT,
                IntentType.FIX,
                IntentType.REFACTOR,
                IntentType.VALIDATE,
                IntentType.MIGRATE,
            }
            return intent_type in action_intents
        
        # Low confidence = always caution
        return True
    
    def _build_routing_reason(
        self,
        intent_type: IntentType,
        confidence: float,
        target: OrchestrationTarget
    ) -> str:
        """Build human-readable routing reason.
        
        Args:
            intent_type: Type of intent
            confidence: Confidence score
            target: Target orchestrator
            
        Returns:
            str: Routing reason
        """
        confidence_level = "high" if confidence >= self.HIGH_CONFIDENCE else \
                          "medium" if confidence >= self.MEDIUM_CONFIDENCE else "low"
        
        reason_parts = [
            f"Intent: {intent_type.value}",
            f"Confidence: {confidence:.2f} ({confidence_level})",
            f"Target: {target.value}",
        ]
        
        # Add caution notice for medium confidence
        if self.MEDIUM_CONFIDENCE <= confidence < self.HIGH_CONFIDENCE:
            reason_parts.append("Caution: Medium confidence - review recommended")
        
        return " | ".join(reason_parts)
    
    def _create_interaction_decision(
        self,
        canonical_intent: Any,
        confidence: float,
        reason: str
    ) -> RoutingDecision:
        """Create a decision to return to interaction for clarification.
        
        Args:
            canonical_intent: Original intent
            confidence: Confidence score
            reason: Reason for interaction
            
        Returns:
            RoutingDecision: Decision routing to interaction
        """
        return RoutingDecision(
            target_orchestrator=OrchestrationTarget.INTERACTION,
            routing_reason=f"Low confidence ({confidence:.2f}) - {reason}",
            canonical_intent=canonical_intent,
            confidence=confidence,
            caution_flag=True,
            requires_delegation=False,
        )


__all__ = [
    "OrchestrationTarget",
    "IntentRouter",
    "RoutingDecision",
]
