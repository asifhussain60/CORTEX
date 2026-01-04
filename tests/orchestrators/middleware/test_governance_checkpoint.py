"""
Unit and Integration Tests for Governance Checkpoint Middleware

Tests:
1. Checkpoint initialization and rule loading
2. Phase start validation (DoR checks)
3. Phase completion validation (DoD checks)
4. Operation validation (runtime checks)
5. SKULL rule enforcement (TDD, PLANNING_ISOLATION, GIT_ISOLATION, etc.)
6. Audit trail logging
7. GovernanceViolationError for blocked violations
8. Integration with orchestrator lifecycle

Coverage Goal: 100%
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from orchestrators.middleware.governance_checkpoint import (
    GovernanceCheckpoint,
    CheckpointResult,
    GovernanceViolation,
    GovernanceViolationError,
    CheckpointType,
    RuleSeverity,
    quick_checkpoint,
)


# Fixtures


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with governance structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Create cortex-brain directory
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir(parents=True)

        # Create minimal brain-protection-rules.yaml
        rules_content = """
schema_version: "5.0"
categories:
  - orchestration_lifecycle
  - development_workflow

---

- rule_id: SETUP_VERIFICATION
  category: orchestration_lifecycle
  severity: blocked
  name: "Phase -2: Setup Verification Mandatory"
  description: "ALL orchestrators MUST run Phase -2 setup verification"

- rule_id: TDD_ENFORCEMENT
  category: development_workflow
  severity: blocked
  name: "RED→GREEN→REFACTOR Required"
  description: "Code changes require tests FIRST"

- rule_id: PLANNING_ISOLATION
  category: orchestration_lifecycle
  severity: blocked
  name: "Planning vs Implementation Isolation"
  description: "Planning commands create plans ONLY"

- rule_id: GIT_ISOLATION
  category: architecture_integrity
  severity: blocked
  name: "CORTEX/User Repository Isolation"
  description: "CORTEX code cannot be committed to user repos"

- rule_id: HOLISTIC_DISCOVERY
  category: development_workflow
  severity: warning
  name: "Search Before Create"
  description: "Search workspace before creating files"

- rule_id: TEARDOWN_REFACTOR
  category: orchestration_lifecycle
  severity: blocked
  name: "Phase N+1: Teardown + REFACTOR + Commit"
  description: "Phase 999 must run whole-file REFACTOR"
"""
        (brain_dir / "brain-protection-rules.yaml").write_text(rules_content)

        # Create tracking directory
        tracking_dir = workspace / "tracking"
        tracking_dir.mkdir(parents=True)

        yield workspace


@pytest.fixture
def governance_checkpoint(temp_workspace):
    """Create GovernanceCheckpoint instance"""
    return GovernanceCheckpoint(str(temp_workspace))


# Initialization Tests


def test_governance_checkpoint_initialization(temp_workspace):
    """Test: GovernanceCheckpoint initializes with workspace path"""
    checkpoint = GovernanceCheckpoint(str(temp_workspace))

    assert checkpoint.workspace_path == temp_workspace
    assert checkpoint.rules_path.exists()
    assert checkpoint.audit_path.parent.exists()
    assert isinstance(checkpoint.rules, dict)


def test_load_rules_from_yaml(governance_checkpoint):
    """Test: _load_rules loads rules from brain-protection-rules.yaml"""
    rules = governance_checkpoint.rules

    assert len(rules) >= 5  # At least 5 rules loaded
    assert "SETUP_VERIFICATION" in rules
    assert "TDD_ENFORCEMENT" in rules
    assert "PLANNING_ISOLATION" in rules
    assert "GIT_ISOLATION" in rules
    assert "HOLISTIC_DISCOVERY" in rules


def test_load_rules_handles_missing_file():
    """Test: _load_rules handles missing brain-protection-rules.yaml gracefully"""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint = GovernanceCheckpoint(tmpdir)
        assert checkpoint.rules == {}


# Phase Start Validation Tests


def test_checkpoint_phase_start_passes_valid_phase(governance_checkpoint):
    """Test: checkpoint_phase_start passes for valid phase context"""
    result = governance_checkpoint.checkpoint_phase_start(
        phase_number=1, orchestrator="refinement", context={"involves_code_changes": False}
    )

    assert result.status == "PASSED"
    assert not result.blocked
    assert len(result.violations) == 0


def test_checkpoint_phase_start_validates_setup_verification(governance_checkpoint):
    """Test: Phase -2 requires setup_verification_complete"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_start(
            phase_number=-2,
            orchestrator="planning_v5",
            context={"setup_verification_complete": False},
        )


