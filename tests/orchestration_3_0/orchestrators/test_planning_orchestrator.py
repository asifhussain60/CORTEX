"""
Smoke tests for Planning Orchestrator.

Tests:
1. Initialization test
2. Basic workflow test (simple feature planning)

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import (
    PlanningOrchestrator,
    create_planning_orchestrator,
    ComplexityLevel
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext
from src.orchestration_3_0.session.session_manager import SessionManager


@pytest.fixture
def session_manager(tmp_path):
    """Create session manager with temp directory."""
    db_file = tmp_path / "test_sessions.db"
    return SessionManager(db_path=db_file)


@pytest.fixture
def planning_orchestrator(session_manager):
    """Create Planning Orchestrator instance."""
    return create_planning_orchestrator(session_manager=session_manager)


def test_planning_orchestrator_initialization(planning_orchestrator):
    """
    SMOKE TEST 1: Planning Orchestrator Initialization
    
    Validates:
    - Orchestrator initializes without errors
    - Name set correctly
    - State machine initialized
    - Session manager connected
    """
    assert planning_orchestrator is not None
    assert planning_orchestrator.orchestrator_name == "PlanningOrchestrator"
    assert planning_orchestrator.state_machine is not None
    assert planning_orchestrator.session_manager is not None
    assert planning_orchestrator.current_plan is None


def test_planning_orchestrator_basic_workflow(planning_orchestrator):
    """
    SMOKE TEST 2: Planning Orchestrator Basic Workflow
    
    Tests complete planning workflow for a simple feature.
    
    Validates:
    - DoR validation passes with valid inputs
    - Plan generation completes
    - Plan contains phases, dependencies, risks, test strategy
    - DoD validation passes (with auto-approval)
    - Complexity analysis works
    """
    # Prepare context
    context = WorkflowContext(
        tenant_id="test-tenant",
        project_id="test-project",
        user_id="test-user",
        session_id="test-planning-001",
        inputs={
            'feature_name': 'User Dashboard Widget',
            'description': 'Implement a new dashboard widget that displays user activity metrics including recent logins, actions taken, and system usage statistics with real-time updates.',
            'acceptance_criteria': [
                'Widget displays recent login history (last 10 logins)',
                'Widget shows actions taken count in last 24 hours',
                'Widget updates in real-time using WebSocket connection',
                'Widget has responsive design for mobile and desktop'
            ],
            'target_release': 'v2.5',
            'timeline_weeks': 2,
            'auto_approve': True  # Auto-approve for testing
        },
        metadata={}
    )
    
    # Test DoR validation
    dor_result = planning_orchestrator.validate_dor(context)
    assert dor_result.passed is True
    assert len(dor_result.errors) == 0
    
    # Execute workflow
    result = planning_orchestrator.execute(
        tenant_id=context.tenant_id,
        project_id=context.project_id,
        user_id=context.user_id,
        inputs=context.inputs
    )
    
    # Validate result
    assert result.success is True
    assert 'plan' in result.outputs
    
    plan = result.outputs['plan']
    
    # Validate plan structure
    assert plan['feature_name'] == 'User Dashboard Widget'
    assert plan['complexity'] in [c.value for c in ComplexityLevel]
    assert len(plan['phases']) >= 2  # At least 2 phases
    assert 'test_strategy' in plan
    assert plan['test_strategy']['unit_tests'] is True
    assert plan['test_strategy']['coverage_target'] >= 80.0
    assert plan['estimated_total_days'] > 0
    assert plan['approved'] is True
    
    # Validate phases have required fields
    for phase in plan['phases']:
        assert 'phase_number' in phase
        assert 'name' in phase
        assert 'description' in phase
        assert 'estimated_days' in phase
        assert 'deliverables' in phase
    
    # Test DoD validation
    dod_result = planning_orchestrator.validate_dod(context)
    assert dod_result.passed is True
    assert len(dod_result.errors) == 0
    
    # Validate orchestrator state
    assert planning_orchestrator.current_plan is not None
    assert planning_orchestrator.current_plan.feature_name == 'User Dashboard Widget'
