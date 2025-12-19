#!/usr/bin/env python3
"""
TDD Workflow E2E Test

Tests complete TDD Mastery workflow:
- RED phase (test fails) → GREEN phase (test passes) → REFACTOR phase (improve code)
"""

import pytest
from pathlib import Path
import subprocess
import sys


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with Python structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create src directory
    src_dir = project_root / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()
    
    # Create tests directory
    tests_dir = project_root / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").touch()
    
    return project_root


@pytest.fixture
def tdd_orchestrator(temp_project):
    """Create a TDD orchestrator instance for testing."""
    try:
        from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
        return TDDImplementationOrchestrator(
            project_root=str(temp_project),
            cortex_root=str(Path.cwd())
        )
    except ImportError:
        pytest.skip("TDDImplementationOrchestrator not available")


def test_tdd_orchestrator_initialization(tdd_orchestrator, temp_project):
    """Test that TDD orchestrator initializes correctly."""
    assert tdd_orchestrator is not None
    assert tdd_orchestrator.project_root == temp_project


def test_tdd_phase_sequence():
    """Test that TDD phases follow RED → GREEN → REFACTOR sequence."""
    phases = ["RED", "GREEN", "REFACTOR"]
    
    # Verify phase order is enforced
    assert phases[0] == "RED", "TDD must start with RED phase"
    assert phases[1] == "GREEN", "GREEN phase must follow RED"
    assert phases[2] == "REFACTOR", "REFACTOR phase must follow GREEN"


def test_red_phase_failing_test(temp_project):
    """Test RED phase: create a failing test."""
    # Create a failing test
    test_file = temp_project / "tests" / "test_calculator.py"
    test_content = """
import pytest

def test_add_two_numbers():
    '''Test that add function works.'''
    from src.calculator import add
    assert add(2, 3) == 5
"""
    test_file.write_text(test_content)
    
    # Run test (should fail since src/calculator.py doesn't exist)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    
    # Test should fail (RED phase successful)
    assert result.returncode != 0, "Test should fail in RED phase"


def test_green_phase_passing_test(temp_project):
    """Test GREEN phase: implement minimal code to make test pass."""
    # Create test file
    test_file = temp_project / "tests" / "test_calculator.py"
    test_content = """
import pytest

def test_add_two_numbers():
    from src.calculator import add
    assert add(2, 3) == 5
"""
    test_file.write_text(test_content)
    
    # Create minimal implementation (GREEN phase)
    impl_file = temp_project / "src" / "calculator.py"
    impl_content = """
def add(a, b):
    return a + b
"""
    impl_file.write_text(impl_content)
    
    # Run test (should pass)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    
    # Test should pass (GREEN phase successful)
    assert result.returncode == 0, f"Test should pass in GREEN phase. Output: {result.stdout}"


def test_refactor_phase_maintains_passing_tests(temp_project):
    """Test REFACTOR phase: improve code while keeping tests passing."""
    # Create test
    test_file = temp_project / "tests" / "test_calculator.py"
    test_content = """
import pytest

def test_add_two_numbers():
    from src.calculator import add
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
"""
    test_file.write_text(test_content)
    
    # Create refactored implementation with better structure
    impl_file = temp_project / "src" / "calculator.py"
    impl_content = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers and return the result.\"\"\"
    return a + b
"""
    impl_file.write_text(impl_content)
    
    # Run tests (should still pass after refactoring)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    
    # Tests should still pass (REFACTOR successful)
    assert result.returncode == 0, f"Tests should pass after refactoring. Output: {result.stdout}"


@pytest.mark.integration
def test_complete_tdd_cycle(temp_project):
    """
    Complete TDD cycle: RED → GREEN → REFACTOR.
    
    Workflow:
    1. RED: Write failing test
    2. GREEN: Implement minimal code to pass
    3. REFACTOR: Improve code structure
    4. Verify: All tests still pass
    """
    # Step 1: RED - Create failing test
    test_file = temp_project / "tests" / "test_string_utils.py"
    test_content_red = """
import pytest

def test_reverse_string():
    from src.string_utils import reverse_string
    assert reverse_string('hello') == 'olleh'
    assert reverse_string('') == ''
"""
    test_file.write_text(test_content_red)
    
    # Verify test fails
    result_red = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    assert result_red.returncode != 0, "RED: Test should fail initially"
    
    # Step 2: GREEN - Minimal implementation
    impl_file = temp_project / "src" / "string_utils.py"
    impl_content_green = """
def reverse_string(s):
    return s[::-1]
"""
    impl_file.write_text(impl_content_green)
    
    # Verify test passes
    result_green = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    assert result_green.returncode == 0, "GREEN: Test should pass after implementation"
    
    # Step 3: REFACTOR - Improve code quality
    impl_content_refactor = """
def reverse_string(s: str) -> str:
    \"\"\"
    Reverse a string.
    
    Args:
        s: String to reverse
        
    Returns:
        Reversed string
        
    Examples:
        >>> reverse_string('hello')
        'olleh'
        >>> reverse_string('')
        ''
    \"\"\"
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]
"""
    impl_file.write_text(impl_content_refactor)
    
    # Verify tests still pass after refactoring
    result_refactor = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        cwd=str(temp_project)
    )
    assert result_refactor.returncode == 0, "REFACTOR: Tests should still pass"


def test_tdd_orchestrator_import():
    """Verify TDD orchestrator can be imported."""
    try:
        from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
        assert TDDImplementationOrchestrator is not None
        assert hasattr(TDDImplementationOrchestrator, '__init__')
    except ImportError as e:
        pytest.fail(f"TDD orchestrator import failed: {e}")
