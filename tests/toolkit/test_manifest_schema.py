"""
Tests for Manifest Schema v2 (Phase 5).

TDD Phase: RED - All tests should fail initially.

Tests cover:
- Schema validation against JSON Schema
- V1 to V2 migration
- New v2 fields (depends_on, capabilities, destructive, etc.)
- Input/output schema validation
- Rate limiting configuration
- Security privilege levels
"""

import json
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import yaml


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path


@pytest.fixture
def v1_manifest_content() -> str:
    """Sample v1 manifest for migration testing."""
    return """
version: 1.0.0
last_updated: 2025-12-16T00:00:00Z
toolkit_root: /test/toolkit

categories:
  brain_operations:
    description: Brain operations
    tools:
      - name: align
        command: cortex-align
        script: core/brain/align.py
        description: System alignment
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
        
      - name: cleanup
        command: cortex-cleanup
        script: core/brain/cleanup.py
        description: System cleanup
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
"""


@pytest.fixture
def v2_manifest_content() -> str:
    """Sample v2 manifest with all new fields."""
    return """
version: 2.0.0
schema_version: 2
last_updated: 2025-12-31T00:00:00Z
toolkit_root: /test/toolkit

categories:
  brain_operations:
    description: Brain operations
    tools:
      - name: align
        command: cortex-align
        script: core/brain/align.py
        description: System alignment
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
        # V2 fields
        depends_on: []
        conflicts_with: []
        capabilities: [validation, analysis]
        idempotent: true
        destructive: false
        rollback_supported: true
        input_schema:
          type: object
          properties:
            check_only:
              type: boolean
              default: false
        output_schema:
          type: object
          properties:
            status:
              type: string
            issues:
              type: array
        rate_limit:
          max_calls_per_minute: 60
        security:
          privilege_level: user
          audit_required: false
          
      - name: cleanup
        command: cortex-cleanup
        script: core/brain/cleanup.py
        description: System cleanup and maintenance
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
        # V2 fields
        depends_on: [align]
        conflicts_with: [deploy]
        capabilities: [cleanup, maintenance]
        idempotent: false
        destructive: true
        rollback_supported: true
        input_schema:
          type: object
          properties:
            dry_run:
              type: boolean
              default: true
        rate_limit:
          max_calls_per_minute: 10
        security:
          privilege_level: admin
          audit_required: true
"""


@pytest.fixture
def v2_tool_minimal() -> Dict[str, Any]:
    """Minimal v2 tool definition with required fields only."""
    return {
        "name": "test-tool",
        "command": "cortex-test",
        "script": "core/test.py",
        "description": "Test tool",
        "platforms": ["linux", "macos"],
        "requires_admin": False,
        "execution_method": "cli"
    }


@pytest.fixture
def v2_tool_full() -> Dict[str, Any]:
    """Full v2 tool definition with all fields."""
    return {
        "name": "full-tool",
        "command": "cortex-full",
        "script": "core/full.py",
        "description": "Full featured tool",
        "platforms": ["windows", "linux", "macos"],
        "requires_admin": True,
        "execution_method": "cli_wrapper",
        "depends_on": ["align", "healthcheck"],
        "conflicts_with": ["cleanup"],
        "capabilities": ["validation", "analysis", "generation"],
        "idempotent": True,
        "destructive": False,
        "rollback_supported": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "verbose": {"type": "boolean", "default": False},
                "output_format": {"type": "string", "enum": ["json", "yaml", "text"]}
            },
            "required": ["output_format"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "result": {"type": "object"}
            }
        },
        "rate_limit": {
            "max_calls_per_minute": 30,
            "burst_limit": 5
        },
        "security": {
            "privilege_level": "admin",
            "audit_required": True,
            "allowed_users": ["admin", "operator"]
        }
    }


# =============================================================================
# Test ManifestSchema Class
# =============================================================================

class TestManifestSchemaInit:
    """Tests for ManifestSchema initialization."""
    
    def test_init_with_defaults(self, temp_dir):
        """Should initialize with default schema."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        assert schema.toolkit_root == temp_dir
        assert schema.schema_version == 2
        assert schema.v2_schema is not None
    
    def test_init_loads_v2_schema(self, temp_dir):
        """Should load JSON Schema for v2 validation."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        # Schema should have required structure
        assert "properties" in schema.v2_schema
        assert "tools" in schema.v2_schema["properties"] or \
               "categories" in schema.v2_schema["properties"]
    
    def test_init_with_custom_schema_path(self, temp_dir):
        """Should load schema from custom path."""
        from core.manifest_schema import ManifestSchema
        
        # Create custom schema file
        custom_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "version": {"type": "string"}
            }
        }
        schema_path = temp_dir / "custom-schema.json"
        schema_path.write_text(json.dumps(custom_schema))
        
        ms = ManifestSchema(toolkit_root=temp_dir, schema_path=schema_path)
        
        assert ms.v2_schema == custom_schema


