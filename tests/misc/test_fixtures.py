"""
Shared Fixtures for System Refactor Plugin Tests

Provides common test fixtures, mocks, and utilities for all refactor plugin tests.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from plugins.system_refactor_plugin import (
    SystemRefactorPlugin,
    CoverageGap,
    RefactorTask,
    ReviewReport
)


# ============================================
# Plugin Instance Fixtures
# ============================================

@pytest.fixture
def refactor_plugin():
    """Create a fresh SystemRefactorPlugin instance."""
    return SystemRefactorPlugin()


@pytest.fixture
def plugin_with_mocked_paths(tmp_path):
    """Create plugin with mocked file system paths."""
    plugin = SystemRefactorPlugin()
    plugin.project_root = tmp_path
    plugin.tests_path = tmp_path / "tests"
    plugin.src_path = tmp_path / "src"
    plugin.brain_path = tmp_path / "cortex-brain"
    
    # Create directory structure
    plugin.tests_path.mkdir(parents=True, exist_ok=True)
    plugin.src_path.mkdir(parents=True, exist_ok=True)
    plugin.brain_path.mkdir(parents=True, exist_ok=True)
    
    return plugin


# ============================================
# Mock Subprocess Fixtures
# ============================================

@pytest.fixture
def mock_pytest_collect():
    """Mock pytest test collection subprocess result."""
    mock = Mock()
    mock.stdout = "<test1>\n<test2>\n<test3>\n<test4>\n<test5>\n"
    mock.returncode = 0
    return mock


@pytest.fixture
def mock_pytest_execution():
    """Mock pytest test execution subprocess result."""
    mock = Mock()
    mock.stdout = """
test1 PASSED
test2 PASSED
test3 FAILED
test4 PASSED
test5 PASSED
"""
    mock.returncode = 0
    return mock


@pytest.fixture
def mock_pytest_all_passing():
    """Mock pytest execution with all tests passing."""
    mock = Mock()
    mock.stdout = """
test1 PASSED
test2 PASSED
test3 PASSED
test4 PASSED
test5 PASSED
"""
    mock.returncode = 0
    return mock


# ============================================
# Data Model Fixtures
# ============================================

@pytest.fixture
def sample_coverage_gap():
    """Create a sample CoverageGap instance."""
    return CoverageGap(
        category="Plugin Testing",
        description="Missing test harness for authentication plugin",
        priority="HIGH",
        affected_files=["src/plugins/auth_plugin.py"],
        recommended_tests=["tests/plugins/test_auth_plugin.py"],
        estimated_effort_hours=2.0
    )


@pytest.fixture
def sample_refactor_task():
    """Create a sample RefactorTask instance."""
    return RefactorTask(
        task_id="test_auth_1",
        title="REFACTOR test_authentication_flow",
        description="Add edge case assertions for invalid credentials",
        file_path="tests/integration/test_auth.py",
        current_state="GREEN",
        target_state="REFACTOR_COMPLETE",
        priority="MEDIUM",
        estimated_minutes=15,
        status="PENDING"
    )


@pytest.fixture
def sample_review_report_excellent():
    """Create a sample ReviewReport with EXCELLENT health."""
    return ReviewReport(
        timestamp="2025-11-27T10:00:00",
        overall_health="EXCELLENT",
        total_tests=500,
        passing_tests=495,
        coverage_gaps=[],
        refactor_tasks=[],
        recommendations=[],
        metrics={
            "pass_rate": 99.0,
            "categories": {
                "brain_protection": 50,
                "plugins": 25,
                "integration": 100,
                "edge_cases": 75,
                "unit": 200,
                "tier1": 30,
                "tier2": 15,
                "tier3": 5
            }
        }
    )


@pytest.fixture
def sample_review_report_critical():
    """Create a sample ReviewReport with CRITICAL health."""
    return ReviewReport(
        timestamp="2025-11-27T10:00:00",
        overall_health="CRITICAL",
        total_tests=150,
        passing_tests=120,
        coverage_gaps=[],
        refactor_tasks=[],
        recommendations=[],
        metrics={
            "pass_rate": 80.0,
            "categories": {
                "brain_protection": 30,
                "plugins": 10,
                "integration": 40,
                "edge_cases": 20,
                "unit": 30,
                "tier1": 10,
                "tier2": 8,
                "tier3": 2
            }
        }
    )


@pytest.fixture
def sample_review_report_with_gaps(sample_coverage_gap):
    """Create a sample ReviewReport with coverage gaps."""
    return ReviewReport(
        timestamp="2025-11-27T10:00:00",
        overall_health="GOOD",
        total_tests=400,
        passing_tests=385,
        coverage_gaps=[sample_coverage_gap],
        refactor_tasks=[],
        recommendations=[],
        metrics={
            "pass_rate": 96.25,
            "categories": {
                "brain_protection": 45,
                "plugins": 20,
                "integration": 80,
                "edge_cases": 60,
                "unit": 150,
                "tier1": 25,
                "tier2": 15,
                "tier3": 5
            }
        }
    )


@pytest.fixture
def sample_review_report_with_tasks(sample_refactor_task):
    """Create a sample ReviewReport with REFACTOR tasks."""
    return ReviewReport(
        timestamp="2025-11-27T10:00:00",
        overall_health="GOOD",
        total_tests=450,
        passing_tests=440,
        coverage_gaps=[],
        refactor_tasks=[sample_refactor_task],
        recommendations=[],
        metrics={
            "pass_rate": 97.78,
            "categories": {
                "brain_protection": 48,
                "plugins": 22,
                "integration": 90,
                "edge_cases": 70,
                "unit": 180,
                "tier1": 28,
                "tier2": 10,
                "tier3": 2
            }
        }
    )


# ============================================
# Mock Test File Fixtures
# ============================================

@pytest.fixture
def sample_test_file_content():
    """Sample test file content with TODO REFACTOR comments."""
    return """
