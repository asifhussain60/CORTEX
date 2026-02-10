"""
Tests for Environment Validation - Phase 76 Stage 3 Task 3

Tests environment variable validation including types, ranges, and custom validators.

Authority: phase-76-production-foundation-trilogy.yaml S3.T3
AC-ID: AC-PHASE76-S3-003
"""

import pytest
import os
from pathlib import Path
import tempfile

from cortex.secrets.environment_validation import (
    EnvironmentValidator,
    validate_secrets_environment,
)
from cortex.secrets.errors import SecretsError


# ============================================================================
# STRING VALIDATION TESTS
# ============================================================================

class TestStringValidation:
    """Tests for string type validation"""
    
    def test_validate_string_default(self):
        """Test string validation with default options."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_STRING", var_type="string")
        
        # Mock environment
        os.environ["TEST_STRING"] = "test_value"
        
        result = validator.validate_var("TEST_STRING")
        assert result["valid"] is True
        assert result["value"] == "test_value"
    
    def test_validate_string_min_length(self):
        """Test string with minimum length."""
        validator = EnvironmentValidator()
        validator.add_schema("MIN_STRING", var_type="string", min_length=5)
        
        # Too short
        os.environ["MIN_STRING"] = "hi"
        result = validator.validate_var("MIN_STRING")
        assert result["valid"] is False
        
        # Correct length
        os.environ["MIN_STRING"] = "hello"
        result = validator.validate_var("MIN_STRING")
        assert result["valid"] is True
    
    def test_validate_string_max_length(self):
        """Test string with maximum length."""
        validator = EnvironmentValidator()
        validator.add_schema("MAX_STRING", var_type="string", max_length=5)
        
        # Too long
        os.environ["MAX_STRING"] = "toolong"
        result = validator.validate_var("MAX_STRING")
        assert result["valid"] is False
        
        # Correct length
        os.environ["MAX_STRING"] = "short"
        result = validator.validate_var("MAX_STRING")
        assert result["valid"] is True
    
    def test_validate_string_pattern(self):
        """Test string with regex pattern."""
        validator = EnvironmentValidator()
        validator.add_schema("PATTERN_STRING", var_type="string", pattern=r"^\d{3}-\d{2}-\d{4}$")
        
        # Invalid pattern
        os.environ["PATTERN_STRING"] = "not-a-number"
        result = validator.validate_var("PATTERN_STRING")
        assert result["valid"] is False
        
        # Valid pattern
        os.environ["PATTERN_STRING"] = "123-45-6789"
        result = validator.validate_var("PATTERN_STRING")
        assert result["valid"] is True


# ============================================================================
# INTEGER VALIDATION TESTS
# ============================================================================

class TestIntegerValidation:
    """Tests for integer type validation"""
    
    def test_validate_int_basic(self):
        """Test basic integer validation."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_INT", var_type="int")
        
        os.environ["TEST_INT"] = "42"
        result = validator.validate_var("TEST_INT")
        assert result["valid"] is True
        assert result["value"] == 42
    
    def test_validate_int_invalid(self):
        """Test invalid integer."""
        validator = EnvironmentValidator()
        validator.add_schema("BAD_INT", var_type="int")
        
        os.environ["BAD_INT"] = "not_a_number"
        result = validator.validate_var("BAD_INT")
        assert result["valid"] is False
    
    def test_validate_int_min(self):
        """Test integer with minimum value."""
        validator = EnvironmentValidator()
        validator.add_schema("MIN_INT", var_type="int", min=10)
        
        # Too low
        os.environ["MIN_INT"] = "5"
        result = validator.validate_var("MIN_INT")
        assert result["valid"] is False
        
        # Correct
        os.environ["MIN_INT"] = "15"
        result = validator.validate_var("MIN_INT")
        assert result["valid"] is True
    
    def test_validate_int_max(self):
        """Test integer with maximum value."""
        validator = EnvironmentValidator()
        validator.add_schema("MAX_INT", var_type="int", max=100)
        
        # Too high
        os.environ["MAX_INT"] = "150"
        result = validator.validate_var("MAX_INT")
        assert result["valid"] is False
        
        # Correct
        os.environ["MAX_INT"] = "50"
        result = validator.validate_var("MAX_INT")
        assert result["valid"] is True
    
    def test_validate_int_range(self):
        """Test integer with both min and max."""
        validator = EnvironmentValidator()
        validator.add_schema("RANGE_INT", var_type="int", min=1, max=10)
        
        # Below min
        os.environ["RANGE_INT"] = "0"
        assert validator.validate_var("RANGE_INT")["valid"] is False
        
        # Within range
        os.environ["RANGE_INT"] = "5"
        assert validator.validate_var("RANGE_INT")["valid"] is True
        
        # Above max
        os.environ["RANGE_INT"] = "11"
        assert validator.validate_var("RANGE_INT")["valid"] is False


# ============================================================================
# FLOAT VALIDATION TESTS
# ============================================================================

