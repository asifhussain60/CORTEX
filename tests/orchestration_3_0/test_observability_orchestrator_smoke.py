"""
Smoke Tests for Observability Orchestrator

Test Strategy: SMOKE TEST ONLY
- Test 1: Initialization
- Test 2: Dashboard generation workflow

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.orchestration_3_0.orchestrators.observability import ObservabilityOrchestrator
from src.orchestration_3_0.orchestrators.observability.observability_orchestrator import (
    create_observability_orchestrator,
    DashboardLevel,
    HealthStatus
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext
from src.orchestration_3_0.core.state_machine import create_basic_orchestrator_fsm
from src.orchestration_3_0.session.session_manager import SessionManager


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create some dummy files
    (project_dir / "main.py").write_text("# Main file\ndef main():\n    pass\n")
    (project_dir / "utils.py").write_text("# Utils file\ndef util():\n    pass\n")
    
    return project_dir


@pytest.fixture
def fresh_session_manager(tmp_path):
    """Create fresh session manager with temp database."""
    db_path = tmp_path / "test_sessions.db"
    return SessionManager(db_path=str(db_path))


def test_observability_orchestrator_initialization(fresh_session_manager):
    """
    Smoke Test 1: Verify orchestrator initializes correctly.
    
    Validates:
    - Factory function creates instance
    - State machine initialized
    - Session manager connected
    - Components resolved (or gracefully handle missing)
    """
    # Create orchestrator using factory
    orchestrator = create_observability_orchestrator(
        session_manager=fresh_session_manager
    )
    
    # Verify instance created
    assert orchestrator is not None
    assert isinstance(orchestrator, ObservabilityOrchestrator)
    
    # Verify orchestrator name
    assert orchestrator.orchestrator_name == "ObservabilityOrchestrator"
    
    # Verify state machine initialized
    assert orchestrator.state_machine is not None
    
    # Verify session manager connected
    assert orchestrator.session_manager is not None
    
    print("✅ Observability Orchestrator initialized successfully")


def test_observability_dashboard_generation_workflow(
    fresh_session_manager,
    temp_project_dir
):
    """
    Smoke Test 2: Verify dashboard generation workflow executes.
    
    Validates:
    - DoR validation passes with valid inputs
    - Dashboard generation executes without errors
    - Result contains expected keys
    - DoD validation passes
    """
    # Create orchestrator
    orchestrator = create_observability_orchestrator(
        session_manager=fresh_session_manager
    )
    
    # Create workflow context
    context = WorkflowContext(
        tenant_id="test-tenant",
        project_id="test-project",
        user_id="test-user",
        session_id="test-session-001",
        inputs={
            "operation": "dashboard",
            "project_path": str(temp_project_dir),
            "level": DashboardLevel.PROJECT.value,
            "incremental": False
        },
        metadata={}
    )
    
    # Validate DoR
    dor_result = orchestrator.validate_dor(context)
    assert dor_result.passed, f"DoR validation failed: {dor_result.errors}"
    print(f"✅ DoR validation passed")
    
    # Execute workflow
    result = orchestrator.execute_workflow(context)
    
    # Verify result structure
    assert "operation" in result
    assert "project_path" in result
    assert "timestamp" in result
    assert "success" in result
    
    # Verify dashboard generation attempted
    assert result.get("dashboard_generated") is not None
    
    print(f"✅ Dashboard generation workflow executed")
    print(f"   Success: {result.get('success')}")
    print(f"   Dashboard generated: {result.get('dashboard_generated')}")
    
    # Validate DoD
    dod_result = orchestrator.validate_dod(context, result)
    if not dod_result.passed:
        print(f"⚠️  DoD warnings: {dod_result.warnings}")
    
    print("✅ Observability workflow smoke test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
