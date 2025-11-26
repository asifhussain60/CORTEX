"""
Unit tests for CodeCleanupValidator

Tests cover:
- Debug statement detection across languages
- Temporary marker detection
- Hardcoded value detection
- Commented code detection
- Exemption marker handling
- File exclusion logic
- Performance requirements

Version: 1.0.0
Author: Asif Hussain
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.workflows.code_cleanup_validator import (
    CodeCleanupValidator,
    CleanupIssue,
    IssueType
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def validator():
    """Create validator instance."""
    return CodeCleanupValidator()


class TestDebugStatementDetection:
    """Test debug statement detection across languages."""
    
    def test_detects_python_print_statements(self, validator, temp_dir):
        """Verify Python print statements are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def hello():
    print("Debug message")
    return "Hello"
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.DEBUG_STATEMENT
        assert issues[0].severity == "CRITICAL"
        assert 'print' in issues[0].message.lower()
    
    def test_detects_python_debugger(self, validator, temp_dir):
        """Verify Python debugger calls are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def debug_me():
    import pdb; pdb.set_trace()
    return True
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) >= 1
        debug_issues = [i for i in issues if 'pdb' in i.message.lower()]
        assert len(debug_issues) >= 1
    
    def test_detects_csharp_console_writeline(self, validator, temp_dir):
        """Verify C# Console.WriteLine is detected."""
        test_file = temp_dir / "test.cs"
        test_file.write_text('''
public class Test {
    public void Debug() {
        Console.WriteLine("Debug message");
    }
}
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.DEBUG_STATEMENT
        assert 'console' in issues[0].message.lower()
    
    def test_detects_javascript_console_log(self, validator, temp_dir):
        """Verify JavaScript console.log is detected."""
        test_file = temp_dir / "test.js"
        test_file.write_text('''
function debug() {
    console.log("Debug message");
    return true;
}
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.DEBUG_STATEMENT
        assert 'console' in issues[0].message.lower()
    
    def test_detects_typescript_debugger(self, validator, temp_dir):
        """Verify TypeScript debugger statement is detected."""
        test_file = temp_dir / "test.ts"
        test_file.write_text('''
function debug(): boolean {
    debugger;
    return true;
}
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.DEBUG_STATEMENT


class TestTemporaryMarkerDetection:
    """Test temporary code marker detection."""
    
    def test_detects_todo_comments(self, validator, temp_dir):
        """Verify TODO comments are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def incomplete():
    # TODO: Implement this function
    pass
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.TEMPORARY_CODE
        assert issues[0].severity == "WARNING"
    
    def test_detects_fixme_comments(self, validator, temp_dir):
        """Verify FIXME comments are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def buggy():
    # FIXME: This has a bug
    return None
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.TEMPORARY_CODE
    
    def test_detects_not_implemented_exception(self, validator, temp_dir):
        """Verify NotImplementedException is detected."""
        test_file = temp_dir / "test.cs"
        test_file.write_text('''
public class Test {
    public void NotDone() {
        throw new NotImplementedException();
    }
}
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.TEMPORARY_CODE


class TestHardcodedValueDetection:
    """Test hardcoded value detection."""
    
    def test_detects_localhost(self, validator, temp_dir):
        """Verify localhost references are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def connect():
    url = "http://localhost:8080/api"
    return url
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.HARDCODED_VALUE
        assert issues[0].severity == "CRITICAL"
    
    def test_detects_hardcoded_password(self, validator, temp_dir):
        """Verify hardcoded passwords are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def auth():
    password = "secret123"
    return password
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.HARDCODED_VALUE
    
    def test_detects_api_key(self, validator, temp_dir):
        """Verify hardcoded API keys are detected."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def init():
    api_key = "sk-1234567890abcdef"
    return api_key
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.HARDCODED_VALUE


class TestExemptionMarkers:
    """Test exemption marker handling."""
    
    def test_respects_production_safe_marker(self, validator, temp_dir):
        """Verify PRODUCTION_SAFE marker exempts code."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def audit_log():
    # PRODUCTION_SAFE: Used for audit logging
    print("User accessed sensitive data")
    return True
''')
        
        issues = validator.scan_file(test_file)
        
        # Should be no issues due to exemption
        assert len(issues) == 0
    
    def test_respects_allow_debug_marker(self, validator, temp_dir):
        """Verify ALLOW_DEBUG marker exempts code."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def diagnostic():
    # ALLOW_DEBUG: Required for diagnostics
    print("System status")
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 0
    
    def test_exemption_only_applies_to_following_line(self, validator, temp_dir):
        """Verify exemption marker only exempts immediate next line."""
        test_file = temp_dir / "test.py"
        test_file.write_text('''
def mixed():
    # PRODUCTION_SAFE: This one is OK
    print("Audit log")
    
    print("This should be flagged")
''')
        
        issues = validator.scan_file(test_file)
        
        # Should detect the second print
        assert len(issues) == 1


class TestFileExclusion:
    """Test file exclusion logic."""
    
    def test_excludes_test_files(self, validator, temp_dir):
        """Verify test files are excluded."""
        test_file = temp_dir / "test_feature.py"
        test_file.write_text('''
def test_something():
    print("Debug in test")  # Should be allowed in tests
    assert True
''')
        
        issues = validator.scan_file(test_file)
        
        # Test files should be excluded
        assert len(issues) == 0
    
    def test_excludes_debug_utilities(self, validator, temp_dir):
        """Verify debug utility files are excluded."""
        test_file = temp_dir / "debug_helper.py"
        test_file.write_text('''
def debug_info():
    print("Debug helper")  # Should be allowed in debug utils
''')
        
        issues = validator.scan_file(test_file)
        
        assert len(issues) == 0
    
    def test_scans_production_files(self, validator, temp_dir):
        """Verify production files are scanned."""
        test_file = temp_dir / "feature.py"
        test_file.write_text('''
def process():
    print("Should be flagged")
''')
        
        issues = validator.scan_file(test_file)
        
        # Production files should be scanned
        assert len(issues) == 1


class TestDirectoryScan:
    """Test directory scanning."""
    
    def test_scans_multiple_files(self, validator, temp_dir):
        """Verify multiple files are scanned."""
        # Create multiple files with issues
        (temp_dir / "file1.py").write_text('print("debug1")')
        (temp_dir / "file2.py").write_text('print("debug2")')
        (temp_dir / "file3.py").write_text('# TODO: implement')
        
        issues_by_file = validator.scan_directory(temp_dir)
        
        assert len(issues_by_file) == 3
        assert sum(len(issues) for issues in issues_by_file.values()) == 3
    
    def test_recursive_scan(self, validator, temp_dir):
        """Verify recursive scanning works."""
        # Create nested structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        (temp_dir / "root.py").write_text('print("debug")')
        (subdir / "nested.py").write_text('print("debug")')
        
        issues_by_file = validator.scan_directory(temp_dir, recursive=True)
        
        assert len(issues_by_file) == 2
    
    def test_non_recursive_scan(self, validator, temp_dir):
        """Verify non-recursive scanning only scans top level."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        (temp_dir / "root.py").write_text('print("debug")')
        (subdir / "nested.py").write_text('print("debug")')
        
        issues_by_file = validator.scan_directory(temp_dir, recursive=False)
        
        # Should only find root file
        assert len(issues_by_file) == 1


class TestProductionReadiness:
    """Test production readiness validation."""
    
    def test_validates_production_ready_code(self, validator, temp_dir):
        """Verify clean code passes validation."""
        test_file = temp_dir / "clean.py"
        test_file.write_text('''
def production_code():
    return "All good"
''')
        
        is_ready, blocking_issues = validator.validate_production_ready([test_file])
        
        assert is_ready is True
        assert len(blocking_issues) == 0
    
    def test_blocks_on_critical_issues(self, validator, temp_dir):
        """Verify critical issues block production."""
        test_file = temp_dir / "bad.py"
        test_file.write_text('''
def bad_code():
    print("Debug")
    password = "hardcoded"
''')
        
        is_ready, blocking_issues = validator.validate_production_ready([test_file])
        
        assert is_ready is False
        assert len(blocking_issues) > 0
    
    def test_warnings_do_not_block(self, validator, temp_dir):
        """Verify warnings don't block production."""
        test_file = temp_dir / "warnings.py"
        test_file.write_text('''
def with_warnings():
    # TODO: optimize this
    return True
''')
        
        is_ready, blocking_issues = validator.validate_production_ready([test_file])
        
        # Warnings (like TODO) should not block
        assert is_ready is True


class TestReportGeneration:
    """Test report generation."""
    
    def test_generates_clean_report(self, validator):
        """Verify clean report for no issues."""
        report = validator.generate_report({})
        
        assert "No cleanup issues found" in report
        assert "production ready" in report
    
    def test_generates_detailed_report(self, validator, temp_dir):
        """Verify detailed report with issues."""
        test_file = temp_dir / "issues.py"
        test_file.write_text('''
def problematic():
    print("Debug")
    # TODO: fix this
''')
        
        issues_by_file = validator.scan_directory(temp_dir)
        report = validator.generate_report(issues_by_file)
        
        assert "Code Cleanup Report" in report
        assert "Total Issues:" in report
        assert str(test_file) in report


class TestPerformance:
    """Test performance requirements."""
    
    def test_scans_100_files_under_500ms(self, validator, temp_dir):
        """Verify performance requirement: <500ms for 100 files."""
        import time
        
        # Create 100 small files
        for i in range(100):
            file_path = temp_dir / f"file_{i}.py"
            file_path.write_text(f'def func_{i}(): return {i}')
        
        start = time.time()
        validator.scan_directory(temp_dir)
        elapsed = time.time() - start
        
        # Should complete in under 500ms
        assert elapsed < 0.5, f"Scan took {elapsed:.3f}s, should be <0.5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
