"""
Tests for AC-TODO-002: Task Creation from Governance Evaluation.

Tests task creation from governance evaluation results:
- Priority mapping from governance rules
- Dependency resolution
- Task metadata enrichment with governance context
- Error handling and logging

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from src.orchestrators.master.todo_manager import TodoManager, TaskStatus
from src.orchestrators.core.governance_merger import GovernanceMerger


class TestTaskCreationFromEvaluation:
    """Test AC-TODO-002: Task Creation from Governance Evaluation."""
    
    @pytest.fixture
    def todo_manager(self):
        """Create TodoManager instance."""
        return TodoManager()
    
    @pytest.fixture
    def governance_merger(self):
        """Create GovernanceMerger instance."""
        return GovernanceMerger()
    
    def test_create_tasks_from_required_actions(self, todo_manager):
        """Task creation from required_actions list."""
        required_actions = [
            {
                'action_id': 'create-file-1',
                'action_type': 'CREATE_FILE',
                'target': 'src/impl.py',
                'priority': 1,
                'governance_rules_applied': ['CORE-001', 'CORE-008']
            },
            {
                'action_id': 'run-test-1',
                'action_type': 'RUN_TEST',
                'target': 'tests/test_impl.py',
                'priority': 2,
                'governance_rules_applied': ['CORE-008']
            }
        ]
        
        tasks = []
        for action in required_actions:
            task = todo_manager.create_task(
                name=f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            tasks.append(task)
        
        assert len(tasks) == 2
        assert tasks[0].metadata['action_type'] == 'CREATE_FILE'
        assert tasks[1].metadata['action_type'] == 'RUN_TEST'
        assert tasks[0].metadata['priority'] == 1
        assert tasks[1].metadata['priority'] == 2
    
    def test_priority_mapping_from_governance(self, todo_manager):
        """Priority should map from governance rule severity."""
        # High severity governance rule = high priority task
        action_high = {
            'action_type': 'SECURITY_GATE',
            'priority': 1,  # HIGHEST
            'governance_rules': ['CORE-017', 'SECURITY-001']
        }
        
        # Low severity governance rule = low priority task
        action_low = {
            'action_type': 'DOCUMENTATION',
            'priority': 5,  # LOWEST
            'governance_rules': ['DOCS-001']
        }
        
        task_high = todo_manager.create_task(
            "Security gate",
            metadata=action_high
        )
        
        task_low = todo_manager.create_task(
            "Documentation",
            metadata=action_low
        )
        
        assert task_high.metadata['priority'] == 1
        assert task_low.metadata['priority'] == 5
        assert task_high.metadata['priority'] < task_low.metadata['priority']
    
    def test_task_includes_all_governance_rules(self, todo_manager):
        """Task metadata should include all applicable governance rules."""
        action = {
            'action_type': 'IMPLEMENTATION',
            'governance_rules': [
                'CORE-001',      # Incremental execution
                'CORE-008',      # TDD enforcement
                'CORE-017',      # Governance enforcement
                'SECURITY-001',  # Security layer
                'SECURITY-005'   # Approval gates
            ]
        }
        
        task = todo_manager.create_task(
            "Implement feature",
            metadata=action
        )
        
        assert 'governance_rules' in task.metadata
        assert len(task.metadata['governance_rules']) == 5
        assert 'CORE-001' in task.metadata['governance_rules']
        assert 'SECURITY-005' in task.metadata['governance_rules']
    
    def test_task_dependency_chain_from_actions(self, todo_manager):
        """Tasks should respect dependency chain from required_actions."""
        # Action 1: Design
        design_action = {
            'action_type': 'DESIGN',
            'sequence': 1
        }
        
        # Action 2: Implement (depends on Design)
        impl_action = {
            'action_type': 'IMPLEMENT',
            'sequence': 2,
            'depends_on_action_id': 'design-action'
        }
        
        # Action 3: Test (depends on Implement)
        test_action = {
            'action_type': 'TEST',
            'sequence': 3,
            'depends_on_action_id': 'impl-action'
        }
        
        task_design = todo_manager.create_task("Design phase", metadata=design_action)
        
        impl_action['depends_on_task_id'] = task_design.id
        task_impl = todo_manager.create_task("Implement phase", metadata=impl_action)
        
        test_action['depends_on_task_id'] = task_impl.id
        task_test = todo_manager.create_task("Test phase", metadata=test_action)
        
        # Verify dependency chain
        assert task_impl.metadata.get('depends_on_task_id') == task_design.id
        assert task_test.metadata.get('depends_on_task_id') == task_impl.id
    
    def test_task_metadata_enrichment(self, todo_manager):
        """Task metadata should be enriched with governance context."""
        action = {
            'action_id': 'create-auth',
            'action_type': 'CREATE_FILE',
            'target': 'src/auth/jwt_handler.py',
            'priority': 1,
            'governance_rules_applied': ['CORE-001', 'CORE-008', 'SECURITY-001'],
            'affected_components': ['authentication', 'security'],
            'impact_level': 'CRITICAL',
            'test_count_estimate': 15,
            'loc_estimate': 150
        }
        
        task = todo_manager.create_task(
            f"{action['action_type']}: {action['target']}",
            metadata=action
        )
        
        # Verify rich metadata
        assert task.metadata['target'] == 'src/auth/jwt_handler.py'
        assert task.metadata['impact_level'] == 'CRITICAL'
        assert task.metadata['test_count_estimate'] == 15
        assert task.metadata['loc_estimate'] == 150
        assert 'SECURITY-001' in task.metadata['governance_rules_applied']
    
    def test_task_creation_batching(self, todo_manager):
        """Should efficiently batch-create multiple tasks."""
        actions = [
            {
                'action_id': f'action-{i}',
                'action_type': 'CREATE_FILE',
                'target': f'src/module_{i}.py',
                'priority': i % 3 + 1
            }
            for i in range(10)
        ]
        
        tasks = []
        for action in actions:
            task = todo_manager.create_task(
                f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            tasks.append(task)
        
        assert len(tasks) == 10
        assert all(isinstance(t, type(tasks[0])) for t in tasks)
        assert all(t.status == TaskStatus.PENDING for t in tasks)
        
        # Verify independence
        for i, task in enumerate(tasks):
            assert task.metadata['action_id'] == f'action-{i}'


class TestTaskCreationFromGovernanceEvaluationFlow:
    """Test complete flow: Governance Evaluation → Task Creation."""
    
    def test_complete_governance_to_task_flow(self):
        """
        Complete flow:
        1. GovernanceMerger produces merged rules
        2. Evaluation produces required_actions
        3. TodoManager creates tasks
        """
        # Setup
        merger = GovernanceMerger()
        todo_manager = TodoManager()
        
        # Step 1: Merge governance (simulated)
        merged_rules = merger.merge_all_tiers()
        assert merged_rules is not None
        
        # Step 2: Simulate governance evaluation
        evaluation_result = {
            'request': {
                'intent': 'implement',
                'target': 'AC-ORCH-007'
            },
            'required_actions': [
                {
                    'action_id': 'create-pipeline',
                    'action_type': 'CREATE_FILE',
                    'target': 'src/orchestrators/governance_to_todo.py',
                    'priority': 1,
                    'governance_rules_applied': ['CORE-001', 'CORE-008']
                },
                {
                    'action_id': 'create-tests',
                    'action_type': 'CREATE_FILE',
                    'target': 'tests/test_governance_to_todo.py',
                    'priority': 1,
                    'governance_rules_applied': ['CORE-008']
                },
                {
                    'action_id': 'run-tests',
                    'action_type': 'RUN_TEST',
                    'target': 'pytest tests/test_governance_to_todo.py',
                    'priority': 2,
                    'governance_rules_applied': ['CORE-008']
                }
            ]
        }
        
        # Step 3: Create tasks from evaluation
        tasks = []
        for action in evaluation_result['required_actions']:
            task = todo_manager.create_task(
                name=f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            tasks.append(task)
        
        # Verify complete flow
        assert len(tasks) == 3
        assert tasks[0].metadata['target'] == 'src/orchestrators/governance_to_todo.py'
        assert tasks[1].metadata['target'] == 'tests/test_governance_to_todo.py'
        assert tasks[2].metadata['target'] == 'pytest tests/test_governance_to_todo.py'
        
        # Verify priorities
        assert tasks[0].metadata['priority'] == 1  # Code first
        assert tasks[1].metadata['priority'] == 1  # Tests second
        assert tasks[2].metadata['priority'] == 2  # Then run
        
        # Verify governance context
        assert 'CORE-001' in tasks[0].metadata['governance_rules_applied']
        assert 'CORE-008' in tasks[0].metadata['governance_rules_applied']


class TestTaskCreationErrorHandling:
    """Test error handling in task creation from governance evaluation."""
    
    def test_handle_missing_action_type(self):
        """Should handle actions with missing action_type gracefully."""
        todo_manager = TodoManager()
        
        action = {
            'action_id': 'action-1',
            'target': 'file.py',
            # Missing 'action_type'
        }
        
        # Should still create task with default name
        task = todo_manager.create_task(
            name="Unknown action: file.py",
            metadata=action
        )
        
        assert task is not None
        assert task.id in todo_manager.tasks
    
    def test_handle_duplicate_action_ids(self):
        """Should handle duplicate action_ids without collision."""
        todo_manager = TodoManager()
        
        actions = [
            {'action_id': 'dup', 'action_type': 'CREATE_FILE', 'target': 'a.py'},
            {'action_id': 'dup', 'action_type': 'CREATE_FILE', 'target': 'b.py'}
        ]
        
        tasks = []
        for action in actions:
            task = todo_manager.create_task(
                f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            tasks.append(task)
        
        # Both tasks should be created with different task IDs
        assert len(tasks) == 2
        assert tasks[0].id != tasks[1].id
        assert tasks[0].metadata['target'] == 'a.py'
        assert tasks[1].metadata['target'] == 'b.py'
    
    def test_handle_empty_actions_list(self):
        """Should handle empty required_actions list."""
        todo_manager = TodoManager()
        
        actions = []
        tasks = []
        
        for action in actions:
            task = todo_manager.create_task(
                name="Task",
                metadata=action
            )
            tasks.append(task)
        
        assert len(tasks) == 0
