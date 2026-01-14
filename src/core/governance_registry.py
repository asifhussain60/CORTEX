"""
Governance Registry - 3-Tier Governance Model (AR-001)

Implements 3-tier governance hierarchy:
- Tier 0: Immutable SKULL rules (loaded from core-rules.yaml)
- Tier 1: Project governance (YAML + SQLite)
- Tier 2: Engineering standards (team conventions)

Features:
- Tier precedence enforcement (0 > 1 > 2)
- Immutability of Tier 0 rules
- Rule lookup and validation
- Thread-safe singleton access

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.path_resolver import resolve_path
from src.core.result import Result, Ok, Err
from src.core.config import load_yaml


class GovernanceRule:
    """Represents a single governance rule."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        tier: int,
        category: str = "general",
        severity: str = "warning",
    ):
        """
        Initialize a governance rule.
        
        Args:
            rule_id: Unique identifier (e.g., "CORE-001")
            name: Human-readable name
            description: Detailed description
            tier: Governance tier (0, 1, or 2)
            category: Rule category
            severity: Severity level (blocked, warning, info)
        """
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.tier = tier
        self.category = category
        self.severity = severity
    
    @property
    def is_immutable(self) -> bool:
        """Check if rule is immutable (Tier 0)."""
        return self.tier == 0
    
    def __repr__(self) -> str:
        """String representation."""
        return f"GovernanceRule(id={self.rule_id}, tier={self.tier}, name={self.name})"
    
    def __eq__(self, other):
        """Equality comparison."""
        if not isinstance(other, GovernanceRule):
            return False
        return self.rule_id == other.rule_id and self.tier == other.tier


class GovernanceRegistry:
    """
    Registry for all governance rules across tiers.
    
    Thread-safe singleton that manages:
    - Loading Tier 0 SKULL rules from core-rules.yaml
    - Maintaining Tier 1 project governance
    - Storing Tier 2 engineering standards
    - Enforcing tier precedence
    """
    
    _instance: Optional['GovernanceRegistry'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize the governance registry."""
        self._tier0_rules: Dict[str, GovernanceRule] = {}
        self._tier1_rules: Dict[str, GovernanceRule] = {}
        self._tier2_rules: Dict[str, GovernanceRule] = {}
        self._logger = logging.getLogger(__name__)
        self._initialized = False
    
    @classmethod
    def instance(cls) -> 'GovernanceRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    def initialize(self) -> Result[None]:
        """
        Initialize registry by loading Tier 0 SKULL rules.
        
        Returns:
            Result containing None if successful, error otherwise
        """
        if self._initialized:
            return Ok(None)
        
        # Load Tier 0 SKULL rules from cortex-brain/tier0/governance/core-rules.yaml
        result = self._load_tier0_rules()
        if result.is_err():
            return result
        
        self._initialized = True
        self._logger.info(
            f"Governance registry initialized with {len(self._tier0_rules)} Tier 0 rules"
        )
        return Ok(None)
    
    def _load_tier0_rules(self) -> Result[None]:
        """
        Load Tier 0 SKULL rules from YAML file.
        
        Returns:
            Result containing None if successful, error otherwise
        """
        rules_path = resolve_path("cortex-brain", "tier0", "governance", "core-rules.yaml")
        
        # Load YAML
        config_result = load_yaml(rules_path)
        if config_result.is_err():
            return config_result
        
        config = config_result.unwrap()
        
        # Parse rules
        if "rules" not in config:
            return Err("core-rules.yaml missing 'rules' section")
        
        for rule_data in config["rules"]:
            rule_id = rule_data.get("rule_id")
            name = rule_data.get("name", "")
            description = rule_data.get("description", "")
            category = rule_data.get("category", "general")
            severity = rule_data.get("severity", "warning")
            
            if not rule_id:
                self._logger.warning("Rule missing rule_id, skipping")
                continue
            
            rule = GovernanceRule(
                rule_id=rule_id,
                name=name,
                description=description,
                tier=0,
                category=category,
                severity=severity,
            )
            
            self._tier0_rules[rule_id] = rule
        
        return Ok(None)
    
    def add_tier1_rule(self, rule: GovernanceRule) -> Result[None]:
        """
        Add a Tier 1 project governance rule.
        
        Args:
            rule: GovernanceRule to add
        
        Returns:
            Result containing None if successful, error otherwise
        """
        if rule.tier != 1:
            return Err(f"Rule tier must be 1, got {rule.tier}")
        
        if rule.rule_id in self._tier0_rules:
            return Err(f"Cannot override Tier 0 rule {rule.rule_id}")
        
        self._tier1_rules[rule.rule_id] = rule
        return Ok(None)
    
    def add_tier2_rule(self, rule: GovernanceRule) -> Result[None]:
        """
        Add a Tier 2 engineering standards rule.
        
        Args:
            rule: GovernanceRule to add
        
        Returns:
            Result containing None if successful, error otherwise
        """
        if rule.tier != 2:
            return Err(f"Rule tier must be 2, got {rule.tier}")
        
        # Check Tier 0 and Tier 1 precedence
        if rule.rule_id in self._tier0_rules:
            return Err(f"Cannot override Tier 0 rule {rule.rule_id}")
        if rule.rule_id in self._tier1_rules:
            return Err(f"Cannot override Tier 1 rule {rule.rule_id}")
        
        self._tier2_rules[rule.rule_id] = rule
        return Ok(None)
    
    def get_rule(self, rule_id: str) -> Result[Optional[GovernanceRule]]:
        """
        Get a rule by ID, applying tier precedence.
        
        Returns:
            Result containing rule if found (Tier 0 > Tier 1 > Tier 2), None if not found
        """
        # Check Tier 0 first (highest precedence)
        if rule_id in self._tier0_rules:
            return Ok(self._tier0_rules[rule_id])
        
        # Check Tier 1
        if rule_id in self._tier1_rules:
            return Ok(self._tier1_rules[rule_id])
        
        # Check Tier 2
        if rule_id in self._tier2_rules:
            return Ok(self._tier2_rules[rule_id])
        
        return Ok(None)
    
    def get_all_tier0_rules(self) -> List[GovernanceRule]:
        """Get all Tier 0 SKULL rules."""
        return list(self._tier0_rules.values())
    
    def get_all_rules(self) -> Dict[str, Dict[str, List[GovernanceRule]]]:
        """
        Get all rules organized by tier.
        
        Returns:
            Dict with keys 'tier0', 'tier1', 'tier2' containing lists of rules
        """
        return {
            "tier0": list(self._tier0_rules.values()),
            "tier1": list(self._tier1_rules.values()),
            "tier2": list(self._tier2_rules.values()),
        }
    
    def is_immutable(self, rule_id: str) -> Result[bool]:
        """
        Check if a rule is immutable (Tier 0).
        
        Args:
            rule_id: Rule ID to check
        
        Returns:
            Result containing True if immutable, False otherwise
        """
        rule_result = self.get_rule(rule_id)
        if rule_result.is_err():
            return rule_result
        
        rule = rule_result.unwrap()
        if rule is None:
            return Ok(False)
        
        return Ok(rule.is_immutable)
    
    def rule_count_by_tier(self) -> Dict[int, int]:
        """Get count of rules by tier."""
        return {
            0: len(self._tier0_rules),
            1: len(self._tier1_rules),
            2: len(self._tier2_rules),
        }
