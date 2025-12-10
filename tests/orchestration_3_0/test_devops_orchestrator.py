"""
Smoke Tests for DevOps Orchestrator - CORTEX 4.0

Test suite:
1. Initialization test
2. Git checkpoint workflow test

Author: Asif Hussain
Date: December 10, 2025
"""

import pytest
from pathlib import Path
import tempfile
import subprocess

from src.orchestration_3_0.orchestrators.devops import (
    DevOpsOrchestrator,
    create_devops_orchestrator
)
from src.orchestration_3_0.core.state_machine import create_basic_orchestrator_fsm
from src.orchestration_3_0.session.session_manager import get_session_manager


@pytest.fixture
def temp_git_repo():
    """Create temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ['git', 'config', 'user.name', 'Test User'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'user.email', 'test@example.com'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        
        # Create initial commit
        test_file = Path(tmpdir) / 'README.md'
        test_file.write_text('# Test Project')
        subprocess.run(['git', 'add', '.'], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        
        yield tmpdir


def test_devops_orchestrator_initialization():
    """
    Smoke Test 1: Verify DevOps orchestrator initializes correctly.
    
    Validates:
    - Orchestrator instance created
    - All 5 components initialized
    - State machine attached
    - Session manager attached
    """
    # Create orchestrator
    orchestrator = create_devops_orchestrator()
    
    # Verify initialization
    assert orchestrator is not None
    assert orchestrator.orchestrator_name == "DevOpsOrchestrator"
    assert orchestrator.git_ops is not None
    assert orchestrator.checkpoint_mgr is not None
    assert orchestrator.deployment_engine is not None
    assert orchestrator.cleanup_engine is not None
    assert orchestrator.sync_coordinator is not None
    assert orchestrator.state_machine is not None
    assert orchestrator.session_manager is not None
    
    print("✅ DevOps Orchestrator initialization test passed")


def test_git_checkpoint_workflow(temp_git_repo):
    """
    Smoke Test 2: Verify git checkpoint workflow executes.
    
    Validates:
    - DoR validation passes
    - Checkpoint created
    - Commit generated
    - DoD validation passes
    - State transitions correct
    """
    # Create orchestrator
    orchestrator = create_devops_orchestrator()
    
    # Add a file change to commit
    test_file = Path(temp_git_repo) / 'test_change.txt'
    test_file.write_text('Test change for checkpoint')
    
    # Execute checkpoint operation
    result = orchestrator.execute(
        tenant_id="test-tenant",
        project_id="test-project",
        user_id="test-user",
        inputs={
            'operation': 'checkpoint',
            'project_path': temp_git_repo,
            'message': 'Test checkpoint'
        }
    )
    
    # Verify result
    assert result is not None
    assert result.success is True
    assert result.orchestrator_name == "DevOpsOrchestrator"
    assert result.final_state == "COMPLETED"
    assert 'checkpoint_id' in result.outputs
    
    # Verify checkpoint was created
    checkpoint_id = result.outputs['checkpoint_id']
    assert checkpoint_id is not None
    assert len(checkpoint_id) == 8  # UUID short form
    
    # Verify git commit exists
    git_log = subprocess.run(
        ['git', 'log', '--oneline', '-1'],
        cwd=temp_git_repo,
        capture_output=True,
        text=True,
        check=True
    )
    assert f'CHECKPOINT-{checkpoint_id}' in git_log.stdout
    
    print("✅ Git checkpoint workflow test passed")
    print(f"   Checkpoint ID: {checkpoint_id}")
    print(f"   Execution time: {result.execution_time_seconds:.2f}s")


if __name__ == '__main__':
    # Run smoke tests
    print("Running DevOps Orchestrator Smoke Tests...\n")
    
    # Test 1: Initialization
    test_devops_orchestrator_initialization()
    
    # Test 2: Checkpoint workflow (needs git repo)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup git repo manually
        subprocess.run(['git', 'init'], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ['git', 'config', 'user.name', 'Test User'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'user.email', 'test@example.com'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        
        test_file = Path(tmpdir) / 'README.md'
        test_file.write_text('# Test Project')
        subprocess.run(['git', 'add', '.'], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit'],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        
        # Add a file change before checkpoint
        change_file = Path(tmpdir) / 'test_change.txt'
        change_file.write_text('Test change for checkpoint')
        
        test_git_checkpoint_workflow(tmpdir)
    
    print("\n🎉 All DevOps Orchestrator smoke tests passed!")
