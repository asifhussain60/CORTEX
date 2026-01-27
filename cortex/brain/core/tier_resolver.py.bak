"""
Tier Resolver - Tier Precedence Enforcement

Enforces the governance tier precedence (Tier 0 > Tier 1 > Tier 2).
Provides utilities for:
- Resolving rules across tiers
- Determining precedence
- Conflict detection

Author: Asif Hussain
"""

import logging
from typing import Optional, Tuple

from cortex.brain.core.governance_registry import GovernanceRegistry, GovernanceRule
from cortex.brain.core.result import Result, Ok, Err


class TierResolver:
    """
    Resolver for determining tier precedence and conflicts.
    
    Implements the rule precedence order:
    - Tier 0 (SKULL rules) has highest precedence
    - Tier 1 (project governance) can extend Tier 0
    - Tier 2 (engineering standards) lowest precedence
    """
    
    def __init__(self, registry: Optional[GovernanceRegistry] = None):
        """
        Initialize tier resolver.
        
        Args:
            registry: GovernanceRegistry instance (uses singleton if None)
        """
        self._registry = registry or GovernanceRegistry.instance()
        self._logger = logging.getLogger(__name__)
    
    def get_effective_rule(self, rule_id: str) -> Result[Optional[GovernanceRule]]:
        """
        Get the effective rule applying tier precedence.
        
        Returns:
            Result containing the effective rule (Tier 0 > Tier 1 > Tier 2),
            or None if rule doesn't exist
        """
        return self._registry.get_rule(rule_id)
    
    def get_tier_for_rule(self, rule_id: str) -> Result[Optional[int]]:
        """
        Get the tier number for a rule.
        
        Returns:
            Result containing tier number (0, 1, or 2), or None if rule doesn't exist
        """
        rule_result = self._registry.get_rule(rule_id)
        if rule_result.is_err():
            return rule_result
        
        rule = rule_result.unwrap()
        if rule is None:
            return Ok(None)
        
        return Ok(rule.tier)
    
    def is_overridden(self, rule_id: str, tier: int) -> Result[bool]:
        """
        Check if a rule in a given tier is overridden by higher tier.
        
        Args:
            rule_id: Rule ID
            tier: Tier to check (1 or 2)
        
        Returns:
            Result containing True if overridden, False otherwise
        """
        if tier == 0:
            return Ok(False)  # Tier 0 can't be overridden
        
        rule_result = self._registry.get_rule(rule_id)
        if rule_result.is_err():
            return rule_result
        
        rule = rule_result.unwrap()
        if rule is None:
            return Ok(False)
        
        # If the effective rule's tier is lower than the checked tier, it's overridden
        return Ok(rule.tier < tier)
    
    def check_tier_precedence(self, rule_id: str) -> Result[Tuple[int, str]]:
        """
        Check tier precedence for a rule.
        
        Returns:
            Result containing (effective_tier, source_description)
        """
        rule_result = self._registry.get_rule(rule_id)
        if rule_result.is_err():
            return rule_result
        
        rule = rule_result.unwrap()
        if rule is None:
            return Err(f"Rule not found: {rule_id}")
        
        tier_names = {0: "Tier 0 (SKULL - Immutable)", 1: "Tier 1 (Project)", 2: "Tier 2 (Engineering)"}
        source = tier_names.get(rule.tier, f"Tier {rule.tier}")
        
        return Ok((rule.tier, source))
    
    def get_precedence_order(self) -> list[Tuple[int, str]]:
        """
        Get tier precedence order.
        
        Returns:
            List of (tier, description) tuples in precedence order
        """
        return [
            (0, "Tier 0 (SKULL - Immutable)"),
            (1, "Tier 1 (Project Governance)"),
            (2, "Tier 2 (Engineering Standards)"),
        ]
