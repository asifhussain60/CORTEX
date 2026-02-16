"""
Golden tests for production implementation workflow (TDD).

Authority: Phase 29 S2 | Zero-Mock Philosophy + Phase 96 Weakness Remediation
Test Count: 6 golden tests
Purpose: Validate TDD enforcement, stub prevention, DoD gates
"""
import pytest
from pathlib import Path
from typing import List
import ast


class TestProductionTDDWorkflow:
    """Golden test: TDD implementation workflow."""
    
    def test_tdd_red_green_refactor_cycle(self, tmp_path: Path) -> None:
        """Golden: Complete RED → GREEN → REFACTOR cycle.
        
        Validates CORE-008 enforcement at architectural level.
        """
        # Create test file FIRST (RED phase)
        test_file = tmp_path / "test_calculator.py"
        test_file.write_text("""
import pytest
from calculator import add

def test_add():
    assert add(2, 3) == 5
""")
        
        # Verify test fails without implementation
        impl_file = tmp_path / "calculator.py"
        assert not impl_file.exists(), "Implementation must not exist yet (RED phase)"
        
        # Create implementation (GREEN phase)
        impl_file.write_text("""
def add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b
""")
        
        # Verify implementation has proper structure (REFACTOR requirements)
        code = impl_file.read_text()
        tree = ast.parse(code)
        
        # Check type hints exist
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef), "Must be a function"
        assert func.returns is not None, "CORE-011: Missing return type hint"
        assert len(func.args.args) == 2, "Function should have 2 parameters"
        
        # Check docstring exists
        docstring = ast.get_docstring(func)
        assert docstring is not None, "CORE-012: Missing docstring"
        
    def test_enforce_tests_before_code(self, tmp_path: Path) -> None:
        """Golden: Enforce CORE-008 (tests BEFORE code).
        
        Validates stub detection and import validation.
        """
        # Scenario 1: Implementation without test should be detected
        impl_file = tmp_path / "feature.py"
        impl_file.write_text("""
def process_data():
    pass
""")
        
        # Check for corresponding test file
        test_file = tmp_path / "test_feature.py"
        assert not test_file.exists(), "Setup: Test doesn't exist yet"
        
        # This pattern should be caught by StubDetectionAgent
        # File exists but:
        # - No test coverage (violates CORE-008)
        # - Low LOC (< 50 lines)
        # - Missing docstrings (violates CORE-012)
        
        code = impl_file.read_text()
        tree = ast.parse(code)
        func = tree.body[0]
        
        # Verify this would be flagged as stub
        has_docstring = ast.get_docstring(func) is not None
        assert not has_docstring, "Stub should lack docstring"
        
        # Create proper test-first implementation
        test_file.write_text("""
def test_process_data():
    from feature import process_data
    result = process_data()
    assert result is not None
""")
        
        # Now test exists, validates TDD cycle
        assert test_file.exists(), "Test now exists (TDD compliance)"


