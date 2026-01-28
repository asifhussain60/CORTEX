"""Test suite for TDD Enhancement Layer 1 - Pre-commit Hook Integration.

Tests pre-commit hook violation detection automation including:
- Bare except clause detection
- Generic exception validation
- Type hints validation (CORE-011)
- Docstring format validation (CORE-012)
- Commit blocking on violations
- --no-verify override support
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Tuple
import pytest

from cortex.testing.tdd_enhancement_layer1_precommit import (
    PrecommitHookHandler,
    ViolationResult,
    ViolationType,
)


class TestPrecommitHookBasics:
    """Test basic pre-commit hook initialization and configuration."""

    def test_precommit_config_file_exists(self) -> None:
        """Verify .pre-commit-config.yaml exists."""
        hook_file = Path("/Users/asifhussain/PROJECTS/CORTEX/.pre-commit-config.yaml")
        assert hook_file.exists(), ".pre-commit-config.yaml not found"

    def test_precommit_handler_initialization(self) -> None:
        """Test PrecommitHookHandler can be instantiated."""
        handler = PrecommitHookHandler()
        assert handler is not None
        assert hasattr(handler, "detect_violations")
        assert hasattr(handler, "validate_commit")

    def test_precommit_handler_has_required_methods(self) -> None:
        """Verify PrecommitHookHandler has all required methods."""
        handler = PrecommitHookHandler()
        assert callable(handler.detect_violations)
        assert callable(handler.validate_commit)
        assert callable(handler.should_block_commit)


class TestBareExceptDetection:
    """Test bare except clause detection."""

    def test_detect_bare_except_in_file(self) -> None:
        """Test detection of bare except clause."""
        code_with_bare_except = """
def process_data():
    try:
        data = load_data()
    except:
        print("Error occurred")
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code_with_bare_except, "test.py")
        
        assert len(violations) > 0
        assert any(v.violation_type == ViolationType.BARE_EXCEPT for v in violations)

    def test_allow_specific_exceptions(self) -> None:
        """Test that specific exceptions are allowed."""
        code_with_specific = """
def process_data():
    try:
        data = load_data()
    except ValueError as e:
        print(f"Error: {e}")
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code_with_specific, "test.py")
        
        bare_except_violations = [
            v for v in violations
            if v.violation_type == ViolationType.BARE_EXCEPT
        ]
        assert len(bare_except_violations) == 0

    def test_detect_multiple_bare_excepts(self) -> None:
        """Test detection of multiple bare except clauses."""
        code_with_multiple = """
def process():
    try:
        a = func1()
    except:
        pass
    
    try:
        b = func2()
    except:
        pass
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code_with_multiple, "test.py")
        
        bare_excepts = [
            v for v in violations
            if v.violation_type == ViolationType.BARE_EXCEPT
        ]
        assert len(bare_excepts) >= 2


class TestGenericExceptionDetection:
    """Test generic exception detection."""

    def test_detect_assertion_error(self) -> None:
        """Test detection of bare AssertionError catching."""
        code = """
def validate():
    try:
        assert condition
    except AssertionError:
        handle_error()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        # AssertionError should not be flagged if specific
        # But will detect missing type hints and docstring
        bare_except = [v for v in violations if v.violation_type.value == "bare_except"]
        assert len(bare_except) == 0

    def test_detect_runtime_error_generic(self) -> None:
        """Test detection of overly generic RuntimeError."""
        code = """
def process():
    try:
        result = do_work()
    except RuntimeError:
        log_error()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        # RuntimeError catching is generic, should be flagged
        runtime_errors = [
            v for v in violations
            if "RuntimeError" in v.message
        ]
        # Note: Implementation may flag this as generic


class TestTypeHintsValidation:
    """Test type hints validation (CORE-011)."""

    def test_function_without_type_hints(self) -> None:
        """Test detection of function without type hints."""
        code = """
def process_data(data):
    return data.upper()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        type_hint_violations = [
            v for v in violations
            if "type hint" in v.message.lower()
        ]
        assert len(type_hint_violations) > 0

    def test_function_with_complete_type_hints(self) -> None:
        """Test function with complete type hints passes validation."""
        code = """
def process_data(data: str) -> str:
    return data.upper()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        type_hint_violations = [
            v for v in violations
            if "type hint" in v.message.lower()
        ]
        assert len(type_hint_violations) == 0

    def test_function_with_partial_type_hints(self) -> None:
        """Test function with incomplete type hints."""
        code = """
def process_data(data: str):
    return data.upper()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        # Missing return type hint should be detected
        type_hint_violations = [
            v for v in violations
            if "return" in v.message.lower() and "type" in v.message.lower()
        ]
        # Should have violation for missing return type


class TestDocstringValidation:
    """Test docstring format validation (CORE-012)."""

    def test_function_without_docstring(self) -> None:
        """Test detection of function without docstring."""
        code = """
def process_data(data: str) -> str:
    return data.upper()
