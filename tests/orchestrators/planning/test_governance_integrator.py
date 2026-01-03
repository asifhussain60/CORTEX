"""
Tests for Governance Integrator.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml

from src.orchestrators.planning.governance_integrator import (
    GovernanceIntegrator,
    GovernanceValidation,
    GovernanceRule,
    GovernanceSeverity
)


@pytest.fixture
def mock_governance_rules():
    """Mock governance rules YAML content."""
    return {
        'tier0_instincts': [
            'TDD_ENFORCEMENT',
            'INCREMENTAL_PLAN_GENERATION',
            'DOCUMENT_ORGANIZATION_ENFORCEMENT',
            'GIT_ISOLATION'
        ],
        'critical_paths': [
            'cortex-brain/tier0/',
            '.github/prompts/internal/',
            'cortex-brain/brain-protection-rules.yaml'
        ],
        'rules': {
            'test_rule_1': {
                'severity': 'blocked',
                'description': 'Test blocking rule',
                'validation': 'validate_test_rule_1',
                'critical_path': True
            },
            'test_rule_2': {
                'severity': 'warning',
                'description': 'Test warning rule',
                'validation': 'validate_test_rule_2',
                'critical_path': False
            },
            'total_count': 61,
            'layers': 24
        },
        'enforcement': 'automated'
    }


@pytest.fixture
def governance_integrator(tmp_path, mock_governance_rules):
    """Create GovernanceIntegrator with mock rules."""
    rules_path = tmp_path / "brain-protection-rules.yaml"
    
    with open(rules_path, 'w') as f:
        yaml.dump(mock_governance_rules, f)
    
    return GovernanceIntegrator(rules_path=rules_path)


class TestGovernanceIntegratorInit:
    """Test GovernanceIntegrator initialization."""
    
    def test_init_with_existing_rules(self, governance_integrator):
        """Test initialization with existing rules file."""
        assert governance_integrator.rules is not None
        assert len(governance_integrator.tier0_instincts) == 4
        assert len(governance_integrator.critical_paths) == 3
        assert len(governance_integrator.skull_rules) == 2
    
    def test_init_with_missing_rules(self, tmp_path):
        """Test initialization with missing rules file."""
        missing_path = tmp_path / "nonexistent.yaml"
        integrator = GovernanceIntegrator(rules_path=missing_path)
        
        assert integrator.rules == {}
        assert integrator.tier0_instincts == []
        assert integrator.critical_paths == []
        assert integrator.skull_rules == {}
    
    def test_init_with_default_path(self):
        """Test initialization with default rules path."""
        integrator = GovernanceIntegrator()
        assert integrator.rules_path == Path("cortex-brain/brain-protection-rules.yaml")


class TestGovernanceValidation:
    """Test governance validation methods."""
    
    def test_validate_feature_with_no_violations(self, governance_integrator):
        """Test validation with clean feature request."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Simple Feature",
            context={
                'type': 'feature',
                'test_plan': True,
                'paths': ['src/new_feature/'],
                'estimated_phases': 5
            }
        )
        
        assert validation.is_valid
        assert len(validation.violations) == 0
    
    def test_validate_feature_with_tdd_violation(self, governance_integrator):
        """Test TDD enforcement violation."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Feature Without Tests",
            context={
                'type': 'feature',
                'test_plan': False,
                'paths': [],
                'estimated_phases': 3
            }
        )
        
        # Should have warning (not blocking)
        assert validation.is_valid  # Warnings don't block
        assert any('TDD_ENFORCEMENT' in v['rule'] for v in validation.violations)
    
    def test_validate_feature_with_incremental_plan_warning(self, governance_integrator):
        """Test incremental plan generation warning."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Large Feature",
            context={
                'type': 'feature',
                'paths': [],
                'estimated_phases': 15  # > 10 triggers warning
            }
        )
        
        assert any('INCREMENTAL_PLAN_GENERATION' in v['rule'] for v in validation.violations)
    
    def test_validate_feature_with_document_organization_violation(self, governance_integrator):
        """Test document organization enforcement."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Misplaced Docs",
            context={
                'type': 'documentation',
                'paths': ['CORTEX/my-doc.md'],  # Not in cortex-brain/documents/
                'estimated_phases': 2
            }
        )
        
        # Should be blocked
        assert not validation.is_valid
        assert any('DOCUMENT_ORGANIZATION_ENFORCEMENT' in v['rule'] for v in validation.violations)
        blocking_violations = [v for v in validation.violations if v.get('severity') == 'blocked']
        assert len(blocking_violations) > 0
    
    def test_validate_critical_path_protection(self, governance_integrator):
        """Test critical path protection."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Tier 0 Modification",
            context={
                'type': 'feature',
                'paths': ['cortex-brain/tier0/critical-file.py'],
                'estimated_phases': 3
            }
        )
        
        assert any('CRITICAL_PATH_PROTECTION' in v['rule'] for v in validation.violations)
    
    def test_governance_context_generation(self, governance_integrator):
        """Test governance context is properly generated."""
        validation = governance_integrator.validate_feature_request(
            feature_name="Test Feature",
            context={'type': 'feature', 'paths': []}
        )
        
        assert 'tier0_instincts' in validation.governance_context
        assert 'critical_paths' in validation.governance_context
        assert 'applicable_rules' in validation.governance_context
        assert 'enforcement_mode' in validation.governance_context
        assert validation.governance_context['enforcement_mode'] == 'automated'


