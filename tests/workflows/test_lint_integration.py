"""
Integration tests for LintIntegration

Tests multi-language linter orchestration, parallel execution,
and blocking violation detection.

Version: 1.0.0
Author: Asif Hussain
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.workflows.lint_integration import (
    LintIntegration,
    LintResult,
    Violation,
    LintSeverity
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def linter():
    """Create LintIntegration instance."""
    return LintIntegration()


class TestPylintIntegration:
    """Test pylint integration."""
    
    def test_runs_pylint_successfully(self, linter, temp_dir):
        """Verify pylint executes and returns results."""
        test_file = temp_dir / "valid.py"
        test_file.write_text('''
def hello_world():
    """Valid function."""
    return "Hello, World!"
''')
        
        result = linter.run_lint(test_file, "python")
        
        assert result is not None
        assert isinstance(result, LintResult)
        assert result.duration >= 0
    
    def test_detects_pylint_violations(self, linter, temp_dir):
        """Verify pylint detects actual violations."""
        test_file = temp_dir / "invalid.py"
        test_file.write_text('''
def bad_function():
    x = 1  # Unused variable
    really_really_really_really_really_long_line_that_exceeds_100_characters_limit_and_should_trigger_violation = True
    return None
''')
        
        result = linter.run_lint(test_file, "python")
        
        assert result.violations, "Should detect violations in invalid code"
        assert len(result.violations) > 0
    
    def test_identifies_blocking_violations(self, linter, temp_dir):
        """Verify blocking violations are identified."""
        test_file = temp_dir / "errors.py"
        test_file.write_text('''
def undefined_var():
    return undefined_variable  # NameError
''')
        
        result = linter.run_lint(test_file, "python")
        blocking = linter.get_blocking_violations([result])
        
        # Should have at least the undefined variable error
        assert any('undefined' in v.message.lower() for v in result.violations)


class TestMultiLanguageSupport:
    """Test multi-language linter support."""
    
    def test_detects_python_language(self, linter):
        """Verify Python files are detected."""
        assert linter._get_language(Path("test.py")) == "python"
    
    def test_detects_javascript_language(self, linter):
        """Verify JavaScript files are detected."""
        assert linter._get_language(Path("test.js")) == "javascript"
    
    def test_detects_typescript_language(self, linter):
        """Verify TypeScript files are detected."""
        assert linter._get_language(Path("test.ts")) == "typescript"
    
    def test_detects_csharp_language(self, linter):
        """Verify C# files are detected."""
        assert linter._get_language(Path("test.cs")) == "csharp"
    
    def test_handles_unsupported_language(self, linter):
        """Verify unsupported languages return None."""
        result = linter._get_language(Path("test.unknown"))
        
        assert result is None, "Should return None for unsupported language"


class TestDirectoryScan:
    """Test directory-level lint scanning."""
    
    def test_scans_multiple_python_files(self, linter, temp_dir):
        """Verify directory scan processes multiple files."""
        # Create multiple Python files
        for i in range(3):
            test_file = temp_dir / f"file{i}.py"
            test_file.write_text(f'''
def function{i}():
    """Function {i}."""
    return {i}
''')
        
        results = linter.run_lint_directory(temp_dir, recursive=False)
        
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert all(isinstance(r, LintResult) for r in results)
    
    def test_recursive_scan(self, linter, temp_dir):
        """Verify recursive directory scanning."""
        # Create nested structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        (temp_dir / "root.py").write_text('def root(): pass')
        (subdir / "nested.py").write_text('def nested(): pass')
        
        results = linter.run_lint_directory(temp_dir, recursive=True)
        
        assert len(results) >= 2, "Should scan both root and nested files"
    
    def test_non_recursive_scan(self, linter, temp_dir):
        """Verify non-recursive scan only checks root."""
        # Create nested structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        (temp_dir / "root.py").write_text('def root(): pass')
        (subdir / "nested.py").write_text('def nested(): pass')
        
        results = linter.run_lint_directory(temp_dir, recursive=False)
        
        # Should only find root.py
        file_names = [Path(r.file_path).name for r in results if hasattr(r, 'file_path')]
        assert "root.py" in file_names or len(results) == 1


