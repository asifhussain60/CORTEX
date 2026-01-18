"""
Test Suite for AC-NFR-003-01: Security Hardening Framework

Tests:
- 15 unit tests
- 6 integration tests
- Total: 21 tests

Covers:
- Input validation (OWASP Top 10)
- Output encoding
- Security policies
- Audit logging
"""

import pytest
import sys
from pathlib import Path

# Add cortex-brain to path for tier2 imports
sys.path.insert(0, str(Path(__file__).parent.parent / "cortex-brain"))

from tier2.security import (
    SecurityViolation,
    InputValidator,
    OutputEncoder,
    SecurityPolicy,
    SecurityContext,
)


# ============================================================================
# UNIT TESTS: Input Validation (OWASP Top 10)
# ============================================================================

class TestInputValidatorSQLInjection:
    """Test SQL Injection detection."""
    
    def test_sql_union_select_detected(self):
        """Test UNION SELECT pattern detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("input' UNION SELECT * FROM users", "username")
    
    def test_sql_insert_detected(self):
        """Test INSERT pattern detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("test'; INSERT INTO users VALUES('x')", "email")
    
    def test_sql_comment_detected(self):
        """Test SQL comment pattern detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("admin'--", "password")
    
    def test_valid_input_passes(self):
        """Test that valid input passes validation."""
        validator = InputValidator(strict_mode=True)
        assert validator.validate_input("john_doe@example.com", "email") is True


class TestInputValidatorCommandInjection:
    """Test Command Injection detection."""
    
    def test_command_shell_metachar_detected(self):
        """Test shell metacharacter detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("test; rm -rf /", "command")
    
    def test_command_pipe_detected(self):
        """Test pipe command detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("file.txt | cat", "filename")
    
    def test_command_backtick_detected(self):
        """Test backtick command execution detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("`whoami`", "input")


class TestInputValidatorPathTraversal:
    """Test Path Traversal detection."""
    
    def test_path_traversal_unix_detected(self):
        """Test Unix path traversal detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("../../etc/passwd", "filepath")
    
    def test_path_traversal_windows_detected(self):
        """Test Windows path traversal detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("..\\..\\windows\\system32", "filepath")
    
    def test_path_traversal_url_encoded_detected(self):
        """Test URL-encoded path traversal detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("..%2f..%2fetc%2fpasswd", "url_param")


class TestInputValidatorXSSInjection:
    """Test XSS Injection detection."""
    
    def test_xss_script_tag_detected(self):
        """Test <script> tag detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("<script>alert('XSS')</script>", "comment")
    
    def test_xss_event_handler_detected(self):
        """Test XSS event handler detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("<img src=x onerror=alert('XSS')>", "html")
    
    def test_xss_javascript_protocol_detected(self):
        """Test javascript: protocol detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("<a href='javascript:void(0)'>click</a>", "link")


class TestInputValidatorScriptInjection:
    """Test Script Injection detection."""
    
    def test_script_import_detected(self):
        """Test __import__ detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("__import__('os').system('ls')", "code")
    
    def test_script_eval_detected(self):
        """Test eval() detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("eval('print(1+1)')", "expression")
    
    def test_script_pickle_detected(self):
        """Test pickle module detection."""
        validator = InputValidator(strict_mode=True)
        with pytest.raises(SecurityViolation):
            validator.validate_input("pickle.loads(data)", "serialization")


# ============================================================================
# UNIT TESTS: Output Encoding
# ============================================================================

class TestOutputEncoder:
    """Test output encoding functionality."""
    
    def test_html_encoding(self):
        """Test HTML encoding."""
        encoder = OutputEncoder()
        result = encoder.encode_html("<script>alert('XSS')</script>")
        assert "&lt;" in result and "&gt;" in result
        assert "<script>" not in result
    
    def test_html_encoding_quotes(self):
        """Test HTML encoding preserves quotes."""
        encoder = OutputEncoder()
        result = encoder.encode_html('He said "hello"')
        assert "&quot;" in result
    
    def test_json_encoding(self):
        """Test JSON encoding."""
        encoder = OutputEncoder()
        result = encoder.encode_json("test\nline")
        assert result.startswith('"')
        assert result.endswith('"')
    
    def test_url_encoding(self):
        """Test URL encoding."""
        encoder = OutputEncoder()
        result = encoder.encode_url("hello world & test")
        assert "%20" in result or "+" in result  # Depending on implementation
        assert "&" in result or "%26" in result
    
    def test_sql_escaping(self):
        """Test SQL escaping."""
        encoder = OutputEncoder()
        result = encoder.escape_sql("O'Reilly")
        assert "''" in result or "\\'" in result


# ============================================================================
# UNIT TESTS: Security Policy
# ============================================================================

class TestSecurityPolicy:
    """Test security policy enforcement."""
    
    def test_max_input_length_policy(self):
        """Test max input length policy."""
        policy = SecurityPolicy()
        assert policy.validate_policy("max_input_length", "short") is True
        long_string = "x" * 10001
        assert policy.validate_policy("max_input_length", long_string) is False
    
    def test_allowed_file_extensions_policy(self):
        """Test file extension whitelist."""
        policy = SecurityPolicy()
        assert policy.validate_policy("allowed_file_extensions", "script.py") is True
        assert policy.validate_policy("allowed_file_extensions", "config.yaml") is True
        assert policy.validate_policy("allowed_file_extensions", "virus.exe") is False
    
    def test_forbidden_modules_policy(self):
        """Test forbidden module detection."""
        policy = SecurityPolicy()
        assert policy.validate_policy("forbidden_modules", "safe_code()") is True
        assert policy.validate_policy("forbidden_modules", "os.system('ls')") is False
    
    def test_get_policy(self):
        """Test retrieving policy values."""
        policy = SecurityPolicy()
        max_length = policy.get_policy("max_input_length")
        assert max_length == 10000
    
    def test_set_policy(self):
        """Test setting policy values."""
        policy = SecurityPolicy()
        policy.set_policy("max_input_length", 5000)
        assert policy.get_policy("max_input_length") == 5000


