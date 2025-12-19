"""
Integration tests for TDD Implementation Orchestrator.

Tests TDD workflow coordination, git checkpoint integration, and RED-GREEN-REFACTOR cycle.
"""

import pytest
import os


def test_tdd_orchestrator_initialization(temp_project, temp_brain):
    """Test TDD orchestrator initialization."""
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    orchestrator = TDDImplementationOrchestrator(project_root=temp_project)
    
    assert orchestrator is not None
    assert orchestrator.project_root == temp_project


def test_tdd_red_phase_workflow(temp_project, temp_brain, sample_tdd_session):
    """Test RED phase workflow."""
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    orchestrator = TDDImplementationOrchestrator(project_root=temp_project)
    
    # Start TDD session
    result = orchestrator.start_tdd_session(
        feature=sample_tdd_session["feature"],
        test_file=sample_tdd_session["test_file"]
    )
    
    assert result is not None
    assert isinstance(result, dict)


def test_tdd_git_checkpoint_integration(temp_project, temp_brain):
    """Test TDD integration with git checkpoint orchestrator."""
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    orchestrator = TDDImplementationOrchestrator(project_root=temp_project)
    
    # TDD orchestrator should coordinate with git checkpointing
    # Verify it has checkpoint capabilities
    assert hasattr(orchestrator, "checkpoint") or hasattr(orchestrator, "git_checkpoint")


def test_tdd_validation_integration(temp_project, temp_brain):
    """Test TDD integration with validation framework."""
    from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
    
    orchestrator = TDDImplementationOrchestrator(project_root=temp_project)
    
    # TDD should validate test phases
    # RED phase: tests must fail
    # GREEN phase: tests must pass
    # REFACTOR phase: tests still pass
    
    # Test validation hooks exist
    assert hasattr(orchestrator, "validate_phase") or hasattr(orchestrator, "validate_red_phase")