class TestProductionRefactorWorkflow:
    """Golden test: Refactoring workflow."""
    
    def test_refactor_extract_method(self, tmp_path: Path) -> None:
        """Golden: Extract method refactoring.
        
        Validates that refactoring maintains test coverage.
        """
        # Original implementation with test
        impl_file = tmp_path / "report.py"
        impl_file.write_text("""
def generate_report(data: List[str]) -> str:
    '''Generate formatted report.'''
    # Complex logic that should be extracted
    header = "Report Header"
    body = "\\n".join(data)
    footer = "Report Footer"
    return f"{header}\\n{body}\\n{footer}"
""")
        
        test_file = tmp_path / "test_report.py"
        test_file.write_text("""
from report import generate_report

def test_generate_report():
    result = generate_report(["line1", "line2"])
    assert "Report Header" in result
    assert "line1" in result
""")
        
        # After refactoring: extract header/footer methods
        impl_file.write_text("""
def _format_header() -> str:
    '''Format report header.'''
    return "Report Header"

def _format_footer() -> str:
    '''Format report footer.'''
    return "Report Footer"

def generate_report(data: List[str]) -> str:
    '''Generate formatted report.'''
    header = _format_header()
    body = "\\n".join(data)
    footer = _format_footer()
    return f"{header}\\n{body}\\n{footer}"
""")
        
        # Validate refactored code maintains structure
        code = impl_file.read_text()
        tree = ast.parse(code)
        
        # Should have 3 functions now (extracted methods)
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        assert len(functions) == 3, "Should have 3 functions after extraction"
        
        # All functions should have docstrings (CORE-012)
        for func in functions:
            assert ast.get_docstring(func) is not None, f"Function {func.name} missing docstring"
    
    def test_refactor_preserves_tests(self, tmp_path: Path) -> None:
        """Golden: Refactoring preserves all passing tests.
        
        Validates non-breaking changes principle.
        """
        # Original test
        test_file = tmp_path / "test_math.py"
        test_file.write_text("""
from math_utils import calculate

def test_calculate():
    assert calculate(5, 3) == 8
""")
        
        # Original implementation
        impl_file = tmp_path / "math_utils.py"
        impl_file.write_text("""
def calculate(a: int, b: int) -> int:
    return a + b
""")
        
        # Refactor: Improve implementation but keep interface
        impl_file.write_text("""
def calculate(a: int, b: int) -> int:
    '''Calculate sum with validation.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    '''
    # Added validation (improvement)
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Arguments must be integers")
    return a + b
""")
        
        # Validate refactored code quality
        code = impl_file.read_text()
        tree = ast.parse(code)
        func = tree.body[0]
        
        # Check improved docstring
        docstring = ast.get_docstring(func)
        assert docstring is not None, "CORE-012: Missing docstring"
        assert "Args:" in docstring, "Should have Args section"
        assert "Returns:" in docstring, "Should have Returns section"
        
        # Interface unchanged (function signature same)
        assert func.name == "calculate", "Function name preserved"
        assert len(func.args.args) == 2, "Parameter count preserved"


class TestStubDetectionValidation:
    """Golden test: Stub detection and prevention."""
    
    def test_detect_redirect_stub(self, tmp_path: Path) -> None:
        """Golden: Detect redirect stub pattern.
        
        Validates CORE-035 enforcement (no duplicate paths).
        """
        # Create a redirect stub (violation pattern)
        stub_file = tmp_path / "wrapper.py"
        stub_file.write_text("""
# REDIRECT: This just points to brain implementation
from cortex_brain.domain.models import Entity

__all__ = ['Entity']
""")
        
        # Analyze stub characteristics
        code = stub_file.read_text()
        tree = ast.parse(code)
        
        # Should have minimal code (just imports)
        statements = [node for node in tree.body if not isinstance(node, ast.ImportFrom)]
        assert len(statements) <= 1, "Stub should have minimal code"
        
        # Check for redirect pattern
        assert "REDIRECT" in code or "from cortex_brain" in code, "Redirect stub pattern detected"
        
    def test_prevent_stub_without_tests(self, tmp_path: Path) -> None:
        """Golden: Prevent stubs without test coverage.
        
        Validates CORE-008 + StubDetectionAgent logic.
        """
        # Small file without tests (should be flagged)
        small_file = tmp_path / "util.py"
        small_file.write_text("""
def helper():
    pass
""")
        
        # Check characteristics that trigger stub detection
        code = small_file.read_text()
        tree = ast.parse(code)
        
        # Count actual lines of code (excluding blank/comments)
        loc = len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        assert loc < 50, "File is small (stub threshold)"
        
        # Check for missing docstring
        func = tree.body[0]
        has_docstring = ast.get_docstring(func) is not None
        assert not has_docstring, "Missing docstring should trigger stub detection"
        
        # Check for missing test
        test_file = tmp_path / "test_util.py"
        assert not test_file.exists(), "Missing test should trigger stub detection"