class TestFloatValidation:
    """Tests for float type validation"""
    
    def test_validate_float_basic(self):
        """Test basic float validation."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_FLOAT", var_type="float")
        
        os.environ["TEST_FLOAT"] = "3.14"
        result = validator.validate_var("TEST_FLOAT")
        assert result["valid"] is True
        assert result["value"] == 3.14
    
    def test_validate_float_range(self):
        """Test float with range."""
        validator = EnvironmentValidator()
        validator.add_schema("RANGE_FLOAT", var_type="float", min=0.0, max=1.0)
        
        # Within range
        os.environ["RANGE_FLOAT"] = "0.5"
        assert validator.validate_var("RANGE_FLOAT")["valid"] is True
        
        # Out of range
        os.environ["RANGE_FLOAT"] = "2.0"
        assert validator.validate_var("RANGE_FLOAT")["valid"] is False


# ============================================================================
# BOOLEAN VALIDATION TESTS
# ============================================================================

class TestBooleanValidation:
    """Tests for boolean type validation"""
    
    def test_validate_bool_true_values(self):
        """Test true boolean values."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_BOOL", var_type="bool")
        
        for value in ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]:
            os.environ["TEST_BOOL"] = value
            result = validator.validate_var("TEST_BOOL")
            assert result["valid"] is True
            assert result["value"] is True
    
    def test_validate_bool_false_values(self):
        """Test false boolean values."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_BOOL", var_type="bool")
        
        for value in ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]:
            os.environ["TEST_BOOL"] = value
            result = validator.validate_var("TEST_BOOL")
            # False values should validate
            assert result["valid"] is True
            assert result["value"] is False


# ============================================================================
# URL VALIDATION TESTS
# ============================================================================

class TestURLValidation:
    """Tests for URL type validation"""
    
    def test_validate_url_valid(self):
        """Test valid URLs."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_URL", var_type="url")
        
        valid_urls = [
            "http://example.com",
            "https://api.github.com",
            "https://example.com:8080/path",
        ]
        
        for url in valid_urls:
            os.environ["TEST_URL"] = url
            result = validator.validate_var("TEST_URL")
            assert result["valid"] is True
    
    def test_validate_url_invalid_no_scheme(self):
        """Test URL without scheme."""
        validator = EnvironmentValidator()
        validator.add_schema("BAD_URL", var_type="url")
        
        os.environ["BAD_URL"] = "example.com"
        result = validator.validate_var("BAD_URL")
        assert result["valid"] is False
    
    def test_validate_url_invalid_no_netloc(self):
        """Test URL without netloc."""
        validator = EnvironmentValidator()
        validator.add_schema("BAD_URL", var_type="url")
        
        os.environ["BAD_URL"] = "http://"
        result = validator.validate_var("BAD_URL")
        assert result["valid"] is False


# ============================================================================
# PORT VALIDATION TESTS
# ============================================================================

class TestPortValidation:
    """Tests for port type validation"""
    
    def test_validate_port_valid(self):
        """Test valid ports."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_PORT", var_type="port")
        
        valid_ports = ["1", "80", "443", "8080", "65535"]
        
        for port in valid_ports:
            os.environ["TEST_PORT"] = port
            result = validator.validate_var("TEST_PORT")
            assert result["valid"] is True
    
    def test_validate_port_too_low(self):
        """Test port below range."""
        validator = EnvironmentValidator()
        validator.add_schema("LOW_PORT", var_type="port")
        
        os.environ["LOW_PORT"] = "0"
        result = validator.validate_var("LOW_PORT")
        assert result["valid"] is False
    
    def test_validate_port_too_high(self):
        """Test port above range."""
        validator = EnvironmentValidator()
        validator.add_schema("HIGH_PORT", var_type="port")
        
        os.environ["HIGH_PORT"] = "65536"
        result = validator.validate_var("HIGH_PORT")
        assert result["valid"] is False
    
    def test_validate_port_not_number(self):
        """Test port that's not a number."""
        validator = EnvironmentValidator()
        validator.add_schema("BAD_PORT", var_type="port")
        
        os.environ["BAD_PORT"] = "not_a_port"
        result = validator.validate_var("BAD_PORT")
        assert result["valid"] is False


# ============================================================================
# PATH VALIDATION TESTS
# ============================================================================

