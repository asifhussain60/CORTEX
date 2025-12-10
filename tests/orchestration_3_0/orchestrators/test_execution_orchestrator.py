"""
Smoke tests for Execution Orchestrator.

Tests:
1. Initialization test
2. Basic workflow test (simple execution plan)

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.orchestration_3_0.orchestrators.execution.execution_orchestrator import (
    ExecutionOrchestrator,
    create_execution_orchestrator,
    ExecutionStatus,
    OrchestratorType
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext
from src.orchestration_3_0.session.session_manager import SessionManager


@pytest.fixture
def session_manager(tmp_path):
    """Create session manager with temp directory."""
    db_file = tmp_path / "test_sessions.db"
    return SessionManager(db_path=db_file)


@pytest.fixture
def execution_orchestrator(session_manager):
    """Create Execution Orchestrator instance."""
    return create_execution_orchestrator(session_manager=session_manager)


def test_execution_orchestrator_initialization(execution_orchestrator):
    """
    SMOKE TEST 1: Execution Orchestrator Initialization
    
    Validates:
    - Orchestrator initializes without errors
    - Name set correctly
    - State machine initialized
    - Session manager connected
    - Orchestrator registry empty
    """
    assert execution_orchestrator is not None
    assert execution_orchestrator.orchestrator_name == "ExecutionOrchestrator"
    assert execution_orchestrator.state_machine is not None
    assert execution_orchestrator.session_manager is not None
    assert execution_orchestrator.current_execution is None
    assert len(execution_orchestrator.orchestrator_registry) == 0


def test_execution_orchestrator_basic_workflow(execution_orchestrator):
    """
    SMOKE TEST 2: Execution Orchestrator Basic Workflow
    
    Tests complete execution workflow for a simple 2-phase plan.
    
    Validates:
    - DoR validation passes with valid inputs
    - Dependency resolution works
    - Phases execute in correct order
    - Progress tracking works
    - DoD validation passes
    """
    # Register mock orchestrator
    def mock_tdd_orchestrator():
        return {'tests_created': 5, 'tests_passed': 5, 'coverage': 85.0}
    
    execution_orchestrator.register_orchestrator(
        OrchestratorType.TDD,
        mock_tdd_orchestrator
    )
    
    # Prepare execution plan
    execution_plan = {
        'feature_name': 'User Login Feature',
        'phases': [
            {
                'phase_number': 1,
                'phase_name': 'Foundation',
                'orchestrator': 'TDD',
                'dependencies': []
            },
            {
                'phase_number': 2,
                'phase_name': 'Implementation',
                'orchestrator': 'TDD',
                'dependencies': ['Foundation']
            }
        ]
    }
    
    context = WorkflowContext(
        tenant_id="test-tenant",
        project_id="test-project",
        user_id="test-user",
        session_id="test-execution-001",
        inputs={
            'execution_plan': execution_plan
        },
        metadata={}
    )
    
    # Test DoR validation
    dor_result = execution_orchestrator.validate_dor(context)
    assert dor_result.passed is True
    assert len(dor_result.errors) == 0
    
    # Execute workflow
    result = execution_orchestrator.execute(
        tenant_id=context.tenant_id,
        project_id=context.project_id,
        user_id=context.user_id,
        inputs=context.inputs
    )
    
    # Validate result
    assert result.success is True
    assert 'execution_plan' in result.outputs
    
    exec_plan = result.outputs['execution_plan']
    
    # Validate execution plan structure
    assert exec_plan['feature_name'] == 'User Login Feature'
    assert len(exec_plan['phases']) == 2
    assert exec_plan['success'] is True
    assert exec_plan['started_at'] is not None
    assert exec_plan['completed_at'] is not None
    
    # Validate phases executed
    phases = exec_plan['phases']
    
    # Phase 1 should be completed
    assert phases[0]['phase_name'] == 'Foundation'
    assert phases[0]['status'] == ExecutionStatus.COMPLETED.value
    assert phases[0]['outputs']['tests_created'] == 5
    
    # Phase 2 should be completed (dependency met)
    assert phases[1]['phase_name'] == 'Implementation'
    assert phases[1]['status'] == ExecutionStatus.COMPLETED.value
    
    # Validate execution order (Foundation before Implementation)
    assert exec_plan['execution_order'] == [1, 2]
    
    # Test DoD validation
    dod_result = execution_orchestrator.validate_dod(context)
    assert dod_result.passed is True
    assert len(dod_result.errors) == 0
    
    # Validate orchestrator state
    assert execution_orchestrator.current_execution is not None
    assert execution_orchestrator.current_execution.feature_name == 'User Login Feature'
    assert execution_orchestrator.current_execution.success is True
