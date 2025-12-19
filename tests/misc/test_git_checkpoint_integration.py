"""
Integration tests for Git Checkpoint Orchestrator.

Tests git operations, checkpoint management, and rollback scenarios.
"""

import pytest
import os


def test_git_checkpoint_initialization(temp_project, temp_brain):
    """Test git checkpoint orchestrator initialization."""
    from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
    
    orchestrator = GitCheckpointOrchestrator(project_root=temp_project)
    
    assert orchestrator is not None
    assert orchestrator.project_root == temp_project


def test_git_checkpoint_creation(temp_project, temp_brain):
    """Test checkpoint creation."""
    from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
    
    # Initialize git repo in temp project
    import subprocess
    subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_project, capture_output=True)
    
    orchestrator = GitCheckpointOrchestrator(project_root=temp_project)
    
    # Create test file
    test_file = os.path.join(temp_project, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    # Create checkpoint
    result = orchestrator.create_checkpoint(
        phase="RED",
        message="Test checkpoint"
    )
    
    assert result is not None
    assert isinstance(result, dict)


def test_git_checkpoint_rollback(temp_project, temp_brain):
    """Test checkpoint rollback."""
    from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
    
    # Initialize git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_project, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_project, capture_output=True)
    
    orchestrator = GitCheckpointOrchestrator(project_root=temp_project)
    
    # Verify rollback capability exists
    assert hasattr(orchestrator, "rollback") or hasattr(orchestrator, "restore_checkpoint")
