"""Test suite for TDD Enhancement - E2E Integration Testing.

Tests complete TDD workflow integration including:
- Pre-commit hook blocking violations
- Pylance highlighting violations in IDE
- Tier0 validation governance enforcement
- RED → GREEN → REFACTOR cycle
- End-to-end integration scenarios
"""

from pathlib import Path
from typing import List
import pytest


class TestRedGreenRefactorCycle:
    """Test RED → GREEN → REFACTOR TDD cycle."""

    def test_red_phase_violation_detected(self) -> None:
        """Test RED phase: violation is detected before fix."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        # RED: Code with violation
        red_code = """
def process():
    try:
        work()
    except:
        pass
"""
        violations = handler.detect_violations(red_code, "test.py")
        
        assert len(violations) > 0, "RED phase: violation should be detected"

    def test_green_phase_violation_fixed(self) -> None:
        """Test GREEN phase: violation is fixed."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        # GREEN: Code with specific exception
        green_code = """
def process():
    try:
        work()
    except Exception as e:
        handle_error(e)
"""
        violations = handler.detect_violations(green_code, "test.py")
        
        bare_except_violations = [
            v for v in violations
            if "bare" in v.message.lower()
        ]
        assert len(bare_except_violations) == 0, "GREEN phase: bare except fixed"

    def test_refactor_phase_code_improvement(self) -> None:
        """Test REFACTOR phase: code is improved without introducing violations."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        # REFACTOR: Code improved with proper typing and docs
        refactored_code = '''
def process(work_func: callable) -> None:
    """Execute work function with error handling.
    
    Args:
        work_func: The function to execute.
        
    Raises:
        ValueError: If work function fails.
    """
    try:
        work_func()
    except ValueError as e:
        raise ValueError(f"Work failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
'''
        violations = handler.detect_violations(refactored_code, "test.py")
        
        # Should have minimal or no violations (just ensure specific exception handling)
        bare_except = [v for v in violations if "bare" in v.message.lower()]
        assert len(bare_except) == 0, "REFACTOR phase: no bare excepts"


class TestMultiLayerIntegration:
    """Test integration of all three layers together."""

    def test_precommit_and_pylance_alignment(self) -> None:
        """Test pre-commit hook and Pylance report same violations."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        precommit = PrecommitHookHandler()
        pylance = PylanceIDEHandler()
        
        code = """
def process(data):
    try:
        work()
    except:
        pass
"""
        precommit_violations = precommit.detect_violations(code, "test.py")
        pylance_violations = pylance.highlight_violations(code)
        
        # Both should detect similar issues
        assert len(precommit_violations) > 0
        assert len(pylance_violations) > 0

    def test_pylance_and_tier0_validation_alignment(self) -> None:
        """Test Pylance and Tier0 validation report aligned violations."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        pylance = PylanceIDEHandler()
        validator = Tier0Validator()
        
        code = """
def func(data):
    pass
"""
        pylance_violations = pylance.highlight_violations(code)
        tier0_violations = validator.validate_code(code, "test.py")
        
        assert len(pylance_violations) > 0
        assert len(tier0_violations) > 0

    def test_all_layers_complete_workflow(self) -> None:
        """Test all three layers in complete workflow."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        precommit = PrecommitHookHandler()
        pylance = PylanceIDEHandler()
        tier0 = Tier0Validator()
        
        # Bad code
        bad_code = """
def bad_func(data):
    try:
        process(data)
    except:
        print("error")
"""
        
        # All layers should detect issues
        precommit_v = precommit.detect_violations(bad_code, "test.py")
        pylance_v = pylance.highlight_violations(bad_code)
        tier0_v = tier0.validate_code(bad_code, "test.py")
        
        assert len(precommit_v) > 0, "Pre-commit should detect"
        assert len(pylance_v) > 0, "Pylance should detect"
        assert len(tier0_v) > 0, "Tier0 should detect"


class TestWorkflowWithFixing:
    """Test complete workflow including violation fixing."""

    def test_workflow_detect_and_fix(self) -> None:
        """Test detecting violations and then fixing them."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        # Initial code with violations
        initial_code = """
def process(data):
    try:
        result = transform(data)
    except:
        result = None
    return result
"""
        
        initial_violations = handler.detect_violations(initial_code, "test.py")
        assert len(initial_violations) > 0, "Initial code should have violations"
        
        # Fixed code
        fixed_code = """
def process(data: str) -> str:
    \"\"\"Process data with error handling.
    
    Args:
        data: Input string.
        
    Returns:
        Transformed string or empty string on error.
    \"\"\"
    try:
        result = transform(data)
    except ValueError as e:
        result = ""
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
    return result
"""
        
        fixed_violations = handler.detect_violations(fixed_code, "test.py")
        
        # Fixed code should have fewer violations
        assert len(fixed_violations) < len(initial_violations)

    def test_workflow_with_multiple_functions(self) -> None:
        """Test workflow with multiple functions in file."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def func1():
    try:
        work1()
    except:
        pass