def test_checkpoint_phase_start_validates_tdd_enforcement(governance_checkpoint):
    """Test: Code phases require tests_written"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_start(
            phase_number=1,
            orchestrator="refinement",
            context={"involves_code_changes": True, "tests_written": False},
        )


def test_checkpoint_phase_start_validates_planning_isolation(governance_checkpoint):
    """Test: Planning orchestrators cannot implement immediately"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_start(
            phase_number=1, orchestrator="planning_v5", context={"immediate_implementation": True}
        )


def test_checkpoint_phase_start_logs_to_audit(governance_checkpoint):
    """Test: checkpoint_phase_start logs to audit trail"""
    governance_checkpoint.checkpoint_phase_start(
        phase_number=1, orchestrator="test_orchestrator", context={}
    )

    assert governance_checkpoint.audit_path.exists()
    with open(governance_checkpoint.audit_path, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        last_entry = json.loads(lines[-1])
        assert last_entry["orchestrator"] == "test_orchestrator"
        assert last_entry["phase"] == 1


# Operation Validation Tests


def test_checkpoint_operation_passes_valid_operation(governance_checkpoint):
    """Test: checkpoint_operation passes for valid operation"""
    result = governance_checkpoint.checkpoint_operation(
        operation_name="file_creation",
        orchestrator="refinement",
        context={"file_path": "src/new_file.py", "search_performed": True},
    )

    assert result.status == "PASSED"
    assert not result.blocked


def test_checkpoint_operation_validates_git_isolation(governance_checkpoint):
    """Test: GIT_ISOLATION prevents CORTEX code in user repos"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_operation(
            operation_name="git_commit",
            orchestrator="refinement",
            context={"file_path": "cortex-brain/config.yaml", "target_repo": "user_project"},
        )


def test_checkpoint_operation_warns_holistic_discovery(governance_checkpoint):
    """Test: HOLISTIC_DISCOVERY warns if no search performed"""
    result = governance_checkpoint.checkpoint_operation(
        operation_name="file_creation",
        orchestrator="refinement",
        context={"file_path": "src/new_file.py", "search_performed": False},
    )

    # Should PASS but with warnings
    assert result.status == "PASSED"
    assert not result.blocked
    assert len(result.violations) == 1
    assert result.violations[0].severity == "warning"


def test_checkpoint_operation_logs_to_audit(governance_checkpoint):
    """Test: checkpoint_operation logs to audit trail"""
    governance_checkpoint.checkpoint_operation(
        operation_name="test_operation", orchestrator="test_orch", context={}
    )

    with open(governance_checkpoint.audit_path, "r") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        assert last_entry["operation"] == "test_operation"


# Phase Completion Validation Tests


def test_checkpoint_phase_complete_passes_valid_phase(governance_checkpoint):
    """Test: checkpoint_phase_complete passes for valid artifacts"""
    result = governance_checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="refinement",
        artifacts={"code_written": True, "tests_passing": True},
    )

    assert result.status == "PASSED"
    assert not result.blocked


def test_checkpoint_phase_complete_validates_teardown_refactor(governance_checkpoint):
    """Test: Phase 999 requires refactor_complete"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_complete(
            phase_number=999, orchestrator="refinement", artifacts={"refactor_complete": False}
        )


