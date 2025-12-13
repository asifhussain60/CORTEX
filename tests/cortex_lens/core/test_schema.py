"""
Test suite for UniversalSchema
Tests schema definition, validation, serialization, and helper methods.
"""

import pytest
import json
from pathlib import Path

from src.cortex_lens.core.schema import UniversalSchema


# ========== Schema Definition Tests ==========

class TestSchemaDefinition:
    """Test schema structure and definitions."""
    
    def test_get_schema_returns_dict(self):
        """Test that get_schema returns a dictionary."""
        schema = UniversalSchema.get_schema()
        
        assert isinstance(schema, dict)
        assert len(schema) > 0
    
    def test_required_sections_defined(self):
        """Test that required sections are properly defined."""
        schema = UniversalSchema.get_schema()
        
        # Metadata and classification should be required
        assert "metadata" in schema
        assert schema["metadata"]["required"] is True
        assert "classification" in schema
        assert schema["classification"]["required"] is True
    
    def test_optional_sections_defined(self):
        """Test that optional sections exist."""
        schema = UniversalSchema.get_schema()
        
        optional_sections = ["architecture", "entities", "metrics", "security", "comments", "narrative"]
        
        for section in optional_sections:
            assert section in schema
            # Optional sections should have required=False or missing required key
            assert schema[section].get("required", False) is False
    
    def test_metadata_fields(self):
        """Test metadata section has required fields."""
        schema = UniversalSchema.get_schema()
        metadata_fields = schema["metadata"]["fields"]
        
        required_fields = ["repo_name", "repo_type", "scan_timestamp", "cortex_version"]
        
        for field in required_fields:
            assert field in metadata_fields
    
    def test_classification_fields(self):
        """Test classification section structure."""
        schema = UniversalSchema.get_schema()
        classification_fields = schema["classification"]["fields"]
        
        assert "primary_type" in classification_fields
        assert "confidence" in classification_fields
        assert "detected_patterns" in classification_fields


# ========== Empty Structure Tests ==========

class TestEmptyStructure:
    """Test empty schema structure creation."""
    
    def test_create_empty_returns_dict(self):
        """Test that create_empty returns a dictionary."""
        empty = UniversalSchema.create_empty()
        
        assert isinstance(empty, dict)
        assert len(empty) > 0
    
    def test_empty_has_required_sections(self):
        """Test empty structure has all required sections."""
        empty = UniversalSchema.create_empty()
        
        assert "metadata" in empty
        assert "classification" in empty
    
    def test_empty_metadata_structure(self):
        """Test metadata in empty structure."""
        empty = UniversalSchema.create_empty()
        metadata = empty["metadata"]
        
        assert "repo_name" in metadata
        assert metadata["repo_name"] == ""
        assert "repo_type" in metadata
        assert isinstance(metadata["repo_type"], list)
        assert "cortex_version" in metadata
        assert metadata["cortex_version"] == "1.0.0"
        assert "total_files" in metadata
        assert metadata["total_files"] == 0
    
    def test_empty_classification_structure(self):
        """Test classification in empty structure."""
        empty = UniversalSchema.create_empty()
        classification = empty["classification"]
        
        assert "primary_type" in classification
        assert classification["primary_type"] == "unknown"
        assert "confidence" in classification
        assert classification["confidence"] == 0.0
        assert "detected_patterns" in classification
        assert isinstance(classification["detected_patterns"], dict)
    
    def test_empty_entities_initialized(self):
        """Test entities section is properly initialized."""
        empty = UniversalSchema.create_empty()
        entities = empty["entities"]
        
        assert "api_endpoints" in entities
        assert isinstance(entities["api_endpoints"], list)
        assert len(entities["api_endpoints"]) == 0
        
        assert "database_tables" in entities
        assert "frontend_routes" in entities
        assert "classes" in entities
        assert "methods" in entities


# ========== Validation Tests ==========

class TestValidation:
    """Test schema validation logic."""
    
    def test_validate_empty_structure(self):
        """Test validation of empty structure."""
        empty = UniversalSchema.create_empty()
        is_valid, errors = UniversalSchema.validate(empty)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_metadata(self):
        """Test validation fails when metadata is missing."""
        data = {
            "classification": {
                "primary_type": "api_service",
                "confidence": 0.85,
                "detected_patterns": {}
            }
        }
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("metadata" in error.lower() for error in errors)
    
    def test_validate_missing_classification(self):
        """Test validation fails when classification is missing."""
        data = {
            "metadata": {
                "repo_name": "test",
                "repo_type": ["api_service"],
                "scan_timestamp": "2025-12-13T10:00:00",
                "cortex_version": "1.0.0"
            }
        }
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is False
        assert any("classification" in error.lower() for error in errors)
    
    def test_validate_missing_required_field(self):
        """Test validation fails when required field is missing."""
        data = {
            "metadata": {
                "repo_name": "test",
                # Missing repo_type
                "scan_timestamp": "2025-12-13T10:00:00",
                "cortex_version": "1.0.0"
            },
            "classification": {
                "primary_type": "api_service",
                "confidence": 0.85,
                "detected_patterns": {}
            }
        }
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is False
        assert any("repo_type" in error for error in errors)
    
    def test_validate_with_optional_sections(self):
        """Test validation passes with optional sections."""
        data = UniversalSchema.create_empty()
        data["metadata"]["repo_name"] = "test-repo"
        data["metadata"]["repo_type"] = ["api_service"]
        data["architecture"] = {"layers": [{"name": "API", "loc": 1000}]}
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_returns_tuple(self):
        """Test validation returns (bool, list) tuple."""
        empty = UniversalSchema.create_empty()
        result = UniversalSchema.validate(empty)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)


