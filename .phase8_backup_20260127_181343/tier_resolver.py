"""Tier Resolver - PHASE-DEPLOYMENT-003-mcp-expansion.

Resolves rule precedence following tier hierarchy: tier0 > tier1 > tier2.

Author: CORTEX Framework
"""

from typing import Dict, Any, Optional


class TierResolver:
    """Resolves rule precedence across governance tiers.
    
    Tier hierarchy:
    - tier0: Core rules (highest precedence, immutable)
    - tier1: Domain-specific rules
    - tier2: Project-specific rules (lowest precedence)
    """
    
    TIER_PRECEDENCE = ["tier0", "tier1", "tier2"]
    
    def __init__(self):
        """Initialize the tier resolver."""
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_precedence(
        self,
        rule_id: str,
        tier0: Optional[Dict[str, Any]] = None,
        tier1: Optional[Dict[str, Any]] = None,
        tier2: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Resolve rule precedence across tiers.
        
        Args:
            rule_id: Rule identifier.
            tier0: Tier0 rule definition (highest precedence).
            tier1: Tier1 rule definition.
            tier2: Tier2 rule definition (lowest precedence).
            
        Returns:
            Resolved rule with source tier indicated.
        """
        # Check tiers in precedence order
        if tier0 is not None:
            return {**tier0, "rule_id": rule_id, "source": "tier0"}
        
        if tier1 is not None:
            return {**tier1, "rule_id": rule_id, "source": "tier1"}
        
        if tier2 is not None:
            return {**tier2, "rule_id": rule_id, "source": "tier2"}
        
        # No rule found
        return {
            "rule_id": rule_id,
            "source": "none",
            "enforce": "none",
            "message": f"Rule {rule_id} not found in any tier",
        }
    
    def get_effective_rules(
        self,
        tier0_rules: Dict[str, Dict[str, Any]],
        tier1_rules: Dict[str, Dict[str, Any]],
        tier2_rules: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Get all effective rules with precedence applied.
        
        Args:
            tier0_rules: All tier0 rules.
            tier1_rules: All tier1 rules.
            tier2_rules: All tier2 rules.
            
        Returns:
            Dictionary of effective rules keyed by rule_id.
        """
        all_rule_ids = set(tier0_rules.keys()) | set(tier1_rules.keys()) | set(tier2_rules.keys())
        
        effective = {}
        for rule_id in all_rule_ids:
            effective[rule_id] = self.resolve_precedence(
                rule_id,
                tier0=tier0_rules.get(rule_id),
                tier1=tier1_rules.get(rule_id),
                tier2=tier2_rules.get(rule_id),
            )
        
        return effective


__all__ = ["TierResolver"]
