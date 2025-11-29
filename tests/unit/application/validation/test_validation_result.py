"""
Tests for ValidationResult and ValidationError classes.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from src.application.validation.validation_result import ValidationResult, ValidationError


class TestValidationError:
    """Tests for ValidationError class."""
    
    def test_create_validation_error(self):
        """Test creating a validation error."""
        error = ValidationError(
            property_name="username",
            error_message="Username is required"
        )
        
        assert error.property_name == "username"
        assert error.error_message == "Username is required"
        assert error.attempted_value is None
        assert error.error_code is None
    
    def test_create_validation_error_with_all_fields(self):
        """Test creating a validation error with all fields."""
        error = ValidationError(
            property_name="age",
            error_message="Age must be positive",
            attempted_value=-5,
            error_code="NEGATIVE_AGE"
        )
        
        assert error.property_name == "age"
        assert error.error_message == "Age must be positive"
        assert error.attempted_value == -5
        assert error.error_code == "NEGATIVE_AGE"
    
    def test_validation_error_string_representation(self):
        """Test string representation of validation error."""
        error = ValidationError(
            property_name="email",
            error_message="Invalid email format"
        )
        
        assert str(error) == "email: Invalid email format"
    
    def test_validation_error_is_frozen(self):
        """Test that ValidationError is immutable."""
        error = ValidationError(
            property_name="test",
            error_message="test message"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            error.property_name = "modified"


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_create_empty_validation_result(self):
        """Test creating an empty validation result."""
        result = ValidationResult()
        
        assert result.is_valid is True
        assert result.is_invalid is False
        assert len(result.errors) == 0
    
    def test_validation_result_success(self):
        """Test creating a successful validation result."""
        result = ValidationResult.success()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_add_error_to_result(self):
        """Test adding an error to validation result."""
        result = ValidationResult()
        result.add_error("username", "Username is required")
        
        assert result.is_valid is False
        assert result.is_invalid is True
        assert len(result.errors) == 1
        assert result.errors[0].property_name == "username"
        assert result.errors[0].error_message == "Username is required"
    
    def test_add_multiple_errors(self):
        """Test adding multiple errors to validation result."""
        result = ValidationResult()
        result.add_error("username", "Username is required")
        result.add_error("email", "Email is invalid")
        result.add_error("age", "Age must be positive")
        
        assert result.is_invalid is True
        assert len(result.errors) == 3
    
    def test_add_error_with_all_fields(self):
        """Test adding error with attempted value and error code."""
        result = ValidationResult()
        result.add_error(
            property_name="age",
            error_message="Age must be positive",
            attempted_value=-5,
            error_code="NEGATIVE_AGE"
        )
        
        assert len(result.errors) == 1
        error = result.errors[0]
        assert error.attempted_value == -5
        assert error.error_code == "NEGATIVE_AGE"
    
    def test_get_errors_for_property(self):
        """Test getting errors for a specific property."""
        result = ValidationResult()
        result.add_error("username", "Username is required")
        result.add_error("email", "Email is invalid")
        result.add_error("email", "Email is already taken")
        
        email_errors = result.get_errors_for_property("email")
        assert len(email_errors) == 2
        assert all(e.property_name == "email" for e in email_errors)
    
    def test_get_errors_for_nonexistent_property(self):
        """Test getting errors for property with no errors."""
        result = ValidationResult()
        result.add_error("username", "Username is required")
        
        errors = result.get_errors_for_property("email")
        assert len(errors) == 0
    
    def test_validation_result_string_success(self):
        """Test string representation of successful validation."""
        result = ValidationResult()
        
        assert str(result) == "Validation succeeded"
    
    def test_validation_result_string_with_errors(self):
        """Test string representation with errors."""
        result = ValidationResult()
        result.add_error("username", "Username is required")
        result.add_error("email", "Email is invalid")
        
        result_str = str(result)
        assert "Validation failed" in result_str
        assert "username: Username is required" in result_str
        assert "email: Email is invalid" in result_str
    
    def test_validation_result_failure(self):
        """Test creating a failed validation result."""
        errors = [
            ValidationError("username", "Username is required"),
            ValidationError("email", "Email is invalid")
        ]
        
        result = ValidationResult.failure(errors)
        
        assert result.is_invalid is True
        assert len(result.errors) == 2