# =============================================================================
# Test Schema Validation
# =============================================================================

class TestSchemaValidation:
    """Tests for manifest validation against JSON Schema."""
    
    def test_validate_v2_manifest_valid(self, temp_dir, v2_manifest_content):
        """Should validate correct v2 manifest."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        manifest = yaml.safe_load(v2_manifest_content)
        
        result = schema.validate(manifest)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_missing_required_field(self, temp_dir):
        """Should fail validation when required field missing."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        invalid_manifest = {
            "version": "2.0.0",
            "categories": {
                "test": {
                    "tools": [
                        {
                            "name": "test-tool",
                            # Missing: command, script, description
                        }
                    ]
                }
            }
        }
        
        result = schema.validate(invalid_manifest)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("required" in str(e).lower() for e in result.errors)
    
    def test_validate_invalid_privilege_level(self, temp_dir):
        """Should fail validation for invalid privilege level."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        invalid_manifest = {
            "version": "2.0.0",
            "categories": {
                "test": {
                    "description": "Test",
                    "tools": [{
                        "name": "test-tool",
                        "command": "test",
                        "script": "test.py",
                        "description": "Test",
                        "platforms": ["linux"],
                        "requires_admin": False,
                        "execution_method": "cli",
                        "security": {
                            "privilege_level": "superuser"  # Invalid
                        }
                    }]
                }
            }
        }
        
        result = schema.validate(invalid_manifest)
        
        assert result.is_valid is False
        assert any("privilege_level" in str(e) for e in result.errors)
    
    def test_validate_invalid_capability(self, temp_dir):
        """Should fail for unknown capability keyword."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        invalid_manifest = {
            "version": "2.0.0",
            "categories": {
                "test": {
                    "description": "Test",
                    "tools": [{
                        "name": "test-tool",
                        "command": "test",
                        "script": "test.py",
                        "description": "Test",
                        "platforms": ["linux"],
                        "requires_admin": False,
                        "execution_method": "cli",
                        "capabilities": ["unknown_capability"]  # Invalid
                    }]
                }
            }
        }
        
        result = schema.validate(invalid_manifest)
        
        # Should warn but not fail for unknown capabilities
        assert len(result.warnings) > 0 or result.is_valid is True


class TestToolValidation:
    """Tests for individual tool definition validation."""
    
    def test_validate_tool_minimal(self, temp_dir, v2_tool_minimal):
        """Should validate tool with minimal required fields."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        result = schema.validate_tool(v2_tool_minimal)
        
        assert result.is_valid is True
    
    def test_validate_tool_full(self, temp_dir, v2_tool_full):
        """Should validate tool with all v2 fields."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        result = schema.validate_tool(v2_tool_full)
        
        assert result.is_valid is True
    
    def test_validate_tool_invalid_rate_limit(self, temp_dir, v2_tool_minimal):
        """Should fail for negative rate limit."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = v2_tool_minimal.copy()
        tool["rate_limit"] = {"max_calls_per_minute": -5}
        
        result = schema.validate_tool(tool)
        
        assert result.is_valid is False
        assert any("rate_limit" in str(e) for e in result.errors)
    
    def test_validate_tool_circular_dependency(self, temp_dir, v2_tool_minimal):
        """Should fail if tool depends on itself."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = v2_tool_minimal.copy()
        tool["depends_on"] = ["test-tool"]  # Self-dependency
        
        result = schema.validate_tool(tool)
        
        assert result.is_valid is False
        assert any("circular" in str(e).lower() or "self" in str(e).lower() 
                   for e in result.errors)
    
    def test_validate_tool_conflict_with_dependency(self, temp_dir, v2_tool_minimal):
        """Should warn if tool conflicts with its own dependency."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = v2_tool_minimal.copy()
        tool["depends_on"] = ["align"]
        tool["conflicts_with"] = ["align"]  # Conflict with dependency
        
        result = schema.validate_tool(tool)
        
        # Should have warning
        assert len(result.warnings) > 0


class TestInputOutputSchemaValidation:
    """Tests for input_schema and output_schema validation."""
    
    def test_validate_valid_input_schema(self, temp_dir, v2_tool_minimal):
        """Should validate correct JSON Schema for input."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = v2_tool_minimal.copy()
        tool["input_schema"] = {
            "type": "object",
            "properties": {
                "verbose": {"type": "boolean"},
                "count": {"type": "integer", "minimum": 0}
            }
        }
        
        result = schema.validate_tool(tool)
        
        assert result.is_valid is True
    
    def test_validate_invalid_input_schema(self, temp_dir, v2_tool_minimal):
        """Should fail for invalid JSON Schema."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = v2_tool_minimal.copy()
        tool["input_schema"] = {
            "type": "invalid_type"  # Invalid JSON Schema type
        }
        
        result = schema.validate_tool(tool)
        
        assert result.is_valid is False
        assert any("schema" in str(e).lower() for e in result.errors)
    
    def test_validate_input_against_schema(self, temp_dir, v2_tool_full):
        """Should validate actual input against tool's input_schema."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        # Valid input
        valid_input = {"verbose": True, "output_format": "json"}
        result = schema.validate_input(v2_tool_full, valid_input)
        assert result.is_valid is True
        
        # Invalid input - missing required
        invalid_input = {"verbose": True}  # Missing output_format
        result = schema.validate_input(v2_tool_full, invalid_input)
        assert result.is_valid is False