def test_checkpoint_phase_complete_validates_git_commit(governance_checkpoint):
    """Test: Phase 999 requires git_commit_complete"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_complete(
            phase_number=999,
            orchestrator="refinement",
            artifacts={"refactor_complete": True, "git_commit_complete": False},
        )


def test_checkpoint_phase_complete_validates_tdd_enforcement(governance_checkpoint):
    """Test: Code phases require tests_passing"""
    with pytest.raises(GovernanceViolationError):
        governance_checkpoint.checkpoint_phase_complete(
            phase_number=1,
            orchestrator="refinement",
            artifacts={"code_written": True, "tests_passing": False},
        )


# Audit Trail Tests


def test_get_audit_summary_returns_entries(governance_checkpoint):
    """Test: get_audit_summary returns audit entries"""
    # Create some checkpoints
    governance_checkpoint.checkpoint_phase_start(1, "orch1", {})
    governance_checkpoint.checkpoint_operation("op1", "orch2", {})
    governance_checkpoint.checkpoint_phase_complete(1, "orch1", {})

    summary = governance_checkpoint.get_audit_summary(limit=10)
    assert len(summary) == 3


def test_get_audit_summary_filters_by_orchestrator(governance_checkpoint):
    """Test: get_audit_summary filters by orchestrator name"""
    governance_checkpoint.checkpoint_phase_start(1, "orch_a", {})
    governance_checkpoint.checkpoint_phase_start(1, "orch_b", {})

    summary = governance_checkpoint.get_audit_summary(orchestrator="orch_a")
    assert len(summary) == 1
    assert summary[0]["orchestrator"] == "orch_a"


def test_get_audit_summary_limits_results(governance_checkpoint):
    """Test: get_audit_summary respects limit parameter"""
    for i in range(20):
        governance_checkpoint.checkpoint_phase_start(i, f"orch_{i}", {})

    summary = governance_checkpoint.get_audit_summary(limit=5)
    assert len(summary) == 5


def test_get_audit_summary_returns_empty_if_no_file(temp_workspace):
    """Test: get_audit_summary returns empty list if no audit file"""
    checkpoint = GovernanceCheckpoint(str(temp_workspace))
    # Delete audit file
    if checkpoint.audit_path.exists():
        checkpoint.audit_path.unlink()

    summary = checkpoint.get_audit_summary()
    assert summary == []


# Data Classes Tests


def test_governance_violation_dataclass():
    """Test: GovernanceViolation dataclass has correct fields"""
    violation = GovernanceViolation(
        rule_id="TEST_RULE",
        rule_name="Test Rule",
        severity="blocked",
        description="Test violation",
        recommendation="Fix it",
        context={"key": "value"},
    )

    assert violation.rule_id == "TEST_RULE"
    assert violation.severity == "blocked"
    assert violation.context == {"key": "value"}


def test_checkpoint_result_dataclass():
    """Test: CheckpointResult dataclass has correct fields"""
    result = CheckpointResult(
        timestamp="2026-01-04T12:00:00",
        checkpoint_type="phase_start",
        orchestrator="test",
        phase=1,
        operation=None,
        rules_validated=["RULE1", "RULE2"],
        violations=[],
        status="PASSED",
        blocked=False,
    )

    assert result.checkpoint_type == "phase_start"
    assert result.phase == 1
    assert len(result.rules_validated) == 2
    assert result.status == "PASSED"


def test_checkpoint_type_enum():
    """Test: CheckpointType enum has correct values"""
    assert CheckpointType.PHASE_START.value == "phase_start"
    assert CheckpointType.PHASE_COMPLETE.value == "phase_complete"
    assert CheckpointType.OPERATION.value == "operation"
    assert CheckpointType.PRE_EXECUTION.value == "pre_execution"
    assert CheckpointType.POST_EXECUTION.value == "post_execution"


def test_rule_severity_enum():
    """Test: RuleSeverity enum has correct values"""
    assert RuleSeverity.BLOCKED.value == "blocked"
    assert RuleSeverity.WARNING.value == "warning"
    assert RuleSeverity.INFO.value == "info"


# Convenience Function Tests


def test_quick_checkpoint_phase_start(temp_workspace):
    """Test: quick_checkpoint works for phase_start"""
    result = quick_checkpoint(
        checkpoint_type="phase_start", orchestrator="test", phase=1, context={}
    )

    assert isinstance(result, CheckpointResult)
    assert result.checkpoint_type == "phase_start"


def test_quick_checkpoint_operation(temp_workspace):
    """Test: quick_checkpoint works for operation"""
    result = quick_checkpoint(
        checkpoint_type="operation", orchestrator="test", operation="test_op", context={}
    )

    assert isinstance(result, CheckpointResult)
    assert result.checkpoint_type == "operation"


def test_quick_checkpoint_phase_complete(temp_workspace):
    """Test: quick_checkpoint works for phase_complete"""
    result = quick_checkpoint(
        checkpoint_type="phase_complete", orchestrator="test", phase=1, artifacts={}
    )

    assert isinstance(result, CheckpointResult)
    assert result.checkpoint_type == "phase_complete"


def test_quick_checkpoint_invalid_type():
    """Test: quick_checkpoint raises ValueError for invalid type"""
    with pytest.raises(ValueError):
        quick_checkpoint(checkpoint_type="invalid_type", orchestrator="test")


# Integration Tests


def test_full_orchestrator_lifecycle(governance_checkpoint):
    """Integration Test: Complete orchestrator lifecycle with checkpoints"""
    # Phase start
    result1 = governance_checkpoint.checkpoint_phase_start(
        phase_number=1,
        orchestrator="test_orchestrator",
        context={"involves_code_changes": True, "tests_written": True},
    )
    assert result1.status == "PASSED"

    # Operation during phase
    result2 = governance_checkpoint.checkpoint_operation(
        operation_name="file_creation",
        orchestrator="test_orchestrator",
        context={"file_path": "src/test.py", "search_performed": True},
    )
    assert result2.status == "PASSED"

    # Phase complete
    result3 = governance_checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="test_orchestrator",
        artifacts={"code_written": True, "tests_passing": True},
    )
    assert result3.status == "PASSED"

    # Verify audit trail
    summary = governance_checkpoint.get_audit_summary(orchestrator="test_orchestrator")
    assert len(summary) == 3


def test_blocked_violation_prevents_execution(governance_checkpoint):
    """Integration Test: Blocked violation halts execution"""
    with pytest.raises(GovernanceViolationError) as exc_info:
        governance_checkpoint.checkpoint_phase_start(
            phase_number=-2, orchestrator="test", context={"setup_verification_complete": False}
        )

    assert "setup verification" in str(exc_info.value).lower()


def test_warning_violations_allow_execution(governance_checkpoint):
    """Integration Test: Warning violations don't block execution"""
    result = governance_checkpoint.checkpoint_operation(
        operation_name="file_creation",
        orchestrator="test",
        context={"file_path": "test.py", "search_performed": False},
    )

    # Should pass despite warning
    assert result.status == "PASSED"
    assert not result.blocked
    assert len(result.violations) == 1
    assert result.violations[0].severity == "warning"


