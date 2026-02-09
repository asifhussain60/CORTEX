"""
Policy Engine for Compliance and Governance

AC_START: AC-PHASE60.0-S2-001
Authority: phase-60-enterprise-pattern-registry.yaml Stage 2
Purpose: Implement policy evaluation and compliance checking
         - Policy definition and registration
         - Rule-based policy evaluation
         - Compliance report generation
         - Multi-policy enforcement

Tests Target: 12 tests (policy loading, rule evaluation, compliance checking)
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import jsonschema


# ============================================================================
# Enums and Constants
# ============================================================================

class PolicyLevel(Enum):
    """Policy enforcement levels."""
    STRICT = "strict"      # Must comply
    WARNING = "warning"    # Should comply
    ADVISORY = "advisory"  # Consider complying


class ComplianceStatus(Enum):
    """Compliance status for evaluated items."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    UNKNOWN = "unknown"


class RuleOperator(Enum):
    """Operators for rule conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PolicyRule:
    """A single policy rule for evaluation."""
    id: str
    description: str
    operator: RuleOperator
    field: str
    value: Any
    severity: str = "error"  # error, warning, info
    error_message: Optional[str] = None
    
    def matches(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluate rule against data.
        
        Args:
            data: Data to evaluate against
        
        Returns:
            Tuple of (rule_passed, reason)
        """
        field_value = data.get(self.field)
        
        try:
            if self.operator == RuleOperator.EQUALS:
                passed = field_value == self.value
            elif self.operator == RuleOperator.NOT_EQUALS:
                passed = field_value != self.value
            elif self.operator == RuleOperator.GREATER_THAN:
                passed = field_value > self.value
            elif self.operator == RuleOperator.LESS_THAN:
                passed = field_value < self.value
            elif self.operator == RuleOperator.CONTAINS:
                passed = self.value in str(field_value)
            elif self.operator == RuleOperator.NOT_CONTAINS:
                passed = self.value not in str(field_value)
            elif self.operator == RuleOperator.IN:
                passed = field_value in self.value
            elif self.operator == RuleOperator.NOT_IN:
                passed = field_value not in self.value
            elif self.operator == RuleOperator.REGEX:
                import re
                passed = bool(re.match(self.value, str(field_value)))
            else:
                return False, f"Unknown operator: {self.operator}"
            
            reason = self.error_message or f"Rule {self.id}: {self.description}"
            return passed, reason
        
        except Exception as e:
            return False, f"Error evaluating rule {self.id}: {str(e)}"


@dataclass
class PolicyMetadata:
    """Metadata for a compliance policy."""
    id: str
    name: str
    description: str
    level: PolicyLevel
    rules: List[PolicyRule] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)  # SOC2, HIPAA, etc.
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    author: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Validate policy metadata."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Policy ID must be a non-empty string")
        
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Policy name must be a non-empty string")
        
        if not isinstance(self.level, PolicyLevel):
            raise ValueError(f"Invalid policy level: {self.level}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.level:
            data['level'] = self.level.value
        data['rules'] = [asdict(r) for r in self.rules]
        for rule_dict in data['rules']:
            if 'operator' in rule_dict and isinstance(rule_dict['operator'], RuleOperator):
                rule_dict['operator'] = rule_dict['operator'].value
        return data


@dataclass
class ComplianceViolation:
    """A compliance violation found during evaluation."""
    policy_id: str
    rule_id: str
    description: str
    severity: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ComplianceReport:
    """Report of compliance evaluation."""
    evaluated_at: str
    policy_id: str
    status: ComplianceStatus
    compliant: bool
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 1.0  # 0-1, 1.0 = fully compliant
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'evaluated_at': self.evaluated_at,
            'policy_id': self.policy_id,
            'status': self.status.value,
            'compliant': self.compliant,
            'violations': [asdict(v) for v in self.violations],
            'warnings': self.warnings,
            'score': self.score
        }


# ============================================================================
# Policy Engine
# ============================================================================

