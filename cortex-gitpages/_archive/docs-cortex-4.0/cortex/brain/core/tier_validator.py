"""
Tier Access Control Validation (AC-AR-012-03)

Validates tier dependencies at registration and runtime to ensure:
- Orchestrators cannot access tiers they don't declare
- Tier access is enforced through governance rules
- Violations are logged for audit trail
- Context injection respects tier boundaries

This module implements the validation layer for the AR-012 plugin framework.
"""

from dataclasses import dataclass
from typing import List, Set, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import logging

from cortex.brain.core.orchestrator_base import OrchestratorBase, OrchestrationContext


logger = logging.getLogger(__name__)


class TierViolationType(Enum):
    """Types of tier access violations"""
    UNDECLARED_ACCESS = "undeclared_access"
    MISSING_REQUIRED_TIER = "missing_required_tier"
    INSUFFICIENT_PERMISSION = "insufficient_permission"
    TIER_DOWNGRADE = "tier_downgrade"
    GOVERNANCE_RULE_VIOLATION = "governance_rule_violation"


@dataclass
class TierViolation:
    """Represents a tier access violation"""
    violation_type: TierViolationType
    orchestrator_id: str
    orchestrator_name: str
    accessed_tier: int
    declared_tiers: Set[int]
    timestamp: datetime
    rule_violated: Optional[str] = None
    enforcement_action: str = "DENY"  # DENY, WARN, LOG
    audit_trail_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for logging"""
        return {
            "violation_type": self.violation_type.value,
            "orchestrator_id": self.orchestrator_id,
            "orchestrator_name": self.orchestrator_name,
            "accessed_tier": self.accessed_tier,
            "declared_tiers": sorted(list(self.declared_tiers)),
            "timestamp": self.timestamp.isoformat(),
            "rule_violated": self.rule_violated,
            "enforcement_action": self.enforcement_action,
            "audit_trail_id": self.audit_trail_id,
        }


class TierAccessValidator:
    """
    Validates tier access for orchestrators.
    
    Enforces:
    - Tier boundaries (only access declared tiers)
    - Governance rules
    - Context integrity
    - Audit logging
    """
    
    def __init__(self, enforce_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            enforce_mode: If True, raise on violations; if False, only log
        """
        self.enforce_mode = enforce_mode
        self.violations: List[TierViolation] = []
        self.logger = logging.getLogger(f"{__name__}.TierAccessValidator")
    
    def validate_tier_declaration(
        self,
        orchestrator_id: str,
        orchestrator_name: str,
        declared_tiers: Set[int],
    ) -> bool:
        """
        Validate that declared tiers are valid.
        
        Args:
            orchestrator_id: ID of orchestrator
            orchestrator_name: Name of orchestrator class
            declared_tiers: Set of declared tier access levels
        
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If enforce_mode is True and validation fails
        """
        # Check tier values are in valid range [0, 3]
        invalid_tiers = {t for t in declared_tiers if t < 0 or t > 3}
        
        if invalid_tiers:
            violation = TierViolation(
                violation_type=TierViolationType.INSUFFICIENT_PERMISSION,
                orchestrator_id=orchestrator_id,
                orchestrator_name=orchestrator_name,
                accessed_tier=list(invalid_tiers)[0],  # First invalid tier
                declared_tiers=declared_tiers,
                timestamp=datetime.now(),
                enforcement_action="DENY",
            )
            self.violations.append(violation)
            
            msg = f"Invalid tier access: {orchestrator_id} declared invalid tiers {invalid_tiers}"
            self.logger.error(msg, extra=violation.to_dict())
            
            if self.enforce_mode:
                raise ValueError(msg)
            return False
        
        return True
    
    def validate_access_attempt(
        self,
        orchestrator: OrchestratorBase,
        tier: int,
        governance_rules: Optional[List[str]] = None,
    ) -> bool:
        """
        Validate access attempt to a tier.
        
        Args:
            orchestrator: The orchestrator attempting access
            tier: Tier being accessed
            governance_rules: Optional governance rules to check
        
        Returns:
            True if access allowed, False otherwise
            
        Raises:
            PermissionError: If enforce_mode is True and access denied
        """
        declared_tiers = orchestrator.get_tier_access()
        
        # Check if tier is in declared set
        if tier not in declared_tiers:
            violation = TierViolation(
                violation_type=TierViolationType.UNDECLARED_ACCESS,
                orchestrator_id=orchestrator.context.orchestrator_id,
                orchestrator_name=orchestrator.__class__.__name__,
                accessed_tier=tier,
                declared_tiers=declared_tiers,
                timestamp=datetime.now(),
                enforcement_action="DENY",
            )
            self.violations.append(violation)
            
            msg = (
                f"Undeclared tier access: {orchestrator.context.orchestrator_id} "
                f"attempted to access tier {tier} (declared: {sorted(list(declared_tiers))})"
            )
            self.logger.warning(msg, extra=violation.to_dict())
            
            if self.enforce_mode:
                raise PermissionError(msg)
            return False
        
        # Check governance rules if provided
        if governance_rules:
            required_rules = orchestrator.get_required_rules()
            missing_rules = set(governance_rules) - set(required_rules)
            
            if missing_rules:
                violation = TierViolation(
                    violation_type=TierViolationType.GOVERNANCE_RULE_VIOLATION,
                    orchestrator_id=orchestrator.context.orchestrator_id,
                    orchestrator_name=orchestrator.__class__.__name__,
                    accessed_tier=tier,
                    declared_tiers=declared_tiers,
                    timestamp=datetime.now(),
                    rule_violated=",".join(sorted(missing_rules)),
                    enforcement_action="DENY",
                )
                self.violations.append(violation)
                
                msg = (
                    f"Governance rule violation: {orchestrator.context.orchestrator_id} "
                    f"missing rules {missing_rules} to access tier {tier}"
                )
                self.logger.warning(msg, extra=violation.to_dict())
                
                if self.enforce_mode:
                    raise PermissionError(msg)
                return False
        
        return True
    
    def validate_context_integrity(
        self,
        orchestrator: OrchestratorBase,
    ) -> bool:
        """
        Validate that context has correct tier access.
        
        Args:
            orchestrator: Orchestrator to validate
        
        Returns:
            True if context is valid, False otherwise
            
        Raises:
            ValueError: If enforce_mode is True and validation fails
        """
        # Check that context tier_access matches orchestrator tier access
        context_tiers = orchestrator.context.tier_access
        declared_tiers = orchestrator.get_tier_access()
        
        if context_tiers != declared_tiers:
            violation = TierViolation(
                violation_type=TierViolationType.INSUFFICIENT_PERMISSION,
                orchestrator_id=orchestrator.context.orchestrator_id,
                orchestrator_name=orchestrator.__class__.__name__,
                accessed_tier=-1,  # N/A
                declared_tiers=declared_tiers,
                timestamp=datetime.now(),
                enforcement_action="DENY",
            )
            self.violations.append(violation)
            
            msg = (
                f"Context integrity violation: {orchestrator.context.orchestrator_id} "
                f"context tiers {context_tiers} != declared tiers {declared_tiers}"
            )
            self.logger.error(msg, extra=violation.to_dict())
            
            if self.enforce_mode:
                raise ValueError(msg)
            return False
        
        return True
    
    def validate_context_injection(
        self,
        context: OrchestrationContext,
        tier_dependencies: Set[int],
        required_rules: List[str],
    ) -> bool:
        """
        Validate that context injection was performed correctly.
        
        Args:
            context: The context to validate
            tier_dependencies: Expected tier dependencies
            required_rules: Expected required rules
        
        Returns:
            True if context injection is valid, False otherwise
            
        Raises:
            ValueError: If enforce_mode is True and validation fails
        """
        # Check tier access was injected
        if context.tier_access != tier_dependencies:
            msg = (
                f"Context injection error: tier_access {context.tier_access} "
                f"!= expected {tier_dependencies}"
            )
            self.logger.error(msg)
            
            if self.enforce_mode:
                raise ValueError(msg)
            return False
        
        # Check required rules were injected
        if set(context.required_rules) != set(required_rules):
            msg = (
                f"Context injection error: required_rules {set(context.required_rules)} "
                f"!= expected {set(required_rules)}"
            )
            self.logger.error(msg)
            
            if self.enforce_mode:
                raise ValueError(msg)
            return False
        
        return True
    
    def get_violations(
        self,
        orchestrator_id: Optional[str] = None,
        violation_type: Optional[TierViolationType] = None,
    ) -> List[TierViolation]:
        """
        Get violations (optionally filtered).
        
        Args:
            orchestrator_id: Filter by orchestrator ID
            violation_type: Filter by violation type
        
        Returns:
            List of violations matching criteria
        """
        results = self.violations
        
        if orchestrator_id:
            results = [v for v in results if v.orchestrator_id == orchestrator_id]
        
        if violation_type:
            results = [v for v in results if v.violation_type == violation_type]
        
        return results
    
    def clear_violations(self) -> None:
        """Clear violation history"""
        self.violations.clear()
    
    def get_violation_count(self) -> int:
        """Get total violation count"""
        return len(self.violations)
    
    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by type"""
        summary = {}
        for violation in self.violations:
            vtype = violation.violation_type.value
            summary[vtype] = summary.get(vtype, 0) + 1
        return summary
    
    def create_audit_report(self) -> Dict[str, Any]:
        """Create comprehensive audit report of all violations"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_violations": self.get_violation_count(),
            "violation_summary": self.get_violation_summary(),
            "violations": [v.to_dict() for v in self.violations],
            "enforce_mode": self.enforce_mode,
        }


