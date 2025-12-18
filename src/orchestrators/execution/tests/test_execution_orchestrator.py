"""
Tests for ExecutionOrchestrator

Tests core orchestrator logic, validation, and execution flow.

Author: Asif Hussain
Date: December 18, 2025
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestrators.execution import (
    ExecutionOrchestrator,
    ExecutionStatus,
    OrchestratorType,
    create_execution_orchestrator
)
from src.orchestrators.base.base_orchestrator import OrchestratorStatus


class TestExecutionOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_create_orchestrator_with_defaults(self):
        """Test creating orchestrator with default configuration."""
        orchestrator = create_execution_orchestrator()
        
        assert orchestrator is not None
        assert isinstance(orchestrator, ExecutionOrchestrator)
        assert orchestrator.current_execution is None
        assert len(orchestrator.orchestrator_registry) == 0
    
    def test_create_orchestrator_with_config(self):
        """Test creating orchestrator with custom configuration."""
        config = {'timeout': 3600, 'max_retries': 3}
        orchestrator = create_execution_orchestrator(config=config)
        
        assert orchestrator is not None
        assert orchestrator.config == config
    
    def test_create_orchestrator_with_container(self):
        """Test creating orchestrator with DI container."""
        mock_container = {'service': 'mock'}
        orchestrator = create_execution_orchestrator(container=mock_container)
        
        assert orchestrator is not None
        assert orchestrator.container == mock_container


class TestOrchestratorRegistration:
    """Test orchestrator registration for phase execution."""
    
    def test_register_single_orchestrator(self):
        """Test registering a single orchestrator."""
        orchestrator = create_execution_orchestrator()
        
        def mock_tdd():
            return {'test': 'passed'}
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, mock_tdd)
        
        assert OrchestratorType.TDD in orchestrator.orchestrator_registry
        assert orchestrator.orchestrator_registry[OrchestratorType.TDD] == mock_tdd
    
    def test_register_multiple_orchestrators(self):
        """Test registering multiple orchestrators."""
        orchestrator = create_execution_orchestrator()
        
        def mock_tdd():
            return {'test': 'passed'}
        
        def mock_qa():
            return {'quality': 'high'}
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, mock_tdd)
        orchestrator.register_orchestrator(OrchestratorType.QA, mock_qa)
        
        assert len(orchestrator.orchestrator_registry) == 2
        assert OrchestratorType.TDD in orchestrator.orchestrator_registry
        assert OrchestratorType.QA in orchestrator.orchestrator_registry


class TestInputValidation:
    """Test DoR validation (validate_input)."""
    
    def test_validation_fails_without_execution_plan(self):
        """Test validation fails when execution plan is missing."""
        orchestrator = create_execution_orchestrator()
        result = orchestrator.validate_input({})
        
        assert not result.valid
        assert len(result.errors) > 0
        assert "Execution plan not provided" in result.errors[0]
    
    def test_validation_fails_with_empty_phases(self):
        """Test validation fails when phases list is empty."""
        orchestrator = create_execution_orchestrator()
        result = orchestrator.validate_input({
            'execution_plan': {'phases': []}
        })
        
        assert not result.valid
        assert "Execution plan has no phases" in result.errors[0]
    
    def test_validation_detects_unknown_dependencies(self):
        """Test validation detects dependencies on non-existent phases."""
        orchestrator = create_execution_orchestrator()
        plan = {
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Phase 1',
                    'orchestrator': 'TDD',
                    'dependencies': ['Unknown Phase']
                }
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert not result.valid
        assert any('depends on unknown phase' in err for err in result.errors)
    
    def test_validation_detects_circular_dependencies(self):
        """Test validation detects circular dependencies."""
        orchestrator = create_execution_orchestrator()
        plan = {
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Phase 1',
                    'orchestrator': 'TDD',
                    'dependencies': ['Phase 2']
                },
                {
                    'phase_number': 2,
                    'phase_name': 'Phase 2',
                    'orchestrator': 'QA',
                    'dependencies': ['Phase 1']
                }
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert not result.valid
        assert "Circular dependencies detected" in result.errors[0]
    
    def test_validation_warns_about_unregistered_orchestrators(self):
        """Test validation warns when orchestrator is not registered."""
        orchestrator = create_execution_orchestrator()
        plan = {
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Phase 1',
                    'orchestrator': 'TDD',
                    'dependencies': []
                }
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert result.valid  # Valid but with warnings
        assert len(result.warnings) > 0
        assert 'not registered' in result.warnings[0]
    
    def test_validation_passes_with_valid_plan(self):
        """Test validation passes with a valid execution plan."""
        orchestrator = create_execution_orchestrator()
        
        # Register orchestrator
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: {})
        
        plan = {
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Phase 1',
                    'orchestrator': 'TDD',
                    'dependencies': []
                }
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert result.valid
        assert len(result.errors) == 0


class TestExecutionFlow:
    """Test execution flow and phase coordination."""
    
    def test_execute_single_phase(self):
        """Test executing a single phase."""
        orchestrator = create_execution_orchestrator()
        
        # Register mock orchestrator
        def mock_tdd():
            return {'tests_passed': True}
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, mock_tdd)
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'TDD Phase',
                    'orchestrator': 'TDD',
                    'dependencies': []
                }
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.data['success'] is True
        assert result.data['completed_phases'] == 1
        assert result.data['failed_phases'] == 0
    
    def test_execute_multiple_phases_in_sequence(self):
        """Test executing multiple phases in sequence."""
        orchestrator = create_execution_orchestrator()
        
        # Register mock orchestrators
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: {'tests': 'passed'})
        orchestrator.register_orchestrator(OrchestratorType.QA, lambda: {'quality': 'high'})
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'TDD Phase',
                    'orchestrator': 'TDD',
                    'dependencies': []
                },
                {
                    'phase_number': 2,
                    'phase_name': 'QA Phase',
                    'orchestrator': 'QA',
                    'dependencies': ['TDD Phase']
                }
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.data['success'] is True
        assert result.data['completed_phases'] == 2
        
        # Verify execution order
        exec_plan = result.data['execution_plan']
        tdd_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'TDD Phase')
        qa_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'QA Phase')
        
        assert tdd_phase['status'] == 'COMPLETED'
        assert qa_phase['status'] == 'COMPLETED'
    
    def test_execute_phases_with_unregistered_orchestrator(self):
        """Test executing phases with unregistered orchestrators (simulation)."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Unknown Phase',
                    'orchestrator': 'TDD',
                    'dependencies': []
                }
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        # Should complete with simulation
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.data['success'] is True
        
        exec_plan = result.data['execution_plan']
        phase = exec_plan['phases'][0]
        assert phase['outputs']['simulated'] is True
    
    def test_execute_handles_orchestrator_failure(self):
        """Test execution handles orchestrator failures gracefully."""
        orchestrator = create_execution_orchestrator()
        
        # Register failing orchestrator
        def failing_orchestrator():
            raise Exception("Orchestrator failed")
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, failing_orchestrator)
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {
                    'phase_number': 1,
                    'phase_name': 'Failing Phase',
                    'orchestrator': 'TDD',
                    'dependencies': []
                }
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.status == OrchestratorStatus.FAILED
        assert result.data['success'] is False
        assert result.data['failed_phases'] == 1
        
        exec_plan = result.data['execution_plan']
        phase = exec_plan['phases'][0]
        assert phase['status'] == 'FAILED'
        assert len(phase['errors']) > 0


