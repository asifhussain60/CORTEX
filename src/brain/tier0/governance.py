"""
Tier 0: Governance Engine for CORTEX 4.0

Enforces SKULL brain protection rules:
- TDD_ENFORCEMENT: RED→GREEN→REFACTOR mandatory
- RED_PHASE_VALIDATION: Tests must fail before implementation
- HOLISTIC_CODE_DISCOVERY_ENFORCEMENT: Search before create
- REFACTOR_CODE_CLEANUP_ENFORCEMENT: Remove orphaned code
- GIT_ISOLATION_ENFORCEMENT: CORTEX code never in user repos
- TEST_LOCATION_SEPARATION: Separate test locations

Storage: ~/.cortex/shared/skull_rules.yaml (centralized, immutable)

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class SkullRuleId(Enum):
    """SKULL protection rule identifiers."""
    TDD_ENFORCEMENT = "SKULL-TDD-001"
    RED_PHASE_VALIDATION = "SKULL-TDD-002"
    HOLISTIC_CODE_DISCOVERY_ENFORCEMENT = "SKULL-DISC-001"
    REFACTOR_CODE_CLEANUP_ENFORCEMENT = "SKULL-REF-001"
    GIT_ISOLATION_ENFORCEMENT = "SKULL-GIT-001"
    TEST_LOCATION_SEPARATION = "SKULL-TEST-001"


class EnforcementLevel(Enum):
    """Enforcement levels for SKULL rules."""
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of SKULL rule validation."""
    passed: bool
    rule_id: SkullRuleId
    rule_name: str
    message: str
    enforcement: EnforcementLevel
    evidence: Optional[Dict[str, Any]] = None