def test_user_authentication(cortex_entry):
    # Arrange
    user = create_test_user()
    
    # Act
    result = cortex_entry.authenticate(user.email, user.password)
    
    # Assert
    assert result is not None
    assert result.success is True
    
    # TODO (REFACTOR): Add edge case tests
    # - Test invalid email format
    # - Test empty password
    # - Test non-existent user
    # - Test account lockout after 3 failed attempts

def test_password_reset(cortex_entry):
    # Arrange
    user = create_test_user()
    
    # Act
    result = cortex_entry.reset_password(user.email)
    
    # Assert
    assert result.success is True
    
    # TODO (REFACTOR): Add validation tests
    # - Test invalid email
    # - Test expired reset token
"""


@pytest.fixture
def mock_test_file(tmp_path, sample_test_file_content):
    """Create a mock test file with TODO REFACTOR comments."""
    test_file = tmp_path / "test_auth.py"
    test_file.write_text(sample_test_file_content)
    return test_file


# ============================================
# Test Metrics Fixtures
# ============================================

@pytest.fixture
def excellent_metrics():
    """Test metrics indicating EXCELLENT health."""
    return {
        "total": 500,
        "passing": 495,
        "pass_rate": 99.0,
        "categories": {
            "brain_protection": 50,
            "plugins": 25,
            "integration": 100,
            "edge_cases": 75,
            "unit": 200,
            "tier1": 30,
            "tier2": 15,
            "tier3": 5
        }
    }


@pytest.fixture
def good_metrics():
    """Test metrics indicating GOOD health."""
    return {
        "total": 350,
        "passing": 340,
        "pass_rate": 97.14,
        "categories": {
            "brain_protection": 45,
            "plugins": 20,
            "integration": 80,
            "edge_cases": 60,
            "unit": 120,
            "tier1": 15,
            "tier2": 8,
            "tier3": 2
        }
    }


@pytest.fixture
def needs_attention_metrics():
    """Test metrics indicating NEEDS_ATTENTION health."""
    return {
        "total": 250,
        "passing": 230,
        "pass_rate": 92.0,
        "categories": {
            "brain_protection": 30,
            "plugins": 15,
            "integration": 50,
            "edge_cases": 40,
            "unit": 90,
            "tier1": 15,
            "tier2": 8,
            "tier3": 2
        }
    }


@pytest.fixture
def critical_metrics():
    """Test metrics indicating CRITICAL health."""
    return {
        "total": 150,
        "passing": 120,
        "pass_rate": 80.0,
        "categories": {
            "brain_protection": 25,
            "plugins": 10,
            "integration": 30,
            "edge_cases": 20,
            "unit": 50,
            "tier1": 10,
            "tier2": 4,
            "tier3": 1
        }
    }