# ========== JSON Export/Import Tests ==========

class TestJSONSerialization:
    """Test JSON export and import functionality."""
    
    def test_to_json_creates_file(self, tmp_path):
        """Test that to_json creates a file."""
        data = UniversalSchema.create_empty()
        output_path = tmp_path / "output.json"
        
        UniversalSchema.to_json(data, output_path)
        
        assert output_path.exists()
        assert output_path.is_file()
    
    def test_to_json_valid_content(self, tmp_path):
        """Test that exported JSON is valid."""
        data = UniversalSchema.create_empty()
        data["metadata"]["repo_name"] = "test-repo"
        output_path = tmp_path / "output.json"
        
        UniversalSchema.to_json(data, output_path)
        
        # Read and parse JSON
        with output_path.open('r') as f:
            loaded = json.load(f)
        
        assert loaded["metadata"]["repo_name"] == "test-repo"
    
    def test_to_json_creates_parent_directory(self, tmp_path):
        """Test that parent directories are created."""
        output_path = tmp_path / "subdir" / "output.json"
        data = UniversalSchema.create_empty()
        
        UniversalSchema.to_json(data, output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()
    
    def test_to_json_with_custom_indent(self, tmp_path):
        """Test JSON export with custom indentation."""
        data = UniversalSchema.create_empty()
        output_path = tmp_path / "output.json"
        
        UniversalSchema.to_json(data, output_path, indent=4)
        
        content = output_path.read_text()
        # With indent=4, should have 4-space indentation
        assert "    " in content
    
    def test_from_json_loads_file(self, tmp_path):
        """Test that from_json loads a file."""
        data = UniversalSchema.create_empty()
        data["metadata"]["repo_name"] = "loaded-repo"
        output_path = tmp_path / "output.json"
        
        UniversalSchema.to_json(data, output_path)
        loaded = UniversalSchema.from_json(output_path)
        
        assert loaded["metadata"]["repo_name"] == "loaded-repo"
    
    def test_roundtrip_json(self, tmp_path):
        """Test export and import roundtrip."""
        original = UniversalSchema.create_empty()
        original["metadata"]["repo_name"] = "roundtrip-test"
        original["classification"]["primary_type"] = "api_service"
        original["classification"]["confidence"] = 0.92
        
        output_path = tmp_path / "roundtrip.json"
        
        # Export
        UniversalSchema.to_json(original, output_path)
        
        # Import
        loaded = UniversalSchema.from_json(output_path)
        
        # Verify
        assert loaded["metadata"]["repo_name"] == original["metadata"]["repo_name"]
        assert loaded["classification"]["primary_type"] == original["classification"]["primary_type"]
        assert loaded["classification"]["confidence"] == original["classification"]["confidence"]


# ========== Integration Tests ==========

class TestSchemaIntegration:
    """Test schema integration with real data."""
    
    def test_complete_valid_data(self):
        """Test validation of complete realistic data."""
        data = {
            "metadata": {
                "repo_name": "my-api",
                "repo_type": ["api_service"],
                "scan_timestamp": "2025-12-13T08:00:00",
                "cortex_version": "1.0.0",
                "languages": {"C#": 0.85, "JavaScript": 0.15},
                "total_files": 42,
                "total_loc": 5000
            },
            "classification": {
                "primary_type": "api_service",
                "confidence": 0.92,
                "detected_patterns": {
                    "has_controllers": True,
                    "has_api_routes": True
                }
            },
            "entities": {
                "api_endpoints": [
                    {"path": "/api/users", "method": "GET"},
                    {"path": "/api/users", "method": "POST"}
                ],
                "database_tables": [],
                "frontend_routes": [],
                "classes": [],
                "methods": []
            },
            "metrics": {
                "complexity": {"average": 5.2, "max": 15},
                "test_coverage": {"percentage": 78.5},
                "performance": {}
            }
        }
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_minimal_valid_data(self):
        """Test validation of minimal valid data."""
        data = {
            "metadata": {
                "repo_name": "minimal",
                "repo_type": ["console_app"],
                "scan_timestamp": "2025-12-13T08:00:00",
                "cortex_version": "1.0.0",
                "languages": {"C#": 1.0},
                "total_files": 5,
                "total_loc": 100
            },
            "classification": {
                "primary_type": "console_app",
                "confidence": 0.60,
                "detected_patterns": {}
            }
        }
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is True
    
    def test_schema_with_all_sections(self):
        """Test schema with all optional sections populated."""
        data = UniversalSchema.create_empty()
        data["metadata"]["repo_name"] = "full-repo"
        data["metadata"]["repo_type"] = ["fullstack_web"]
        data["metadata"]["scan_timestamp"] = "2025-12-13T08:00:00"
        
        # Populate all optional sections
        data["architecture"]["layers"] = [{"name": "API", "loc": 1000}]
        data["entities"]["api_endpoints"] = [{"path": "/api/test", "method": "GET"}]
        data["metrics"]["complexity"] = {"average": 4.5}
        data["security"]["vulnerabilities"] = []
        data["comments"]["extraction"] = []
        data["narrative"]["executive_summary"] = "Test summary"
        
        is_valid, errors = UniversalSchema.validate(data)
        
        assert is_valid is True
        assert len(errors) == 0
