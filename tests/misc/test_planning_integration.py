"""
Integration tests for Planning Orchestrator.

Tests planning workflow, DoR/DoD validation, and cross-component coordination.
"""

import pytest
import os
from pathlib import Path


def test_planning_orchestrator_initialization(temp_project, temp_brain):
    """Test planning orchestrator initialization."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    orchestrator = PlanningOrchestrator(project_root=temp_project)
    
    assert orchestrator is not None
    assert orchestrator.project_root == temp_project
    assert hasattr(orchestrator, "execute")


def test_planning_workflow_basic(temp_project, temp_brain, sample_planning_request):
    """Test basic planning workflow."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    orchestrator = PlanningOrchestrator(project_root=temp_project)
    
    # Create plan
    result = orchestrator.create_plan(
        feature_name=sample_planning_request["feature_name"],
        description=sample_planning_request["description"],
        acceptance_criteria=sample_planning_request["acceptance_criteria"]
    )
    
    # Verify plan structure
    assert result is not None
    assert isinstance(result, dict)
    assert "plan_id" in result or "feature_name" in result


def test_planning_dor_validation(temp_project, temp_brain):
    """Test Definition of Ready validation."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    orchestrator = PlanningOrchestrator(project_root=temp_project)
    
    # Test incomplete plan (should fail DoR)
    incomplete_plan = {
        "feature_name": "Test Feature"
        # Missing description, acceptance_criteria
    }
    
    validation_result = orchestrator.validate_definition_of_ready(incomplete_plan)
    
    assert validation_result is not None
    assert isinstance(validation_result, dict)
    # Should indicate missing requirements


def test_planning_execution_integration(temp_project, temp_brain):
    """Test planning orchestrator integration with execution orchestrator."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    orchestrator = PlanningOrchestrator(project_root=temp_project)
    
    # Create a complete plan
    plan = orchestrator.create_plan(
        feature_name="Integration Test Feature",
        description="Test feature for integration",
        acceptance_criteria=["Criterion 1", "Criterion 2"]
    )
    
    # Verify plan can be passed to execution
    assert plan is not None
    assert "phases" in plan or "tasks" in plan or "feature_name" in plan
