"""
AC-FIX-004-01: Prompt Injection Prevention Module

Provides sanitization and validation to prevent prompt injection attacks:
1. YAML-safe escaping for template values
2. Whitelist validation for operation names
3. Whitelist validation for AC-IDs
4. Template variable validation
5. Input length and encoding validation

FINDING-004 (HIGH): Insufficient template input validation allows injection attacks
CORE-006: Security testing framework compliance
"""

import re
import unicodedata
from typing import Dict, Set, Optional, List, Any
from dataclasses import dataclass

from src.core.result import Result, Ok, Err


# =============================================================================
# WHITELISTS
# =============================================================================

VALID_OPERATION_NAMES = {
    'create_conversation',
    'execute_turn',
    'rollback_state',
    'validate_governance',
    'apply_fix',
    'audit_log',
    'query_domain_brain',
    'check_tier_access',
    'enforce_governance',
}

VALID_AC_IDS = {
    'AC-FIX-001-01',
    'AC-FIX-002-01',
    'AC-FIX-003-01',
    'AC-FIX-004-01',
    'AC-FIX-005-01',
    'AC-FIX-006-01',
    'AC-DOC-007-01',
    'AC-MINOR-008-01',
}

# Maximum input lengths to prevent DoS
MAX_OPERATION_NAME_LENGTH = 50
MAX_AC_ID_LENGTH = 15
MAX_TEMPLATE_INPUT_LENGTH = 10000
MAX_VARIABLE_NAME_LENGTH = 100


# =============================================================================
# YAML SAFE ESCAPING
# =============================================================================

class YAMLSanitizer:
    """Provides YAML-safe escaping for template values."""
    
    # YAML special characters that need escaping
    YAML_SPECIAL_CHARS = {
        '"': '\\"',
        "'": "\\'",
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\\': '\\\\',
    }
    
    YAML_NEEDS_QUOTING = r'[&*|><%@`{}\[\]:]'
    
    @staticmethod
    def sanitize_for_yaml(value: str) -> str:
        """
        Escape value to be safe for YAML interpolation.
        
        Args:
            value: String value to sanitize
            
        Returns:
            YAML-safe escaped string
        """
        if not isinstance(value, str):
            return str(value)
        
        # If value contains special YAML characters, quote it
        if re.search(YAMLSanitizer.YAML_NEEDS_QUOTING, value):
            # Use double quotes and escape them
            escaped = value.replace('\\', '\\\\')  # Escape backslashes first
            escaped = escaped.replace('"', '\\"')
            return f'"{escaped}"'
        
        return value


# =============================================================================
# OPERATION NAME VALIDATION
# =============================================================================

class OperationNameValidator:
    """Validates operation names against whitelist."""
    
    @staticmethod
    def validate(operation_name: str) -> Result:
        """
        Validate that operation name is in approved whitelist.
        
        Args:
            operation_name: Operation name to validate
            
        Returns:
            Result: Ok if valid, Err with message if invalid
        """
        # Check length
        if len(operation_name) > MAX_OPERATION_NAME_LENGTH:
            return Err(f"Operation name exceeds max length {MAX_OPERATION_NAME_LENGTH}")
        
        # Check whitelist (case-sensitive)
        if operation_name not in VALID_OPERATION_NAMES:
            return Err(f"Operation '{operation_name}' not in approved whitelist")
        
        return Ok(operation_name)
    
    @staticmethod
    def get_whitelist() -> Set[str]:
        """Get the operation name whitelist."""
        return VALID_OPERATION_NAMES.copy()


# =============================================================================
# AC-ID VALIDATION
# =============================================================================