def test_multiple_rules_validated_simultaneously(governance_checkpoint):
    """Integration Test: Multiple rules validated in single checkpoint"""
    result = governance_checkpoint.checkpoint_phase_start(
        phase_number=1, orchestrator="planning_v5", context={"involves_code_changes": False}
    )

    # Should validate both TDD_ENFORCEMENT and PLANNING_ISOLATION
    assert len(result.rules_validated) >= 2


# Edge Cases


def test_checkpoint_with_none_context(governance_checkpoint):
    """Test: Checkpoints handle None context gracefully"""
    result = governance_checkpoint.checkpoint_phase_start(
        phase_number=1, orchestrator="test", context=None
    )
    assert result.status == "PASSED"


def test_checkpoint_with_none_artifacts(governance_checkpoint):
    """Test: Checkpoints handle None artifacts gracefully"""
    result = governance_checkpoint.checkpoint_phase_complete(
        phase_number=1, orchestrator="test", artifacts=None
    )
    assert result.status == "PASSED"


def test_audit_trail_survives_multiple_checkpoints(governance_checkpoint):
    """Test: Audit trail persists across multiple checkpoint instances"""
    # First instance creates entries
    governance_checkpoint.checkpoint_phase_start(1, "orch1", {})

    # Second instance reads same audit file
    checkpoint2 = GovernanceCheckpoint(str(governance_checkpoint.workspace_path))
    checkpoint2.checkpoint_phase_start(2, "orch2", {})

    # Both entries should be in audit
    summary = checkpoint2.get_audit_summary()
    assert len(summary) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-k", "not integration"])