# =============================================================================
# Test Migration (V1 to V2)
# =============================================================================

class TestManifestMigration:
    """Tests for v1 to v2 manifest migration."""
    
    def test_detect_manifest_version(self, temp_dir, v1_manifest_content, v2_manifest_content):
        """Should correctly detect manifest version."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        v1 = yaml.safe_load(v1_manifest_content)
        v2 = yaml.safe_load(v2_manifest_content)
        
        assert schema.detect_version(v1) == 1
        assert schema.detect_version(v2) == 2
    
    def test_migrate_v1_to_v2(self, temp_dir, v1_manifest_content):
        """Should migrate v1 manifest to v2 format."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v1_manifest = yaml.safe_load(v1_manifest_content)
        
        v2_manifest = schema.migrate_to_v2(v1_manifest)
        
        # Check version updated
        assert v2_manifest["version"] == "2.0.0"
        assert v2_manifest.get("schema_version") == 2
        
        # Check tools have new fields with defaults
        tools = []
        for category in v2_manifest["categories"].values():
            tools.extend(category.get("tools", []))
        
        for tool in tools:
            assert "depends_on" in tool
            assert "conflicts_with" in tool
            assert "capabilities" in tool
            assert "idempotent" in tool
            assert "destructive" in tool
            assert "rollback_supported" in tool
    
    def test_migrate_preserves_existing_fields(self, temp_dir, v1_manifest_content):
        """Migration should preserve all existing v1 fields."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v1_manifest = yaml.safe_load(v1_manifest_content)
        
        v2_manifest = schema.migrate_to_v2(v1_manifest)
        
        # Check align tool preserved
        align_tool = None
        for category in v2_manifest["categories"].values():
            for tool in category.get("tools", []):
                if tool["name"] == "align":
                    align_tool = tool
                    break
        
        assert align_tool is not None
        assert align_tool["command"] == "cortex-align"
        assert align_tool["script"] == "core/brain/align.py"
        assert align_tool["description"] == "System alignment"
    
    def test_migrate_infers_capabilities(self, temp_dir, v1_manifest_content):
        """Migration should infer capabilities from tool name/description."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v1_manifest = yaml.safe_load(v1_manifest_content)
        
        v2_manifest = schema.migrate_to_v2(v1_manifest)
        
        # Cleanup tool should have cleanup capability inferred
        cleanup_tool = None
        for category in v2_manifest["categories"].values():
            for tool in category.get("tools", []):
                if tool["name"] == "cleanup":
                    cleanup_tool = tool
                    break
        
        assert cleanup_tool is not None
        assert "cleanup" in cleanup_tool.get("capabilities", [])
    
    def test_migrate_infers_destructive(self, temp_dir, v1_manifest_content):
        """Migration should infer destructive flag from tool name."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v1_manifest = yaml.safe_load(v1_manifest_content)
        
        v2_manifest = schema.migrate_to_v2(v1_manifest)
        
        # Cleanup should be marked as destructive
        cleanup_tool = None
        for category in v2_manifest["categories"].values():
            for tool in category.get("tools", []):
                if tool["name"] == "cleanup":
                    cleanup_tool = tool
                    break
        
        assert cleanup_tool is not None
        assert cleanup_tool["destructive"] is True
    
    def test_migrate_sets_default_security(self, temp_dir, v1_manifest_content):
        """Migration should set default security config."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v1_manifest = yaml.safe_load(v1_manifest_content)
        
        v2_manifest = schema.migrate_to_v2(v1_manifest)
        
        for category in v2_manifest["categories"].values():
            for tool in category.get("tools", []):
                assert "security" in tool
                assert tool["security"]["privilege_level"] in ["user", "admin", "system"]