class ACIDValidator:
    """Validates AC-IDs against whitelist and format requirements."""
    
    # AC-ID format: AC-{TYPE}-{NUM}-{SUB}
    # Example: AC-FIX-001-01
    AC_ID_PATTERN = re.compile(r'^AC-[A-Z]+-\d{3}-\d{2}$')
    
    @staticmethod
    def validate(ac_id: str) -> Result:
        """
        Validate that AC-ID is properly formatted and in whitelist.
        
        Args:
            ac_id: AC-ID to validate
            
        Returns:
            Result: Ok if valid, Err with message if invalid
        """
        # Check length
        if len(ac_id) > MAX_AC_ID_LENGTH:
            return Err(f"AC-ID exceeds max length {MAX_AC_ID_LENGTH}")
        
        # Check format
        if not ACIDValidator.AC_ID_PATTERN.match(ac_id):
            return Err(f"AC-ID '{ac_id}' does not match format AC-TYPE-NUM-SUB")
        
        # Check whitelist
        if ac_id not in VALID_AC_IDS:
            return Err(f"AC-ID '{ac_id}' not in approved whitelist")
        
        return Ok(ac_id)
    
    @staticmethod
    def get_whitelist() -> Set[str]:
        """Get the AC-ID whitelist."""
        return VALID_AC_IDS.copy()


# =============================================================================
# TEMPLATE VARIABLE VALIDATION
# =============================================================================

class TemplateVariableValidator:
    """Validates template variables for safe substitution."""
    
    @staticmethod
    def validate_declared_variables(template: str, declared_vars: Set[str]) -> Result:
        """
        Validate that all variables in template are declared.
        
        Args:
            template: Template string with {variable} placeholders
            declared_vars: Set of declared variable names
            
        Returns:
            Result: Ok if valid, Err if undeclared variables found
        """
        # Find all {variable} patterns
        pattern = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}')
        found_vars = set(pattern.findall(template))
        
        undeclared = found_vars - declared_vars
        if undeclared:
            return Err(f"Undeclared template variables: {', '.join(sorted(undeclared))}")
        
        return Ok(None)
    
    @staticmethod
    def validate_variable_types(values: Dict[str, Any], expected_types: Dict[str, type]) -> Result:
        """
        Validate that variable values match expected types.
        
        Args:
            values: Dictionary of variable values
            expected_types: Dictionary mapping variable names to expected types
            
        Returns:
            Result: Ok if all valid, Err if type mismatch
        """
        for var_name, expected_type in expected_types.items():
            if var_name in values:
                value = values[var_name]
                if not isinstance(value, expected_type):
                    return Err(
                        f"Variable '{var_name}': expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        return Ok(None)
    
    @staticmethod
    def validate_variable_lengths(values: Dict[str, str], max_lengths: Dict[str, int]) -> Result:
        """
        Validate that variable values don't exceed maximum lengths.
        
        Args:
            values: Dictionary of variable values
            max_lengths: Dictionary mapping variable names to max lengths
            
        Returns:
            Result: Ok if valid, Err if length exceeded
        """
        for var_name, max_len in max_lengths.items():
            if var_name in values:
                value = values[var_name]
                if isinstance(value, str) and len(value) > max_len:
                    return Err(
                        f"Variable '{var_name}' exceeds max length {max_len} "
                        f"(current: {len(value)})"
                    )
        
        return Ok(None)


# =============================================================================
# GENERAL INPUT SANITIZATION
# =============================================================================

class InputSanitizer:
    """Provides general input sanitization and validation."""
    
    # Dangerous patterns that might indicate injection attempts
    INJECTION_PATTERNS = [
        r'[;&|`$\(\)\[\]]',  # Shell metacharacters
        r'[\'"].*(?:;|&&|\|\||`).*[\'"]',  # Quoted commands with operators
        r'\$\{.*\}',  # Variable expansion
        r'__.*__',  # Dunder methods
    ]
    
    @staticmethod
    def sanitize_length(value: str, max_length: int = MAX_TEMPLATE_INPUT_LENGTH) -> Result:
        """
        Validate that input doesn't exceed maximum length.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Result: Ok if valid, Err if too long
        """
        if len(value) > max_length:
            return Err(f"Input exceeds max length {max_length} (current: {len(value)})")
        
        return Ok(value)
    
    @staticmethod
    def sanitize_encoding(value: str) -> str:
        """
        Sanitize by removing or escaping problematic encodings.
        
        Args:
            value: Input string
            
        Returns:
            Sanitized string
        """
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize Unicode (NFC form)
        value = unicodedata.normalize('NFC', value)
        
        # Remove bidirectional override characters
        bidi_chars = ['\u202E', '\u202D', '\u202C', '\u2066', '\u2067', '\u2068', '\u2069']
        for char in bidi_chars:
            value = value.replace(char, '')
        
        return value
    
    @staticmethod
    def check_for_injection_patterns(value: str) -> List[str]:
        """
        Check if value contains known injection patterns.
        
        Args:
            value: Input string
            
        Returns:
            List of patterns found (empty if safe)
        """
        found_patterns = []
        for pattern in InputSanitizer.INJECTION_PATTERNS:
            if re.search(pattern, value):
                found_patterns.append(pattern)
        
        return found_patterns
    
    @staticmethod
    def remove_bidirectional_overrides(value: str) -> str:
        """Remove bidirectional override characters."""
        bidi_chars = ['\u202E', '\u202D', '\u202C', '\u2066', '\u2067', '\u2068', '\u2069']
        for char in bidi_chars:
            value = value.replace(char, '')
        return value
    
    @staticmethod
    def remove_template_expansion_markers(value: str) -> str:
        """Remove/escape template expansion markers like {{ }}."""
        # Replace {{ with escaped version or empty
        value = value.replace('{{', '')
        value = value.replace('}}', '')
        return value


# =============================================================================
# PATH TRAVERSAL PREVENTION
# =============================================================================

class PathTraversalValidator:
    """Validates that values don't contain path traversal attempts."""
    
    DANGEROUS_PATTERNS = [
        r'\.\.',  # Parent directory reference
        r'~',     # Home directory
        r'/',     # Absolute paths
        r'\\',    # Windows paths
    ]
    
    @staticmethod
    def validate(path_value: str) -> Result:
        """
        Validate that value doesn't contain path traversal attempts.
        
        Args:
            path_value: Value that might be used in a path context
            
        Returns:
            Result: Ok if safe, Err if dangerous pattern found
        """
        for pattern in PathTraversalValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, path_value):
                return Err(f"Path traversal pattern detected: {pattern}")
        
        return Ok(path_value)