class GovernanceEngine:
    """
    Tier 0: Governance Engine - SKULL Protection Layer
    
    Validates operations against brain protection rules before execution.
    Prevents harmful operations, enforces TDD, maintains code quality.
    
    Usage:
        governance = GovernanceEngine(rules_path)
        
        # Validate TDD phase transition
        result = governance.validate_tdd_phase("green", tests_run=["test_foo.py"])
        if not result.passed:
            raise ValueError(result.message)
    """
    
    def __init__(self, rules_path: Path):
        """
        Initialize governance engine.
        
        Args:
            rules_path: Path to skull_rules.yaml
        """
        self.rules_path = Path(rules_path)
        self.logger = logging.getLogger(__name__)
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """
        Load SKULL rules from YAML.
        
        Returns:
            Dictionary of rules configuration
        """
        if not self.rules_path.exists():
            self.logger.warning(f"SKULL rules not found at {self.rules_path}, using defaults")
            return self._get_default_rules()
        
        try:
            with open(self.rules_path, 'r') as f:
                rules = yaml.safe_load(f)
                self.logger.info(f"Loaded SKULL rules from {self.rules_path}")
                return rules
        except Exception as e:
            self.logger.error(f"Failed to load SKULL rules: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default SKULL rules configuration."""
        return {
            "version": "4.0",
            "rules": {
                "TDD_ENFORCEMENT": {
                    "enabled": True,
                    "enforcement_level": "blocking",
                    "description": "RED→GREEN→REFACTOR cycle mandatory"
                },
                "RED_PHASE_VALIDATION": {
                    "enabled": True,
                    "enforcement_level": "blocking",
                    "description": "Tests must fail before implementation"
                },
                "HOLISTIC_CODE_DISCOVERY_ENFORCEMENT": {
                    "enabled": True,
                    "enforcement_level": "warning",
                    "description": "Search before create to prevent duplication"
                },
                "REFACTOR_CODE_CLEANUP_ENFORCEMENT": {
                    "enabled": True,
                    "enforcement_level": "warning",
                    "description": "Remove orphaned/duplicate code during refactor"
                },
                "GIT_ISOLATION_ENFORCEMENT": {
                    "enabled": True,
                    "enforcement_level": "blocking",
                    "description": "CORTEX code never in user repositories"
                },
                "TEST_LOCATION_SEPARATION": {
                    "enabled": True,
                    "enforcement_level": "blocking",
                    "description": "App tests in user repo, CORTEX tests in tests/"
                }
            }
        }
    
    def validate_tdd_phase(
        self,
        target_phase: str,
        tests_run: Optional[List[str]] = None,
        test_results: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate TDD phase transition.
        
        Args:
            target_phase: Target phase (red, green, refactor)
            tests_run: List of test files executed
            test_results: Test execution results
            
        Returns:
            ValidationResult with pass/fail status
        """
        target_phase = target_phase.lower()
        
        # Validate RED → GREEN transition
        if target_phase == "green":
            if not tests_run:
                return ValidationResult(
                    passed=False,
                    rule_id=SkullRuleId.TDD_ENFORCEMENT,
                    rule_name="TDD Enforcement",
                    message="Cannot transition to GREEN: No tests executed in RED phase",
                    enforcement=EnforcementLevel.BLOCKING,
                    evidence={"tests_run": tests_run}
                )
            
            # Validate tests failed in RED phase
            if test_results and test_results.get("all_passed", False):
                return ValidationResult(
                    passed=False,
                    rule_id=SkullRuleId.RED_PHASE_VALIDATION,
                    rule_name="RED Phase Validation",
                    message="Cannot transition to GREEN: Tests already passing (RED phase not validated)",
                    enforcement=EnforcementLevel.BLOCKING,
                    evidence={"test_results": test_results}
                )
        
        # Validate GREEN → REFACTOR transition
        if target_phase == "refactor":
            if test_results and not test_results.get("all_passed", False):
                return ValidationResult(
                    passed=False,
                    rule_id=SkullRuleId.TDD_ENFORCEMENT,
                    rule_name="TDD Enforcement",
                    message="Cannot transition to REFACTOR: Tests not passing in GREEN phase",
                    enforcement=EnforcementLevel.BLOCKING,
                    evidence={"test_results": test_results}
                )
        
        return ValidationResult(
            passed=True,
            rule_id=SkullRuleId.TDD_ENFORCEMENT,
            rule_name="TDD Enforcement",
            message=f"TDD phase transition to {target_phase.upper()} validated",
            enforcement=EnforcementLevel.INFO
        )
    
    def validate_code_creation(
        self,
        file_path: Path,
        search_performed: bool = False,
        duplicates_found: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate new code creation (holistic discovery).
        
        Args:
            file_path: Path to file being created
            search_performed: Whether search for existing code was performed
            duplicates_found: List of potential duplicate files
            
        Returns:
            ValidationResult with pass/fail status
        """
        if not search_performed:
            return ValidationResult(
                passed=False,
                rule_id=SkullRuleId.HOLISTIC_CODE_DISCOVERY_ENFORCEMENT,
                rule_name="Holistic Code Discovery",
                message=f"Creating {file_path.name}: Must search for existing implementations first",
                enforcement=EnforcementLevel.WARNING,
                evidence={"file_path": str(file_path)}
            )
        
        if duplicates_found:
            return ValidationResult(
                passed=False,
                rule_id=SkullRuleId.HOLISTIC_CODE_DISCOVERY_ENFORCEMENT,
                rule_name="Holistic Code Discovery",
                message=f"Potential duplicates found: {', '.join(duplicates_found)}. Consider reusing existing code.",
                enforcement=EnforcementLevel.WARNING,
                evidence={"duplicates": duplicates_found}
            )
        
        return ValidationResult(
            passed=True,
            rule_id=SkullRuleId.HOLISTIC_CODE_DISCOVERY_ENFORCEMENT,
            rule_name="Holistic Code Discovery",
            message=f"Code creation validated: no duplicates found",
            enforcement=EnforcementLevel.INFO
        )
    
    def validate_git_isolation(
        self,
        file_path: Path,
        workspace_root: Path
    ) -> ValidationResult:
        """
        Validate git isolation (CORTEX code not in user repos).
        
        Args:
            file_path: Path to file being modified
            workspace_root: Root of the workspace
            
        Returns:
            ValidationResult with pass/fail status
        """
        # Check if file is in CORTEX directory or user repo
        try:
            relative_path = file_path.relative_to(workspace_root)
            
            # CORTEX files should NOT be in user repos
            is_cortex_file = any(part.startswith("cortex") for part in relative_path.parts)
            is_in_src = "src" in relative_path.parts
            
            if is_cortex_file and not is_in_src:
                # CORTEX files outside src/ might be in user repo
                return ValidationResult(
                    passed=False,
                    rule_id=SkullRuleId.GIT_ISOLATION_ENFORCEMENT,
                    rule_name="Git Isolation",
                    message=f"CORTEX file {relative_path} appears to be in user repository",
                    enforcement=EnforcementLevel.BLOCKING,
                    evidence={"file_path": str(relative_path)}
                )
        
        except ValueError:
            # File not in workspace, likely external
            pass
        
        return ValidationResult(
            passed=True,
            rule_id=SkullRuleId.GIT_ISOLATION_ENFORCEMENT,
            rule_name="Git Isolation",
            message="Git isolation validated",
            enforcement=EnforcementLevel.INFO
        )
    
    def validate_test_location(
        self,
        test_file: Path,
        workspace_root: Path,
        is_cortex_test: bool = False
    ) -> ValidationResult:
        """
        Validate test file location.
        
        Args:
            test_file: Path to test file
            workspace_root: Root of the workspace
            is_cortex_test: Whether this is a CORTEX internal test
            
        Returns:
            ValidationResult with pass/fail status
        """
        try:
            relative_path = test_file.relative_to(workspace_root)
            
            # CORTEX tests should be in tests/ directory
            if is_cortex_test:
                if not str(relative_path).startswith("tests/"):
                    return ValidationResult(
                        passed=False,
                        rule_id=SkullRuleId.TEST_LOCATION_SEPARATION,
                        rule_name="Test Location Separation",
                        message=f"CORTEX test {relative_path} must be in tests/ directory",
                        enforcement=EnforcementLevel.BLOCKING,
                        evidence={"test_file": str(relative_path)}
                    )
            
            # User tests should NOT be in tests/ directory
            else:
                if str(relative_path).startswith("tests/"):
                    return ValidationResult(
                        passed=False,
                        rule_id=SkullRuleId.TEST_LOCATION_SEPARATION,
                        rule_name="Test Location Separation",
                        message=f"User test {relative_path} should be in application test directory, not tests/",
                        enforcement=EnforcementLevel.WARNING,
                        evidence={"test_file": str(relative_path)}
                    )
        
        except ValueError:
            # File not in workspace
            pass
        
        return ValidationResult(
            passed=True,
            rule_id=SkullRuleId.TEST_LOCATION_SEPARATION,
            rule_name="Test Location Separation",
            message="Test location validated",
            enforcement=EnforcementLevel.INFO
        )
    
    def is_rule_enabled(self, rule_id: SkullRuleId) -> bool:
        """
        Check if a SKULL rule is enabled.
        
        Args:
            rule_id: SKULL rule identifier
            
        Returns:
            True if rule is enabled
        """
        rule_name = rule_id.name
        return self.rules.get("rules", {}).get(rule_name, {}).get("enabled", False)
    
    def get_enforcement_level(self, rule_id: SkullRuleId) -> EnforcementLevel:
        """
        Get enforcement level for a SKULL rule.
        
        Args:
            rule_id: SKULL rule identifier
            
        Returns:
            Enforcement level
        """
        rule_name = rule_id.name
        level_str = self.rules.get("rules", {}).get(rule_name, {}).get("enforcement_level", "warning")
        return EnforcementLevel(level_str)
