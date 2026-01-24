"""
Intent Reflection and DoR Approval Gate.

AC-ID: AC-GOVE-DOR-001
Purpose: Display intent classification in concise markdown, require user approval

This module provides:
1. Concise intent reflection in markdown format
2. Definition of Ready (DoR) checkpoint before execution
3. User approval gate for each turn
4. Integration with IntentRouterFactory
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.intent_router import RoutingDecision, IntentType
from cortex.orchestrators.core.intent_router_factory import (
    RouterInstance,
    get_intent_router_factory,
)
from cortex.core.result import Ok


class ApprovalStatus(Enum):
    """Status of user approval for intent execution."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class IntentReflection:
    """
    Structured reflection of classified intent.
    
    Designed for concise markdown display without overwhelming the user.
    """
    
    intent_type: str
    """Primary intent category (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)"""
    
    target_handler: str
    """Orchestrator that will handle this request"""
    
    confidence: float
    """Confidence score (0.0 to 1.0)"""
    
    scope: str
    """Scope of operation (FILE, MODULE, SYSTEM, DOMAIN)"""
    
    key_entities: List[str] = field(default_factory=lambda: [])
    """Key entities identified in the request"""
    
    estimated_impact: str = "low"
    """Estimated impact level (low, medium, high)"""
    
    requires_tests: bool = True
    """Whether TDD applies (CORE-008)"""
    
    governance_rules: List[str] = field(default_factory=lambda: [])
    """Applicable governance rules"""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    """When reflection was generated"""

    def to_markdown(self) -> str:
        """
        Generate concise markdown representation.
        
        Designed to be scannable in <10 seconds.
        
        Returns:
            Markdown string for user display
        """
        # Confidence indicator
        if self.confidence >= 0.8:
            confidence_badge = "🟢 High"
        elif self.confidence >= 0.6:
            confidence_badge = "🟡 Medium"
        else:
            confidence_badge = "🔴 Low"
        
        # Impact indicator
        impact_badges = {
            "low": "🔵",
            "medium": "🟡", 
            "high": "🔴"
        }
        impact_badge = impact_badges.get(self.estimated_impact, "⚪")
        
        # Build concise markdown
        lines = [
            "### 📋 Intent Classification",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Intent** | `{self.intent_type}` |",
            f"| **Handler** | `{self.target_handler}` |",
            f"| **Confidence** | {confidence_badge} ({self.confidence:.0%}) |",
            f"| **Scope** | `{self.scope}` |",
            f"| **Impact** | {impact_badge} {self.estimated_impact.title()} |",
        ]
        
        # Only show entities if present (keep concise)
        if self.key_entities:
            entities_str = ", ".join(f"`{e}`" for e in self.key_entities[:3])
            if len(self.key_entities) > 3:
                entities_str += f" +{len(self.key_entities) - 3} more"
            lines.append(f"| **Entities** | {entities_str} |")
        
        # Governance (only if applicable rules)
        if self.governance_rules:
            rules_str = ", ".join(self.governance_rules[:3])
            lines.append(f"| **Rules** | {rules_str} |")
        
        lines.extend([
            "",
            "---",
            "",
            "**⏳ Awaiting approval to proceed...**",
        ])
        
        return "\n".join(lines)


