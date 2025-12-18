"""
Tests for Dependency Resolution

Tests topological sort, circular dependency detection, and execution ordering.

Author: Asif Hussain
Date: December 18, 2025
"""

import pytest

from src.orchestrators.execution import (
    ExecutionOrchestrator,
    OrchestratorType,
    create_execution_orchestrator
)


class TestTopologicalSort:
    """Test topological sorting of phases."""
    
    def test_empty_dependencies(self):
        """Test phases with no dependencies execute in order."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': []},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': []}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        # All phases have no dependencies, so order is preserved
        execution_order = orchestrator.current_execution.execution_order
        assert len(execution_order) == 3
        assert execution_order[0] == 1
    
    def test_simple_chain(self):
        """Test simple dependency chain A → B → C."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['B']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order == [1, 2, 3]
    
    def test_reverse_order_input(self):
        """Test topological sort works regardless of input order."""
        orchestrator = create_execution_orchestrator()
        
        # Phases defined in reverse order
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['B']},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order == [1, 2, 3]
    
    def test_multiple_roots(self):
        """Test graph with multiple roots (no dependencies)."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': []},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['A', 'B']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        execution_order = orchestrator.current_execution.execution_order
        assert execution_order[-1] == 3  # C must be last
        assert set(execution_order[:2]) == {1, 2}  # A and B first (order doesn't matter)
    
    def test_complex_dag(self):
        """Test complex directed acyclic graph."""
        orchestrator = create_execution_orchestrator()
        
        # Graph structure:
        #     A → C → E
        #   /   ↗   ↗
        # B → D → F
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': []},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['A', 'B']},
                {'phase_number': 4, 'phase_name': 'D', 'dependencies': ['B']},
                {'phase_number': 5, 'phase_name': 'E', 'dependencies': ['C', 'D']},
                {'phase_number': 6, 'phase_name': 'F', 'dependencies': ['D']}
            ]
        }
        
        orchestrator.execute({'execution_plan': plan})
        
        execution_order = orchestrator.current_execution.execution_order
        
        # Verify correct ordering constraints
        a_idx = execution_order.index(1)
        b_idx = execution_order.index(2)
        c_idx = execution_order.index(3)
        d_idx = execution_order.index(4)
        e_idx = execution_order.index(5)
        f_idx = execution_order.index(6)
        
        # A, B first
        assert a_idx < c_idx
        assert b_idx < c_idx
        assert b_idx < d_idx
        
        # C, D before E
        assert c_idx < e_idx
        assert d_idx < e_idx
        
        # D before F
        assert d_idx < f_idx


class TestCircularDependencyDetection:
    """Test circular dependency detection."""
    
    def test_simple_cycle_two_nodes(self):
        """Test detecting simple cycle: A → B → A."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': ['B']},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']}
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert not result.valid
        assert "Circular dependencies detected" in result.errors[0]
    
    def test_self_cycle(self):
        """Test detecting self-cycle: A → A."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': ['A']}
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert not result.valid
        assert "Circular dependencies detected" in result.errors[0]
    
    def test_three_node_cycle(self):
        """Test detecting three-node cycle: A → B → C → A."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': ['C']},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['B']}
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert not result.valid
        assert "Circular dependencies detected" in result.errors[0]
    
    def test_no_cycle_in_dag(self):
        """Test no false positives for valid DAG."""
        orchestrator = create_execution_orchestrator()
        
        plan = {
            'phases': [
                {'phase_number': 1, 'phase_name': 'A', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'B', 'dependencies': ['A']},
                {'phase_number': 3, 'phase_name': 'C', 'dependencies': ['A']},
                {'phase_number': 4, 'phase_name': 'D', 'dependencies': ['B', 'C']}
            ]
        }
        
        result = orchestrator.validate_input({'execution_plan': plan})
        
        assert result.valid or "Circular" not in ' '.join(result.errors)


class TestDependencyBlocking:
    """Test dependency blocking behavior."""
    
    def test_phase_blocks_until_dependency_completes(self):
        """Test phase does not execute until dependencies complete."""
        orchestrator = create_execution_orchestrator()
        
        # Mock orchestrators
        orchestrator.register_orchestrator(
            OrchestratorType.TDD,
            lambda: {'tests': 'passed'}
        )
        orchestrator.register_orchestrator(
            OrchestratorType.QA,
            lambda: {'quality': 'high'}
        )
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'QA', 'orchestrator': 'QA', 'dependencies': ['TDD']}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        # Both phases should complete in order
        exec_plan = result.data['execution_plan']
        tdd_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'TDD')
        qa_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'QA')
        
        # TDD must complete before QA starts
        tdd_completed = tdd_phase['completed_at']
        qa_started = qa_phase['started_at']
        
        assert tdd_completed is not None
        assert qa_started is not None
        assert tdd_completed < qa_started
    
    def test_failed_dependency_blocks_dependent(self):
        """Test failed dependency blocks dependent phase."""
        orchestrator = create_execution_orchestrator()
        
        # First orchestrator fails
        orchestrator.register_orchestrator(
            OrchestratorType.TDD,
            lambda: 1/0  # Fails
        )
        orchestrator.register_orchestrator(
            OrchestratorType.QA,
            lambda: {'quality': 'high'}
        )
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'QA', 'orchestrator': 'QA', 'dependencies': ['TDD']}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        # TDD fails, QA should not execute
        assert result.data['failed_phases'] > 0
        
        exec_plan = result.data['execution_plan']
        tdd_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'TDD')
        qa_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'QA')
        
        assert tdd_phase['status'] == 'FAILED'
        # QA should be PENDING (never started) since execution stops on critical failure
        assert qa_phase['status'] in ['PENDING', 'BLOCKED']


class TestMultipleDependencies:
    """Test phases with multiple dependencies."""
    
    def test_all_dependencies_must_complete(self):
        """Test phase requires all dependencies to complete."""
        orchestrator = create_execution_orchestrator()
        
        orchestrator.register_orchestrator(OrchestratorType.TDD, lambda: {'tests': 'passed'})
        orchestrator.register_orchestrator(OrchestratorType.QA, lambda: {'quality': 'high'})
        orchestrator.register_orchestrator(OrchestratorType.DOCUMENTATION, lambda: {'docs': 'ready'})
        orchestrator.register_orchestrator(OrchestratorType.DEVOPS, lambda: {'deployed': True})
        
        plan = {
            'feature_name': 'Test',
            'phases': [
                {'phase_number': 1, 'phase_name': 'TDD', 'orchestrator': 'TDD', 'dependencies': []},
                {'phase_number': 2, 'phase_name': 'QA', 'orchestrator': 'QA', 'dependencies': []},
                {'phase_number': 3, 'phase_name': 'Documentation', 'orchestrator': 'DOCUMENTATION', 'dependencies': []},
                {'phase_number': 4, 'phase_name': 'Deploy', 'orchestrator': 'DEVOPS', 'dependencies': ['TDD', 'QA', 'Documentation']}
            ]
        }
        
        result = orchestrator.execute({'execution_plan': plan})
        
        # Deploy should execute last
        exec_plan = result.data['execution_plan']
        deploy_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'Deploy')
        
        assert deploy_phase['status'] == 'COMPLETED'
        
        # Deploy should start after all dependencies complete
        tdd_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'TDD')
        qa_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'QA')
        doc_phase = next(p for p in exec_plan['phases'] if p['phase_name'] == 'Documentation')
        
        assert tdd_phase['completed_at'] < deploy_phase['started_at']
        assert qa_phase['completed_at'] < deploy_phase['started_at']
        assert doc_phase['completed_at'] < deploy_phase['started_at']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
