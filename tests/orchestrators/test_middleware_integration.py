"""
End-to-End Middleware Integration Tests (C50-20)

Tests complete middleware execution with real orchestrator workflow:
1. SetupVerifier validates dependencies before execution
2. GovernanceCheckpoint validates SKULL rules at runtime
3. TeardownRefactor cleans up and commits after execution

Author: CORTEX
Date: January 4, 2026
Sub-Plan: C50-20 (Governance Middleware Implementation)
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrators.middleware.setup_verification import SetupVerifier
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpoint
from src.orchestrators.middleware.teardown_refactor import TeardownRefactor


# Fixtures


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with git and CORTEX structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Initialize git
        subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace)

        # Create cortex-brain structure
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir(parents=True)

        # Create brain-protection-rules.yaml
        rules = """
schema_version: "5.0"
categories:
  - orchestration_lifecycle
  - development_workflow

---

- rule_id: SETUP_VERIFICATION
  category: orchestration_lifecycle
  severity: blocked
  name: "Phase -2: Setup Verification Mandatory"

- rule_id: TDD_ENFORCEMENT
  category: development_workflow
  severity: blocked
  name: "RED→GREEN→REFACTOR Required"

- rule_id: TEARDOWN_REFACTOR
  category: orchestration_lifecycle
  severity: blocked
  name: "Phase N+1: Teardown + REFACTOR + Commit"
"""
        (brain_dir / "brain-protection-rules.yaml").write_text(rules)

        # Create tracking directory for audit logs
        (workspace / "tracking").mkdir(parents=True)

        # Initial commit
        readme = workspace / "README.md"
        readme.write_text("# Test Project\n")
        subprocess.run(["git", "add", "."], cwd=workspace)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=workspace, capture_output=True)

        yield workspace


@pytest.fixture
def middleware_stack(temp_workspace):
    """Create complete middleware stack"""
    setup_verifier = SetupVerifier(workspace_root=temp_workspace)
    governance_checkpoint = GovernanceCheckpoint(workspace_path=str(temp_workspace))
    teardown_refactor = TeardownRefactor(workspace_root=temp_workspace)

    return {
        'setup_verifier': setup_verifier,
        'governance_checkpoint': governance_checkpoint,
        'teardown_refactor': teardown_refactor,
        'workspace': temp_workspace
    }


# Phase -2: Setup Verification Integration


def test_phase_minus_2_setup_verification(middleware_stack):
    """Test: Phase -2 runs before orchestrator execution"""
    setup_verifier = middleware_stack['setup_verifier']
    workspace = middleware_stack['workspace']

    # Create dependencies
    dep1 = workspace / "src" / "module1.py"
    dep1.parent.mkdir(parents=True, exist_ok=True)
    dep1.write_text("def function1():\n    return True\n")

    dep2 = workspace / "src" / "module2.py"
    dep2.write_text("def function2():\n    return True\n")

    # Run Phase -2
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[str(dep1), str(dep2)],
        cache_check_enabled=True
    )

    assert result.passed is True
    assert len(result.dependencies_validated) == 2
    assert all(dep.functional for dep in result.dependencies_validated)


def test_phase_minus_2_detects_false_positives(middleware_stack):
    """Test: Phase -2 detects broken dependencies (false positives)"""
    setup_verifier = middleware_stack['setup_verifier']
    workspace = middleware_stack['workspace']

    # Create broken dependency
    broken_dep = workspace / "src" / "broken.py"
    broken_dep.parent.mkdir(parents=True, exist_ok=True)
    broken_dep.write_text("def broken(\n")  # Syntax error

    # Run Phase -2
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[str(broken_dep)],
        cache_check_enabled=False
    )

    assert result.passed is False
    assert len(result.dependencies_validated) == 1
    assert result.dependencies_validated[0].false_positive is True


# Runtime: Governance Checkpoint Integration


def test_runtime_governance_phase_start(middleware_stack):
    """Test: Runtime governance validates at phase start"""
    checkpoint = middleware_stack['governance_checkpoint']

    # Validate phase start
    result = checkpoint.checkpoint_phase_start(
        phase_number=1,
        orchestrator="test_orch",
        context={}
    )

    assert result.status == "PASSED"
    assert not result.blocked


def test_runtime_governance_phase_complete(middleware_stack):
    """Test: Runtime governance validates at phase completion"""
    checkpoint = middleware_stack['governance_checkpoint']

    # Validate phase completion
    result = checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="test_orch",
        artifacts={'files_created': 3}
    )

    assert result.status == "PASSED"
    assert not result.blocked


def test_runtime_governance_audit_logging(middleware_stack):
    """Test: Runtime governance writes audit logs"""
    checkpoint = middleware_stack['governance_checkpoint']
    workspace = middleware_stack['workspace']

    # Run checkpoint
    checkpoint.checkpoint_phase_start(
        phase_number=1,
        orchestrator="test_orch",
        context={}
    )

    # Check audit log created
    audit_log = workspace / "tracking" / "governance-audit.jsonl"
    assert audit_log.exists()


# Phase N+1: Teardown + REFACTOR + Commit Integration


def test_phase_n_plus_1_refactor_and_commit(middleware_stack):
    """Test: Phase N+1 refactors files and commits with /cortex-git-commit pattern"""
    refactor = middleware_stack['teardown_refactor']
    workspace = middleware_stack['workspace']

    # Create file with unused imports
    test_file = workspace / "src" / "test.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
import os  # Used
import sys  # Unused

def main():
    print(os.getcwd())
""")

    # Stage file
    subprocess.run(["git", "add", "src/test.py"], cwd=workspace)

    # Run Phase N+1
    result = refactor.execute_teardown(
        orchestrator_name="test_orch",
        modified_files=[test_file],
        phase_summary="Implementation complete",
        skip_git_commit=False
    )

    assert len(result.refactor_results) == 1
    assert result.refactor_results[0].refactor_successful is True
    assert result.git_commit_result.commit_successful is True
    assert "Co-authored-by: CORTEX" in result.git_commit_result.commit_message