class PolicyEngine:
    """Engine for evaluating policies and compliance."""
    
    def __init__(self):
        """Initialize policy engine."""
        self.policies: Dict[str, PolicyMetadata] = {}
        self._evaluation_history: List[ComplianceReport] = []
    
    def register_policy(self, policy: PolicyMetadata) -> Tuple[bool, str]:
        """Register a policy.
        
        Args:
            policy: Policy to register
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if policy.id in self.policies:
                return False, f"Policy '{policy.id}' already exists"
            
            self.policies[policy.id] = policy
            return True, f"Policy '{policy.id}' registered successfully"
        
        except Exception as e:
            return False, f"Error registering policy: {str(e)}"
    
    def evaluate_data(self, policy_id: str, data: Dict[str, Any]) -> ComplianceReport:
        """Evaluate data against policy.
        
        Args:
            policy_id: ID of policy to evaluate
            data: Data to evaluate
        
        Returns:
            ComplianceReport with results
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return ComplianceReport(
                evaluated_at=datetime.utcnow().isoformat(),
                policy_id=policy_id,
                status=ComplianceStatus.UNKNOWN,
                compliant=False,
                violations=[],
                warnings=[f"Policy '{policy_id}' not found"]
            )
        
        violations: List[ComplianceViolation] = []
        warnings: List[str] = []
        
        # Evaluate all rules
        for rule in policy.rules:
            passed, reason = rule.matches(data)
            
            if not passed:
                violation = ComplianceViolation(
                    policy_id=policy_id,
                    rule_id=rule.id,
                    description=reason,
                    severity=rule.severity,
                    data=data
                )
                violations.append(violation)
                
                if rule.severity == "warning":
                    warnings.append(reason)
        
        # Determine compliance status
        if not violations:
            status = ComplianceStatus.COMPLIANT
            compliant = True
            score = 1.0
        else:
            has_errors = any(v.severity == "error" for v in violations)
            if has_errors:
                status = ComplianceStatus.NON_COMPLIANT
                compliant = False
            else:
                status = ComplianceStatus.WARNING
                compliant = False
            
            score = max(0.0, 1.0 - (len(violations) / len(policy.rules)))
        
        report = ComplianceReport(
            evaluated_at=datetime.utcnow().isoformat(),
            policy_id=policy_id,
            status=status,
            compliant=compliant,
            violations=violations,
            warnings=warnings,
            score=score
        )
        
        self._evaluation_history.append(report)
        return report
    
    def evaluate_multiple_policies(
        self,
        policy_ids: List[str],
        data: Dict[str, Any]
    ) -> List[ComplianceReport]:
        """Evaluate data against multiple policies.
        
        Args:
            policy_ids: List of policy IDs to evaluate
            data: Data to evaluate
        
        Returns:
            List of ComplianceReports
        """
        return [self.evaluate_data(policy_id, data) for policy_id in policy_ids]
    
    def get_policy(self, policy_id: str) -> Optional[PolicyMetadata]:
        """Get policy by ID.
        
        Args:
            policy_id: Policy identifier
        
        Returns:
            PolicyMetadata or None
        """
        return self.policies.get(policy_id)
    
    def list_policies(self) -> List[PolicyMetadata]:
        """List all registered policies.
        
        Returns:
            List of policies
        """
        return list(self.policies.values())
    
    def get_policies_by_framework(self, framework: str) -> List[PolicyMetadata]:
        """Get policies for a compliance framework.
        
        Args:
            framework: Framework name (e.g., 'SOC2', 'HIPAA')
        
        Returns:
            List of policies
        """
        return [
            p for p in self.policies.values()
            if framework in p.frameworks
        ]
    
    def get_evaluation_history(self, policy_id: Optional[str] = None) -> List[ComplianceReport]:
        """Get evaluation history.
        
        Args:
            policy_id: Optional filter by policy ID
        
        Returns:
            List of ComplianceReports
        """
        if policy_id:
            return [r for r in self._evaluation_history if r.policy_id == policy_id]
        return self._evaluation_history


# AC_COMPLETE: AC-PHASE60.0-S2-001 ✅
# ✅ PolicyEngine with rule evaluation
# ✅ Compliance status determination
# ✅ Multi-policy evaluation
# ✅ Evaluation history tracking
# ✅ Framework-based policy querying
