"""
Governance Pre-Execution Gates (AC-FIX-002-01).

Implements pre-execution governance validation to prevent unauthorized 
orchestrator operations BEFORE they execute (not after).

ISSUE ADDRESSED:
- FINDING-002: Governance validation was post-execution (reactive logging only)
- FIX: Pre-execution gates (proactive prevention) before orchestrator execution

Key Components:
1. GovernancePregate: Abstract interface for pre-execution checks
2. PreGateDecision: Result of pre-gate evaluation
3. ResourceQuotaGate: Checks token quota availability
4. AuthorizationGate: Checks actor authorization
5. TierAccessGate: Checks tier access declarations

Governance Rules Enforced:
- CORE-017: Strict Governance Enforcement (gates prevent execution)
- CORE-027: Audit Trail Per Turn (all gate decisions logged)
- AR-001-03: Tier 0 Immutability (enforced per-turn)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.result import Result, Ok, Err


# ============================================================================
# PRE-GATE DECISION STRUCTURE
# ============================================================================

@dataclass
class PreGateDecision:
    """
    Result of a pre-gate evaluation.
    
    Represents the decision whether an operation is allowed to proceed
    based on governance validation checks.
    """
    
    allowed: bool
    """Whether the operation is allowed to proceed."""
    
    reason: str
    """Human-readable explanation of the decision."""
    
    violation_type: Optional[str] = None
    """Type of violation if blocked: RESOURCE_QUOTA | AUTHORIZATION | TIER_ACCESS | None."""
    
    audit_context: Dict[str, Any] = field(default_factory=dict)
    """Context for audit logging (timestamp, actor_id, checks_performed, etc.)."""
    
    def __post_init__(self) -> None:
        """Initialize audit context with defaults."""
        if not self.audit_context:
            self.audit_context = {}
        
        # Always include timestamp
        if "timestamp" not in self.audit_context:
            self.audit_context["timestamp"] = datetime.utcnow().isoformat()
        
        # If blocked, set violation_type if not provided
        if not self.allowed and not self.violation_type:
            self.violation_type = "UNKNOWN"


# ============================================================================
# GOVERNANCE PREGATE INTERFACE
# ============================================================================

class GovernancePregate(ABC):
    """
    Abstract base class for pre-execution governance gates.
    
    Pre-gates validate that operations are authorized to proceed BEFORE
    the orchestrator executes them. This prevents unauthorized operations
    from executing (proactive prevention) rather than just logging violations
    (reactive detection).
    
    Implementing classes should override the abstract methods to provide
    specific validation logic.
    """
    
    def __init__(self) -> None:
        """Initialize base pre-gate."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._lock = threading.RLock()
    
    @abstractmethod
    def check_resource_quota(
        self,
        operation_id: str,
        estimated_token_cost: int,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """
        Check if operation has sufficient resource quota.
        
        Validates that the operation's estimated token cost doesn't exceed
        available quota for the current session/actor.
        
        Args:
            operation_id: Unique identifier for the operation
            estimated_token_cost: Estimated tokens needed for operation
            context: Optional context (actor_id, session_id, etc.)
        
        Returns:
            PreGateDecision with allowed=True or False, with reason
        """
        pass
    
    @abstractmethod
    def check_authorization(
        self,
        operation_id: str,
        actor_id: str,
        target_resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """
        Check if actor is authorized for the operation.
        
        Validates that the actor has necessary permissions to perform
        the operation on the target resource.
        
        Args:
            operation_id: Unique identifier for the operation
            actor_id: Identifier of the actor (user, system, etc.)
            target_resource: Resource the operation targets
            context: Optional context for authorization check
        
        Returns:
            PreGateDecision with allowed=True or False, with reason
        """
        pass
    
    @abstractmethod
    def check_tier_access(
        self,
        tier_id: str,
        operation_id: str,
        declared_access: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """
        Check if operation is authorized to access the tier.
        
        Validates that:
        1. TIER-0 rules cannot be modified (immutability)
        2. Operation only accesses tiers it declared in context
        3. Access respects tier hierarchy (0 > 1 > 2)
        
        Args:
            tier_id: Tier being accessed (TIER-0, TIER-1, TIER-2)
            operation_id: Operation requesting access
            declared_access: List of tiers operation declared it needs
            context: Optional context
        
        Returns:
            PreGateDecision with allowed=True or False, with reason
        """
        pass
    
    def evaluate_all_gates(
        self,
        operation_id: str,
        actor_id: str,
        target_resource: str,
        estimated_token_cost: int = 1000,
        tier_access: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """
        Evaluate all pre-gates for an operation.
        
        Runs all three gate checks and returns combined decision.
        If ANY gate blocks, operation is blocked.
        
        Args:
            operation_id: Operation identifier
            actor_id: Actor identifier
            target_resource: Target resource
            estimated_token_cost: Estimated token cost
            tier_access: Declared tier access
            context: Optional context
        
        Returns:
            PreGateDecision allowing or blocking operation
        """
        with self._lock:
            audit_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "actor_id": actor_id,
                "operation_id": operation_id,
                "target_resource": target_resource,
                "checks_performed": [],
                "all_passed": True
            }
            
            # Check 1: Resource quota
            quota_decision = self.check_resource_quota(
                operation_id, 
                estimated_token_cost, 
                context
            )
            audit_context["checks_performed"].append("RESOURCE_QUOTA")
            if not quota_decision.allowed:
                audit_context["all_passed"] = False
                audit_context["quota_violation"] = quota_decision.reason
                return PreGateDecision(
                    allowed=False,
                    reason=quota_decision.reason,
                    violation_type="RESOURCE_QUOTA",
                    audit_context=audit_context
                )
            
            # Check 2: Authorization
            auth_decision = self.check_authorization(
                operation_id,
                actor_id,
                target_resource,
                context
            )
            audit_context["checks_performed"].append("AUTHORIZATION")
            if not auth_decision.allowed:
                audit_context["all_passed"] = False
                audit_context["authorization_violation"] = auth_decision.reason
                return PreGateDecision(
                    allowed=False,
                    reason=auth_decision.reason,
                    violation_type="AUTHORIZATION",
                    audit_context=audit_context
                )
            
            # Check 3: Tier access
            if tier_access:
                for tier in tier_access:
                    tier_decision = self.check_tier_access(
                        tier,
                        operation_id,
                        tier_access,
                        context
                    )
                    audit_context["checks_performed"].append(f"TIER_ACCESS:{tier}")
                    if not tier_decision.allowed:
                        audit_context["all_passed"] = False
                        audit_context["tier_violation"] = tier_decision.reason
                        return PreGateDecision(
                            allowed=False,
                            reason=tier_decision.reason,
                            violation_type="TIER_ACCESS",
                            audit_context=audit_context
                        )
            
            # All gates passed
            audit_context["decision"] = "ALLOWED"
            return PreGateDecision(
                allowed=True,
                reason="All pre-execution gates passed",
                violation_type=None,
                audit_context=audit_context
            )


# ============================================================================
# CONCRETE GATE IMPLEMENTATIONS
# ============================================================================

class DefaultGovernancePregate(GovernancePregate):
    """
    Default implementation of governance pre-gate.
    
    Provides basic gate implementations with configurable quotas and
    authorization rules.
    """
    
    def __init__(self, max_token_quota: int = 100000) -> None:
        """
        Initialize default pre-gate.
        
        Args:
            max_token_quota: Maximum tokens allowed per session
        """
        super().__init__()
        self.max_token_quota = max_token_quota
        self.used_tokens: Dict[str, int] = {}
        self._auth_rules: Dict[str, List[str]] = {}
        self._tier0_immutable = True
    
    def check_resource_quota(
        self,
        operation_id: str,
        estimated_token_cost: int,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """Check resource quota."""
        actor_id = context.get("actor_id", "unknown") if context else "unknown"
        
        # Get used tokens for this actor
        used = self.used_tokens.get(actor_id, 0)
        available = self.max_token_quota - used
        
        if estimated_token_cost > available:
            return PreGateDecision(
                allowed=False,
                reason=f"Quota exceeded: {estimated_token_cost} tokens requested, "
                       f"{available} available (used {used}/{self.max_token_quota})",
                violation_type="RESOURCE_QUOTA",
                audit_context={
                    "actor_id": actor_id,
                    "tokens_requested": estimated_token_cost,
                    "tokens_available": available,
                    "tokens_used": used
                }
            )
        
        # Deduct tokens
        self.used_tokens[actor_id] = used + estimated_token_cost
        
        return PreGateDecision(
            allowed=True,
            reason=f"Quota check passed: {estimated_token_cost} tokens "
                   f"available ({available - estimated_token_cost} remaining)",
            audit_context={
                "actor_id": actor_id,
                "tokens_requested": estimated_token_cost,
                "tokens_available": available,
                "tokens_after": available - estimated_token_cost
            }
        )
    
    def check_authorization(
        self,
        operation_id: str,
        actor_id: str,
        target_resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """Check actor authorization."""
        # Check if actor has declared access to target resource
        if actor_id not in self._auth_rules:
            # No explicit rules = allow by default (can be overridden)
            return PreGateDecision(
                allowed=True,
                reason=f"Actor {actor_id} authorized for {target_resource}",
                audit_context={
                    "actor_id": actor_id,
                    "target_resource": target_resource,
                    "check": "default_allow"
                }
            )
        
        allowed_resources = self._auth_rules[actor_id]
        if target_resource not in allowed_resources:
            return PreGateDecision(
                allowed=False,
                reason=f"Actor {actor_id} not authorized for {target_resource}",
                violation_type="AUTHORIZATION",
                audit_context={
                    "actor_id": actor_id,
                    "target_resource": target_resource,
                    "allowed_resources": allowed_resources
                }
            )
        
        return PreGateDecision(
            allowed=True,
            reason=f"Actor {actor_id} authorized for {target_resource}",
            audit_context={
                "actor_id": actor_id,
                "target_resource": target_resource,
                "check": "explicit_allow"
            }
        )
    
    def check_tier_access(
        self,
        tier_id: str,
        operation_id: str,
        declared_access: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PreGateDecision:
        """Check tier access."""
        # TIER-0 is immutable - no modifications allowed
        if tier_id == "TIER-0" and context and context.get("is_modification", False):
            return PreGateDecision(
                allowed=False,
                reason="TIER-0 rules are immutable - modification not allowed",
                violation_type="TIER_ACCESS",
                audit_context={
                    "tier_id": tier_id,
                    "operation_id": operation_id,
                    "violation": "tier0_immutability"
                }
            )
        
        # Check if tier was declared
        if declared_access and tier_id not in declared_access:
            return PreGateDecision(
                allowed=False,
                reason=f"Operation did not declare access to {tier_id} "
                       f"(declared: {declared_access})",
                violation_type="TIER_ACCESS",
                audit_context={
                    "tier_id": tier_id,
                    "operation_id": operation_id,
                    "declared_access": declared_access
                }
            )
        
        return PreGateDecision(
            allowed=True,
            reason=f"Tier access check passed for {tier_id}",
            audit_context={
                "tier_id": tier_id,
                "operation_id": operation_id,
                "check": "tier_access_allowed"
            }
        )
    
    def set_authorization_rule(self, actor_id: str, allowed_resources: List[str]) -> None:
        """Set authorization rules for an actor."""
        with self._lock:
            self._auth_rules[actor_id] = allowed_resources
    
    def reset_quota(self, actor_id: str) -> None:
        """Reset token quota for an actor."""
        with self._lock:
            self.used_tokens[actor_id] = 0


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_pregate_instance: Optional[GovernancePregate] = None
_pregate_lock = threading.RLock()


def get_governance_pregate() -> GovernancePregate:
    """
    Get the singleton GovernancePregate instance.
    
    Returns:
        GovernancePregate: Singleton pre-gate instance
    """
    global _pregate_instance
    
    if _pregate_instance is None:
        with _pregate_lock:
            if _pregate_instance is None:
                _pregate_instance = DefaultGovernancePregate()
    
    return _pregate_instance


def set_governance_pregate(pregate: GovernancePregate) -> None:
    """
    Set the singleton GovernancePregate instance (for testing).
    
    Args:
        pregate: GovernancePregate instance to use
    """
    global _pregate_instance
    with _pregate_lock:
        _pregate_instance = pregate