class TestPathValidation:
    """Tests for path type validation"""
    
    def test_validate_path_basic(self):
        """Test basic path validation."""
        validator = EnvironmentValidator()
        validator.add_schema("TEST_PATH", var_type="path")
        
        os.environ["TEST_PATH"] = "/tmp/test"
        result = validator.validate_var("TEST_PATH")
        assert result["valid"] is True
    
    def test_validate_path_expanduser(self):
        """Test path with ~ expansion."""
        validator = EnvironmentValidator()
        validator.add_schema("HOME_PATH", var_type="path")
        
        os.environ["HOME_PATH"] = "~/test"
        result = validator.validate_var("HOME_PATH")
        assert result["valid"] is True
        assert "~" not in result["value"]  # Should be expanded
    
    def test_validate_path_must_exist(self):
        """Test path that must exist."""
        validator = EnvironmentValidator()
        validator.add_schema("EXIST_PATH", var_type="path", must_exist=True)
        
        # Non-existent path
        os.environ["EXIST_PATH"] = "/nonexistent/path/12345"
        result = validator.validate_var("EXIST_PATH")
        assert result["valid"] is False
        
        # Existing path
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["EXIST_PATH"] = tmpdir
            result = validator.validate_var("EXIST_PATH")
            assert result["valid"] is True
    
    def test_validate_path_must_be_file(self):
        """Test path that must be a file."""
        validator = EnvironmentValidator()
        validator.add_schema("FILE_PATH", var_type="path", must_be_file=True)
        
        with tempfile.NamedTemporaryFile() as f:
            os.environ["FILE_PATH"] = f.name
            result = validator.validate_var("FILE_PATH")
            assert result["valid"] is True
    
    def test_validate_path_must_be_dir(self):
        """Test path that must be a directory."""
        validator = EnvironmentValidator()
        validator.add_schema("DIR_PATH", var_type="path", must_be_dir=True)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["DIR_PATH"] = tmpdir
            result = validator.validate_var("DIR_PATH")
            assert result["valid"] is True


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

class TestSchemaValidation:
    """Tests for schema-based validation"""
    
    def test_validate_schema_all_valid(self):
        """Test validating all schema variables when valid."""
        validator = EnvironmentValidator()
        validator.add_schema("VAR1", var_type="string", required=True)
        validator.add_schema("VAR2", var_type="int", required=True, min=0)
        
        os.environ["VAR1"] = "test"
        os.environ["VAR2"] = "42"
        
        result = validator.validate_all()
        assert result["valid"] is True
        assert result["values"]["VAR1"] == "test"
        assert result["values"]["VAR2"] == 42
    
    def test_validate_schema_required_missing(self):
        """Test schema validation with missing required variable."""
        validator = EnvironmentValidator()
        validator.add_schema("REQUIRED", var_type="string", required=True)
        
        # Remove from environment
        os.environ.pop("REQUIRED", None)
        
        with pytest.raises(SecretsError):
            validator.validate_all()
    
    def test_validate_schema_optional_missing(self):
        """Test schema validation with missing optional variable."""
        validator = EnvironmentValidator()
        validator.add_schema("OPTIONAL", var_type="string", required=False, default="default_value")
        
        # Remove from environment
        os.environ.pop("OPTIONAL", None)
        
        result = validator.validate_all()
        assert result["valid"] is True
        assert result["values"]["OPTIONAL"] == "default_value"


# ============================================================================
# CUSTOM VALIDATOR TESTS
# ============================================================================

class TestCustomValidator:
    """Tests for custom validator functions"""
    
    def test_custom_validator_pass(self):
        """Test custom validator that passes."""
        def custom_check(value):
            return value.startswith("test_")
        
        validator = EnvironmentValidator()
        validator.add_schema("CUSTOM", var_type="string", validator=custom_check)
        
        os.environ["CUSTOM"] = "test_value"
        result = validator.validate_var("CUSTOM")
        assert result["valid"] is True
    
    def test_custom_validator_fail(self):
        """Test custom validator that fails."""
        def custom_check(value):
            return value.startswith("test_")
        
        validator = EnvironmentValidator()
        validator.add_schema("CUSTOM", var_type="string", validator=custom_check)
        
        os.environ["CUSTOM"] = "bad_value"
        result = validator.validate_var("CUSTOM")
        assert result["valid"] is False


# ============================================================================
# SECRETS ENVIRONMENT VALIDATION TESTS
# ============================================================================

class TestSecretsEnvironmentValidation:
    """Tests for validate_secrets_environment() function"""
    
    def test_validate_secrets_env_success(self, monkeypatch):
        """Test successful secrets environment validation."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", "0" * 32 + "a" * 32)
        
        result = validate_secrets_environment()
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_secrets_env_missing_key(self, monkeypatch):
        """Test validation fails without CORTEX_MASTER_KEY."""
        monkeypatch.delenv("CORTEX_MASTER_KEY", raising=False)
        
        with pytest.raises(SecretsError):
            validate_secrets_environment()
    
    def test_validate_secrets_env_weak_key(self, monkeypatch):
        """Test validation fails with weak master key."""
        monkeypatch.setenv("CORTEX_MASTER_KEY", "short")
        
        with pytest.raises(SecretsError):
            validate_secrets_environment()


# ============================================================================
# REQUIRED VARIABLES TESTS
# ============================================================================

class TestRequiredVariables:
    """Tests for required variables tracking"""
    
    def test_add_required(self):
        """Test adding required variables."""
        validator = EnvironmentValidator()
        validator.add_required("VAR1")
        validator.add_required("VAR2")
        
        assert "VAR1" in validator.required_vars
        assert "VAR2" in validator.required_vars
    
    def test_required_enforced_in_schema(self):
        """Test that schema required is enforced."""
        validator = EnvironmentValidator()
        validator.add_schema("REQ_VAR", var_type="string", required=True)
        
        os.environ.pop("REQ_VAR", None)
        
        with pytest.raises(SecretsError):
            validator.validate_all()