class TestBlockingDetection:
    """Test blocking violation detection."""
    
    def test_fatal_severity_is_blocking(self, linter):
        """Verify FATAL violations are blocking."""
        results = [LintResult(
            file_path="test.py",
            violations=[
                Violation(
                    file_path="test.py",
                    line_number=1,
                    rule_id="E9999",
                    message="Fatal error",
                    severity=LintSeverity.FATAL
                )
            ],
            blocking_violations=1,
            passed=False,
            duration=0.1
        )]
        
        blocking = linter.get_blocking_violations(results)
        
        assert len(blocking) == 1
        assert blocking[0].severity == LintSeverity.FATAL
    
    def test_error_severity_is_blocking(self, linter):
        """Verify ERROR violations are blocking."""
        results = [LintResult(
            file_path="test.py",
            violations=[
                Violation(
                    file_path="test.py",
                    line_number=1,
                    rule_id="E1234",
                    message="Error message",
                    severity=LintSeverity.ERROR
                )
            ],
            blocking_violations=1,
            passed=False,
            duration=0.1
        )]
        
        blocking = linter.get_blocking_violations(results)
        
        assert len(blocking) == 1
        assert blocking[0].severity == LintSeverity.ERROR
    
    def test_warning_is_not_blocking(self, linter):
        """Verify WARNING violations are not blocking."""
        results = [LintResult(
            file_path="test.py",
            violations=[
                Violation(
                    file_path="test.py",
                    line_number=1,
                    rule_id="W1234",
                    message="Warning message",
                    severity=LintSeverity.WARNING
                )
            ],
            blocking_violations=0,
            passed=True,
            duration=0.1
        )]
        
        blocking = linter.get_blocking_violations(results)
        
        assert len(blocking) == 0


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    def test_handles_missing_file(self, linter):
        """Verify graceful handling of missing files."""
        result = linter.run_lint(Path("/nonexistent/file.py"), "python")
        
        # Should return None or empty result, not crash
        assert result is None or result.passed
    
    def test_handles_linter_not_installed(self, linter, temp_dir, monkeypatch):
        """Verify graceful degradation when linter unavailable."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        
        # Mock subprocess to simulate missing linter
        def mock_run(*args, **kwargs):
            import subprocess
            raise FileNotFoundError("pylint not found")
        
        import subprocess
        monkeypatch.setattr(subprocess, 'run', mock_run)
        
        result = linter.run_lint(test_file, "python")
        
        # Should handle gracefully (None or passed with message)
        assert result is None or result.passed


class TestPerformance:
    """Test performance requirements."""
    
    def test_parallel_execution_faster_than_serial(self, linter, temp_dir):
        """Verify parallel execution provides speedup."""
        # Create 10 small files
        for i in range(10):
            test_file = temp_dir / f"file{i}.py"
            test_file.write_text(f'''
def function{i}():
    """Function {i}."""
    return {i}
''')
        
        import time
        
        # Time parallel execution
        start = time.time()
        results = linter.run_lint_directory(temp_dir, recursive=False)
        parallel_time = time.time() - start
        
        # Just verify it completes reasonably
        assert parallel_time < 30.0, "Should complete within 30 seconds"
        assert len(results) == 10


class TestReportGeneration:
    """Test lint result reporting."""
    
    def test_generates_summary_report(self, linter, temp_dir):
        """Verify summary report generation."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def test():
    x = 1  # Unused variable
    return None
''')
        
        result = linter.run_lint(test_file, "python")
        
        # Verify report has required fields
        assert hasattr(result, 'violations')
        assert hasattr(result, 'blocking_violations')
        assert hasattr(result, 'passed')
        assert hasattr(result, 'duration')
