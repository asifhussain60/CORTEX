"""
Tests for Security Guard (Phase 6).

TDD Phase: RED - All tests should fail initially.

Tests cover:
- Input sanitization and validation
- Shell injection prevention
- Path traversal prevention
- SQL injection patterns
- XSS pattern detection
- Privilege level enforcement
- Security violation reporting
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path


@pytest.fixture
def security_guard(temp_dir):
    """Create SecurityGuard instance."""
    from core.security_guard import SecurityGuard
    return SecurityGuard()


# =============================================================================
# Test SecurityGuard Initialization
# =============================================================================

class TestSecurityGuardInit:
    """Tests for SecurityGuard initialization."""
    
    def test_init_with_defaults(self):
        """Should initialize with default forbidden patterns."""
        from core.security_guard import SecurityGuard
        
        guard = SecurityGuard()
        
        assert guard.forbidden_patterns is not None
        assert len(guard.forbidden_patterns) > 0
    
    def test_init_with_custom_patterns(self):
        """Should accept custom forbidden patterns."""
        from core.security_guard import SecurityGuard
        
        custom_patterns = [r'custom_pattern', r'another_pattern']
        guard = SecurityGuard(additional_patterns=custom_patterns)
        
        # Should include both default and custom
        assert len(guard.forbidden_patterns) > 2
    
    def test_init_with_strict_mode(self):
        """Should support strict mode with additional checks."""
        from core.security_guard import SecurityGuard
        
        guard = SecurityGuard(strict_mode=True)
        
        assert guard.strict_mode is True


# =============================================================================
# Test Shell Injection Prevention
# =============================================================================

class TestShellInjectionPrevention:
    """Tests for shell injection pattern detection."""
    
    def test_detects_semicolon_injection(self, security_guard):
        """Should detect semicolon shell command chaining."""
        from core.security_guard import SecurityGuard
        
        args = ["--file", "test.txt; rm -rf /"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert len(result.violations) > 0
        assert any(v.pattern_type == "shell_metachar" for v in result.violations)
    
    def test_detects_pipe_injection(self, security_guard):
        """Should detect pipe command chaining."""
        args = ["--input", "data | cat /etc/passwd"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert any("pipe" in str(v).lower() or "shell" in str(v).lower() 
                   for v in result.violations)
    
    def test_detects_ampersand_injection(self, security_guard):
        """Should detect ampersand background command."""
        args = ["--cmd", "echo hello & malicious"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_detects_backtick_injection(self, security_guard):
        """Should detect backtick command substitution."""
        args = ["--name", "`whoami`"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_detects_dollar_substitution(self, security_guard):
        """Should detect dollar sign command substitution."""
        args = ["--value", "$(cat /etc/shadow)"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_allows_safe_dollar_in_paths(self, security_guard):
        """Should allow dollar sign in safe contexts (like env vars in paths)."""
        # Environment variable reference in safe context
        args = ["--output", "/home/$USER/output.txt"]
        
        result = security_guard.sanitize_arguments(args)
        
        # This may be blocked or allowed depending on policy
        # Test documents the behavior
        assert result is not None


# =============================================================================
# Test Path Traversal Prevention
# =============================================================================

class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""
    
    def test_detects_dotdot_traversal(self, security_guard):
        """Should detect .. path traversal."""
        args = ["--file", "../../../etc/passwd"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert any(v.pattern_type == "path_traversal" for v in result.violations)
    
    def test_detects_encoded_traversal(self, security_guard):
        """Should detect URL-encoded path traversal."""
        args = ["--path", "%2e%2e/%2e%2e/etc/passwd"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_detects_absolute_path_when_restricted(self, security_guard):
        """Should flag absolute paths when not explicitly allowed."""
        args = ["--file", "/etc/passwd"]
        
        result = security_guard.sanitize_arguments(args, allow_absolute=False)
        
        assert result.safe is False
        assert any(v.pattern_type == "absolute_path" for v in result.violations)
    
    def test_allows_absolute_path_when_permitted(self, security_guard):
        """Should allow absolute paths when explicitly permitted."""
        args = ["--file", "/home/user/safe.txt"]
        
        result = security_guard.sanitize_arguments(args, allow_absolute=True)
        
        assert result.safe is True
    
    def test_detects_windows_unc_path(self, security_guard):
        """Should detect Windows UNC paths."""
        args = ["--share", "\\\\server\\share\\file"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False


# =============================================================================
# Test SQL Injection Prevention
# =============================================================================

class TestSQLInjectionPrevention:
    """Tests for SQL injection pattern detection."""
    
    def test_detects_drop_table(self, security_guard):
        """Should detect DROP TABLE injection."""
        args = ["--query", "SELECT * FROM users; DROP TABLE users;--"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert any(v.pattern_type == "sql_injection" for v in result.violations)
    
    def test_detects_union_select(self, security_guard):
        """Should detect UNION SELECT injection."""
        args = ["--search", "' UNION SELECT * FROM passwords --"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_detects_or_1_equals_1(self, security_guard):
        """Should detect classic OR 1=1 injection."""
        args = ["--user", "admin' OR '1'='1"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False


# =============================================================================
# Test XSS Prevention
# =============================================================================

class TestXSSPrevention:
    """Tests for XSS pattern detection."""
    
    def test_detects_script_tag(self, security_guard):
        """Should detect script tag injection."""
        args = ["--name", "<script>alert('xss')</script>"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert any(v.pattern_type == "xss" for v in result.violations)
    
    def test_detects_event_handler(self, security_guard):
        """Should detect event handler injection."""
        args = ["--title", "<img onerror='alert(1)'>"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
    
    def test_detects_javascript_protocol(self, security_guard):
        """Should detect javascript: protocol."""
        args = ["--link", "javascript:alert('xss')"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False


# =============================================================================
# Test SanitizeResult
# =============================================================================

class TestSanitizeResult:
    """Tests for SanitizeResult dataclass."""
    
    def test_create_safe_result(self):
        """Should create safe result with no violations."""
        from core.security_guard import SanitizeResult
        
        result = SanitizeResult(safe=True, violations=[])
        
        assert result.safe is True
        assert result.violations == []
    
    def test_create_unsafe_result(self):
        """Should create unsafe result with violations."""
        from core.security_guard import SanitizeResult, SecurityViolation
        
        violation = SecurityViolation(
            arg_index=0,
            argument="malicious",
            pattern="test",
            pattern_type="test",
            severity="critical"
        )
        result = SanitizeResult(safe=False, violations=[violation])
        
        assert result.safe is False
        assert len(result.violations) == 1
    
    def test_sanitize_result_has_summary(self):
        """Should provide summary of violations."""
        from core.security_guard import SanitizeResult, SecurityViolation
        
        violation = SecurityViolation(
            arg_index=0,
            argument="test; rm -rf /",
            pattern=r'[;&|]',
            pattern_type="shell_metachar",
            severity="critical"
        )
        result = SanitizeResult(safe=False, violations=[violation])
        
        summary = result.get_summary()
        
        assert "critical" in summary.lower() or "violation" in summary.lower()


# =============================================================================
# Test SecurityViolation
# =============================================================================

class TestSecurityViolation:
    """Tests for SecurityViolation dataclass."""
    
    def test_create_violation(self):
        """Should create violation with all fields."""
        from core.security_guard import SecurityViolation
        
        violation = SecurityViolation(
            arg_index=1,
            argument="../etc/passwd",
            pattern=r'\.\.',
            pattern_type="path_traversal",
            severity="high"
        )
        
        assert violation.arg_index == 1
        assert violation.pattern_type == "path_traversal"
        assert violation.severity == "high"
    
    def test_violation_severity_levels(self):
        """Should support different severity levels."""
        from core.security_guard import SecurityViolation, Severity
        
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"


# =============================================================================
# Test Privilege Levels
# =============================================================================

class TestPrivilegeLevels:
    """Tests for privilege level enforcement."""
    
    def test_check_user_level_tools(self, security_guard):
        """Should allow user-level operations by default."""
        result = security_guard.check_privilege("align", required_level="user")
        
        assert result.allowed is True
    
    def test_check_admin_level_tools(self, security_guard):
        """Should require explicit admin permission."""
        result = security_guard.check_privilege(
            "cleanup", 
            required_level="admin",
            current_level="user"
        )
        
        assert result.allowed is False
        assert "privilege" in result.reason.lower() or "admin" in result.reason.lower()
    
    def test_admin_can_run_user_tools(self, security_guard):
        """Admin should be able to run user-level tools."""
        result = security_guard.check_privilege(
            "align",
            required_level="user",
            current_level="admin"
        )
        
        assert result.allowed is True
    
    def test_system_level_requires_special_flag(self, security_guard):
        """System-level tools require explicit system flag."""
        result = security_guard.check_privilege(
            "migrate",
            required_level="system",
            current_level="admin"
        )
        
        assert result.allowed is False


# =============================================================================
# Test Safe Arguments
# =============================================================================

class TestSafeArguments:
    """Tests for allowing safe arguments."""
    
    def test_allows_simple_flags(self, security_guard):
        """Should allow simple command flags."""
        args = ["--verbose", "-v", "--output", "result.txt"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True
    
    def test_allows_relative_paths(self, security_guard):
        """Should allow safe relative paths."""
        args = ["--file", "data/input.json", "--out", "output/result.yaml"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True
    
    def test_allows_numeric_values(self, security_guard):
        """Should allow numeric values."""
        args = ["--count", "100", "--timeout", "30.5"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True
    
    def test_allows_boolean_values(self, security_guard):
        """Should allow boolean string values."""
        args = ["--dry-run", "true", "--verbose", "false"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_arguments(self, security_guard):
        """Should handle empty argument list."""
        args = []
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True
        assert result.violations == []
    
    def test_none_argument_value(self, security_guard):
        """Should handle None in argument list."""
        args = ["--flag", None, "--value"]
        
        result = security_guard.sanitize_arguments(args)
        
        # Should either handle gracefully or report
        assert result is not None
    
    def test_very_long_argument(self, security_guard):
        """Should handle very long arguments."""
        long_arg = "a" * 10000
        args = ["--data", long_arg]
        
        result = security_guard.sanitize_arguments(args)
        
        # Should not crash, may warn about length
        assert result is not None
    
    def test_unicode_in_arguments(self, security_guard):
        """Should handle unicode characters."""
        args = ["--name", "日本語テスト", "--emoji", "🚀🎉"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is True
    
    def test_mixed_safe_and_unsafe(self, security_guard):
        """Should report only the unsafe arguments."""
        args = ["--safe", "value", "--unsafe", "test; rm -rf /", "--ok", "fine"]
        
        result = security_guard.sanitize_arguments(args)
        
        assert result.safe is False
        assert len(result.violations) >= 1
        # Should identify the specific unsafe argument
        assert any(v.arg_index == 3 for v in result.violations)


# =============================================================================
# Test Integration with ToolkitManager
# =============================================================================

class TestIntegrationWithManager:
    """Tests for integration with ToolkitManager."""
    
    @pytest.fixture
    def manager_temp_dir(self, tmp_path):
        """Create temp directory with manifest for ToolkitManager."""
        manifest_content = """
version: 1.0.0
categories:
  test:
    description: Test tools
    tools:
      - name: align
        command: cortex-align
        script: core/align.py
        description: Alignment tool
        platforms: [linux, macos]
        requires_admin: false
        execution_method: cli
"""
        manifest_path = tmp_path / "toolkit-manifest.yaml"
        manifest_path.write_text(manifest_content)
        (tmp_path / ".checkpoints").mkdir(exist_ok=True)
        return tmp_path
    
    def test_manager_has_security_guard(self, manager_temp_dir):
        """ToolkitManager should have SecurityGuard."""
        from core.toolkit_manager import ToolkitManager
        from core.security_guard import SecurityGuard
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        
        assert hasattr(manager, 'security_guard')
        assert isinstance(manager.security_guard, SecurityGuard)
    
    def test_manager_sanitize_before_execute(self, manager_temp_dir):
        """Manager should sanitize args before execution."""
        from core.toolkit_manager import ToolkitManager
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        
        # Should have method to sanitize
        result = manager.sanitize_arguments(["--safe", "value"])
        
        assert result.safe is True
