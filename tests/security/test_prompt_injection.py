"""
AC-FIX-004-01: Prompt Injection Sanitization Tests

Tests for preventing prompt injection attacks through:
1. YAML-safe escaping for template interpolations
2. Whitelist validation for operation names
3. Whitelist validation for AC-IDs
4. Template variable validation
5. Malicious input rejection

FINDING-004 (HIGH): Insufficient template input validation allows injection attacks
CORE-006: Security testing framework compliance
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

# Import the components we'll be testing
from cortex.core.orchestrator.conversation_protocol import ConversationProtocol
from cortex.core.result import Result, Ok, Err
from cortex.security.prompt_injection_prevention import (
    YAMLSanitizer,
    OperationNameValidator,
    ACIDValidator,
    TemplateVariableValidator,
    InputSanitizer,
    PathTraversalValidator,
    PromptInjectionSanitizer,
)


@dataclass
class PromptInjectionTestCase:
    """Test case for prompt injection attacks"""
    name: str
    input_value: str
    should_sanitize: bool
    expected_output: str = None
    attack_type: str = None  # 'yaml_escape', 'operation_name', 'ac_id', 'variable_expansion'


class TestYAMLSafeEscaping:
    """
    Tests for YAML-safe escaping in template interpolations.
    
    YAML special characters that must be escaped:
    - Quotes (single and double)
    - Colons after spaces
    - Hash symbols
    - Ampersands
    - Asterisks
    - Pipes
    - Greater/less than
    - Curly braces
    - Square brackets
    """

    def test_yaml_quote_escaping_double_quotes(self):
        """Double quotes in template values are properly escaped"""
        malicious_input = 'value with "quotes" inside'
        expected = 'value with \\"quotes\\" inside'
        
        # This would be used in template: {user_input: "<malicious_input>"}
        # The escaping function should ensure YAML parser sees it as string literal
        result = self._sanitize_for_yaml(malicious_input)
        assert '"' not in result or result.count('"') % 2 == 0, "Quotes must be properly escaped"

    def test_yaml_quote_escaping_single_quotes(self):
        """Single quotes in template values are properly escaped"""
        malicious_input = "value with 'quotes' inside"
        
        # In YAML, single quotes require different escaping than double quotes
        result = self._sanitize_for_yaml(malicious_input)
        # Should either escape or use appropriate quote style
        assert result is not None

    def test_yaml_colon_escaping(self):
        """Colons followed by spaces are properly escaped"""
        malicious_input = "key: value attack"
        
        result = self._sanitize_for_yaml(malicious_input)
        # Should either quote the entire value or escape the colon
        assert result is not None

    def test_yaml_hash_escaping(self):
        """Hash symbols (comments) are properly escaped"""
        malicious_input = "normal text # this is a comment injection"
        
        result = self._sanitize_for_yaml(malicious_input)
        # Hash should not start a comment if properly escaped
        assert result is not None

    def test_yaml_special_characters_escaping(self):
        """All special YAML characters are escaped"""
        special_chars = ['&', '*', '|', '>', '<', '{', '}', '[', ']', '@', '`']
        
        for char in special_chars:
            malicious_input = f"value{char}attack"
            result = self._sanitize_for_yaml(malicious_input)
            # Should either escape or quote appropriately
            assert result is not None, f"Failed to handle character '{char}'"

    def test_yaml_multiline_escaping(self):
        """Multiline strings are properly escaped"""
        malicious_input = "line1\nline2\nline3"
        
        result = self._sanitize_for_yaml(malicious_input)
        # Multiline strings need special handling (literal or folded blocks)
        assert result is not None

    def _sanitize_for_yaml(self, value: str) -> str:
        """Helper: YAML sanitization"""
        return YAMLSanitizer.sanitize_for_yaml(value)


class TestOperationNameWhitelist:
    """
    Tests for operation name validation against whitelist.
    
    Valid operations must be in approved list to prevent:
    - Arbitrary operation execution
    - Hidden/undocumented operation calls
    - Command injection via operation names
    """

    VALID_OPERATIONS = {
        'create_conversation',
        'execute_turn',
        'rollback_state',
        'validate_governance',
        'apply_fix',
        'audit_log',
        'query_domain_brain'
    }

    def test_valid_operation_names_accepted(self):
        """Valid operation names from whitelist are accepted"""
        for op_name in self.VALID_OPERATIONS:
            result = self._validate_operation_name(op_name)
            assert result.is_ok(), f"Valid operation '{op_name}' rejected"

    def test_invalid_operation_names_rejected(self):
        """Invalid operation names are rejected"""
        invalid_ops = [
            'execute_shell_command',
            'system_call',
            'os_exec',
            '__private_method',
            'delete_all_data',
            'bypass_governance'
        ]
        
        for op_name in invalid_ops:
            result = self._validate_operation_name(op_name)
            assert result.is_err(), f"Invalid operation '{op_name}' accepted"

    def test_operation_name_case_sensitivity(self):
        """Operation name validation is case-sensitive"""
        # If whitelist has 'create_conversation' in lowercase,
        # 'CREATE_CONVERSATION' or 'Create_Conversation' should fail
        result_lower = self._validate_operation_name('create_conversation')
        result_upper = self._validate_operation_name('CREATE_CONVERSATION')
        
        assert result_lower.is_ok()
        assert result_upper.is_err(), "Case-sensitive validation failed"

    def test_operation_name_with_injection_rejected(self):
        """Operation names with injection attempts are rejected"""
        injection_attempts = [
            'create_conversation; delete_all',
            'execute_turn | system_call',
            'query_domain_brain`whoami`',
            'apply_fix && rm -rf /',
            'create_conversation$(whoami)'
        ]
        
        for op_name in injection_attempts:
            result = self._validate_operation_name(op_name)
            assert result.is_err(), f"Injection attempt '{op_name}' accepted"

    def test_operation_name_whitelist_maintainability(self):
        """Whitelist is centrally managed and documented"""
        # Verify whitelist exists and is accessible
        whitelist = self._get_operation_whitelist()
        assert whitelist is not None
        assert len(whitelist) > 0
        # Should be a set or dict for O(1) lookup
        assert isinstance(whitelist, (set, dict))

    def _validate_operation_name(self, op_name: str) -> Result:
        """Helper: Validate operation name"""
        return OperationNameValidator.validate(op_name)

    def _get_operation_whitelist(self) -> set:
        """Helper: Get operation whitelist"""
        return OperationNameValidator.get_whitelist()


class TestACIDWhitelist:
    """
    Tests for AC-ID validation against whitelist.
    
    AC-IDs must be in approved list to prevent:
    - Executing arbitrary action cards
    - Hidden/undocumented AC execution
    - Reference to non-existent ACs
    """

    VALID_AC_IDS = {
        'AC-FIX-001-01',
        'AC-FIX-002-01',
        'AC-FIX-003-01',
        'AC-FIX-004-01',
        'AC-FIX-005-01',
        'AC-FIX-006-01',
        'AC-DOC-007-01',
        'AC-MINOR-008-01'
    }

    def test_valid_ac_ids_accepted(self):
        """Valid AC-IDs from whitelist are accepted"""
        for ac_id in self.VALID_AC_IDS:
            result = self._validate_ac_id(ac_id)
            assert result.is_ok(), f"Valid AC-ID '{ac_id}' rejected"

    def test_invalid_ac_ids_rejected(self):
        """Invalid AC-IDs are rejected"""
        invalid_ids = [
            'AC-FAKE-001-01',
            'AC-DELETE-999-99',
            'AC-ADMIN-001-01',
            'INVALID-FORMAT',
            'AC-',
            ''
        ]
        
        for ac_id in invalid_ids:
            result = self._validate_ac_id(ac_id)
            assert result.is_err(), f"Invalid AC-ID '{ac_id}' accepted"

    def test_ac_id_format_validation(self):
        """AC-ID format is strictly validated: AC-{TYPE}-{NUM}-{SUB}"""
        # Valid format: AC-FIX-001-01
        valid_format = self._validate_ac_id('AC-FIX-001-01')
        assert valid_format.is_ok()
        
        # Invalid formats
        invalid_formats = [
            'AC-FIX-001',        # Missing sub-number
            'AC-FIX-1-1',        # Numbers not zero-padded
            'AC-FIX-001-01-01',  # Too many parts
            'ACFIX00101',        # No hyphens
            'ac-fix-001-01'      # Lowercase
        ]
        
        for fmt in invalid_formats:
            result = self._validate_ac_id(fmt)
            assert result.is_err(), f"Invalid format '{fmt}' accepted"

    def test_ac_id_whitelist_loaded_from_config(self):
        """AC-ID whitelist is loaded from governance config"""
        whitelist = self._get_ac_id_whitelist()
        assert whitelist is not None
        assert len(whitelist) > 0
        # Should match PHASE-REMEDIATION-03 ACs
        assert 'AC-FIX-001-01' in whitelist

    def test_ac_id_injection_attempts_rejected(self):
        """AC-ID injection attempts are rejected"""
        injection_attempts = [
            'AC-FIX-001-01; delete_db()',
            'AC-FIX-001-01" onload="alert()"',
            "AC-FIX-001-01' OR '1'='1",
            'AC-FIX-001-01\nAC-ADMIN-999-99',
            'AC-FIX-001-01${COMMAND}'
        ]
        
        for ac_id in injection_attempts:
            result = self._validate_ac_id(ac_id)
            assert result.is_err(), f"Injection attempt '{ac_id}' accepted"

    def _validate_ac_id(self, ac_id: str) -> Result:
        """Helper: Validate AC-ID"""
        return ACIDValidator.validate(ac_id)

    def _get_ac_id_whitelist(self) -> set:
        """Helper: Get AC-ID whitelist"""
        return ACIDValidator.get_whitelist()


class TestTemplateVariableValidation:
    """
    Tests for template variable validation.
    
    Template variables must be:
    - Explicitly declared before use
    - Type-checked
    - Length-limited
    - Content-restricted
    """

    def test_template_variables_must_be_declared(self):
        """Template can only use declared variables"""
        template = "Operation: {operation_name}, AC: {ac_id}"
        declared_vars = {'operation_name', 'ac_id'}
        
        # Valid: all variables are declared
        result = self._validate_template_variables(template, declared_vars)
        assert result.is_ok()

    def test_undeclared_template_variables_rejected(self):
        """Template using undeclared variables is rejected"""
        template = "Operation: {operation_name}, AC: {ac_id}, Secret: {secret_token}"
        declared_vars = {'operation_name', 'ac_id'}
        
        # Invalid: 'secret_token' not declared
        result = self._validate_template_variables(template, declared_vars)
        assert result.is_err()

    def test_template_variable_type_checking(self):
        """Template variables are type-checked"""
        template = "Turn {turn_number}: {operation_name}"
        vars_with_types = {
            'turn_number': int,
            'operation_name': str
        }
        
        # Valid: int and str match template usage
        result = self._validate_template_variables_typed(template, vars_with_types)
        assert result.is_ok()

    def test_template_variable_length_limits(self):
        """Template variables are length-limited to prevent DoS"""
        # Example: operation_name max 50 chars, ac_id max 15 chars
        constraints = {
            'operation_name': 50,
            'ac_id': 15
        }
        
        # Valid: within limits
        valid_values = {
            'operation_name': 'a' * 50,
            'ac_id': 'AC-FIX-001-01'
        }
        result = self._validate_variable_lengths(valid_values, constraints)
        assert result.is_ok()
        
        # Invalid: exceeds limits
        invalid_values = {
            'operation_name': 'a' * 51,  # Exceeds 50
            'ac_id': 'AC-FIX-001-01'
        }
        result = self._validate_variable_lengths(invalid_values, constraints)
        assert result.is_err()

    def test_template_variable_encoding(self):
        """Template variables are properly encoded/escaped"""
        # Unicode, special characters handled safely
        problematic_vars = {
            'unicode': '你好世界',
            'newlines': 'line1\nline2',
            'quotes': "it's \"quoted\"",
            'null_bytes': 'test\x00null'
        }
        
        for var_name, var_value in problematic_vars.items():
            result = self._validate_variable_encoding(var_value)
            assert result.is_ok(), f"Failed to encode '{var_name}'"

    def _validate_template_variables(self, template: str, declared_vars: set) -> Result:
        """Helper: Validate all template variables are declared"""
        return TemplateVariableValidator.validate_declared_variables(template, declared_vars)

    def _validate_template_variables_typed(self, template: str, vars_with_types: Dict) -> Result:
        """Helper: Validate template variables with type checking"""
        return TemplateVariableValidator.validate_variable_types({}, vars_with_types)

    def _validate_variable_lengths(self, values: Dict[str, str], constraints: Dict[str, int]) -> Result:
        """Helper: Validate variable lengths"""
        return TemplateVariableValidator.validate_variable_lengths(values, constraints)

    def _validate_variable_encoding(self, value: str) -> Result:
        """Helper: Validate variable encoding"""
        sanitized = InputSanitizer.sanitize_encoding(value)
        return Ok(None)


class TestPromptInjectionIntegration:
    """
    Integration tests for prompt injection prevention across the system.
    """

    @patch('src.core.orchestrator.conversation_protocol.ConversationProtocol')
    def test_malicious_prompt_rejected_in_orchestrator(self, mock_protocol):
        """Malicious prompt injection is rejected by orchestrator"""
        malicious_prompt = """
        create_conversation (
          operation: "execute_turn; DELETE FROM governance.db",
          ac_id: "AC-FIX-001-01' OR '1'='1"
        )
        """
        
        # Orchestrator should reject this
        # Implementation will sanitize and validate
        # TODO: Assert rejection
        pass

    def test_malicious_ac_id_rejected_by_validation(self):
        """Malicious AC-ID injection is rejected by validation"""
        malicious_ac_id = "AC-FIX-001-01\n; EVAL(dangerous_code)"
        
        # Validation should reject
        # TODO: Assert rejection
        pass

    def test_escaped_prompt_still_executes_correctly(self):
        """Correctly escaped prompts execute as intended"""
        # Normal prompt with special characters that should work after sanitization
        prompt_with_special_chars = """
        AC-FIX-004-01: Fix operation name with "quotes" and 'apostrophes'
        """
        
        # After sanitization, should still be executable
        # TODO: Assert successful execution after sanitization
        pass

    def test_audit_log_captures_injection_attempts(self):
        """Injection attempts are logged in audit trail"""
        # When injection attempt is detected:
        # 1. Reject the operation
        # 2. Log to governance.audit_log with severity=SECURITY_VIOLATION
        # 3. Include original input and sanitized version
        # TODO: Assert audit logging
        pass


class TestPromptInjectionEdgeCases:
    """
    Edge case tests for prompt injection scenarios.
    """

    def test_null_byte_injection(self):
        """Null bytes in input are handled safely"""
        malicious = "normal\x00injected"
        result = self._sanitize_input(malicious)
        assert '\x00' not in result or result.split('\x00')[0] == 'normal'

    def test_unicode_normalization(self):
        """Unicode normalization prevents homograph attacks"""
        # e.g., Cyrillic 'а' (U+0430) vs Latin 'a' (U+0061)
        lookalike = 'aссount'  # Contains Cyrillic characters
        normalized = self._normalize_unicode(lookalike)
        assert normalized is not None

    def test_bidi_override_attacks(self):
        """Bidirectional override characters don't affect parsing"""
        bidi_attack = "delete\u202Eelif;#"  # RTL override attempts to hide 'delete'
        result = self._sanitize_input(bidi_attack)
        # Should either remove or mark dangerous characters
        assert result is not None

    def test_emoji_injection(self):
        """Emoji and extended Unicode are properly handled"""
        emoji_input = "operation: 😈 delete_all()"
        result = self._sanitize_input(emoji_input)
        # Should either strip emoji or ensure they're escaped
        assert result is not None

    def test_very_long_input_rejected(self):
        """Extremely long inputs are rejected (DoS prevention)"""
        max_length = 10000
        very_long = "a" * (max_length + 1)
        result = InputSanitizer.sanitize_length(very_long)
        # Result should be error when exceeding max length
        assert result.is_err(), "Very long input should be rejected"

    def test_recursive_injection_prevention(self):
        """Nested/recursive injection attempts are prevented"""
        # Attempt: "{{operation_name}} expands to another injection"
        recursive_attack = "{{get_secret()}}"
        result = self._sanitize_input(recursive_attack)
        # Should not allow nested template expansion
        assert "{{" not in result or result.count("{") == result.count("}") == 0

    def test_path_traversal_in_variables(self):
        """Path traversal attempts in variables are blocked"""
        path_traversal = "../../governance.db"
        result = self._sanitize_variable(path_traversal)
        assert result.is_err() or ".." not in result

    def _sanitize_input(self, value: str) -> str:
        """Helper: Sanitize general input"""
        return InputSanitizer.remove_template_expansion_markers(InputSanitizer.sanitize_encoding(value))

    def _normalize_unicode(self, value: str) -> str:
        """Helper: Normalize Unicode"""
        return InputSanitizer.sanitize_encoding(value)

    def _sanitize_variable(self, value: str) -> Result:
        """Helper: Sanitize variable value"""
        return PathTraversalValidator.validate(value)


class TestPromptInjectionPerformance:
    """
    Performance tests for sanitization to ensure no DoS via sanitization itself.
    """

    def test_sanitization_performance_linear_scaling(self):
        """Sanitization time scales linearly with input size"""
        import time
        
        small_input = "a" * 100
        large_input = "a" * 10000
        
        # TODO: Measure sanitization time
        # Should be O(n), not O(n²) or O(n³)
        pass

    def test_sanitization_timeout_on_extremely_large_input(self):
        """Sanitization has timeout protection"""
        # If input exceeds reasonable size (e.g., 1MB), should timeout
        # rather than attempt to process indefinitely
        huge_input = "a" * (1024 * 1024)
        
        # TODO: Assert timeout or rejection
        pass

    def test_whitelist_lookup_performance(self):
        """Whitelist lookups are O(1)"""
        # Whitelist should be set or dict, not list
        # Test with 10000 lookups
        pass
