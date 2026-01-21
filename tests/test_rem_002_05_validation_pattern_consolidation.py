"""
tests/test_rem_002_05_validation_pattern_consolidation.py

Tests for DUP-005: Validation pattern consolidation.

REMEDIATION-002-PHASE-C: Implements unified validators module.
"""

import unittest
from typing import Any, Dict, List, Optional


class TestValidatorDecorators(unittest.TestCase):
    """Tests for validator decorator pattern."""
    
    def test_required_validator_passes_with_value(self) -> None:
        """required validator should pass when value is present."""
        from cortex.common.validators import required
        
        @required("name")
        def process_data(name: str) -> str:
            return name
        
        result = process_data(name="test")
        self.assertEqual(result, "test")
    
    def test_required_validator_fails_without_value(self) -> None:
        """required validator should raise ValueError when value is missing."""
        from cortex.common.validators import required, ValidationError
        
        @required("name")
        def process_data(name: str = None) -> str:
            return name
        
        with self.assertRaises(ValidationError):
            process_data(name=None)
    
    def test_type_validator_passes_correct_type(self) -> None:
        """type_check validator should pass with correct type."""
        from cortex.common.validators import type_check
        
        @type_check("count", int)
        def process(count: int) -> int:
            return count * 2
        
        result = process(count=5)
        self.assertEqual(result, 10)
    
    def test_type_validator_fails_wrong_type(self) -> None:
        """type_check validator should raise TypeError on wrong type."""
        from cortex.common.validators import type_check, ValidationError
        
        @type_check("count", int)
        def process(count: int) -> int:
            return count * 2
        
        with self.assertRaises(ValidationError):
            process(count="not_an_int")
    
    def test_range_validator_passes_valid_range(self) -> None:
        """range_check validator should pass within range."""
        from cortex.common.validators import range_check
        
        @range_check("value", min_val=0, max_val=100)
        def process(value: int) -> int:
            return value
        
        result = process(value=50)
        self.assertEqual(result, 50)
    
    def test_range_validator_fails_below_min(self) -> None:
        """range_check validator should fail below min."""
        from cortex.common.validators import range_check, ValidationError
        
        @range_check("value", min_val=0, max_val=100)
        def process(value: int) -> int:
            return value
        
        with self.assertRaises(ValidationError):
            process(value=-5)
    
    def test_range_validator_fails_above_max(self) -> None:
        """range_check validator should fail above max."""
        from cortex.common.validators import range_check, ValidationError
        
        @range_check("value", min_val=0, max_val=100)
        def process(value: int) -> int:
            return value
        
        with self.assertRaises(ValidationError):
            process(value=150)


class TestPatternValidators(unittest.TestCase):
    """Tests for pattern-based validators."""
    
    def test_regex_validator_passes_matching_pattern(self) -> None:
        """regex_match validator should pass on matching pattern."""
        from cortex.common.validators import regex_match
        
        @regex_match("email", r"^[\w.-]+@[\w.-]+\.\w+$")
        def send_email(email: str) -> str:
            return email
        
        result = send_email(email="test@example.com")
        self.assertEqual(result, "test@example.com")
    
    def test_regex_validator_fails_non_matching(self) -> None:
        """regex_match validator should fail on non-matching pattern."""
        from cortex.common.validators import regex_match, ValidationError
        
        @regex_match("email", r"^[\w.-]+@[\w.-]+\.\w+$")
        def send_email(email: str) -> str:
            return email
        
        with self.assertRaises(ValidationError):
            send_email(email="not_an_email")


class TestSchemaValidation(unittest.TestCase):
    """Tests for schema-based validation."""
    
    def test_schema_validator_passes_valid_dict(self) -> None:
        """validate_schema should pass with valid schema."""
        from cortex.common.validators import validate_schema
        
        schema = {
            "name": str,
            "age": int,
        }
        
        data = {"name": "John", "age": 30}
        result = validate_schema(data, schema)
        self.assertTrue(result.is_valid)
    
    def test_schema_validator_fails_missing_field(self) -> None:
        """validate_schema should fail with missing required field."""
        from cortex.common.validators import validate_schema
        
        schema = {
            "name": str,
            "age": int,
        }
        
        data = {"name": "John"}  # Missing age
        result = validate_schema(data, schema)
        self.assertFalse(result.is_valid)
        self.assertIn("age", result.errors)
    
    def test_schema_validator_fails_wrong_type(self) -> None:
        """validate_schema should fail with wrong field type."""
        from cortex.common.validators import validate_schema
        
        schema = {
            "name": str,
            "age": int,
        }
        
        data = {"name": "John", "age": "thirty"}  # Wrong type
        result = validate_schema(data, schema)
        self.assertFalse(result.is_valid)
        self.assertIn("age", result.errors)


class TestValidatorChaining(unittest.TestCase):
    """Tests for composable validators."""
    
    def test_multiple_validators_all_pass(self) -> None:
        """Multiple validators should all be applied."""
        from cortex.common.validators import required, type_check, range_check
        
        @required("value")
        @type_check("value", int)
        @range_check("value", min_val=0, max_val=100)
        def process(value: int) -> int:
            return value
        
        result = process(value=50)
        self.assertEqual(result, 50)
    
    def test_multiple_validators_first_fails(self) -> None:
        """First failing validator should raise."""
        from cortex.common.validators import required, type_check, ValidationError
        
        @required("value")
        @type_check("value", int)
        def process(value: int = None) -> int:
            return value
        
        with self.assertRaises(ValidationError):
            process(value=None)


class TestValidationResult(unittest.TestCase):
    """Tests for ValidationResult class."""
    
    def test_validation_result_success(self) -> None:
        """ValidationResult should indicate success."""
        from cortex.common.validators import ValidationResult
        
        result = ValidationResult(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, {})
    
    def test_validation_result_with_errors(self) -> None:
        """ValidationResult should contain errors."""
        from cortex.common.validators import ValidationResult
        
        result = ValidationResult(
            is_valid=False,
            errors={"name": "Name is required"}
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors["name"], "Name is required")
    
    def test_validation_result_to_dict(self) -> None:
        """ValidationResult should convert to dict."""
        from cortex.common.validators import ValidationResult
        
        result = ValidationResult(
            is_valid=False,
            errors={"name": "Required"}
        )
        d = result.to_dict()
        self.assertEqual(d["is_valid"], False)
        self.assertEqual(d["errors"], {"name": "Required"})


if __name__ == "__main__":
    unittest.main()