def func2(x: int):
    return x * 2

def func3(data):
    try:
        process(data)
    except:
        pass
"""
        
        violations = handler.detect_violations(code, "test.py")
        
        # Should find violations in func1 and func3
        bare_excepts = [v for v in violations if "bare" in v.message.lower()]
        assert len(bare_excepts) >= 2


class TestCommitBlockingScenarios:
    """Test various commit blocking scenarios."""

    def test_commit_blocked_on_bare_except(self) -> None:
        """Test commit is blocked when bare except exists."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process():
    try:
        work()
    except:
        pass
"""
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True
        assert len(result.violations) > 0

    def test_commit_blocked_on_missing_types(self) -> None:
        """Test commit is blocked when types are missing."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data):
    return data
"""
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True

    def test_commit_allowed_on_clean_code(self) -> None:
        """Test commit is allowed when code is clean."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        clean_code = '''
def process(data: str) -> str:
    """Process data.
    
    Args:
        data: Input string.
        
    Returns:
        Processed string.
    """
    return data.upper()
'''
        result = handler.validate_commit(clean_code, "test.py")
        
        assert result.should_block is False


class TestIDEFeedback:
    """Test IDE feedback during development."""

    def test_ide_shows_violations_while_typing(self) -> None:
        """Test IDE shows violations in real-time while typing."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler(environment="local")
        
        # Incomplete code while typing
        code = "def process(data):"
        
        violations = handler.highlight_violations(code)
        
        # Should provide feedback for incomplete code
        assert isinstance(violations, list)

    def test_ide_shows_quick_fixes(self) -> None:
        """Test IDE shows quick fix suggestions."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler()
        
        code = """
def process(data):
    return data
"""
        violations = handler.highlight_violations(code)
        
        # Should have suggestions for fixes
        has_suggestions = any("suggestion" in v for v in violations)
        assert has_suggestions

    def test_ide_provides_contextual_help(self) -> None:
        """Test IDE provides context-aware help."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler()
        
        code = """
try:
    do_work()
except:
    pass
"""
        violations = handler.highlight_violations(code)
        
        # Should provide suggestions for violations
        has_suggestions = any("suggestion" in v for v in violations)
        assert has_suggestions


class TestGovernanceEnforcement:
    """Test governance rule enforcement in workflow."""

    def test_core_013_enforced_in_workflow(self) -> None:
        """Test CORE-013 (no bare except) is enforced."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
try:
    work()
except:
    pass
"""
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True

    def test_core_011_enforced_in_workflow(self) -> None:
        """Test CORE-011 (type hints) is enforced."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data):
    return data.upper()
"""
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True

    def test_core_012_enforced_in_workflow(self) -> None:
        """Test CORE-012 (docstrings) is enforced."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data: str) -> str:
    return data.upper()
"""
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True


class TestErrorRecovery:
    """Test error recovery in workflow."""

    def test_recover_from_syntax_error(self) -> None:
        """Test graceful recovery from syntax error."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        bad_code = "def process(\n    incomplete"
        
        violations = handler.detect_violations(bad_code, "test.py")
        
        # Should handle gracefully
        assert isinstance(violations, list)
        assert len(violations) > 0

    def test_continue_after_error(self) -> None:
        """Test workflow continues after handling error."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        # First file with error
        bad_code = "def process(\n    syntax error"
        violations1 = handler.detect_violations(bad_code, "file1.py")
        
        # Second file with violations
        code_with_violation = """
def process():
    try:
        work()
    except:
        pass
"""
        violations2 = handler.detect_violations(code_with_violation, "file2.py")
        
        # Both should be handled
        assert len(violations1) > 0
        assert len(violations2) > 0


class TestPerformanceIntegration:
    """Test performance of integrated workflow."""

    def test_complete_workflow_performance(self) -> None:
        """Test complete workflow executes within time budget."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        import time
        
        handler = PrecommitHookHandler()
        pylance = PylanceIDEHandler()
        tier0 = Tier0Validator()
        
        code = """
def process(data):
    try:
        work(data)
    except:
        pass
"""
        
        start = time.time()
        
        # Execute all layers
        precommit_v = handler.detect_violations(code, "test.py")
        pylance_v = pylance.highlight_violations(code)
        tier0_v = tier0.validate_code(code, "test.py")
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 2.0, f"Workflow took {elapsed}s, expected <2s"

    def test_scalability_with_many_files(self) -> None:
        """Test workflow scales to many files."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        import time
        
        handler = PrecommitHookHandler()
        
        # Simulate checking 100 files
        start = time.time()
        
        code = """
def func(data):
    try:
        work(data)
    except:
        pass
"""
        
        for i in range(100):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        elapsed = time.time() - start
        
        # Should handle 100 files in reasonable time
        assert elapsed < 10.0, f"100 files took {elapsed}s, expected <10s"