# Full Pipeline Integration (Phase -2 → Runtime → Phase N+1)


def test_full_middleware_pipeline(middleware_stack):
    """Test: Complete middleware pipeline execution"""
    setup_verifier = middleware_stack['setup_verifier']
    checkpoint = middleware_stack['governance_checkpoint']
    refactor = middleware_stack['teardown_refactor']
    workspace = middleware_stack['workspace']

    # === PHASE -2: Setup Verification ===
    dep_file = workspace / "src" / "dependency.py"
    dep_file.parent.mkdir(parents=True, exist_ok=True)
    dep_file.write_text("def dep_function():\n    return True\n")

    setup_result = setup_verifier.verify_setup(
        orchestrator_name="full_pipeline_test",
        dependencies=[str(dep_file)],
        cache_check_enabled=False
    )

    assert setup_result.passed is True, "Phase -2 setup verification failed"

    # === RUNTIME: Governance Checkpoints ===
    phase_start_result = checkpoint.checkpoint_phase_start(
        phase_number=1,
        orchestrator="full_pipeline_test",
        context={}
    )

    assert phase_start_result.status == "PASSED", "Runtime phase start validation failed"

    # Simulate orchestrator execution (modify file)
    impl_file = workspace / "src" / "implementation.py"
    impl_file.write_text("""
import json  # Unused
import os

def implement():
    return os.path.exists('.')
""")
    subprocess.run(["git", "add", "src/implementation.py"], cwd=workspace)

    phase_complete_result = checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="full_pipeline_test",
        artifacts={'files_created': 1}
    )

    assert phase_complete_result.status == "PASSED", "Runtime phase complete validation failed"

    # === PHASE N+1: Teardown + REFACTOR + Commit ===
    teardown_result = refactor.execute_teardown(
        orchestrator_name="full_pipeline_test",
        modified_files=[impl_file],
        phase_summary="Full pipeline test complete",
        skip_git_commit=False
    )

    assert len(teardown_result.refactor_results) == 1, "Refactor failed"
    assert teardown_result.refactor_results[0].refactor_successful is True, "Refactor unsuccessful"
    assert teardown_result.git_commit_result.commit_successful is True, "Git commit failed"

    # Verify commit message pattern
    commit_msg = teardown_result.git_commit_result.commit_message
    assert "full_pipeline_test:" in commit_msg, "Orchestrator name missing from commit"
    assert "Co-authored-by: CORTEX" in commit_msg, "/cortex-git-commit pattern missing"


def test_pipeline_with_failures(middleware_stack):
    """Test: Pipeline handles failures gracefully"""
    setup_verifier = middleware_stack['setup_verifier']
    workspace = middleware_stack['workspace']

    # Create broken dependency
    broken_dep = workspace / "src" / "broken.py"
    broken_dep.parent.mkdir(parents=True, exist_ok=True)
    broken_dep.write_text("def broken(\n")  # Syntax error

    # Phase -2 should catch this
    setup_result = setup_verifier.verify_setup(
        orchestrator_name="failure_test",
        dependencies=[str(broken_dep)],
        cache_check_enabled=False
    )

    assert setup_result.passed is False
    assert len(setup_result.errors) > 0
    assert "dependency validation failed" in setup_result.errors[0].lower()


# Audit Trail Validation


def test_audit_trail_completeness(middleware_stack):
    """Test: Audit trail captures all governance checkpoints"""
    checkpoint = middleware_stack['governance_checkpoint']
    workspace = middleware_stack['workspace']

    # Run multiple checkpoints
    checkpoint.checkpoint_phase_start(phase_number=1, orchestrator="audit_test", context={})
    checkpoint.checkpoint_phase_complete(phase_number=1, orchestrator="audit_test", artifacts={})
    checkpoint.checkpoint_phase_start(phase_number=2, orchestrator="audit_test", context={})

    # Check audit log
    audit_log = workspace / "tracking" / "governance-audit.jsonl"
    assert audit_log.exists()

    # Count entries (should have at least 3)
    with open(audit_log, 'r') as f:
        entries = f.readlines()
    assert len(entries) >= 3


# Performance Tests


def test_middleware_performance_acceptable(middleware_stack):
    """Test: Middleware overhead is acceptable (< 1 second for simple case)"""
    import time

    setup_verifier = middleware_stack['setup_verifier']
    checkpoint = middleware_stack['governance_checkpoint']
    refactor = middleware_stack['teardown_refactor']

    start_time = time.time()

    # Run all middleware
    setup_verifier.verify_setup(
        orchestrator_name="perf_test",
        dependencies=[],
        cache_check_enabled=False
    )

    checkpoint.checkpoint_phase_start(
        phase_number=1,
        orchestrator="perf_test",
        context={}
    )

    checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="perf_test",
        artifacts={}
    )

    refactor.execute_teardown(
        orchestrator_name="perf_test",
        modified_files=[],
        phase_summary="Performance test",
        skip_git_commit=True
    )

    elapsed = time.time() - start_time

    # Middleware overhead should be < 1 second for simple case
    assert elapsed < 1.0, f"Middleware too slow: {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