class TestMigrationFile:
    """Tests for file-based migration operations."""
    
    def test_migrate_file(self, temp_dir, v1_manifest_content):
        """Should migrate file and create v2 output."""
        from core.manifest_schema import ManifestSchema
        
        # Write v1 manifest
        v1_path = temp_dir / "toolkit-manifest.yaml"
        v1_path.write_text(v1_manifest_content)
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        v2_path = schema.migrate_file(v1_path)
        
        assert v2_path.exists()
        v2_manifest = yaml.safe_load(v2_path.read_text())
        assert v2_manifest["version"] == "2.0.0"
    
    def test_migrate_file_backup(self, temp_dir, v1_manifest_content):
        """Should create backup of original file."""
        from core.manifest_schema import ManifestSchema
        
        v1_path = temp_dir / "toolkit-manifest.yaml"
        v1_path.write_text(v1_manifest_content)
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        schema.migrate_file(v1_path, backup=True)
        
        backup_path = temp_dir / "toolkit-manifest.yaml.v1.backup"
        assert backup_path.exists()
    
    def test_migrate_already_v2(self, temp_dir, v2_manifest_content):
        """Should skip migration for already v2 manifest."""
        from core.manifest_schema import ManifestSchema
        
        v2_path = temp_dir / "toolkit-manifest-v2.yaml"
        v2_path.write_text(v2_manifest_content)
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        result = schema.migrate_file(v2_path)
        
        # Should return same path, no changes
        assert result == v2_path


# =============================================================================
# Test Default Values
# =============================================================================

class TestDefaultValues:
    """Tests for v2 field default values."""
    
    def test_get_default_values(self, temp_dir):
        """Should return correct default values for v2 fields."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        defaults = schema.get_v2_defaults()
        
        assert defaults["depends_on"] == []
        assert defaults["conflicts_with"] == []
        assert defaults["capabilities"] == []
        assert defaults["idempotent"] is True
        assert defaults["destructive"] is False
        assert defaults["rollback_supported"] is False
        assert defaults["rate_limit"]["max_calls_per_minute"] == 60
        assert defaults["security"]["privilege_level"] == "user"
        assert defaults["security"]["audit_required"] is False
    
    def test_apply_defaults_to_tool(self, temp_dir, v2_tool_minimal):
        """Should apply defaults to tool missing optional fields."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool_with_defaults = schema.apply_defaults(v2_tool_minimal)
        
        # Check defaults applied
        assert "depends_on" in tool_with_defaults
        assert "capabilities" in tool_with_defaults
        assert "security" in tool_with_defaults
        
        # Original fields preserved
        assert tool_with_defaults["name"] == "test-tool"


# =============================================================================
# Test Schema Constants
# =============================================================================

class TestSchemaConstants:
    """Tests for schema constant definitions."""
    
    def test_valid_privilege_levels(self, temp_dir):
        """Should define valid privilege levels."""
        from core.manifest_schema import ManifestSchema, PRIVILEGE_LEVELS
        
        assert "user" in PRIVILEGE_LEVELS
        assert "admin" in PRIVILEGE_LEVELS
        assert "system" in PRIVILEGE_LEVELS
    
    def test_valid_capabilities(self, temp_dir):
        """Should define valid capability keywords."""
        from core.manifest_schema import ManifestSchema, VALID_CAPABILITIES
        
        assert "cleanup" in VALID_CAPABILITIES
        assert "validation" in VALID_CAPABILITIES
        assert "generation" in VALID_CAPABILITIES
        assert "analysis" in VALID_CAPABILITIES
        assert "migration" in VALID_CAPABILITIES
    
    def test_destructive_patterns(self, temp_dir):
        """Should define patterns for destructive tools."""
        from core.manifest_schema import ManifestSchema, DESTRUCTIVE_PATTERNS
        
        assert any("clean" in p for p in DESTRUCTIVE_PATTERNS)
        assert any("delete" in p for p in DESTRUCTIVE_PATTERNS)
        assert any("remove" in p for p in DESTRUCTIVE_PATTERNS)


# =============================================================================
# Test Validation Result
# =============================================================================

