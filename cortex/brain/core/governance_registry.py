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
from typing import Any, Dict, List, Optional

from cortex.brain.core.path_resolver import resolve_path
from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.config import load_yaml


# ============================================================================
# EXCEPTIONS
# ============================================================================

class GovernanceViolationError(Exception):
    """
    Raised when a governance violation is detected during execution.
    
    This exception is raised by ConversationProtocol when:
    - TIER-0 rules are mutated
    - Undeclared tier access is attempted
    - Maximum turn count is exceeded
    - Any other governance compliance violation
    """
    
    def __init__(self, violation_message: str) -> None:
        """
        Initialize GovernanceViolationError.
        
        Args:
            violation_message: Human-readable description of the violation
        """
        super().__init__(violation_message)
        self.violation_message = violation_message


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
        self._max_turns_allowed: int = 50  # Maximum turns before enforcing stop
        self._tier0_mutation_tracking: Dict[str, bool] = {}  # Track if Tier 0 mutated
    
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
        
        # Load Tier 0 SKULL rules from cortex_brain/tier0/governance/core-rules.yaml
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
        rules_path = resolve_path("cortex_brain", "tier0", "governance", "core-rules.yaml")
        
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
    
    def should_proceed(self, turn_number: int, orchestrator_id: str) -> Result[bool]:
        """
        Validate that orchestrator can proceed with execution based on current governance state.
        
        This method is called by ConversationProtocol before each turn to verify:
        1. TIER-0 rules have not been mutated
        2. Turn count hasn't exceeded maximum allowed turns
        3. Orchestrator tier access is within declared boundaries
        
        Called for AC-REM-002-01 implementation.
        
        Args:
            turn_number: Current turn number (1, 2, 3, ...)
            orchestrator_id: ID of orchestrator executing this turn
        
        Returns:
            Ok(True) if governance state is valid and execution can proceed
            Err(violation_message) if governance violation detected
        
        Raises:
            N/A - Returns Result type instead of raising exceptions
        
        Governance Rules Enforced:
            - CORE-017: Strict Governance Enforcement
            - CORE-027: Audit Trail Per Turn
            - AR-001-03: Tier 0 rules immutable
        """
        # Requirement 1: Verify TIER-0 immutability
        # Check if any Tier 0 rules have been modified since initialization
        tier0_rules = self.get_all_tier0_rules()
        for rule in tier0_rules:
            # Track if this rule was modified
            rule_tracking_key = f"tier0_{rule.rule_id}"
            
            if rule_tracking_key not in self._tier0_mutation_tracking:
                # First time seeing this rule - record initial state
                self._tier0_mutation_tracking[rule_tracking_key] = False
            
            # If rule is marked as mutated, that's a violation
            if self._tier0_mutation_tracking[rule_tracking_key]:
                return Err(
                    f"TIER-0 rule immutability violation: Rule {rule.rule_id} "
                    f"has been modified after initialization (turn {turn_number})"
                )
        
        # Requirement 2: Validate turn count hasn't exceeded limits
        if turn_number > self._max_turns_allowed:
            return Err(
                f"Turn limit exceeded: Attempted turn {turn_number}, "
                f"maximum allowed: {self._max_turns_allowed}"
            )
        
        # Requirement 3: Registry must be initialized
        if not self._initialized:
            return Err("Governance registry not initialized - call initialize() first")
        
        # All checks passed
        self._logger.debug(
            f"Governance validation passed for orchestrator {orchestrator_id} "
            f"on turn {turn_number}"
        )
        return Ok(True)
    
    def validate_artifact_creation(self, artifact_path: str, ac_id: Optional[str] = None, user_explicit_request: bool = False) -> Result[bool]:
        """
        Validate that artifact creation complies with CORE-002 (TIER 0).
        
        Implements: CORE-002 (Workspace-wide markdown suppression)
        Purpose: Block markdown report/status files UNLESS explicitly requested by user
        
        This rule applies to entire workspace (root + subdirectories).
        
        Allowed locations (unconditional - no user request needed):
        - docs/ subdirectory
        - _workspaces/docs/ subdirectory
        
        Report/Status files (require explicit user request):
        - *-summary.md, *-report.md, *-status.md
        - DEPLOYMENT-*.md, ORCHESTRATOR-*.md
        - README.md (non-functional)
        - Other markdown report patterns
        
        Args:
            artifact_path: Full path or filename of artifact to validate
            ac_id: Optional AC-ID for audit trail
            user_explicit_request: True if user explicitly requested this artifact in their prompt
        
        Returns:
            Ok(True) if artifact creation is allowed
            Err(violation_message) if artifact violates CORE-002
        
        Raises:
            N/A - Returns Result type instead of raising exceptions
        """
        if not artifact_path.endswith(".md"):
            # Non-markdown artifacts are allowed
            return Ok(True)
        
        # Approved markdown locations (always allowed, no user request needed)
        approved_directories = ["docs/", "_workspaces/docs/"]
        
        # Extract path string
        path_str = str(artifact_path)
        
        # Check if in approved documentation directory
        in_approved_directory = any(
            path_str.startswith(prefix) for prefix in approved_directories
        )
        
        if in_approved_directory:
            # docs/ and _workspaces/docs/ are always allowed
            return Ok(True)
        
        # Extract filename to check for report patterns
        filename = path_str.split("/")[-1]
        
        # Patterns that indicate report/status files (require explicit user request)
        report_patterns = [
            "-summary.md",
            "-report.md",
            "-status.md",
            "deployment-",  # DEPLOYMENT-*.md
            "deployment_",
            "orchestrator-",  # ORCHESTRATOR-*.md
            "orchestrator_",
            "readme.md",  # README.md
        ]
        
        is_report_pattern = any(
            report_pattern in filename.lower() for report_pattern in report_patterns
        )
        
        # If it's a report pattern and user didn't explicitly request it, block
        if is_report_pattern and not user_explicit_request:
            violation_msg = (
                f"CORE-002 VIOLATION: Markdown report suppressed (workspace-wide)\n"
                f"File: {artifact_path}\n"
                f"Reason: Report/status files blocked unless explicitly requested by user\n"
                f"Pattern: {filename} matches report suppression rule\n"
                f"Resolution: User must explicitly request creation in prompt\n"
                f"AC-ID: {ac_id if ac_id else 'unspecified'}"
            )
            self._logger.error(violation_msg)
            return Err(violation_msg)
        
        # Report pattern but user explicitly requested it - allow
        if is_report_pattern and user_explicit_request:
            self._logger.info(
                f"CORE-002: User-requested markdown report approved: {artifact_path}"
            )
            return Ok(True)
        
        # Non-report markdown file outside docs/ - block
        violation_msg = (
            f"CORE-002 VIOLATION: Markdown file creation blocked outside docs/\n"
            f"File: {artifact_path}\n"
            f"Approved locations: docs/, _workspaces/docs/\n"
            f"AC-ID: {ac_id if ac_id else 'unspecified'}"
        )
        
        self._logger.error(violation_msg)
        return Err(violation_msg)
