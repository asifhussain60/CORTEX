"""
Pytest Configuration for System Refactor Plugin Tests

Provides shared fixtures and configuration for all refactor plugin tests.
Centralizes common setup, mocks, and utilities.

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
# Mock Subprocess Results
# ============================================

@pytest.fixture
def mock_pytest_collect_success():
    """Mock successful pytest --collect-only output."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = """
test_tier1.py::test_working_memory PASSED
test_tier2.py::test_pattern_storage PASSED
test_tier3.py::test_code_metrics PASSED
test_plugins.py::test_plugin_system PASSED
collected 450 items
"""
    return mock_result


@pytest.fixture
def mock_pytest_run_success():
    """Mock successful pytest -v output."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = """
test_tier1.py::test_working_memory PASSED
test_tier2.py::test_pattern_storage PASSED
test_tier3.py::test_code_metrics PASSED
test_plugins.py::test_plugin_system PASSED
============== 450 passed in 12.34s ==============
"""
    return mock_result


@pytest.fixture
def mock_pytest_with_failures():
    """Mock pytest output with failures."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = """
test_tier1.py::test_working_memory PASSED
test_tier2.py::test_pattern_storage FAILED
test_tier3.py::test_code_metrics PASSED
============== 2 passed, 1 failed in 5.67s ==============
"""
    return mock_result


# ============================================
# Sample Test Files
# ============================================

@pytest.fixture
def sample_test_file_with_refactor_todos(tmp_path):
    """Create sample test file with TODO REFACTOR comments."""
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("""
def test_example():
    '''Test example functionality.'''
    # TODO REFACTOR: Extract database query to separate method
    result = db.query("SELECT * FROM users")
    assert result is not None

def test_another():
    '''Another test.'''
    # TODO REFACTOR: Replace mock with fixture for better reusability
    mock_data = {"id": 1, "name": "test"}
    assert process(mock_data)
""")
    return test_file


@pytest.fixture
def sample_test_file_without_todos(tmp_path):
    """Create sample test file without TODO comments."""
    test_file = tmp_path / "test_clean.py"
    test_file.write_text("""
def test_clean_example():
    '''Clean test without TODOs.'''
    result = calculate(5, 3)
    assert result == 8
""")
    return test_file


# ============================================
# Plugin Structure Fixtures
# ============================================

@pytest.fixture
def mock_plugin_files(tmp_path):
    """Create mock plugin file structure."""
    plugins_dir = tmp_path / "src" / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample plugin files
    (plugins_dir / "sample_plugin.py").write_text("""
class SamplePlugin:
    pass
""")
    (plugins_dir / "another_plugin.py").write_text("""
class AnotherPlugin:
    pass
""")
    
    return plugins_dir


@pytest.fixture
def mock_test_categories(tmp_path):
    """Create mock test category directories."""
    tests_dir = tmp_path / "tests"
    categories = [
        "tier0", "tier1", "tier2", "tier3",
        "plugins", "integration", "edge_cases",
        "unit", "entry_point"
    ]
    
    for category in categories:
        category_dir = tests_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Add sample test file
        (category_dir / f"test_{category}_sample.py").write_text(f"""
def test_{category}_example():
    assert True
""")
    
    return tests_dir


# ============================================
# Report Data Fixtures
# ============================================

@pytest.fixture
def sample_coverage_gap():
    """Create sample CoverageGap object."""
    return CoverageGap(
        category="plugin_coverage",
        description="Plugin XYZ has no test coverage",
        priority="HIGH",
        affected_files=["src/plugins/xyz_plugin.py"],
        recommended_tests=["tests/plugins/test_xyz_plugin.py"],
        estimated_effort_hours=2.0
    )


@pytest.fixture
def sample_refactor_task():
    """Create sample RefactorTask object."""
    return RefactorTask(
        task_id="RT001",
        title="Extract database query",
        description="Move database query logic to separate method",
        file_path="tests/test_sample.py",
        current_state="Query embedded in test",
        target_state="Query in dedicated method",
        priority="MEDIUM",
        estimated_minutes=30,
        status="pending"
    )


@pytest.fixture
def sample_review_report():
    """Create sample ReviewReport object."""
    from datetime import datetime
    
    return ReviewReport(
        timestamp=datetime.now().isoformat(),
        overall_health="GOOD",
        total_tests=450,
        passing_tests=445,
        coverage_gaps=[],
        refactor_tasks=[],
        recommendations=[
            "Add performance test coverage",
            "Document test categories",
            "Review test execution time"
        ],
        metrics={
            "pass_rate": 98.9,
            "test_count": 450,
            "failed_tests": 5,
            "execution_time": 12.34
        }
    )


# ============================================
# Mock Agent Request/Response
# ============================================

@pytest.fixture
def mock_agent_request():
    """Create mock AgentRequest object."""
    request = Mock()
    request.intent = "self_review"
    request.command = "/refactor"
    request.args = []
    request.kwargs = {}
    request.user_message = "Review the system"
    return request


@pytest.fixture
def mock_agent_context():
    """Create mock agent execution context."""
    context = Mock()
    context.project_root = Path("/mock/project")
    context.brain_path = Path("/mock/project/cortex-brain")
    context.current_file = None
    return context


# ============================================
# Performance Fixtures
# ============================================

@pytest.fixture
def performance_test_dir(tmp_path):
    """Create performance test directory structure."""
    perf_dir = tmp_path / "tests" / "performance"
    perf_dir.mkdir(parents=True, exist_ok=True)
    
    (perf_dir / "test_performance_sample.py").write_text("""
def test_performance_example():
    '''Performance test example.'''
    import time
    start = time.time()
    # Simulate work
    time.sleep(0.1)
    assert time.time() - start < 1.0
""")
    
    return perf_dir


# ============================================
# Pytest Configuration
# ============================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
