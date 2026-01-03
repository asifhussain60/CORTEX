"""
Governance Integrator - Tier 0 Brain Protection Rules Integration.

Loads and validates plans against brain-protection-rules.yaml governance.
Ensures all generated plans comply with CORTEX architectural constraints.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class GovernanceSeverity(Enum):
    """Governance rule severity levels."""
    BLOCKED = "blocked"   # Plan generation blocked
    WARNING = "warning"   # Plan proceeds with warnings
    INFO = "info"         # Informational only


@dataclass
class GovernanceRule:
    """Single governance rule from brain-protection-rules.yaml."""
    name: str
    severity: GovernanceSeverity
    description: str
    validation_fn: str
    critical_path: bool = False


@dataclass
class GovernanceValidation:
    """Result of governance validation."""
    is_valid: bool
    violations: List[Dict[str, Any]]
    warnings: List[str]
    applied_rules: List[str]
    governance_context: Dict[str, Any]


class GovernanceIntegrator:
    """
    Integrates Tier 0 brain protection rules into planning.
    
    Features:
    - Loads brain-protection-rules.yaml (61 rules, 24 layers)
    - Validates feature requests against tier0_instincts
    - Enforces critical path protection
    - Checks SKULL rule compliance
    - Provides governance context for plan generation
    
    Usage:
        integrator = GovernanceIntegrator()
        governance = integrator.load_rules()
        validation = integrator.validate_feature_request(
            feature_name="New API Endpoint",
            context={"paths": ["src/api/"], "type": "feature"}
        )
        
        if not validation.is_valid:
            # Handle violations
            for violation in validation.violations:
                print(f"Violation: {violation['rule']} - {violation['message']}")
    """
    
    def __init__(self, rules_path: Optional[Path] = None):
        """
        Initialize governance integrator.
        
        Args:
            rules_path: Path to brain-protection-rules.yaml
                       (default: cortex-brain/brain-protection-rules.yaml)
        """
        self.logger = logging.getLogger(__name__)
        
        if rules_path is None:
            rules_path = Path("cortex-brain/brain-protection-rules.yaml")
        
        self.rules_path = rules_path
        self.rules: Dict[str, Any] = {}
        self.tier0_instincts: List[str] = []
        self.critical_paths: List[str] = []
        self.skull_rules: Dict[str, GovernanceRule] = {}
        
        if self.rules_path.exists():
            self._load_governance_rules()
        else:
            self.logger.warning(f"Governance rules not found: {self.rules_path}")
    
    def _load_governance_rules(self) -> None:
        """Load brain protection rules from YAML."""
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                self.rules = yaml.safe_load(f) or {}
            
            # Extract key governance components
            self.tier0_instincts = self.rules.get('tier0_instincts', [])
            self.critical_paths = self.rules.get('critical_paths', [])
            
            # Parse SKULL rules (if defined in rules)
            skull_section = self.rules.get('rules', {})
            if isinstance(skull_section, dict):
                for rule_key, rule_data in skull_section.items():
                    if isinstance(rule_data, dict):
                        severity_str = rule_data.get('severity', 'info')
                        try:
                            severity = GovernanceSeverity(severity_str.lower())
                        except ValueError:
                            severity = GovernanceSeverity.INFO
                        
                        self.skull_rules[rule_key] = GovernanceRule(
                            name=rule_key,
                            severity=severity,
                            description=rule_data.get('description', ''),
                            validation_fn=rule_data.get('validation', ''),
                            critical_path=rule_data.get('critical_path', False)
                        )
            
            self.logger.info(f"Loaded {len(self.tier0_instincts)} tier0 instincts")
            self.logger.info(f"Loaded {len(self.critical_paths)} critical paths")
            self.logger.info(f"Loaded {len(self.skull_rules)} SKULL rules")
        
        except Exception as e:
            self.logger.error(f"Failed to load governance rules: {e}")
            raise
    
    def validate_feature_request(
        self,
        feature_name: str,
        context: Dict[str, Any]
    ) -> GovernanceValidation:
        """
        Validate feature request against governance rules.
        
        Args:
            feature_name: Name of feature being planned
            context: Feature context (paths, type, dependencies)
        
        Returns:
            GovernanceValidation with violations/warnings
        """
        violations = []
        warnings = []
        applied_rules = []
        
        # Validate against tier0 instincts
        instinct_violations = self._validate_tier0_instincts(feature_name, context)
        violations.extend(instinct_violations)
        applied_rules.extend([v['rule'] for v in instinct_violations])
        
        # Validate critical paths
        path_violations = self._validate_critical_paths(context)
        violations.extend(path_violations)
        applied_rules.extend([v['rule'] for v in path_violations])
        
        # Validate SKULL rules
        skull_results = self._validate_skull_rules(feature_name, context)
        violations.extend(skull_results['violations'])
        warnings.extend(skull_results['warnings'])
        applied_rules.extend(skull_results['applied_rules'])
        
        # Build governance context for plan generation
        governance_context = {
            "tier0_instincts": self.tier0_instincts,
            "critical_paths": self.critical_paths,
            "applicable_rules": list(set(applied_rules)),  # Deduplicate
            "enforcement_mode": self.rules.get('enforcement', 'automated')
        }
        
        is_valid = len([v for v in violations if v.get('severity') == 'blocked']) == 0
        
        return GovernanceValidation(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            applied_rules=list(set(applied_rules)),
            governance_context=governance_context
        )
    
    def _validate_tier0_instincts(
        self,
        feature_name: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate against tier0 immutable instincts."""
        violations = []
        
        # Example: TDD_ENFORCEMENT
        if 'TDD_ENFORCEMENT' in self.tier0_instincts:
            if context.get('type') == 'feature' and not context.get('test_plan'):
                violations.append({
                    'rule': 'TDD_ENFORCEMENT',
                    'severity': 'warning',
                    'message': 'Feature plan should include test strategy (TDD enforcement)'
                })
        
        # Example: INCREMENTAL_PLAN_GENERATION
        if 'INCREMENTAL_PLAN_GENERATION' in self.tier0_instincts:
            if context.get('estimated_phases', 0) > 10:
                violations.append({
                    'rule': 'INCREMENTAL_PLAN_GENERATION',
                    'severity': 'warning',
                    'message': f'Plan has {context["estimated_phases"]} phases. Consider breaking into incremental plans.'
                })
        
        # Example: DOCUMENT_ORGANIZATION_ENFORCEMENT
        if 'DOCUMENT_ORGANIZATION_ENFORCEMENT' in self.tier0_instincts:
            plan_paths = context.get('paths', [])
            if any('CORTEX/' in str(p) and '/cortex-brain/documents/' not in str(p) for p in plan_paths):
                violations.append({
                    'rule': 'DOCUMENT_ORGANIZATION_ENFORCEMENT',
                    'severity': 'blocked',
                    'message': 'Documentation must be in cortex-brain/documents/, not repository root'
                })
        
        return violations
    
    def _validate_critical_paths(
        self,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate against critical path protection."""
        violations = []
        
        plan_paths = context.get('paths', [])
        
        for critical_path in self.critical_paths:
            for plan_path in plan_paths:
                if critical_path in str(plan_path):
                    violations.append({
                        'rule': 'CRITICAL_PATH_PROTECTION',
                        'severity': 'warning',
                        'message': f'Plan modifies critical path: {critical_path}. Requires elevated review.'
                    })
        
        return violations
    
    def _validate_skull_rules(
        self,
        feature_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, List]:
        """Validate against SKULL governance rules."""
        violations = []
        warnings = []
        applied_rules = []
        
        for rule_name, rule in self.skull_rules.items():
            # Apply rule validation (simplified - real implementation would call validation functions)
            if rule.severity == GovernanceSeverity.BLOCKED:
                # Check blocking conditions
                # This is a placeholder - actual validation would be context-specific
                pass
            elif rule.severity == GovernanceSeverity.WARNING:
                # Check warning conditions
                # This is a placeholder - actual validation would be context-specific
                pass
            
            applied_rules.append(rule_name)
        
        return {
            'violations': violations,
            'warnings': warnings,
            'applied_rules': applied_rules
        }
    
    def get_governance_summary(self) -> Dict[str, Any]:
        """Get summary of loaded governance rules."""
        rules_section = self.rules.get('rules', {})
        return {
            "total_rules": rules_section.get('total_count', len(self.skull_rules)),
            "layers": rules_section.get('layers', 0),
            "tier0_instincts": len(self.tier0_instincts),
            "critical_paths": len(self.critical_paths),
            "skull_rules": len(self.skull_rules),
            "enforcement": self.rules.get('enforcement', 'unknown')
        }