# ============================================================================
# UNIT TESTS: Security Context & Audit Logging
# ============================================================================

class TestSecurityContext:
    """Test security context and audit logging."""
    
    def test_context_initialization(self):
        """Test context is properly initialized."""
        context = SecurityContext(user_id="test_user")
        assert context.user_id == "test_user"
    
    def test_validate_and_process_valid_input(self):
        """Test valid input passes through."""
        context = SecurityContext()
        result = context.validate_and_process("safe_data", "field1", "test")
        assert result == "safe_data"
    
    def test_validate_and_process_invalid_input(self):
        """Test invalid input raises exception."""
        context = SecurityContext()
        with pytest.raises(SecurityViolation):
            context.validate_and_process("'; DROP TABLE users;--", "sql", "query")
    
    def test_audit_log_violation(self):
        """Test violation is logged to audit trail."""
        context = SecurityContext(user_id="admin")
        try:
            context.validate_and_process("rm -rf /", "cmd", "shell")
        except SecurityViolation:
            pass
        
        audit_log = context.get_audit_log()
        assert len(audit_log) > 0
        assert audit_log[0]["user_id"] == "admin"
        assert "violation_type" in audit_log[0]
    
    def test_encode_response_html(self):
        """Test HTML response encoding."""
        context = SecurityContext()
        encoded = context.encode_response("<tag>content</tag>", "html")
        assert "&lt;" in encoded or "<" not in encoded.replace("&lt;", "")
    
    def test_encode_response_json(self):
        """Test JSON response encoding."""
        context = SecurityContext()
        encoded = context.encode_response("test data", "json")
        assert '"' in encoded  # JSON strings are quoted
    
    def test_multiple_violations_logged(self):
        """Test multiple violations accumulate in audit log."""
        context = SecurityContext()
        
        # Try multiple violations
        for payload in ["'; DROP TABLE;--", "../../etc/passwd", "<script>alert()</script>"]:
            try:
                context.validate_and_process(payload, "test", "security")
            except SecurityViolation:
                pass
        
        audit_log = context.get_audit_log()
        assert len(audit_log) == 3


# ============================================================================
# INTEGRATION TESTS: End-to-End Security Workflow
# ============================================================================

class TestSecurityHardeningIntegration:
    """Integration tests for complete security workflow."""
    
    def test_complete_security_workflow_safe_input(self):
        """Test complete workflow with safe input."""
        context = SecurityContext(user_id="integration_user")
        
        # Validate safe input
        validated = context.validate_and_process("user@example.com", "email", "registration")
        assert validated == "user@example.com"
        
        # Encode for HTML output
        encoded = context.encode_response(validated, "html")
        assert "@" in encoded
        
        # No violations should be logged
        assert len(context.get_audit_log()) == 0
    
    def test_security_policy_enforcement_integration(self):
        """Test security policy integration."""
        context = SecurityContext()
        
        # Policy should allow .py files
        assert context.policy.validate_policy("allowed_file_extensions", "module.py") is True
        
        # Policy should reject .exe files
        assert context.policy.validate_policy("allowed_file_extensions", "malware.exe") is False
    
    def test_multi_layer_protection(self):
        """Test multiple layers of protection work together."""
        context = SecurityContext(user_id="security_tester")
        
        # Attack payload
        payload = "<script>alert('XSS')</script>'; DROP TABLE users;--"
        
        # Should fail at input validation
        with pytest.raises(SecurityViolation):
            context.validate_and_process(payload, "user_input", "form")
        
        # Should be logged
        audit_log = context.get_audit_log()
        assert len(audit_log) > 0
        assert "violation_type" in audit_log[0]
    
    def test_safe_data_flow_through_system(self):
        """Test safe data flows through all layers."""
        context = SecurityContext()
        
        # Clean data
        clean_data = "John Doe"
        
        # Pass through validation
        validated = context.validate_and_process(clean_data, "name", "profile")
        
        # Encode for output
        for encoding in ["html", "json", "url"]:
            encoded = context.encode_response(validated, encoding)
            assert len(encoded) > 0
        
        # No violations
        assert len(context.get_audit_log()) == 0
    
    def test_security_context_with_multiple_users(self):
        """Test security context properly tracks multiple users."""
        ctx1 = SecurityContext(user_id="user1")
        ctx2 = SecurityContext(user_id="user2")
        
        # User 1 violation
        try:
            ctx1.validate_and_process("rm -rf /", "cmd", "shell")
        except SecurityViolation:
            pass
        
        # User 2 violation
        try:
            ctx2.validate_and_process("'; DROP TABLE users;--", "sql", "query")
        except SecurityViolation:
            pass
        
        # Each should have their own log
        log1 = ctx1.get_audit_log()
        log2 = ctx2.get_audit_log()
        
        assert log1[0]["user_id"] == "user1"
        assert log2[0]["user_id"] == "user2"
    
    def test_combined_encoding_safety(self):
        """Test combined encoding for multiple output formats."""
        context = SecurityContext()
        value = "test<>&\"'\n"
        
        # Each encoding should produce safe output
        html_encoded = context.encode_response(value, "html")
        json_encoded = context.encode_response(value, "json")
        url_encoded = context.encode_response(value, "url")
        
        # HTML should escape tags
        assert "<" not in html_encoded or "&lt;" in html_encoded
        
        # All should be strings
        assert isinstance(html_encoded, str)
        assert isinstance(json_encoded, str)
        assert isinstance(url_encoded, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
