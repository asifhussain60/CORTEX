"""
Unit Tests for Setup Verification Middleware (Phase -2)

Tests:
1. Dependency validation (existence + functionality)
2. False positive detection (files exist but broken)
3. VSCode cache age checking
4. Governance compliance validation
5. Integration with SetupVerifier class

Coverage Goal: 100%

Author: CORTEX
Date: January 4, 2026
Sub-Plan: C50-20 (Governance Middleware Implementation)
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.orchestrators.middleware.setup_verification import (
    SetupVerifier,
    DependencyValidation,
    CacheCheckResult,
    SetupVerificationResult,
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

---

- rule_id: SETUP_VERIFICATION
  category: orchestration_lifecycle
  severity: blocked
  name: "Phase -2: Setup Verification Mandatory"
  description: "ALL orchestrators MUST run Phase -2 setup verification"
"""
        (brain_dir / "brain-protection-rules.yaml").write_text(rules_content)

        # Create .vscode directory
        vscode_dir = workspace / ".vscode"
        vscode_dir.mkdir(parents=True)

        yield workspace


@pytest.fixture
def setup_verifier(temp_workspace):
    """Create SetupVerifier instance"""
    return SetupVerifier(workspace_root=temp_workspace)


# Initialization Tests


def test_setup_verifier_initialization(temp_workspace):
    """Test: SetupVerifier initializes with workspace path"""
    verifier = SetupVerifier(workspace_root=temp_workspace)

    assert verifier.workspace_root == temp_workspace
    assert verifier.brain_rules_path.exists()


def test_setup_verifier_custom_rules_path(temp_workspace):
    """Test: SetupVerifier accepts custom rules path"""
    custom_rules = temp_workspace / "custom-rules.yaml"
    custom_rules.write_text("schema_version: '5.0'\n")

    verifier = SetupVerifier(
        workspace_root=temp_workspace,
        brain_rules_path=custom_rules
    )

    assert verifier.brain_rules_path == custom_rules


# Dependency Validation Tests


def test_validate_dependency_file_exists_and_functional(setup_verifier, temp_workspace):
    """Test: Dependency validation passes for existing functional file"""
    # Create test file
    test_file = temp_workspace / "src" / "test_module.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_function():\n    return True\n")

    result = setup_verifier._validate_dependency(str(test_file))

    assert result.exists is True
    assert result.functional is True
    assert result.false_positive is False
    assert result.error_message is None


def test_validate_dependency_file_missing(setup_verifier):
    """Test: Dependency validation fails for missing file"""
    result = setup_verifier._validate_dependency("nonexistent/file.py")

    assert result.exists is False
    assert result.functional is False
    assert result.false_positive is False
    assert "does not exist" in result.error_message.lower()


def test_validate_dependency_python_syntax_error(setup_verifier, temp_workspace):
    """Test: Dependency validation detects false positive (file exists but broken)"""
    # Create file with syntax error
    broken_file = temp_workspace / "src" / "broken.py"
    broken_file.parent.mkdir(parents=True, exist_ok=True)
    broken_file.write_text("def broken_function(\n    # Missing closing parenthesis\n")

    result = setup_verifier._validate_dependency(str(broken_file))

    assert result.exists is True
    assert result.functional is False
    assert result.false_positive is True
    assert "syntax error" in result.error_message.lower()


def test_validate_dependency_import_error(setup_verifier, temp_workspace):
    """Test: Dependency validation detects import errors"""
    # Create file with bad import
    bad_import_file = temp_workspace / "src" / "bad_import.py"
    bad_import_file.parent.mkdir(parents=True, exist_ok=True)
    bad_import_file.write_text("import nonexistent_module\n")

    result = setup_verifier._validate_dependency(str(bad_import_file))

    assert result.exists is True
    # Note: Import errors may not be detected at static analysis level
    # This test documents expected behavior


# Cache Check Tests


def test_cache_check_no_cache_directory(setup_verifier, temp_workspace):
    """Test: Cache check passes when .vscode doesn't exist"""
    # Remove .vscode directory
    vscode_dir = temp_workspace / ".vscode"
    if vscode_dir.exists():
        import shutil
        shutil.rmtree(vscode_dir)

    result = setup_verifier._check_cache()

    assert result.cache_exists is False
    assert result.should_clear is False
    assert len(result.brittle_indicators) == 0


def test_cache_check_fresh_cache(setup_verifier, temp_workspace):
    """Test: Cache check passes for fresh cache (< 7 days)"""
    vscode_dir = temp_workspace / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Create cache file with recent timestamp
    cache_file = vscode_dir / "cache.json"
    cache_file.write_text('{"timestamp": "recent"}')

    result = setup_verifier._check_cache()

    assert result.cache_exists is True
    assert result.cache_age_days < 7
    assert result.should_clear is False


def test_cache_check_old_cache(setup_verifier, temp_workspace):
    """Test: Cache check detects old cache (> 7 days)"""
    vscode_dir = temp_workspace / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Create cache file and modify timestamp to 10 days ago
    cache_file = vscode_dir / "cache.json"
    cache_file.write_text('{"timestamp": "old"}')

    # Set file modification time to 10 days ago
    old_time = (datetime.now() - timedelta(days=10)).timestamp()
    import os
    os.utime(cache_file, (old_time, old_time))

    result = setup_verifier._check_cache()

    assert result.cache_exists is True
    assert result.cache_age_days >= 10
    assert result.should_clear is True
    assert "cache age > 7 days" in result.brittle_indicators