@dataclass
class ApprovalDecision:
    """User's decision on the intent classification."""
    
    status: ApprovalStatus
    """Approval status"""
    
    feedback: Optional[str] = None
    """Optional user feedback or modification"""
    
    modified_intent: Optional[str] = None
    """Modified intent if user corrected classification"""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DoRApprovalGate:
    """
    Definition of Ready (DoR) Approval Gate.
    
    Enforces user approval before orchestration execution.
    Displays intent reflection in concise markdown format.
    
    Flow:
    1. classify_and_reflect() - Classify intent, generate reflection
    2. User reviews markdown reflection
    3. approve() or reject() - User provides decision
    4. execute_if_approved() - Execute only if approved
    
    Usage:
        gate = DoRApprovalGate()
        
        # Step 1: Classify and show reflection
        reflection = gate.classify_and_reflect(
            text="Implement user authentication",
            context={"domain": "security"}
        )
        print(reflection.to_markdown())  # Show to user
        
        # Step 2: Wait for user approval
        # ... user reviews ...
        
        # Step 3: User approves
        gate.approve()
        
        # Step 4: Execute
        result = gate.execute_if_approved(text, context)
    """
    
    def __init__(self) -> None:
        """Initialize DoR Approval Gate."""
        self._factory = get_intent_router_factory()
        self._router: Optional[RouterInstance] = None
        self._current_reflection: Optional[IntentReflection] = None
        self._approval_decision: Optional[ApprovalDecision] = None
        self._pending_text: Optional[str] = None
        self._pending_context: Optional[Dict[str, Any]] = None
    
    def classify_and_reflect(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> IntentReflection:
        """
        Classify intent and generate reflection for user review.
        
        Args:
            text: User request text
            context: Request context
        
        Returns:
            IntentReflection for markdown display
        
        Raises:
            ValueError: If text empty
            RuntimeError: If classification fails
        """
        if not text or not text.strip():
            raise ValueError("Request text cannot be empty")
        
        # Store for later execution
        self._pending_text = text
        self._pending_context = context
        
        # Get router and classify
        self._router = self._factory.create_router()
        routing_decision = self._router.classify_intent(text, context)
        
        if routing_decision is None:
            raise RuntimeError("Intent classification returned None")
        
        # Build reflection
        self._current_reflection = self._build_reflection(routing_decision, text, context)
        
        # Reset approval state
        self._approval_decision = None
        
        return self._current_reflection
    
    def _build_reflection(
        self,
        decision: RoutingDecision,
        text: str,
        context: Dict[str, Any]
    ) -> IntentReflection:
        """
        Build IntentReflection from routing decision.
        
        Args:
            decision: Routing decision from classifier
            text: Original request text
            context: Request context
        
        Returns:
            Populated IntentReflection
        """
        # Determine scope from decision or context
        scope = context.get("scope", "MODULE")
        if "file" in text.lower() or "single" in text.lower():
            scope = "FILE"
        elif "system" in text.lower() or "entire" in text.lower():
            scope = "SYSTEM"
        elif "domain" in text.lower():
            scope = "DOMAIN"
        
        # Estimate impact
        impact = "low"
        if decision.intent_type == IntentType.REFACTOR:
            impact = "medium"
        if scope in ["SYSTEM", "DOMAIN"]:
            impact = "high"
        
        # Determine applicable governance rules
        rules: List[str] = ["CORE-008"]  # TDD always applies
        if decision.intent_type == IntentType.IMPLEMENT:
            rules.extend(["CORE-011", "CORE-012"])  # Type hints, docstrings
        if "test" in text.lower():
            rules.append("CORE-008")
        
        # Extract key entities (simple heuristic)
        entities: List[str] = []
        for word in text.split():
            if word.startswith(("AC-", "CORE-", "PHASE-")):
                entities.append(word.rstrip(".,;:"))
        
        return IntentReflection(
            intent_type=decision.intent_type.value,
            target_handler=decision.target_handler,
            confidence=decision.confidence_score,
            scope=scope,
            key_entities=entities,
            estimated_impact=impact,
            requires_tests=True,
            governance_rules=list(set(rules)),
        )
    
    def approve(self, feedback: Optional[str] = None) -> None:
        """
        Approve the current intent classification.
        
        Args:
            feedback: Optional approval feedback
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to approve")
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.APPROVED,
            feedback=feedback,
        )
    
    def reject(self, reason: str) -> None:
        """
        Reject the current intent classification.
        
        Args:
            reason: Reason for rejection
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to reject")
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.REJECTED,
            feedback=reason,
        )
    
    def modify(self, corrected_intent: str, feedback: Optional[str] = None) -> None:
        """
        Modify the intent classification.
        
        Args:
            corrected_intent: Corrected intent type
            feedback: Optional modification feedback
        """
        if self._current_reflection is None:
            raise RuntimeError("No pending classification to modify")
        
        self._approval_decision = ApprovalDecision(
            status=ApprovalStatus.MODIFIED,
            feedback=feedback,
            modified_intent=corrected_intent,
        )
    
    @property
    def is_approved(self) -> bool:
        """Check if current intent is approved for execution."""
        if self._approval_decision is None:
            return False
        return self._approval_decision.status in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.MODIFIED,
        ]
    
    @property
    def is_pending(self) -> bool:
        """Check if approval is pending."""
        return (
            self._current_reflection is not None
            and self._approval_decision is None
        )
    
    def get_reflection_markdown(self) -> str:
        """
        Get current reflection as markdown.
        
        Returns:
            Markdown string or empty if no reflection
        """
        if self._current_reflection is None:
            return ""
        return self._current_reflection.to_markdown()
    
    def execute_if_approved(self) -> Dict[str, Any]:
        """
        Execute orchestration if approved.
        
        Returns:
            Execution result dictionary
        
        Raises:
            RuntimeError: If not approved or no pending request
        """
        if not self.is_approved:
            raise RuntimeError(
                "Cannot execute: approval required. "
                "Call approve() or modify() first."
            )
        
        if self._router is None or self._pending_text is None:
            raise RuntimeError("No pending request to execute")
        
        # Execute via router
        result = self._router.execute_orchestrated(
            text=self._pending_text,
            context=self._pending_context or {},
        )
        
        # Clear pending state
        self._pending_text = None
        self._pending_context = None
        
        if isinstance(result, Ok):
            return {"status": "success", "result": result.value}
        else:
            return {"status": "error", "error": getattr(result, "error", str(result))}
    
    def reset(self) -> None:
        """Reset gate state for new request."""
        self._router = None
        self._current_reflection = None
        self._approval_decision = None
        self._pending_text = None
        self._pending_context = None


# Convenience function for quick reflection
def reflect_intent(text: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Quick function to classify and return markdown reflection.
    
    Args:
        text: Request text
        context: Optional context
    
    Returns:
        Markdown reflection string
    """
    gate = DoRApprovalGate()
    reflection = gate.classify_and_reflect(text, context or {})
    return reflection.to_markdown()
