"""
CORTEX Tier 0: Governance Engine
Enforces immutable governance rules and protects system integrity.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class Severity(Enum):
    """Rule severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ViolationType(Enum):
    """Types of governance violations"""
    TDD_IMPLEMENTATION_WITHOUT_TEST = "implementing_without_test"
    TDD_SKIPPING_RED_PHASE = "skipping_red_phase"
    TDD_NO_REFACTOR = "no_refactor"
    DOD_CRITERIA_NOT_MET = "dod_criteria_not_met"
    DOR_CRITERIA_NOT_MET = "dor_criteria_not_met"
    TIER_BOUNDARY_VIOLATION = "tier_boundary_violation"
    SOLID_SRP_VIOLATION = "srp_violation"
    SOLID_ISP_VIOLATION = "isp_violation"
    SOLID_DIP_VIOLATION = "dip_violation"
    FILE_ORG_DUAL_INTERFACE = "dual_interface_violation"
    FILE_ORG_LIVE_DESIGN_DOC = "live_design_doc_not_updated"
    FILE_ORG_ARCHIVE_CREATED = "archive_folder_created"


class GovernanceEngine:
    """
    Tier 0 Governance Engine
    
    Responsibilities:
    - Load and validate governance rules
    - Check for rule violations
    - Create challenges for risky changes
    - Validate Definition of Done/Ready
    - Enforce tier boundaries
    """
    
    def __init__(self, governance_file: Optional[Path] = None):
        """
        Initialize the governance engine.
        
        Args:
            governance_file: Path to governance.yaml. If None, uses default location.
        """
        if governance_file is None:
            governance_file = Path(__file__).parent / "governance.yaml"
        
        self.governance_file = governance_file
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.violations_log: List[Dict[str, Any]] = []
        self._load_governance()
    
    def _load_governance(self) -> None:
        """Load governance rules from YAML file with caching."""
        if not self.governance_file.exists():
            raise FileNotFoundError(
                f"Governance file not found: {self.governance_file}"
            )
        
        try:
            # Use universal YAML cache for performance
            from src.utils.yaml_cache import load_yaml_cached
            data = load_yaml_cached(self.governance_file)
        except ImportError:
            # Fallback to direct loading
            with open(self.governance_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        
        # Validate governance file structure
        if not data or 'rules' not in data:
            raise ValueError("Invalid governance file: missing 'rules' section")
        
        # Index rules by ID for fast lookup
        for rule in data['rules']:
            if 'id' not in rule:
                raise ValueError("Invalid rule: missing 'id' field")
            self.rules[rule['id']] = rule
        
        # Store metadata
        self.version = data.get('version', '1.0')
        self.rule_count = data.get('rule_count', len(self.rules))
        self.last_updated = data.get('last_updated')
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a governance rule by ID.
        
        Args:
            rule_id: Rule identifier (e.g., 'TEST_FIRST_TDD')
        
        Returns:
            Rule dictionary or None if not found
        """
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all governance rules."""
        return list(self.rules.values())
    
    def get_rules_by_severity(self, severity: Severity) -> List[Dict[str, Any]]:
        """
        Get all rules of a specific severity.
        
        Args:
            severity: Severity level to filter by
        
        Returns:
            List of rules matching the severity
        """
        return [
            rule for rule in self.rules.values()
            if rule.get('severity') == severity.value
        ]
    
    def check_tdd_violation(
        self,
        has_new_code: bool,
        has_new_test: bool,
        test_written_first: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Check for TDD (Test-First Development) violations.
        
        Args:
            has_new_code: Whether new production code was added
            has_new_test: Whether new test was added
            test_written_first: Whether test was written before code
        
        Returns:
            Violation details or None if no violation
        """
        rule = self.get_rule('TEST_FIRST_TDD')
        if not rule:
            return None
        
        violation = None
        
        if has_new_code and not has_new_test:
            violation = {
                'rule_id': 'TEST_FIRST_TDD',
                'rule_name': rule['name'],
                'violation_type': ViolationType.TDD_IMPLEMENTATION_WITHOUT_TEST.value,
                'severity': rule['severity'],
                'action': 'BLOCKED',
                'message': 'New code detected without corresponding test. TDD requires test-first development.',
                'timestamp': datetime.now().isoformat()
            }
        elif has_new_code and has_new_test and not test_written_first:
            violation = {
                'rule_id': 'TEST_FIRST_TDD',
                'rule_name': rule['name'],
                'violation_type': ViolationType.TDD_SKIPPING_RED_PHASE.value,
                'severity': rule['severity'],
                'action': 'CHALLENGED',
                'message': 'Test appears to be written after code. TDD requires RED phase first.',
                'timestamp': datetime.now().isoformat()
            }
        
        if violation:
            self.violations_log.append(violation)
        
        return violation
    
    def validate_definition_of_done(
        self,
        compilation_clean: bool = True,
        tests_pass: bool = True,
        new_tests_created: bool = True,
        tdd_cycle_complete: bool = True,
        code_formatted: bool = True,
        no_lint_violations: bool = True,
        docs_updated: bool = True,
        app_runs: bool = True,
        no_exceptions: bool = True,
        functionality_verified: bool = True
    ) -> Dict[str, Any]:
        """
        Validate Definition of Done criteria.
        
        Returns:
            Validation result with status and failed criteria
        """
        rule = self.get_rule('DEFINITION_OF_DONE')
        if not rule:
            return {'valid': False, 'error': 'DoD rule not found'}
        
        criteria_results = {
            'compilation': compilation_clean,
            'tests_pass': tests_pass,
            'new_tests_created': new_tests_created,
            'tdd_cycle_complete': tdd_cycle_complete,
            'code_formatted': code_formatted,
            'no_lint_violations': no_lint_violations,
            'docs_updated': docs_updated,
            'app_runs': app_runs,
            'no_exceptions': no_exceptions,
            'functionality_verified': functionality_verified
        }
        
        failed_criteria = [
            criterion for criterion, passed in criteria_results.items()
            if not passed
        ]
        
        is_valid = len(failed_criteria) == 0
        
        result = {
            'valid': is_valid,
            'rule_id': 'DEFINITION_OF_DONE',
            'failed_criteria': failed_criteria,
            'timestamp': datetime.now().isoformat()
        }
        
        if not is_valid:
            violation = {
                'rule_id': 'DEFINITION_OF_DONE',
                'rule_name': rule['name'],
                'violation_type': ViolationType.DOD_CRITERIA_NOT_MET.value,
                'severity': rule['severity'],
                'action': 'BLOCKED',
                'message': f'Definition of Done not met. Failed criteria: {", ".join(failed_criteria)}',
                'timestamp': datetime.now().isoformat()
            }
            self.violations_log.append(violation)
            result['violation'] = violation
        
        return result
    
    def validate_definition_of_ready(
        self,
        user_story_clear: bool = True,
        acceptance_criteria_defined: bool = True,
        testable_outcomes: bool = True,
        scope_bounded: bool = True,
        dependencies_identified: bool = True,
        estimate_possible: bool = True,
        files_known: bool = True,
        architecture_clear: bool = True,
        no_blocking_dependencies: bool = True
    ) -> Dict[str, Any]:
        """
        Validate Definition of Ready criteria.
        
        Returns:
            Validation result with status and failed criteria
        """
        rule = self.get_rule('DEFINITION_OF_READY')
        if not rule:
            return {'valid': False, 'error': 'DoR rule not found'}
        
        criteria_results = {
            'user_story_clear': user_story_clear,
            'acceptance_criteria_defined': acceptance_criteria_defined,
            'testable_outcomes': testable_outcomes,
            'scope_bounded': scope_bounded,
            'dependencies_identified': dependencies_identified,
            'estimate_possible': estimate_possible,
            'files_known': files_known,
            'architecture_clear': architecture_clear,
            'no_blocking_dependencies': no_blocking_dependencies
        }
        
        failed_criteria = [
            criterion for criterion, passed in criteria_results.items()
            if not passed
        ]
        
        is_valid = len(failed_criteria) == 0
        
        result = {
            'valid': is_valid,
            'rule_id': 'DEFINITION_OF_READY',
            'failed_criteria': failed_criteria,
            'timestamp': datetime.now().isoformat()
        }
        
        if not is_valid:
            violation = {
                'rule_id': 'DEFINITION_OF_READY',
                'rule_name': rule['name'],
                'violation_type': ViolationType.DOR_CRITERIA_NOT_MET.value,
                'severity': rule['severity'],
                'action': 'BLOCKED',
                'message': f'Definition of Ready not met. Failed criteria: {", ".join(failed_criteria)}',
                'timestamp': datetime.now().isoformat()
            }
            self.violations_log.append(violation)
            result['violation'] = violation
        
        return result
    
    def check_tier_boundary_violation(
        self,
        tier: int,
        data_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if data is in the correct tier.
        
        Args:
            tier: Tier number (0-3)
            data_type: Type of data (e.g., 'conversation', 'pattern', 'governance')
        
        Returns:
            Violation details or None if no violation
        """
        rule = self.get_rule('TIER_BOUNDARIES')
        if not rule:
            return None
        
        # Define forbidden data types per tier
        tier_rules = {
            0: {
                'allowed': ['governance', 'core_principles'],
                'forbidden': ['application_data', 'file_paths', 'conversations']
            },
            1: {
                'allowed': ['conversations', 'entities'],
                'forbidden': ['patterns', 'git_metrics', 'governance']
            },
            2: {
                'allowed': ['patterns', 'learnings'],
                'forbidden': ['conversation_details', 'raw_events', 'governance']
            },
            3: {
                'allowed': ['git_metrics', 'test_metrics', 'build_metrics'],
                'forbidden': ['conversations', 'governance', 'patterns']
            }
        }
        
        if tier not in tier_rules:
            return None
        
        tier_config = tier_rules[tier]
        
        if data_type in tier_config['forbidden']:
            violation = {
                'rule_id': 'TIER_BOUNDARIES',
                'rule_name': rule['name'],
                'violation_type': ViolationType.TIER_BOUNDARY_VIOLATION.value,
                'severity': rule['severity'],
                'action': 'CHALLENGED',
                'message': f'{data_type} data is forbidden in Tier {tier}. Should be migrated.',
                'details': {
                    'tier': tier,
                    'data_type': data_type,
                    'allowed_types': tier_config['allowed']
                },
                'timestamp': datetime.now().isoformat()
            }
            self.violations_log.append(violation)
            return violation
        
        return None
    
    def create_challenge(
        self,
        proposed_change: str,
        risks: List[str],
        alternatives: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a challenge for a risky user-proposed change.
        
        Args:
            proposed_change: Description of what user wants to change
            risks: List of identified risks
            alternatives: Optional list of safer alternatives
        
        Returns:
            Challenge details to present to user
        """
        rule = self.get_rule('CHALLENGE_USER_CHANGES')
        if not rule:
            return {'challenge_created': False, 'error': 'Challenge rule not found'}
        
        challenge = {
            'rule_id': 'CHALLENGE_USER_CHANGES',
            'proposed_change': proposed_change,
            'risks_identified': risks,
            'alternatives': alternatives or [],
            'requires_explicit_override': True,
            'challenge_timestamp': datetime.now().isoformat()
        }
        
        return challenge
    
    def get_violations(
        self,
        severity: Optional[Severity] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logged violations.
        
        Args:
            severity: Filter by severity level
            limit: Maximum number of violations to return
        
        Returns:
            List of violations
        """
        violations = self.violations_log
        
        if severity:
            violations = [
                v for v in violations
                if v.get('severity') == severity.value
            ]
        
        if limit:
            violations = violations[-limit:]
        
        return violations
    
    def clear_violations(self) -> None:
        """Clear the violations log."""
        self.violations_log.clear()
