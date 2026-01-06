"""
Integration Test: P02 Master Orchestrator Subsystems

Tests integration of 3 key subsystems added in Phase P02:
1. TodoManager - Task tracking with GitHub Copilot integration
2. ResponseRenderer - Template-driven markdown generation
3. SKULL Middleware - Phase -2 and Phase N+1 hooks

Verifies complete orchestrator execution flow with all subsystems active.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import orchestrator components
from src.orchestrators.master import TodoManager
from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.base.base_orchestrator import OrchestratorResult, OrchestratorStatus
from src.orchestrators.middleware import SetupVerifier, TeardownRefactor


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with brain structure."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create cortex-brain structure
    brain = workspace / "cortex-brain"
    brain.mkdir()
    (brain / "brain-protection-rules.yaml").write_text("""
schema_version: '5.0'
rules:
  - rule_id: SETUP_VERIFICATION
    category: orchestration_lifecycle
    severity: blocked
  - rule_id: TEARDOWN_REFACTOR
    category: orchestration_lifecycle
    severity: blocked
""")
    
    # Create tracking directory
    tracking = workspace / "tracking"
    tracking.mkdir()
    
    return workspace


@pytest.fixture
def todo_manager(temp_workspace):
    """Create TodoManager instance."""
    return TodoManager(plan_dir=temp_workspace / "tracking")


@pytest.fixture
def response_renderer(temp_workspace):
    """Create ResponseRenderer instance."""
    # Create response templates file
    templates_path = temp_workspace / "cortex-brain" / "response-templates-v4.yaml"
    templates_path.parent.mkdir(parents=True, exist_ok=True)
    templates_path.write_text("""
tiers:
  INSTANT:
    max_tokens: 50
  FOCUSED:
    max_tokens: 200
  STRUCTURED:
    max_tokens: 600
  COMPREHENSIVE:
    max_tokens: 1000
""")
    
    return ResponseRenderer(template_path=str(templates_path))


def test_todo_manager_task_lifecycle(todo_manager):
    """Test TodoManager CRUD operations."""
    # Create task
    task_id = todo_manager.create_task(
        title="Test Task",
        description="Integration test task",
        priority=1
    )
    
    assert task_id == 1
    
    # Start task
    assert todo_manager.start_task(task_id)
    task = todo_manager.get_task(task_id)
    assert task.status == "in-progress"
    
    # Complete task
    assert todo_manager.complete_task(task_id)
    task = todo_manager.get_task(task_id)
    assert task.status == "completed"
    
    # Verify progress summary
    summary = todo_manager.get_progress_summary()
    assert summary['total_tasks'] == 1
    assert summary['completed'] == 1
    assert summary['progress_percentage'] == 100.0


def test_todo_manager_copilot_format(todo_manager):
    """Test GitHub Copilot format conversion."""
    todo_manager.create_task("Task 1", "First task", status="completed")
    todo_manager.create_task("Task 2", "Second task", status="in-progress")
    
    copilot_tasks = todo_manager.get_copilot_format()
    
    assert len(copilot_tasks) == 2
    assert copilot_tasks[0]['id'] == 1
    assert copilot_tasks[0]['status'] == 'completed'
    assert copilot_tasks[1]['id'] == 2
    assert copilot_tasks[1]['status'] == 'in-progress'


def test_response_renderer_basic(response_renderer):
    """Test ResponseRenderer basic rendering."""
    result = OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message="Operation completed successfully",
        data={'plan_id': 'test-123'},
        errors=[],
        warnings=[],
        execution_time_seconds=2.5
    )
    
    markdown = response_renderer.render(result, tier='FOCUSED')
    
    assert "## 🧠 CORTEX Response" in markdown
    assert "Operation completed successfully" in markdown


def test_response_renderer_with_context(response_renderer):
    """Test ResponseRenderer with continuation context."""
    result = OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message="Plan created successfully",
        data={'plan_id': 'user-auth-v1', 'phases': 5},
        errors=[],
        warnings=[],
        execution_time_seconds=10.0
    )
    
    context = {
        'orchestrator_type': 'planning_v5',
        'plan_id': 'user-auth-v1',
        'multi_phase_operation': True
    }
    
    markdown = response_renderer.render(result, tier='STRUCTURED', context=context)
    
    assert "## 🧠 CORTEX Response" in markdown
    assert "Plan created successfully" in markdown


def test_response_renderer_error_handling(response_renderer):
    """Test ResponseRenderer error state rendering."""
    result = OrchestratorResult(
        status=OrchestratorStatus.FAILED,
        success=False,
        message="Execution failed",
        data={},
        errors=["Error 1: Invalid configuration", "Error 2: Missing dependency"],
        warnings=[],
        execution_time_seconds=0.5
    )
    
    markdown = response_renderer.render(result, tier='FOCUSED')
    
    assert "## 🧠 CORTEX Response" in markdown
    assert "Execution failed" in markdown


def test_setup_verifier_initialization(temp_workspace):
    """Test SetupVerifier initialization."""
    verifier = SetupVerifier(
        workspace_root=temp_workspace,
        brain_rules_path=temp_workspace / "cortex-brain" / "brain-protection-rules.yaml"
    )
    
    assert verifier.workspace_root == temp_workspace
    assert verifier.brain_rules_path.exists()


def test_teardown_refactor_initialization(temp_workspace):
    """Test TeardownRefactor initialization."""
    refactor = TeardownRefactor(workspace_root=temp_workspace)
    
    assert refactor.workspace_root == temp_workspace


def test_integrated_workflow(todo_manager, response_renderer, temp_workspace):
    """
    Test complete integrated workflow:
    1. Create tasks with TodoManager
    2. Execute orchestrator logic (mocked)
    3. Render response with ResponseRenderer
    4. Verify SKULL middleware hooks (mocked)
    """
    # Step 1: Create tasks
    task1_id = todo_manager.create_task("Setup Environment", "Initialize workspace", priority=1)
    task2_id = todo_manager.create_task("Execute Phase 1", "Run main logic", priority=2)
    
    # Step 2: Start first task
    todo_manager.start_task(task1_id)
    
    # Step 3: Complete first task
    todo_manager.complete_task(task1_id)
    
    # Step 4: Start second task
    todo_manager.start_task(task2_id)
    
    # Step 5: Mock orchestrator execution
    execution_result = OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message="Phase 1 completed successfully",
        data={
            'artifacts': ['plan.yaml', 'progress-tracker.json'],
            'plan_id': 'integrated-test-v1'
        },
        errors=[],
        warnings=[],
        execution_time_seconds=5.0
    )
    
    # Step 6: Render response
    context = {
        'orchestrator_type': 'test_orchestrator',
        'multi_phase_operation': True,
        'files_modified': True
    }
    
    markdown = response_renderer.render(execution_result, tier='STRUCTURED', context=context)
    
    # Verify response
    assert "## 🧠 CORTEX Response" in markdown
    assert "Phase 1 completed successfully" in markdown
    
    # Step 7: Complete second task
    todo_manager.complete_task(task2_id)
    
    # Step 8: Verify final state
    summary = todo_manager.get_progress_summary()
    assert summary['total_tasks'] == 2
    assert summary['completed'] == 2
    assert summary['progress_percentage'] == 100.0


def test_middleware_hooks_disabled(temp_workspace):
    """Test middleware behavior when disabled."""
    from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
    from src.database.planning_state_db import PlanningStateDB
    
    # Create config with middleware disabled
    config_path = temp_workspace / "test-config.yaml"
    config_path.write_text("""