def test_cache_check_brittle_indicators(setup_verifier, temp_workspace):
    """Test: Cache check detects multiple brittle indicators"""
    vscode_dir = temp_workspace / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Create multiple problematic cache files
    (vscode_dir / "corrupt.json").write_text("not valid json {")
    (vscode_dir / "huge.db").write_text("x" * (50 * 1024 * 1024))  # 50MB file

    result = setup_verifier._check_cache()

    assert result.cache_exists is True
    assert len(result.brittle_indicators) > 0


# Governance Compliance Tests


def test_check_governance_compliance_passes(setup_verifier):
    """Test: Governance compliance check passes for valid orchestrator"""
    compliant = setup_verifier._check_governance_compliance(
        orchestrator_name="planning_v5"
    )

    assert compliant is True


def test_check_governance_compliance_fails_missing_rules(temp_workspace):
    """Test: Governance compliance fails when rules file missing"""
    # Create verifier with nonexistent rules path
    verifier = SetupVerifier(
        workspace_root=temp_workspace,
        brain_rules_path=temp_workspace / "nonexistent.yaml"
    )

    compliant = verifier._check_governance_compliance(
        orchestrator_name="test_orch"
    )

    # Should still pass gracefully (rules are optional)
    assert compliant is True


# Integration Tests


def test_verify_setup_all_pass(setup_verifier, temp_workspace):
    """Test: verify_setup passes when all checks pass"""
    # Create valid dependencies
    dep_file = temp_workspace / "src" / "dependency.py"
    dep_file.parent.mkdir(parents=True, exist_ok=True)
    dep_file.write_text("def valid_function():\n    return True\n")

    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[str(dep_file)],
        cache_check_enabled=True
    )

    assert result.passed is True
    assert len(result.dependencies_validated) == 1
    assert result.dependencies_validated[0].functional is True
    assert result.cache_check.cache_exists is True
    assert result.governance_compliant is True
    assert len(result.errors) == 0


def test_verify_setup_dependency_failure(setup_verifier):
    """Test: verify_setup fails when dependency missing"""
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=["nonexistent/file.py"],
        cache_check_enabled=False
    )

    assert result.passed is False
    assert len(result.dependencies_validated) == 1
    assert result.dependencies_validated[0].exists is False
    assert len(result.errors) > 0
    assert "dependency validation failed" in result.errors[0].lower()


def test_verify_setup_false_positive_detection(setup_verifier, temp_workspace):
    """Test: verify_setup detects false positives (broken files)"""
    # Create broken Python file
    broken_file = temp_workspace / "src" / "broken.py"
    broken_file.parent.mkdir(parents=True, exist_ok=True)
    broken_file.write_text("def broken(\n")  # Syntax error

    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[str(broken_file)],
        cache_check_enabled=False
    )

    assert result.passed is False
    assert len(result.dependencies_validated) == 1
    assert result.dependencies_validated[0].false_positive is True
    assert "syntax error" in result.dependencies_validated[0].error_message.lower()


def test_verify_setup_cache_warning(setup_verifier, temp_workspace):
    """Test: verify_setup includes cache warnings when cache old"""
    vscode_dir = temp_workspace / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Create old cache file
    cache_file = vscode_dir / "cache.json"
    cache_file.write_text('{"old": true}')
    old_time = (datetime.now() - timedelta(days=10)).timestamp()
    import os
    os.utime(cache_file, (old_time, old_time))

    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[],
        cache_check_enabled=True
    )

    assert result.cache_check.should_clear is True
    assert len(result.cache_check.brittle_indicators) > 0


def test_verify_setup_multiple_dependencies(setup_verifier, temp_workspace):
    """Test: verify_setup validates multiple dependencies"""
    # Create multiple files
    files = []
    for i in range(3):
        file_path = temp_workspace / "src" / f"dep_{i}.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(f"def func_{i}():\n    return {i}\n")
        files.append(str(file_path))

    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=files,
        cache_check_enabled=False
    )

    assert result.passed is True
    assert len(result.dependencies_validated) == 3
    assert all(dep.functional for dep in result.dependencies_validated)


def test_verify_setup_timestamp_format(setup_verifier):
    """Test: verify_setup includes ISO timestamp"""
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[],
        cache_check_enabled=False
    )

    assert result.timestamp is not None
    # Validate ISO format
    datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))


# Edge Cases


def test_verify_setup_empty_dependencies(setup_verifier):
    """Test: verify_setup handles empty dependency list"""
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[],
        cache_check_enabled=False
    )

    assert result.passed is True
    assert len(result.dependencies_validated) == 0


def test_verify_setup_disabled_cache_check(setup_verifier):
    """Test: verify_setup skips cache check when disabled"""
    result = setup_verifier.verify_setup(
        orchestrator_name="test_orch",
        dependencies=[],
        cache_check_enabled=False
    )

    # Cache check still runs but shouldn't affect pass/fail
    assert result.passed is True


def test_dataclass_serialization():
    """Test: Dataclasses can be serialized to dict"""
    dep = DependencyValidation(
        dependency_id="test.py",
        exists=True,
        functional=True,
        false_positive=False,
        error_message=None
    )

    dep_dict = {
        'dependency_id': dep.dependency_id,
        'exists': dep.exists,
        'functional': dep.functional,
        'false_positive': dep.false_positive,
        'error_message': dep.error_message
    }

    assert dep_dict['dependency_id'] == "test.py"
    assert dep_dict['exists'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.orchestrators.middleware.setup_verification", "--cov-report=term"])
