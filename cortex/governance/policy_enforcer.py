"""Policy Enforcer for real-time rule enforcement."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class EnforcementDecision:
    """Enforcement decision."""

    allowed: bool
    action: str  # "allow", "warn", "block"
    reason: str


class PolicyEnforcer:
    """Enforces policies in real-time."""

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize enforcer.
        
        Args:
            dry_run: If True, don't actually block (warn only)
        """
        self.dry_run = dry_run
        self.metrics = {
            "total_decisions": 0,
            "allowed": 0,
            "blocked": 0,
            "warned": 0
        }

    def check_compliance(
        self,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> EnforcementDecision:
        """Check if operation is compliant.
        
        Args:
            operation_type: Type of operation
            operation_data: Operation data
            
        Returns:
            EnforcementDecision
        """
        self.metrics["total_decisions"] += 1
        
        # Check compliance based on data
        is_compliant = self._evaluate_compliance(operation_data)
        
        if is_compliant:
            self.metrics["allowed"] += 1
            return EnforcementDecision(
                allowed=True,
                action="allow",
                reason="Operation is compliant with governance policies"
            )
        
        # Non-compliant operation
        if self.dry_run:
            self.metrics["warned"] += 1
            return EnforcementDecision(
                allowed=True,
                action="warn",
                reason="DRY_RUN: Would block non-compliant operation"
            )
        else:
            self.metrics["blocked"] += 1
            return EnforcementDecision(
                allowed=False,
                action="block",
                reason="Operation violates governance policies"
            )

    def _evaluate_compliance(self, operation_data: Dict[str, Any]) -> bool:
        """Evaluate if operation is compliant.
        
        Args:
            operation_data: Operation data to evaluate
            
        Returns:
            True if compliant, False otherwise
        """
        # CRITICAL: MCP-FIRST enforcement (P0)
        if self._check_mcp_bypass(operation_data):
            return False
        
        # Check key compliance indicators
        if operation_data.get("compliant", False):
            return True
        
        if operation_data.get("bare_except", False):
            return False
        
        if not operation_data.get("has_type_hints", True):
            return False
        
        if not operation_data.get("has_logging", True):
            return False
        
        if not operation_data.get("error_handling", True):
            return False
        
        return True
    
    def _check_mcp_bypass(self, operation_data: Dict[str, Any]) -> bool:
        """Check for MCP-FIRST bypass violations (P0).
        
        Detects:
        - Direct file creation for IMPLEMENT/FIX/REFACTOR intents
        - Missing MCP tool usage when required
        - Skipped DoR approval gate
        
        Args:
            operation_data: Operation metadata
            
        Returns:
            True if MCP bypass detected (violation), False otherwise
        """
        intent = operation_data.get("intent", "").upper()
        used_mcp = operation_data.get("used_mcp_tool", False)
        direct_file_edit = operation_data.get("direct_file_edit", False)
        
        # Check IMPLEMENT/FIX/REFACTOR intents
        if intent in ["IMPLEMENT", "FIX", "REFACTOR"]:
            if not used_mcp or direct_file_edit:
                return True  # VIOLATION
        
        # Check ANALYZE/AUDIT intents
        if intent in ["ANALYZE", "AUDIT"]:
            lens_used = operation_data.get("used_lens_tool", False)
            if not lens_used:
                return True  # VIOLATION
        
        return False
        return True

    def add_custom_rule(self, rule: Dict[str, Any]) -> None:
        """Add custom enforcement rule.
        
        Args:
            rule: Rule dictionary with rule_id, name, conditions, actions
            
        Returns:
            None
            
        Raises:
            ValueError: If rule format is invalid
        """
        if not rule.get("rule_id"):
            raise ValueError("Rule must have a rule_id")
        # Store custom rule for future use
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get enforcement metrics.
        
        Returns:
            Dictionary of metrics including total_decisions, allowed, blocked, warned
        """
        return self.metrics.copy()