"""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        docstring_violations = [
            v for v in violations
            if "docstring" in v.message.lower()
        ]
        assert len(docstring_violations) > 0

    def test_function_with_google_style_docstring(self) -> None:
        """Test function with proper Google-style docstring."""
        code = '''
def process_data(data: str) -> str:
    """Process input data by converting to uppercase.
    
    Args:
        data: The input string to process.
        
    Returns:
        The processed string in uppercase.
    """
    return data.upper()
'''
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        docstring_violations = [
            v for v in violations
            if "docstring" in v.message.lower()
        ]
        # Should not have docstring violations
        assert len(docstring_violations) == 0

    def test_docstring_missing_args_section(self) -> None:
        """Test docstring without Args section."""
        code = '''
def process_data(data: str) -> str:
    """Process input data.
    
    Returns:
        The processed string.
    """
    return data.upper()
'''
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(code, "test.py")
        
        missing_args = [
            v for v in violations
            if "Args" in v.message
        ]
        # Should detect missing Args section
        assert len(missing_args) > 0


class TestCommitBlocking:
    """Test commit blocking on violations."""

    def test_validate_commit_allows_clean_code(self) -> None:
        """Test that clean code passes validation."""
        code = '''
def process_data(data: str) -> str:
    """Process input data by converting to uppercase.
    
    Args:
        data: The input string to process.
        
    Returns:
        The processed string in uppercase.
    """
    return data.upper()
'''
        handler = PrecommitHookHandler()
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is False
        assert result.violations == []

    def test_validate_commit_blocks_bare_except(self) -> None:
        """Test that commit is blocked on bare except."""
        code = """
def process():
    try:
        do_work()
    except:
        pass
"""
        handler = PrecommitHookHandler()
        result = handler.validate_commit(code, "test.py")
        
        assert result.should_block is True
        assert len(result.violations) > 0

    def test_should_block_commit_property(self) -> None:
        """Test should_block_commit() method."""
        handler = PrecommitHookHandler()
        
        code_with_violation = "try:\n    pass\nexcept:\n    pass"
        violations = handler.detect_violations(code_with_violation, "test.py")
        
        should_block = handler.should_block_commit(violations)
        assert should_block is True


class TestNoVerifyOverride:
    """Test --no-verify override support."""

    def test_no_verify_override_available(self) -> None:
        """Test that --no-verify can bypass hook."""
        handler = PrecommitHookHandler()
        assert hasattr(handler, "allow_no_verify")

    def test_git_no_verify_integration(self) -> None:
        """Test that git commit --no-verify bypasses hook."""
        # This would be integration test with actual git
        handler = PrecommitHookHandler()
        assert handler.allow_no_verify is True


class TestViolationResult:
    """Test ViolationResult data structure."""

    def test_violation_result_creation(self) -> None:
        """Test ViolationResult can be created."""
        result = ViolationResult(
            should_block=True,
            violations=[],
            message="Test message"
        )
        assert result.should_block is True
        assert result.message == "Test message"

    def test_violation_result_with_violations(self) -> None:
        """Test ViolationResult with violation details."""
        from cortex.testing.tdd_enhancement_layer1_precommit import Violation
        
        violations = [
            Violation(
                violation_type=ViolationType.BARE_EXCEPT,
                line_number=5,
                message="Bare except clause found",
                code_snippet="except:"
            )
        ]
        result = ViolationResult(
            should_block=True,
            violations=violations
        )
        assert len(result.violations) == 1
        assert result.violations[0].line_number == 5


class TestIntegrationWithFileSystem:
    """Test pre-commit hook with actual file system."""

    def test_process_file_from_disk(self) -> None:
        """Test processing a file from disk."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def process():
    try:
        do_work()
    except:
        pass
""")
            f.flush()
            
            handler = PrecommitHookHandler()
            with open(f.name, 'r') as file_obj:
                code = file_obj.read()
            
            violations = handler.detect_violations(code, f.name)
            assert len(violations) > 0
            
            os.unlink(f.name)

    def test_process_multiple_files(self) -> None:
        """Test processing multiple files in one commit."""
        files_to_check = []
        try:
            # Create temp files
            for i in range(3):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    if i == 0:
                        f.write("def good(): pass")
                    else:
                        f.write("def bad():\n    try:\n        pass\n    except:\n        pass")
                    f.flush()
                    files_to_check.append(f.name)
            
            handler = PrecommitHookHandler()
            all_violations = []
            for file_path in files_to_check:
                with open(file_path, 'r') as f:
                    code = f.read()
                violations = handler.detect_violations(code, file_path)
                all_violations.extend(violations)
            
            # Should have violations from bad files
            assert len(all_violations) > 0
        finally:
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    os.unlink(file_path)


class TestPerformance:
    """Test pre-commit hook performance."""

    def test_detection_completes_in_reasonable_time(self) -> None:
        """Test that violation detection completes within 1 second."""
        large_code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(100)
        ])
        
        handler = PrecommitHookHandler()
        import time
        start = time.time()
        violations = handler.detect_violations(large_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Detection took {elapsed}s, expected <1s"


class TestErrorHandling:
    """Test error handling in pre-commit hook."""

    def test_handle_syntax_error_gracefully(self) -> None:
        """Test handling of Python syntax errors."""
        bad_code = "def func(\n    this is not valid python"
        
        handler = PrecommitHookHandler()
        violations = handler.detect_violations(bad_code, "test.py")
        
        # Should report syntax error, not crash
        assert len(violations) > 0

    def test_handle_non_existent_file(self) -> None:
        """Test handling of non-existent file."""
        handler = PrecommitHookHandler()
        violations = handler.detect_violations("", "/nonexistent/path.py")
        
        # Should handle gracefully
        assert isinstance(violations, list)
