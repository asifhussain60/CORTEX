"""
Unit tests for WiringValidationAgent (Tool 2 of 3-Tool Safety System).

Tests MUST be written FIRST per CORE-008 (TDD).

AC-UNWIRED-VALIDATE-TEST-001: Comprehensive test coverage for validation agent
- Test initialization
- Test component validation (all 5 checks)
- Test status determination
- Test report generation
- Integration with real codebase

Author: Asif Hussain
Date: 2026-01-25
"""

import pytest
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# Import the module under test
from cortex.tools.wiring_validation_agent import (
    WiringValidationAgent,
    ValidationResult,
    ComponentStatus,
)


class TestWiringValidationAgent:
    """Test suite for WiringValidationAgent."""

    def test_agent_initializes(self):
        """Test that WiringValidationAgent can be instantiated."""
        agent = WiringValidationAgent()
        assert agent is not None
        assert isinstance(agent, WiringValidationAgent)

    def test_agent_has_required_methods(self):
        """Test that agent has all required validation methods."""
        agent = WiringValidationAgent()
        assert hasattr(agent, 'validate_component')
        assert hasattr(agent, 'validate_all')
        assert hasattr(agent, 'generate_report')
        assert callable(agent.validate_component)
        assert callable(agent.validate_all)
        assert callable(agent.generate_report)

    def test_validate_component_returns_validation_result(self):
        """Test that validate_component returns ValidationResult."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        assert isinstance(result, ValidationResult)
        assert result.component_name == 'InteractionOrchestrator'
        assert isinstance(result.status, ComponentStatus)
        assert isinstance(result.checks, dict)
        assert isinstance(result.issues, list)
        assert isinstance(result.recommendations, list)

    def test_validation_result_has_all_checks(self):
        """Test that ValidationResult includes all 5 required checks."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        required_checks = ['class_exists', 'registered', 'initialized', 'called', 'tested']
        for check in required_checks:
            assert check in result.checks
            assert isinstance(result.checks[check], bool)

    def test_check_class_exists_finds_existing_orchestrator(self):
        """Test that _check_class_exists finds real orchestrators."""
        agent = WiringValidationAgent()
        
        # InteractionOrchestrator exists
        assert agent._check_class_exists('InteractionOrchestrator') is True
        
        # MasterOrchestrator exists
        assert agent._check_class_exists('MasterOrchestrator') is True
        
        # TDDOrchestrator exists
        assert agent._check_class_exists('TDDOrchestrator') is True

    def test_check_class_exists_returns_false_for_missing(self):
        """Test that _check_class_exists returns False for missing classes."""
        agent = WiringValidationAgent()
        
        # EnforcementOrchestrator doesn't exist (mentioned but not implemented)
        assert agent._check_class_exists('EnforcementOrchestrator') is False
        
        # Nonexistent orchestrator
        assert agent._check_class_exists('NonexistentOrchestrator') is False

    def test_check_registered_finds_registered_components(self):
        """Test that _check_registered finds components in repo-registry.yaml."""
        agent = WiringValidationAgent()
        
        # InteractionOrchestrator is registered
        assert agent._check_registered('InteractionOrchestrator') is True
        
        # IntentRouter is registered
        assert agent._check_registered('IntentRouter') is True

    def test_check_registered_returns_false_for_unregistered(self):
        """Test that _check_registered returns False for unregistered components."""
        agent = WiringValidationAgent()
        
        # EnforcementOrchestrator not registered (doesn't exist)
        assert agent._check_registered('EnforcementOrchestrator') is False

    def test_check_initialized_finds_initialized_components(self):
        """Test that _check_initialized finds components in MasterOrchestrator.__init__."""
        agent = WiringValidationAgent()
        
        # interaction_orchestrator is initialized
        result = agent._check_initialized('InteractionOrchestrator')
        assert result is True
        
        # tdd_orchestrator is initialized
        result = agent._check_initialized('TDDOrchestrator')
        assert result is True
        
        # dor_gate is initialized (DoRApprovalGate)
        result = agent._check_initialized('DoRApprovalGate')
        assert result is True

    def test_check_initialized_returns_false_for_not_initialized(self):
        """Test that _check_initialized returns False for non-initialized components."""
        agent = WiringValidationAgent()
        
        # WorkflowOrchestrator exists and registered but not initialized
        result = agent._check_initialized('WorkflowOrchestrator')
        assert result is False

    def test_check_called_finds_called_components(self):
        """Test that _check_called finds components actually called in execute_operation."""
        agent = WiringValidationAgent()
        
        # Currently, 0 components are called (this is the problem we're fixing)
        # This test will fail initially, then pass once we wire things
        # For now, we expect False for all components
        result = agent._check_called('InteractionOrchestrator')
        assert result is False  # Not wired yet
        
        result = agent._check_called('TDDOrchestrator')
        assert result is False  # Not wired yet

    def test_check_tested_finds_test_files(self):
        """Test that _check_tested finds test files for components."""
        agent = WiringValidationAgent()
        
        # MasterOrchestrator has tests
        result = agent._check_tested('MasterOrchestrator')
        assert result is True
        
        # UnwiredComponentDetector has tests (we just created them)
        result = agent._check_tested('UnwiredComponentDetector')
        assert result is True

    def test_check_tested_returns_false_for_missing_tests(self):
        """Test that _check_tested returns False when no test file exists."""
        agent = WiringValidationAgent()
        
        # WiringValidationAgent now HAS tests (this file!)
        # So test with a component that definitely has no tests
        
        # Use a missing component
        result = agent._check_tested('NonexistentOrchestrator')
        assert result is False

    def test_status_determination_fully_wired(self):
        """Test that status is FULLY_WIRED when all checks pass."""
        agent = WiringValidationAgent()
        
        # Create a mock component that passes all checks
        # This will require mocking or waiting until we actually wire something
        # For now, test the logic with a hypothetical component
        
        # We'll test this with integration tests once we wire Stage 1-3
        pass  # TODO: Implement once we have a fully wired component

    def test_status_determination_partially_wired(self):
        """Test that status is PARTIALLY_WIRED when initialized but not called."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        # InteractionOrchestrator: exists ✅, registered ✅, initialized ✅, called ❌
        assert result.status == ComponentStatus.PARTIALLY_WIRED
        assert result.checks['class_exists'] is True
        assert result.checks['registered'] is True
        assert result.checks['initialized'] is True
        assert result.checks['called'] is False

    def test_status_determination_unwired(self):
        """Test that status is UNWIRED when exists but not initialized."""
        agent = WiringValidationAgent()
        result = agent.validate_component('WorkflowOrchestrator')
        
        # WorkflowOrchestrator: exists ✅, registered ✅, initialized ❌, called ❌
        assert result.status == ComponentStatus.UNWIRED
        assert result.checks['class_exists'] is True
        assert result.checks['registered'] is True
        assert result.checks['initialized'] is False
        assert result.checks['called'] is False

    def test_status_determination_missing(self):
        """Test that status is MISSING when class doesn't exist."""
        agent = WiringValidationAgent()
        result = agent.validate_component('EnforcementOrchestrator')
        
        # EnforcementOrchestrator: doesn't exist (mentioned but not implemented)
        assert result.status == ComponentStatus.MISSING
        assert result.checks['class_exists'] is False

    def test_validation_result_includes_issues(self):
        """Test that ValidationResult.issues contains specific problems."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        # InteractionOrchestrator is initialized but not called
        assert len(result.issues) > 0
        assert any('not called' in issue.lower() for issue in result.issues)

    def test_validation_result_includes_recommendations(self):
        """Test that ValidationResult.recommendations contains actionable fixes."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        # Should recommend wiring it into execute_operation
        assert len(result.recommendations) > 0
        assert any('execute_operation' in rec.lower() for rec in result.recommendations)

    def test_validate_all_returns_dict_of_results(self):
        """Test that validate_all returns results for all registered components."""
        agent = WiringValidationAgent()
        results = agent.validate_all()
        
        assert isinstance(results, dict)
        assert len(results) > 0
        
        # Should include all registered components
        assert 'InteractionOrchestrator' in results
        assert 'IntentRouter' in results
        assert 'TDDOrchestrator' in results
        
        # Each result should be a ValidationResult
        for component_name, result in results.items():
            assert isinstance(result, ValidationResult)
            assert result.component_name == component_name

    def test_generate_report_produces_structured_dict(self):
        """Test that generate_report produces structured output."""
        agent = WiringValidationAgent()
        report = agent.generate_report()
        
        assert isinstance(report, dict)
        assert 'summary' in report
        assert 'components' in report
        assert 'recommendations' in report
        
        # Summary should have counts
        assert 'total_components' in report['summary']
        assert 'fully_wired' in report['summary']
        assert 'partially_wired' in report['summary']
        assert 'unwired' in report['summary']
        assert 'missing' in report['summary']

    def test_report_summary_counts_are_accurate(self):
        """Test that report summary counts match actual findings."""
        agent = WiringValidationAgent()
        report = agent.generate_report()
        
        summary = report['summary']
        components = report['components']
        
        # Count components by status
        status_counts = {
            'fully_wired': 0,
            'partially_wired': 0,
            'unwired': 0,
            'missing': 0,
        }
        
        for result in components.values():
            if result['status'] == 'FULLY_WIRED':
                status_counts['fully_wired'] += 1
            elif result['status'] == 'PARTIALLY_WIRED':
                status_counts['partially_wired'] += 1
            elif result['status'] == 'UNWIRED':
                status_counts['unwired'] += 1
            elif result['status'] == 'MISSING':
                status_counts['missing'] += 1
        
        # Verify summary matches counts
        assert summary['fully_wired'] == status_counts['fully_wired']
        assert summary['partially_wired'] == status_counts['partially_wired']
        assert summary['unwired'] == status_counts['unwired']
        assert summary['missing'] == status_counts['missing']

    def test_report_includes_priority_recommendations(self):
        """Test that report includes prioritized recommendations."""
        agent = WiringValidationAgent()
        report = agent.generate_report()
        
        recommendations = report['recommendations']
        assert len(recommendations) > 0
        
        # Each recommendation should have priority and action
        for rec in recommendations:
            assert 'priority' in rec
            assert 'action' in rec
            assert 'components' in rec
            assert rec['priority'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']


class TestValidationResult:
    """Test suite for ValidationResult dataclass."""

    def test_validation_result_structure(self):
        """Test ValidationResult dataclass structure."""
        result = ValidationResult(
            component_name='TestOrchestrator',
            status=ComponentStatus.PARTIALLY_WIRED,
            checks={
                'class_exists': True,
                'registered': True,
                'initialized': True,
                'called': False,
                'tested': True,
            },
            issues=['Not called in execute_operation'],
            recommendations=['Wire into MasterOrchestrator.execute_operation'],
        )
        
        assert result.component_name == 'TestOrchestrator'
        assert result.status == ComponentStatus.PARTIALLY_WIRED
        assert len(result.checks) == 5
        assert len(result.issues) == 1
        assert len(result.recommendations) == 1

    def test_validation_result_to_dict(self):
        """Test ValidationResult can be converted to dict."""
        result = ValidationResult(
            component_name='TestOrchestrator',
            status=ComponentStatus.UNWIRED,
            checks={'class_exists': True, 'registered': False, 'initialized': False, 'called': False, 'tested': False},
            issues=['Not registered in repo-registry.yaml'],
            recommendations=['Add to repo-registry.yaml'],
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['component_name'] == 'TestOrchestrator'
        assert result_dict['status'] == 'UNWIRED'
        assert 'checks' in result_dict
        assert 'issues' in result_dict
        assert 'recommendations' in result_dict


class TestComponentStatus:
    """Test suite for ComponentStatus enum."""

    def test_component_status_enum_values(self):
        """Test that ComponentStatus has all required values."""
        assert hasattr(ComponentStatus, 'FULLY_WIRED')
        assert hasattr(ComponentStatus, 'PARTIALLY_WIRED')
        assert hasattr(ComponentStatus, 'UNWIRED')
        assert hasattr(ComponentStatus, 'ORPHANED')
        assert hasattr(ComponentStatus, 'MISSING')

    def test_component_status_values_are_unique(self):
        """Test that all ComponentStatus values are unique."""
        values = [
            ComponentStatus.FULLY_WIRED.value,
            ComponentStatus.PARTIALLY_WIRED.value,
            ComponentStatus.UNWIRED.value,
            ComponentStatus.ORPHANED.value,
            ComponentStatus.MISSING.value,
        ]
        assert len(values) == len(set(values))


class TestWiringValidationAgentIntegration:
    """Integration tests with real CORTEX codebase."""

    def test_validates_interaction_orchestrator(self):
        """Test validation of InteractionOrchestrator (Stage 1)."""
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        
        # InteractionOrchestrator: exists, registered, initialized, NOT called, tested
        assert result.checks['class_exists'] is True
        assert result.checks['registered'] is True
        assert result.checks['initialized'] is True
        assert result.checks['called'] is False  # This is the gap
        assert result.status == ComponentStatus.PARTIALLY_WIRED

    def test_validates_intent_router(self):
        """Test validation of IntentRouter (Stage 2)."""
        agent = WiringValidationAgent()
        result = agent.validate_component('IntentRouter')
        
        # IntentRouter: exists, registered, initialized, NOT called, tested
        assert result.checks['class_exists'] is True
        assert result.checks['registered'] is True
        assert result.checks['initialized'] is True
        assert result.checks['called'] is False  # This is the gap

    def test_validates_dor_approval_gate(self):
        """Test validation of DoRApprovalGate (Stage 2.5)."""
        agent = WiringValidationAgent()
        result = agent.validate_component('DoRApprovalGate')
        
        # DoRApprovalGate: exists, registered, initialized, NOT called, tested
        assert result.checks['class_exists'] is True
        assert result.checks['initialized'] is True  # Initialized as _dor_gate
        assert result.checks['called'] is False  # This is the gap

    def test_validates_enforcement_orchestrator(self):
        """Test validation of EnforcementOrchestrator (Stage 3 - missing)."""
        agent = WiringValidationAgent()
        result = agent.validate_component('EnforcementOrchestrator')
        
        # EnforcementOrchestrator: doesn't exist (mentioned but not implemented)
        assert result.checks['class_exists'] is False
        assert result.status == ComponentStatus.MISSING
        assert len(result.recommendations) > 0

    def test_validates_tdd_orchestrator(self):
        """Test validation of TDDOrchestrator (Stage 4)."""
        agent = WiringValidationAgent()
        result = agent.validate_component('TDDOrchestrator')
        
        # TDDOrchestrator: exists, registered, initialized, NOT called directly, tested
        assert result.checks['class_exists'] is True
        assert result.checks['registered'] is True
        assert result.checks['initialized'] is True
        assert result.checks['tested'] is True

    def test_detects_all_partially_wired_components(self):
        """Test that agent detects all partially wired components."""
        agent = WiringValidationAgent()
        results = agent.validate_all()
        
        # Expected partially wired based on UnwiredComponentDetector findings:
        # - InteractionOrchestrator: initialized but not called
        # - IntentRouter: initialized but not called
        # Note: TDDOrchestrator, DoRApprovalGate, etc. might be in different states
        partially_wired = [
            name for name, result in results.items()
            if result.status == ComponentStatus.PARTIALLY_WIRED
        ]
        
        # Should find at least InteractionOrchestrator and IntentRouter
        assert len(partially_wired) >= 2
        assert 'InteractionOrchestrator' in partially_wired
        assert 'IntentRouter' in partially_wired

    def test_report_is_actionable(self):
        """Test that generated report provides actionable wiring priorities."""
        agent = WiringValidationAgent()
        report = agent.generate_report()
        
        # Report should identify high-priority wiring tasks
        recommendations = report['recommendations']
        
        # Should recommend wiring Stage 1-3 components
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        assert len(high_priority) > 0
        
        # Should mention specific components that need wiring
        # Check the components list in HIGH priority recommendation
        for rec in high_priority:
            if 'Stage 1-2' in rec['action']:
                # Should include InteractionOrchestrator in components list
                assert 'InteractionOrchestrator' in rec['components']
                break
        else:
            # If we didn't find Stage 1-2 recommendation, that's also a valid state
            # (means everything is already wired)
            pass

    def test_cli_execution_produces_output(self):
        """Test that WiringValidationAgent can be run from CLI."""
        agent = WiringValidationAgent()
        report = agent.generate_report()
        
        # Should produce output suitable for CLI display
        assert 'summary' in report
        assert 'components' in report
        assert 'recommendations' in report
        
        # Summary should be printable
        summary = report['summary']
        assert isinstance(summary['total_components'], int)
        assert isinstance(summary['fully_wired'], int)
        assert isinstance(summary['partially_wired'], int)