class TierAccessEnforcer:
    """
    Enforces tier access control during orchestrator execution.
    
    Works with OrchestratorBase lifecycle:
    - validate_context: Check context tier access
    - on_start: Validate context injection
    - execute: Monitor tier access
    - on_complete: Log any violations
    """
    
    def __init__(self, validator: Optional[TierAccessValidator] = None):
        """
        Initialize enforcer.
        
        Args:
            validator: TierAccessValidator to use (creates default if None)
        """
        self.validator = validator or TierAccessValidator(enforce_mode=True)
        self.logger = logging.getLogger(f"{__name__}.TierAccessEnforcer")
    
    def enforce_on_orchestrator(
        self,
        orchestrator: OrchestratorBase,
        governance_rules: Optional[List[str]] = None,
    ) -> bool:
        """
        Enforce tier access control on an orchestrator.
        
        Args:
            orchestrator: The orchestrator to enforce on
            governance_rules: Governance rules to check
        
        Returns:
            True if enforcement passes, False otherwise
        """
        # Validate context integrity
        if not self.validator.validate_context_integrity(orchestrator):
            return False
        
        # Validate tier access
        for tier in orchestrator.get_tier_access():
            if not self.validator.validate_access_attempt(
                orchestrator,
                tier,
                governance_rules,
            ):
                return False
        
        return True
    
    def get_violations(self) -> List[TierViolation]:
        """Get all recorded violations"""
        return self.validator.get_violations()