schema_version: '5.0'
orchestrator:
  name: test_orchestrator
  version: '1.0'
  type: autonomous
execution:
  middleware_enabled: false
""")
    
    # Create test database
    db_path = temp_workspace / "test.db"
    state_db = PlanningStateDB(str(db_path))
    
    # Create mock orchestrator
    class TestOrchestrator(BaseOrchestratorV4_1):
        def execute(self, user_request: str, **kwargs):
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message="Test completed",
                data={},
                errors=[],
                warnings=[]
            )
    
    # Initialize with middleware disabled
    orchestrator = TestOrchestrator(
        config_path=str(config_path),
        state_db=state_db,
        plan_id=None
    )
    
    assert orchestrator.middleware_enabled is False
    
    # Verify setup verification returns passing result when disabled
    result = orchestrator._run_setup_verification(dependencies=[])
    assert result.passed is True
    assert len(result.dependencies_validated) == 0


def test_end_to_end_orchestrator_flow(todo_manager, response_renderer, temp_workspace):
    """
    Test complete end-to-end flow simulating real orchestrator execution:
    1. Phase -2: Setup verification
    2. Main execution with task tracking
    3. Phase N+1: Teardown refactor
    4. Response rendering
    """
    # Mock SKULL middleware
    with patch('src.orchestrators.middleware.SetupVerifier') as MockSetup, \
         patch('src.orchestrators.middleware.TeardownRefactor') as MockTeardown:
        
        # Configure mocks
        mock_setup_instance = MockSetup.return_value
        mock_setup_result = Mock()
        mock_setup_result.passed = True
        mock_setup_result.dependencies_validated = []
        mock_setup_result.errors = []
        mock_setup_instance.verify_setup.return_value = mock_setup_result
        
        mock_teardown_instance = MockTeardown.return_value
        mock_teardown_result = Mock()
        mock_teardown_result.passed = True
        mock_teardown_result.refactored_files = []
        mock_teardown_result.errors = []
        mock_teardown_instance.run_teardown.return_value = mock_teardown_result
        
        # Simulate Phase -2: Setup
        setup_result = mock_setup_instance.verify_setup(
            orchestrator_name="test_orchestrator",
            dependencies=[],
            cache_check_enabled=True
        )
        assert setup_result.passed
        
        # Simulate main execution with tasks
        task1 = todo_manager.create_task("Phase 1", "Execute phase 1", priority=1)
        todo_manager.start_task(task1)
        
        # Simulate work...
        todo_manager.complete_task(task1)
        
        # Simulate Phase N+1: Teardown
        teardown_result = mock_teardown_instance.run_teardown(
            orchestrator_name="test_orchestrator",
            modified_files=["file1.py", "file2.py"],
            commit_message="test: Orchestrator execution complete"
        )
        assert teardown_result.passed
        
        # Render final response
        execution_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="All phases completed successfully",
            data={'total_tasks': 1},
            errors=[],
            warnings=[],
            execution_time_seconds=10.0
        )
        
        markdown = response_renderer.render(execution_result, tier='FOCUSED')
        
        # Verify complete flow
        assert "## 🧠 CORTEX Response" in markdown
        assert todo_manager.get_progress_summary()['completed'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