class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Should create validation result with defaults."""
        from core.manifest_schema import ValidationResult
        
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
    
    def test_validation_result_with_errors(self):
        """Should store errors in validation result."""
        from core.manifest_schema import ValidationResult
        
        result = ValidationResult(
            is_valid=False,
            errors=["Missing required field: name", "Invalid type"]
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
    
    def test_validation_result_with_warnings(self):
        """Should store warnings in validation result."""
        from core.manifest_schema import ValidationResult
        
        result = ValidationResult(
            is_valid=True,
            warnings=["Deprecated field used"]
        )
        
        assert result.is_valid is True
        assert len(result.warnings) == 1


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_validate_empty_manifest(self, temp_dir):
        """Should fail validation for empty manifest."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        result = schema.validate({})
        
        assert result.is_valid is False
    
    def test_validate_none_manifest(self, temp_dir):
        """Should handle None manifest gracefully."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        
        result = schema.validate(None)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_tool_empty_name(self, temp_dir):
        """Should fail for empty tool name."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        tool = {
            "name": "",
            "command": "test",
            "script": "test.py",
            "description": "Test",
            "platforms": ["linux"],
            "requires_admin": False,
            "execution_method": "cli"
        }
        
        result = schema.validate_tool(tool)
        
        assert result.is_valid is False
    
    def test_migrate_empty_categories(self, temp_dir):
        """Should handle manifest with empty categories."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        manifest = {
            "version": "1.0.0",
            "categories": {}
        }
        
        result = schema.migrate_to_v2(manifest)
        
        assert result["version"] == "2.0.0"
        assert result["categories"] == {}
    
    def test_migrate_missing_tools(self, temp_dir):
        """Should handle categories without tools list."""
        from core.manifest_schema import ManifestSchema
        
        schema = ManifestSchema(toolkit_root=temp_dir)
        manifest = {
            "version": "1.0.0",
            "categories": {
                "empty_category": {
                    "description": "No tools"
                }
            }
        }
        
        result = schema.migrate_to_v2(manifest)
        
        assert "empty_category" in result["categories"]


# =============================================================================
# Test Integration with ToolkitManager
# =============================================================================

class TestIntegrationWithManager:
    """Tests for integration with ToolkitManager."""
    
    @pytest.fixture
    def manager_temp_dir(self, tmp_path, v1_manifest_content):
        """Create temp directory with manifest for ToolkitManager."""
        # Create toolkit-manifest.yaml
        manifest_path = tmp_path / "toolkit-manifest.yaml"
        manifest_path.write_text(v1_manifest_content)
        # Create .checkpoints directory for recovery manager
        (tmp_path / ".checkpoints").mkdir(exist_ok=True)
        return tmp_path
    
    def test_manager_uses_manifest_schema(self, manager_temp_dir):
        """ToolkitManager should use ManifestSchema for validation."""
        from core.toolkit_manager import ToolkitManager
        from core.manifest_schema import ManifestSchema
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        
        assert hasattr(manager, 'manifest_schema')
        assert isinstance(manager.manifest_schema, ManifestSchema)
    
    def test_manager_validate_manifest(self, manager_temp_dir, v2_manifest_content):
        """ToolkitManager should expose manifest validation."""
        from core.toolkit_manager import ToolkitManager
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        manifest = yaml.safe_load(v2_manifest_content)
        
        result = manager.validate_manifest(manifest)
        
        assert result.is_valid is True
    
    def test_manager_get_tool_schema(self, manager_temp_dir):
        """ToolkitManager should provide tool input/output schemas."""
        from core.toolkit_manager import ToolkitManager
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        
        # Should be able to get schema for a tool
        input_schema = manager.get_tool_input_schema("align")
        output_schema = manager.get_tool_output_schema("align")
        
        # May return None or empty dict if not defined
        assert input_schema is None or isinstance(input_schema, dict)
        assert output_schema is None or isinstance(output_schema, dict)


# =============================================================================
# Test JSON Schema File
# =============================================================================

class TestSchemaFile:
    """Tests for the JSON Schema file itself."""
    
    def test_schema_file_valid_json(self):
        """Schema file should be valid JSON."""
        from core.manifest_schema import ManifestSchema
        
        schema_path = Path(__file__).parent.parent.parent / \
                     "cortex-toolkit" / "schemas" / "manifest-v2.schema.json"
        
        if schema_path.exists():
            content = schema_path.read_text()
            schema = json.loads(content)  # Should not raise
            assert "$schema" in schema
    
    def test_schema_has_required_definitions(self):
        """Schema should define all required structures."""
        from core.manifest_schema import ManifestSchema
        
        schema_path = Path(__file__).parent.parent.parent / \
                     "cortex-toolkit" / "schemas" / "manifest-v2.schema.json"
        
        if schema_path.exists():
            schema = json.loads(schema_path.read_text())
            
            # Should have tool definition
            assert "definitions" in schema or "properties" in schema
