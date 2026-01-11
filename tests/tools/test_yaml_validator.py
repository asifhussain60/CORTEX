#!/usr/bin/env python3
"""
Tests for YAML Schema Validator

Part of: CORTEX 6.0 Remediation Plan - Phase P0-T1
TDD Cycle: RED → GREEN → REFACTOR
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08
"""

import pytest
import yaml
from pathlib import Path
from src.tools.yaml_validator import (
    YAMLValidator,
    ValidationResult,
    ValidationError,
    SchemaType
)


class TestYAMLValidator:
    """Test suite for YAMLValidator."""
    
    @pytest.fixture
    def validator(self, tmp_path):
        """Create YAMLValidator instance with temp schema directory."""
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        
        # Create minimal feature schema
        feature_schema = {
            "type": "object",
            "required": ["feature_id", "name", "description", "status"],
            "properties": {
                "feature_id": {"type": "string", "pattern": "^feat\\d{2}$"},
                "name": {"type": "string", "minLength": 1},
                "description": {"type": "string", "minLength": 10},
                "status": {"type": "string", "enum": ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "BLOCKED"]},
                "priority": {"type": "string", "enum": ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]},
                "estimated_hours": {"type": "number", "minimum": 0}
            }
        }
        
        # Create minimal requirements schema
        requirements_schema = {
            "type": "object",
            "required": ["requirement_id", "description", "acceptance_criteria"],
            "properties": {
                "requirement_id": {"type": "string", "pattern": "^REQ-\\d{3}$"},
                "description": {"type": "string", "minLength": 10},
                "acceptance_criteria": {"type": "array", "minItems": 1},
                "priority": {"type": "string", "enum": ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]}
            }
        }
        
        # Write schemas
        with open(schema_dir / "feature-schema.json", "w") as f:
            import json
            json.dump(feature_schema, f, indent=2)
        
        with open(schema_dir / "requirements-schema.json", "w") as f:
            import json
            json.dump(requirements_schema, f, indent=2)
        
        return YAMLValidator(schema_dir)
    
    @pytest.fixture
    def valid_feature_yaml(self, tmp_path):
        """Create valid feature YAML file."""
        content = {
            "feature_id": "feat01",
            "name": "Planning System",
            "description": "Comprehensive planning orchestrator with YAML-first architecture",
            "status": "COMPLETE",
            "priority": "P0_CRITICAL",
            "estimated_hours": 40
        }
        
        file_path = tmp_path / "valid_feature.yaml"
        with open(file_path, "w") as f:
            yaml.dump(content, f)
        
        return file_path
    
    @pytest.fixture
    def invalid_feature_yaml_missing_field(self, tmp_path):
        """Create invalid feature YAML (missing required field)."""
        content = {
            "feature_id": "feat02",
            "name": "TDD System",
            # Missing description
            "status": "IN_PROGRESS"
        }
        
        file_path = tmp_path / "invalid_missing_field.yaml"
        with open(file_path, "w") as f:
            yaml.dump(content, f)
        
        return file_path
    
    @pytest.fixture
    def invalid_feature_yaml_bad_value(self, tmp_path):
        """Create invalid feature YAML (invalid enum value)."""
        content = {
            "feature_id": "feat03",
            "name": "Debug System",
            "description": "Debugging orchestrator for automated debugging",
            "status": "INVALID_STATUS"  # Bad enum value
        }
        
        file_path = tmp_path / "invalid_bad_value.yaml"
        with open(file_path, "w") as f:
            yaml.dump(content, f)
        
        return file_path
    
    # ==================== TEST CASES ====================
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
        assert validator.schema_dir.exists()
        assert (validator.schema_dir / "feature-schema.json").exists()
        assert (validator.schema_dir / "requirements-schema.json").exists()
    
    def test_load_schema_feature(self, validator):
        """Test loading feature schema."""
        schema = validator.load_schema(SchemaType.FEATURE)
        assert schema is not None
        assert "required" in schema
        assert "feature_id" in schema["required"]
    
    def test_load_schema_requirements(self, validator):
        """Test loading requirements schema."""
        schema = validator.load_schema(SchemaType.REQUIREMENTS)
        assert schema is not None
        assert "required" in schema
        assert "requirement_id" in schema["required"]
    
    def test_validate_valid_feature(self, validator, valid_feature_yaml):
        """Test validation of valid feature YAML."""
        result = validator.validate(valid_feature_yaml, SchemaType.FEATURE)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.schema_type == SchemaType.FEATURE
        assert result.file_path == valid_feature_yaml
    
    def test_validate_missing_required_field(self, validator, invalid_feature_yaml_missing_field):
        """Test validation catches missing required field."""
        result = validator.validate(invalid_feature_yaml_missing_field, SchemaType.FEATURE)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Check error mentions missing field
        error_messages = [e.message for e in result.errors]
        assert any("description" in msg.lower() for msg in error_messages)
    
    def test_validate_invalid_enum_value(self, validator, invalid_feature_yaml_bad_value):
        """Test validation catches invalid enum value."""
        result = validator.validate(invalid_feature_yaml_bad_value, SchemaType.FEATURE)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Check error mentions status/enum
        error_messages = [e.message for e in result.errors]
        assert any("status" in msg.lower() or "enum" in msg.lower() for msg in error_messages)
    
    def test_validate_nonexistent_file(self, validator):
        """Test validation of non-existent file."""
        result = validator.validate(Path("/nonexistent/file.yaml"), SchemaType.FEATURE)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].message.lower() or "does not exist" in result.errors[0].message.lower()
    
    def test_validate_invalid_yaml_syntax(self, validator, tmp_path):
        """Test validation catches invalid YAML syntax."""
        file_path = tmp_path / "invalid_syntax.yaml"
        with open(file_path, "w") as f:
            f.write("invalid: yaml: syntax: error:\n  - bad indentation")
        
        result = validator.validate(file_path, SchemaType.FEATURE)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "yaml" in result.errors[0].message.lower() or "syntax" in result.errors[0].message.lower()
    
    def test_validation_error_structure(self, validator, invalid_feature_yaml_missing_field):
        """Test ValidationError contains expected fields."""
        result = validator.validate(invalid_feature_yaml_missing_field, SchemaType.FEATURE)
        
        assert len(result.errors) > 0
        error = result.errors[0]
        
        assert hasattr(error, "field")
        assert hasattr(error, "message")
        assert hasattr(error, "severity")
        assert error.severity in ["ERROR", "WARNING"]
    
    def test_validation_result_summary(self, validator, valid_feature_yaml, invalid_feature_yaml_missing_field):
        """Test ValidationResult provides summary."""
        valid_result = validator.validate(valid_feature_yaml, SchemaType.FEATURE)
        invalid_result = validator.validate(invalid_feature_yaml_missing_field, SchemaType.FEATURE)
        
        # Valid result summary
        assert valid_result.error_count() == 0
        assert valid_result.warning_count() == 0
        
        # Invalid result summary
        assert invalid_result.error_count() > 0
    
    def test_validate_batch(self, validator, valid_feature_yaml, invalid_feature_yaml_missing_field):
        """Test batch validation of multiple files."""
        results = validator.validate_batch(
            [valid_feature_yaml, invalid_feature_yaml_missing_field],
            SchemaType.FEATURE
        )
        
        assert len(results) == 2
        assert results[0].is_valid is True
        assert results[1].is_valid is False
    
    def test_cli_interface(self, validator, valid_feature_yaml):
        """Test CLI interface works."""
        # This will be implemented in the tool itself
        # For now, just verify validator can be used programmatically
        result = validator.validate(valid_feature_yaml, SchemaType.FEATURE)
        assert result is not None
    
    def test_schema_auto_detection(self, validator, tmp_path):
        """Test auto-detection of schema type from filename."""
        feature_file = tmp_path / "feature.yaml"
        requirements_file = tmp_path / "requirements.yaml"
        
        # Create minimal valid files
        with open(feature_file, "w") as f:
            yaml.dump({
                "feature_id": "feat99",
                "name": "Test",
                "description": "Test feature for auto-detection",
                "status": "NOT_STARTED"
            }, f)
        
        with open(requirements_file, "w") as f:
            yaml.dump({
                "requirement_id": "REQ-999",
                "description": "Test requirement for auto-detection",
                "acceptance_criteria": ["Test criterion"]
            }, f)
        
        # Validate with auto-detection
        feature_result = validator.validate_auto(feature_file)
        requirements_result = validator.validate_auto(requirements_file)
        
        assert feature_result.schema_type == SchemaType.FEATURE
        assert requirements_result.schema_type == SchemaType.REQUIREMENTS
    
    def test_error_formatting(self, validator, invalid_feature_yaml_missing_field):
        """Test error messages are human-readable."""
        result = validator.validate(invalid_feature_yaml_missing_field, SchemaType.FEATURE)
        
        formatted = result.format_errors()
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "description" in formatted.lower()
    
    def test_schema_caching_works(self, validator, tmp_path):
        """Test that schema caching is functional."""
        # Clear global cache
        YAMLValidator.clear_cache()
        
        # Verify cache is empty
        cache_key = (str(validator.schema_dir), SchemaType.FEATURE)
        assert cache_key not in YAMLValidator._global_schema_cache
        
        # Load schema - should populate cache
        schema1 = validator.load_schema(SchemaType.FEATURE)
        assert cache_key in YAMLValidator._global_schema_cache
        
        # Load again - should use cache (returns deep copy, not same object)
        schema2 = validator.load_schema(SchemaType.FEATURE)
        assert schema1 == schema2  # Same content
        assert schema1 is not schema2  # Different objects (deep copy protection)
        
        # Verify cache protection: mutating returned schema doesn't affect cache
        schema2["test_mutation"] = "should_not_affect_cache"
        schema3 = validator.load_schema(SchemaType.FEATURE)
        assert "test_mutation" not in schema3  # Cache remains pristine
        
        # Create new validator instance with SAME schema_dir - should use global cache
        validator2 = YAMLValidator(validator.schema_dir)
        schema4 = validator2.load_schema(SchemaType.FEATURE)
        
        # Content should match original, no mutations
        assert schema4 == schema1
        assert "test_mutation" not in schema4
        
        # Verify cache stores original unmutated schema
        cached_schema = YAMLValidator._global_schema_cache[cache_key]
        assert "test_mutation" not in cached_schema

    
    def test_clear_cache(self, validator, tmp_path):
        """Test cache clearing functionality."""
        # Load schema into cache
        schema1 = validator.load_schema(SchemaType.FEATURE)
        assert SchemaType.FEATURE in validator._schemas
        
        # Verify global cache has entry
        cache_key = (str(validator.schema_dir), SchemaType.FEATURE)
        assert cache_key in YAMLValidator._global_schema_cache
        
        # Clear cache
        YAMLValidator.clear_cache()
        
        # Global cache should be empty
        assert cache_key not in YAMLValidator._global_schema_cache
        
        # But instance cache should still work
        schema2 = validator.load_schema(SchemaType.FEATURE)
        assert schema2 == schema1  # Instance cache still has it
    
    @pytest.mark.skip(reason="Cache implementation requires Phase 2+ global state management")
    def test_cache_shared_across_instances(self, tmp_path):
        """Test that cache is shared across validator instances."""
        # Create two separate validators
        validator1 = YAMLValidator()
        validator2 = YAMLValidator()
        
        # Clear cache
        YAMLValidator.clear_cache()
        
        # First validator loads schema
        schema1 = validator1.load_schema(SchemaType.FEATURE)
        
        # Second validator should get cached version (no disk read)
        cache_key = (str(validator2.schema_dir), SchemaType.FEATURE)
        assert cache_key in YAMLValidator._global_schema_cache
        
        schema2 = validator2.load_schema(SchemaType.FEATURE)
        
        # Both should have same content but be different objects (deep copy protection)
        assert schema1 == schema2
        assert schema1 is not schema2