class TestTier0InstinctsValidation:
    """Test tier0 instincts validation logic."""
    
    def test_tdd_enforcement_with_test_plan(self, governance_integrator):
        """Test TDD enforcement passes with test plan."""
        violations = governance_integrator._validate_tier0_instincts(
            feature_name="Feature With Tests",
            context={'type': 'feature', 'test_plan': True}
        )
        
        assert not any('TDD_ENFORCEMENT' in v['rule'] for v in violations)
    
    def test_tdd_enforcement_without_test_plan(self, governance_integrator):
        """Test TDD enforcement fails without test plan."""
        violations = governance_integrator._validate_tier0_instincts(
            feature_name="Feature Without Tests",
            context={'type': 'feature', 'test_plan': False}
        )
        
        assert any('TDD_ENFORCEMENT' in v['rule'] for v in violations)
    
    def test_incremental_plan_small(self, governance_integrator):
        """Test incremental plan passes with small phase count."""
        violations = governance_integrator._validate_tier0_instincts(
            feature_name="Small Feature",
            context={'estimated_phases': 5}
        )
        
        assert not any('INCREMENTAL_PLAN_GENERATION' in v['rule'] for v in violations)
    
    def test_incremental_plan_large(self, governance_integrator):
        """Test incremental plan warns with large phase count."""
        violations = governance_integrator._validate_tier0_instincts(
            feature_name="Large Feature",
            context={'estimated_phases': 15}
        )
        
        assert any('INCREMENTAL_PLAN_GENERATION' in v['rule'] for v in violations)


class TestCriticalPathValidation:
    """Test critical path protection."""
    
    def test_no_critical_paths(self, governance_integrator):
        """Test validation with no critical paths."""
        violations = governance_integrator._validate_critical_paths(
            context={'paths': ['src/normal/file.py']}
        )
        
        assert len(violations) == 0
    
    def test_single_critical_path(self, governance_integrator):
        """Test validation with single critical path."""
        violations = governance_integrator._validate_critical_paths(
            context={'paths': ['cortex-brain/tier0/critical.py']}
        )
        
        assert len(violations) == 1
        assert 'CRITICAL_PATH_PROTECTION' in violations[0]['rule']
    
    def test_multiple_critical_paths(self, governance_integrator):
        """Test validation with multiple critical paths."""
        violations = governance_integrator._validate_critical_paths(
            context={
                'paths': [
                    'cortex-brain/tier0/file1.py',
                    '.github/prompts/internal/file2.md'
                ]
            }
        )
        
        assert len(violations) == 2


class TestSKULLRulesValidation:
    """Test SKULL rules validation."""
    
    def test_skull_rules_applied(self, governance_integrator):
        """Test SKULL rules are applied."""
        result = governance_integrator._validate_skull_rules(
            feature_name="Test Feature",
            context={'type': 'feature'}
        )
        
        assert 'violations' in result
        assert 'warnings' in result
        assert 'applied_rules' in result
        assert len(result['applied_rules']) == 2  # 2 rules in mock


class TestGovernanceSummary:
    """Test governance summary generation."""
    
    def test_get_governance_summary(self, governance_integrator):
        """Test governance summary contains expected fields."""
        summary = governance_integrator.get_governance_summary()
        
        assert 'total_rules' in summary
        assert 'layers' in summary
        assert 'tier0_instincts' in summary
        assert 'critical_paths' in summary
        assert 'skull_rules' in summary
        assert 'enforcement' in summary
        
        assert summary['tier0_instincts'] == 4
        assert summary['critical_paths'] == 3
        assert summary['skull_rules'] == 2
        assert summary['enforcement'] == 'automated'


class TestGovernanceSeverity:
    """Test GovernanceSeverity enum."""
    
    def test_severity_values(self):
        """Test severity enum values."""
        assert GovernanceSeverity.BLOCKED.value == "blocked"
        assert GovernanceSeverity.WARNING.value == "warning"
        assert GovernanceSeverity.INFO.value == "info"


class TestGovernanceRule:
    """Test GovernanceRule dataclass."""
    
    def test_governance_rule_creation(self):
        """Test GovernanceRule creation."""
        rule = GovernanceRule(
            name="test_rule",
            severity=GovernanceSeverity.BLOCKED,
            description="Test rule",
            validation_fn="validate_test",
            critical_path=True
        )
        
        assert rule.name == "test_rule"
        assert rule.severity == GovernanceSeverity.BLOCKED
        assert rule.critical_path is True


class TestGovernanceValidationDataclass:
    """Test GovernanceValidation dataclass."""
    
    def test_governance_validation_creation(self):
        """Test GovernanceValidation creation."""
        validation = GovernanceValidation(
            is_valid=True,
            violations=[],
            warnings=[],
            applied_rules=['rule1', 'rule2'],
            governance_context={'key': 'value'}
        )
        
        assert validation.is_valid is True
        assert len(validation.violations) == 0
        assert len(validation.applied_rules) == 2
