"""
SKULL Protection Test Framework
Base infrastructure for testing brain protection rules
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class Severity(Enum):
    """Rule severity levels."""
    BLOCKED = "blocked"
    WARNING = "warning"
    INFO = "info"


@dataclass
class RuleCheckResult:
    """Result of a SKULL rule check."""
    rule_id: str
    violated: bool
    compliant: bool
    severity: Severity
    message: str
    alternatives: List[str]
    
    def __init__(self, rule_id: str, violated: bool, severity: str = "blocked", 
                 message: str = "", alternatives: List[str] = None):
        self.rule_id = rule_id
        self.violated = violated
        self.compliant = not violated
        self.severity = Severity(severity)
        self.message = message
        self.alternatives = alternatives or []


class SkullViolationError(Exception):
    """Raised when a SKULL rule is violated and enforcement is enabled."""
    pass


class SkullProtector:
    """
    Mock SKULL protection system for testing.
    Simulates brain protection rule checking and enforcement.
    """
    
    def __init__(self):
        self.rules_checked = []
        self.violations_logged = []
    
    def check_rule(self, rule_id: str, data: Dict[str, Any]) -> RuleCheckResult:
        """
        Check if data violates a SKULL rule.
        
        Args:
            rule_id: The SKULL rule to check
            data: The data/scenario to validate
            
        Returns:
            RuleCheckResult with violation status
        """
        self.rules_checked.append(rule_id)
        
        # Simulate rule checking logic
        violated = data.get('violates', False)
        severity = data.get('severity', 'blocked')
        message = data.get('message', f'{rule_id} check completed')
        
        result = RuleCheckResult(
            rule_id=rule_id,
            violated=violated,
            severity=severity,
            message=message,
            alternatives=[
                f"Follow {rule_id} guidelines",
                f"Review brain-protection-rules.yaml for {rule_id}",
                f"Use recommended patterns for {rule_id}"
            ]
        )
        
        if violated:
            self.violations_logged.append(result)
        
        return result
    
    def enforce(self, rule_id: str, operation: callable, **kwargs) -> Any:
        """
        Enforce a SKULL rule before executing an operation.
        
        Args:
            rule_id: The SKULL rule to enforce
            operation: The operation to execute if compliant
            **kwargs: Data to validate against the rule
            
        Returns:
            Result of operation if compliant
            
        Raises:
            SkullViolationError: If rule is violated
        """
        result = self.check_rule(rule_id, kwargs)
        
        if result.violated and result.severity == Severity.BLOCKED:
            raise SkullViolationError(
                f"SKULL Rule Violation: {rule_id}\n"
                f"Message: {result.message}\n"
                f"Alternatives: {', '.join(result.alternatives)}"
            )
        
        return operation()
    
    def get_rule_metadata(self, rule_id: str) -> Dict[str, Any]:
        """Get metadata about a SKULL rule."""
        return {
            'rule_id': rule_id,
            'severity': 'blocked',
            'description': f'Brain protection rule: {rule_id}',
            'enforcement': 'automated'
        }


class BrainProtectionValidator:
    """
    Validator for brain protection compliance.
    Used in test scenarios to validate specific protection scenarios.
    """
    
    def __init__(self):
        self.skull = SkullProtector()
    
    def validate_tdd_workflow(self, data: Dict[str, Any]) -> bool:
        """Validate TDD workflow compliance."""
        required = ['red_phase', 'green_phase', 'refactor_phase']
        return all(key in data for key in required)
    
    def validate_file_organization(self, file_path: str) -> bool:
        """Validate file is in correct location."""
        valid_paths = ['tests/', 'src/', 'cortex-brain/documents/']
        return any(file_path.startswith(path) for path in valid_paths)
    
    def validate_planning_structure(self, plan: Dict[str, Any]) -> bool:
        """Validate plan structure compliance."""
        required = ['phases', 'context', 'artifacts', 'tracking']
        return all(key in plan for key in required)
    
    def validate_git_checkpoint(self, checkpoint: Dict[str, Any]) -> bool:
        """Validate git checkpoint exists and is valid."""
        return checkpoint.get('commit_hash') and checkpoint.get('timestamp')
    
    def validate_documentation_location(self, doc_path: str) -> bool:
        """Validate documentation is in correct location."""
        return doc_path.startswith('cortex-brain/documents/')
