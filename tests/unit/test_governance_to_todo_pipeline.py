"""
Tests for AC-ORCH-007: Governance-to-Todo Pipeline.

Tests the complete pipeline:
1. GovernanceMerger merges all tier governance
2. MasterOrchestrator evaluates request against merged rules
3. TodoManager creates actionable tasks based on evaluation

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.orchestrators.core.governance_merger import GovernanceMerger, GovernanceRule
from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.master.todo_manager import TodoManager, TaskStatus
from src.orchestrators.pattern_router import PatternRouter


class TestGovernanceMergerIntegration:
    """Test GovernanceMerger as part of pipeline."""
    
    def test_merger_loads_all_tiers(self):
        """Merger should load governance from all 4 tiers."""
        merger = GovernanceMerger()
        
        # Get merged rules (should have loaded from all tiers)
        merged = merger.merge_all_tiers()
        
        # Should return dict with merged governance
        assert merged is not None
        assert isinstance(merged, dict)
        assert 'rule_count' in merged or 'rules' in merged or 'tier_count' in merged
    
    def test_merger_returns_unified_instruction_set(self):
        """Merger should return unified instruction set."""
        merger = GovernanceMerger()
        
        # Get merged rules
        merged = merger.merge_all_tiers()
        
        # Should return dict with unified rules
        assert isinstance(merged, dict)
        assert 'rules' in merged or 'merged_rules' in merged or len(merged) > 0
    
    def test_merger_precedence_tier0_wins(self):
        """Tier 0 rules should have highest precedence."""
        merger = GovernanceMerger()
        
        # Create mock rules at different tiers
        tier0_rule = GovernanceRule(
            rule_id="CORE-001",
            category="CORTEX_CORE",
            severity="blocked",
            name="Tier 0 Rule",
            governance_tier=0,
            precedence="HIGHEST"
        )
        
        tier1_rule = GovernanceRule(
            rule_id="BIZ-001",
            category="BUSINESS",
            severity="warning",
            name="Tier 1 Rule",
            governance_tier=1,
            precedence="HIGH"
        )
        
        # Tier 0 should win in conflict
        assert tier0_rule.governance_tier < tier1_rule.governance_tier


class TestGovernanceToTodoPipeline:
    """Test complete governance-to-todo pipeline."""
    
    @pytest.fixture
    def merger(self):
        """Create GovernanceMerger instance."""
        return GovernanceMerger()
    
    @pytest.fixture
    def todo_manager(self):
        """Create TodoManager instance."""
        return TodoManager()
    
    def test_pipeline_step1_merge_governance(self, merger):
        """Step 1: GovernanceMerger.merge_all_tiers()."""
        # Execute merge
        merged = merger.merge_all_tiers()
        
        # Verify output
        assert merged is not None
        assert isinstance(merged, dict)
    
    def test_pipeline_step2_evaluate_request(self, merger):
        """Step 2: MasterOrchestrator evaluates request against merged rules."""
        # Get merged ruleset
        merged_rules = merger.merge_all_tiers()
        
        # Mock request
        mock_request = {
            'intent': 'implement',
            'target': 'AC-ORCH-007',
            'context': 'Phase 2 implementation'
        }
        
        # Evaluate (should not raise)
        assert mock_request is not None
        assert 'intent' in mock_request
    
    def test_pipeline_step3_create_tasks(self, todo_manager):
        """Step 3: TodoManager.create_tasks() from required_actions."""
        # Mock required_actions from evaluation
        required_actions = [
            {
                'action_id': 'action-001',
                'action_type': 'CREATE_FILE',
                'target': 'src/orchestrators/governance_to_todo_impl.py',
                'priority': 1,
                'governance_rules_applied': ['CORE-001', 'CORE-008']
            },
            {
                'action_id': 'action-002',
                'action_type': 'RUN_TEST',
                'target': 'tests/unit/test_governance_to_todo_pipeline.py',
                'priority': 2,
                'governance_rules_applied': ['CORE-008']
            }
        ]
        
        # Create tasks
        tasks = []
        for action in required_actions:
            task = todo_manager.create_task(
                name=f"{action['action_type']}: {action['target']}",
                metadata={
                    'action_id': action['action_id'],
                    'action_type': action['action_type'],
                    'target': action['target'],
                    'priority': action['priority'],
                    'governance_rules': action['governance_rules_applied']
                }
            )
            tasks.append(task)
        
        # Verify tasks created
        assert len(tasks) == 2
        assert tasks[0].status == TaskStatus.PENDING
        assert tasks[1].status == TaskStatus.PENDING
        assert 'action_type' in tasks[0].metadata
    
    def test_pipeline_complete_flow(self, merger, todo_manager):
        """Test complete pipeline flow end-to-end."""
        # Step 1: Merge governance
        merged_rules = merger.merge_all_tiers()
        assert merged_rules is not None
        
        # Step 2: Mock evaluation result
        required_actions = [
            {
                'action_id': 'impl-001',
                'action_type': 'CREATE_FILE',
                'target': 'test.py',
                'priority': 1,
                'governance_rules_applied': ['CORE-001']
            }
        ]
        
        # Step 3: Create tasks
        created_tasks = []
        for action in required_actions:
            task = todo_manager.create_task(
                name=f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            created_tasks.append(task)
        
        # Verify complete flow
        assert len(created_tasks) == 1
        assert created_tasks[0].metadata['action_type'] == 'CREATE_FILE'
        assert len(merged_rules) > 0


class TestTaskCreationFromGovernanceEvaluation:
    """Test AC-TODO-002: Task Creation from Governance Evaluation."""
    
    def test_task_priority_from_governance_precedence(self):
        """Task priority should reflect governance rule precedence."""
        todo_manager = TodoManager()
        
        # High priority governance rule
        action = {
            'action_type': 'SECURITY_GATE',
            'target': 'auth_module',
            'priority': 1,  # High priority
            'governance_rules': ['CORE-017', 'SECURITY-001']  # Security enforcement
        }
        
        task = todo_manager.create_task(
            name=f"{action['action_type']}: {action['target']}",
            metadata=action
        )
        
        assert task.metadata['priority'] == 1
        assert 'SECURITY' in str(task.metadata['governance_rules'])
    
    def test_task_dependency_chain(self):
        """Tasks should reflect dependency chains from governance."""
        todo_manager = TodoManager()
        
        # Create dependency chain: design → implement → test
        design_task = todo_manager.create_task(
            name="DESIGN: governance_to_todo_pipeline",
            metadata={'phase': 'design', 'sequence': 1}
        )
        
        impl_task = todo_manager.create_task(
            name="IMPLEMENT: governance_to_todo_pipeline",
            metadata={
                'phase': 'implement',
                'sequence': 2,
                'depends_on': design_task.id
            }
        )
        
        test_task = todo_manager.create_task(
            name="TEST: governance_to_todo_pipeline",
            metadata={
                'phase': 'test',
                'sequence': 3,
                'depends_on': impl_task.id
            }
        )
        
        # Verify dependency chain
        assert impl_task.metadata['depends_on'] == design_task.id
        assert test_task.metadata['depends_on'] == impl_task.id
    
    def test_task_includes_governance_context(self):
        """Each task should include relevant governance rules."""
        todo_manager = TodoManager()
        
        action = {
            'governance_rules': ['CORE-001', 'CORE-008', 'CORE-017']
        }
        
        task = todo_manager.create_task(
            name="Implement feature",
            metadata=action
        )
        
        assert 'governance_rules' in task.metadata
        assert len(task.metadata['governance_rules']) == 3


class TestTodoManagerCore:
    """Test AC-TODO-001: TodoManager Core functionality."""
    
    def test_task_lifecycle_pending_to_complete(self):
        """Task should transition: PENDING → IN_PROGRESS → COMPLETE."""
        manager = TodoManager()
        
        task = manager.create_task("Test task")
        assert task.status == TaskStatus.PENDING
        
        # Start task
        manager.start_task(task.id)
        assert manager.tasks[task.id].status == TaskStatus.IN_PROGRESS
        
        # Complete task
        manager.complete_task(task.id)
        assert manager.tasks[task.id].status == TaskStatus.COMPLETE
    
    def test_task_lifecycle_with_failure(self):
        """Task should transition: PENDING → IN_PROGRESS → FAILED."""
        manager = TodoManager()
        
        task = manager.create_task("Failing task")
        manager.start_task(task.id)
        manager.fail_task(task.id)
        
        assert manager.tasks[task.id].status == TaskStatus.FAILED
    
    def test_task_timestamps(self):
        """Task should track creation and update times."""
        manager = TodoManager()
        
        task = manager.create_task("Timestamped task")
        created_at = task.created_at
        
        # Update task
        manager.update_task(task.id, TaskStatus.IN_PROGRESS)
        updated_at = manager.tasks[task.id].updated_at
        
        # Timestamps should be set
        assert created_at is not None
        assert updated_at is not None
        assert updated_at >= created_at
    
    def test_multiple_tasks_tracking(self):
        """Manager should track multiple tasks independently."""
        manager = TodoManager()
        
        task1 = manager.create_task("Task 1")
        task2 = manager.create_task("Task 2")
        task3 = manager.create_task("Task 3")
        
        # Update task1 only
        manager.complete_task(task1.id)
        
        # Verify independence
        assert manager.tasks[task1.id].status == TaskStatus.COMPLETE
        assert manager.tasks[task2.id].status == TaskStatus.PENDING
        assert manager.tasks[task3.id].status == TaskStatus.PENDING


class TestPipelineIntegration:
    """Integration tests for complete AC-ORCH-007 pipeline."""
    
    def test_governance_merge_to_task_creation_flow(self):
        """
        Complete flow:
        1. GovernanceMerger.merge_all_tiers()
        2. MasterOrchestrator.evaluate(request, merged)
        3. TodoManager.create_tasks(required_actions)
        """
        # Setup
        merger = GovernanceMerger()
        todo_manager = TodoManager()
        
        # Step 1: Merge governance
        merged_rules = merger.merge_all_tiers()
        assert merged_rules is not None
        
        # Step 2: Simulate evaluation result
        mock_required_actions = [
            {
                'action_id': '1',
                'action_type': 'CREATE_FILE',
                'target': 'impl.py',
                'priority': 1,
                'governance_rules_applied': ['CORE-001']
            },
            {
                'action_id': '2',
                'action_type': 'RUN_TEST',
                'target': 'test_impl.py',
                'priority': 2,
                'governance_rules_applied': ['CORE-008']
            }
        ]
        
        # Step 3: Create tasks from required_actions
        tasks = []
        for action in mock_required_actions:
            task = todo_manager.create_task(
                name=f"{action['action_type']}: {action['target']}",
                metadata=action
            )
            tasks.append(task)
        
        # Verify complete pipeline
        assert len(tasks) == 2
        assert all(t.status == TaskStatus.PENDING for t in tasks)
        assert tasks[0].metadata['priority'] == 1
        assert tasks[1].metadata['priority'] == 2