# =============================================================================
# COMPREHENSIVE SANITIZATION PIPELINE
# =============================================================================

class PromptInjectionSanitizer:
    """
    Comprehensive prompt injection prevention using multiple validation layers.
    Implements defense-in-depth approach.
    """
    
    @staticmethod
    def sanitize_operation_name(value: str) -> Result:
        """
        Full sanitization pipeline for operation names.
        
        Args:
            value: Operation name to sanitize
            
        Returns:
            Result: Sanitized value or error
        """
        # Length check
        result = InputSanitizer.sanitize_length(value, MAX_OPERATION_NAME_LENGTH)
        if result.is_err():
            return result
        
        # Encoding sanitization
        value = InputSanitizer.sanitize_encoding(value)
        
        # Whitelist validation
        return OperationNameValidator.validate(value)
    
    @staticmethod
    def sanitize_ac_id(value: str) -> Result:
        """
        Full sanitization pipeline for AC-IDs.
        
        Args:
            value: AC-ID to sanitize
            
        Returns:
            Result: Sanitized value or error
        """
        # Length check
        result = InputSanitizer.sanitize_length(value, MAX_AC_ID_LENGTH)
        if result.is_err():
            return result
        
        # Encoding sanitization
        value = InputSanitizer.sanitize_encoding(value)
        
        # Remove template expansion markers
        value = InputSanitizer.remove_template_expansion_markers(value)
        
        # Whitelist and format validation
        return ACIDValidator.validate(value)
    
    @staticmethod
    def sanitize_for_yaml_template(value: str) -> Result:
        """
        Full sanitization pipeline for YAML template values.
        
        Args:
            value: Value to be used in YAML template
            
        Returns:
            Result: Sanitized and escaped value or error
        """
        # Length check
        result = InputSanitizer.sanitize_length(value)
        if result.is_err():
            return result
        
        # Encoding sanitization
        value = InputSanitizer.sanitize_encoding(value)
        
        # Apply YAML escaping
        escaped = YAMLSanitizer.sanitize_for_yaml(value)
        
        return Ok(escaped)