class TestDependencyResolution:
    """Test dependency resolution and topological sort."""
    
    def test_resolve_linear_dependencies(self):
        """Test resolving linear dependencies (A → B → C)."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['B']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        # Verify execution order
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order == [1, 2, 3]
    
    def test_resolve_parallel_dependencies(self):
        """Test resolving parallel dependencies (A → B, A → C)."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['A']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        # Verify A comes first, B and C can be in any order
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order[0] == 1
        assert set(execution_order[1:]) == {2, 3}
    
    def test_resolve_diamond_dependencies(self):
        """Test resolving diamond dependencies (A → B, A → C, B → D, C → D)."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['A']},
                {'phase_number': 4, 'phase_name': 'D', 'dependencies': ['B', 'C']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        # Verify correct ordering
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order[0] == 1  # A first
        assert execution_order[-1] == 4  # D last
        assert set(execution_order[1:3]) == {2, 3}  # B, C in middle


class TestErrorHandling:
    """Test error handling and rollback."""
    
    def test_blocked_phase_due_to_failed_dependency(self):
        """Test phase is blocked when dependency fails."""
        orchestrator = create_execution_orchestrator()
        
        # Register orchestrators
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: 1/0)  # Fails
        orchestrator.register_orchestrator(OrchestratorType.QA, lambda: {'quality': 'high'})
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'QA', 'orchestrator': 'QA', 'dependencies': ['TDD']}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        # TDD should fail, QA should not execute
        assert result.data['failed_phases'] == 1
        
        exec_plan = result.data['execution_plan']
        tdd_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'TDD')
        assert tdd_phase['status'] == 'FAILED'
    
    def test_orchestrator_captures_execution_duration(self):
        """Test that execution duration is captured."""
        orchestrator = create_execution_orchestrator()
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: {'test': 'passed'})
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.data['duration_seconds'] > 0
        
        exec_plan = result.data['execution_plan']
        phase = exec_plan['phases'][0]
        assert phase['duration_seconds'] > 0


class TestCompletionSignaling:
    """Test completion signaling for success template triggering."""
    
    def test_is_complete_true_when_all_phases_succeed(self):
        """Test is_complete=True when all phases complete successfully."""
        orchestrator = create_execution_orchestrator()
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: {'test': 'passed'})
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.data['is_complete'] is True
        assert result.data['success'] is True
        assert result.data['failed_phases'] == 0
    
    def test_is_complete_false_when_phases_fail(self):
        """Test is_complete=False when phases fail."""
        orchestrator = create_execution_orchestrator()
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: 1/0)
        
        plan = {
            'feature_name': 'Test Feature',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        assert result.data.get('is_complete', False) is False
        assert result.data['success'] is False
        assert result.data['failed_phases'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
