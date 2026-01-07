"""
Manifest Schema v2 for CORTEX Toolkit.

This module provides:
- Schema validation against JSON Schema
- V1 to V2 manifest migration
- Tool definition validation
- Input/output schema validation
- Default value management

Part of Phase 5: Manifest Schema v2 implementation.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml


# =============================================================================
# Constants
# =============================================================================

PRIVILEGE_LEVELS = ["user", "admin", "system"]

VALID_CAPABILITIES = [
    "cleanup",
    "validation", 
    "generation",
    "analysis",
    "migration",
    "documentation",
    "testing",
    "deployment",
    "monitoring",
    "maintenance",
    "security",
    "optimization"
]

DESTRUCTIVE_PATTERNS = [
    "clean",
    "delete",
    "remove",
    "purge",
    "clear",
    "drop",
    "destroy",
    "wipe",
    "erase"
]

CAPABILITY_INFERENCE_PATTERNS = {
    "cleanup": ["clean", "clear", "purge", "sweep"],
    "validation": ["validate", "check", "verify", "lint", "test"],
    "generation": ["generate", "create", "build", "scaffold", "make"],
    "analysis": ["analyze", "inspect", "profile", "measure", "report"],
    "migration": ["migrate", "upgrade", "convert", "transform"],
    "documentation": ["doc", "document", "readme"],
    "testing": ["test", "spec", "assert"],
    "deployment": ["deploy", "publish", "release"],
    "monitoring": ["monitor", "watch", "observe", "track"],
    "maintenance": ["maintain", "fix", "repair", "update"],
    "security": ["secure", "auth", "encrypt", "sanitize"],
    "optimization": ["optimize", "tune", "improve", "enhance"]
}

VALID_JSON_SCHEMA_TYPES = ["object", "array", "string", "number", "integer", "boolean", "null"]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ValidationResult:
    """Result of schema or tool validation."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge another validation result into this one."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings
        )


# =============================================================================
# ManifestSchema Class
# =============================================================================

class ManifestSchema:
    """
    Manages manifest schema validation and migration.
    
    Features:
    - Validate manifests against JSON Schema v2
    - Migrate v1 manifests to v2 format
    - Validate individual tool definitions
    - Validate tool input/output against schemas
    """
    
    # Default schema path relative to this file
    DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "manifest-v2.schema.json"
    
    def __init__(
        self,
        toolkit_root: Path,
        schema_path: Optional[Path] = None
    ):
        """
        Initialize ManifestSchema.
        
        Args:
            toolkit_root: Root directory of the toolkit
            schema_path: Optional custom JSON Schema file path
        """
        self.toolkit_root = Path(toolkit_root)
        self.schema_version = 2
        self.schema_path = schema_path or self.DEFAULT_SCHEMA_PATH
        self.v2_schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON Schema from file or return embedded schema."""
        if self.schema_path.exists():
            try:
                return json.loads(self.schema_path.read_text())
            except json.JSONDecodeError:
                pass
        
        # Return embedded minimal schema if file not found
        return self._get_embedded_schema()
    
    def _get_embedded_schema(self) -> Dict[str, Any]:
        """Return embedded JSON Schema for v2 manifests."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "categories"],
            "properties": {
                "version": {"type": "string"},
                "schema_version": {"type": "integer"},
                "categories": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "tools": {"type": "array"}
                        }
                    }
                }
            }
        }
    
    # =========================================================================
    # Validation Methods
    # =========================================================================
    
    def validate(self, manifest: Optional[Dict[str, Any]]) -> ValidationResult:
        """
        Validate a manifest against the v2 schema.
        
        Args:
            manifest: Manifest dictionary to validate
            
        Returns:
            ValidationResult with is_valid, errors, and warnings
        """
        if manifest is None:
            return ValidationResult(
                is_valid=False,
                errors=["Manifest is None"]
            )
        
        if not manifest:
            return ValidationResult(
                is_valid=False,
                errors=["Manifest is empty"]
            )
        
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if "version" not in manifest:
            result.add_error("Missing required field: version")
        
        if "categories" not in manifest:
            result.add_error("Missing required field: categories")
        
        if not result.is_valid:
            return result
        
        # Validate each category and tool
        for category_name, category in manifest.get("categories", {}).items():
            tools = category.get("tools", [])
            for tool in tools:
                tool_result = self.validate_tool(tool)
                result = result.merge(tool_result)
        
        return result
    
    def validate_tool(self, tool: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single tool definition.
        
        Args:
            tool: Tool definition dictionary
            
        Returns:
            ValidationResult for the tool
        """
        result = ValidationResult(is_valid=True)
        
        # Required fields
        required_fields = [
            "name", "command", "script", "description",
            "platforms", "requires_admin", "execution_method"
        ]
        
        for field_name in required_fields:
            if field_name not in tool:
                result.add_error(f"Missing required field: {field_name}")
        
        if not result.is_valid:
            return result
        
        # Validate name
        name = tool.get("name", "")
        if not name:
            result.add_error("Tool name cannot be empty")
        elif not re.match(r'^[a-z][a-z0-9-]*$', name):
            result.add_warning(f"Tool name '{name}' should be lowercase with hyphens")
        
        # Validate rate_limit
        rate_limit = tool.get("rate_limit", {})
        if rate_limit:
            max_calls = rate_limit.get("max_calls_per_minute")
            if max_calls is not None and max_calls < 0:
                result.add_error(f"rate_limit.max_calls_per_minute must be non-negative")
        
        # Validate security
        security = tool.get("security", {})
        if security:
            privilege = security.get("privilege_level")
            if privilege and privilege not in PRIVILEGE_LEVELS:
                result.add_error(f"Invalid privilege_level: {privilege}. Must be one of {PRIVILEGE_LEVELS}")
        
        # Validate capabilities
        capabilities = tool.get("capabilities", [])
        for cap in capabilities:
            if cap not in VALID_CAPABILITIES:
                result.add_warning(f"Unknown capability: {cap}")
        
        # Check for self-dependency
        depends_on = tool.get("depends_on", [])
        if name in depends_on:
            result.add_error(f"Tool '{name}' cannot depend on itself (circular self-dependency)")
        
        # Check for conflict with dependency
        conflicts_with = tool.get("conflicts_with", [])
        for dep in depends_on:
            if dep in conflicts_with:
                result.add_warning(f"Tool '{name}' conflicts with its dependency '{dep}'")
        
        # Validate input_schema
        input_schema = tool.get("input_schema")
        if input_schema:
            schema_result = self._validate_json_schema(input_schema, "input_schema")
            result = result.merge(schema_result)
        
        # Validate output_schema
        output_schema = tool.get("output_schema")
        if output_schema:
            schema_result = self._validate_json_schema(output_schema, "output_schema")
            result = result.merge(schema_result)
        
        return result
    
    def _validate_json_schema(
        self, 
        schema: Dict[str, Any], 
        field_name: str
    ) -> ValidationResult:
        """Validate that a dictionary is a valid JSON Schema."""
        result = ValidationResult(is_valid=True)
        
        schema_type = schema.get("type")
        if schema_type and schema_type not in VALID_JSON_SCHEMA_TYPES:
            result.add_error(f"{field_name} has invalid schema type: {schema_type}")
        
        return result
    
    def validate_input(
        self, 
        tool: Dict[str, Any], 
        input_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate actual input data against a tool's input_schema.
        
        Args:
            tool: Tool definition with input_schema
            input_data: Input data to validate
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        input_schema = tool.get("input_schema")
        if not input_schema:
            return result
        
        # Check required fields
        required = input_schema.get("required", [])
        properties = input_schema.get("properties", {})
        
        for field_name in required:
            if field_name not in input_data:
                result.add_error(f"Missing required input field: {field_name}")
        
        # Type validation for provided fields
        for field_name, value in input_data.items():
            if field_name in properties:
                prop_schema = properties[field_name]
                expected_type = prop_schema.get("type")
                
                if expected_type:
                    if not self._check_type(value, expected_type):
                        result.add_error(
                            f"Field '{field_name}' has wrong type. "
                            f"Expected {expected_type}, got {type(value).__name__}"
                        )
                
                # Check enum
                enum_values = prop_schema.get("enum")
                if enum_values and value not in enum_values:
                    result.add_error(
                        f"Field '{field_name}' value '{value}' not in allowed values: {enum_values}"
                    )
        
        return result
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if a value matches the expected JSON Schema type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected = type_mapping.get(expected_type)
        if expected is None:
            return True  # Unknown type, allow
        
        # Special case: integer should not match bool
        if expected_type == "integer" and isinstance(value, bool):
            return False
        
        return isinstance(value, expected)
    
    # =========================================================================
    # Migration Methods
    # =========================================================================
    
    def detect_version(self, manifest: Dict[str, Any]) -> int:
        """
        Detect the version of a manifest.
        
        Args:
            manifest: Manifest dictionary
            
        Returns:
            Version number (1 or 2)
        """
        # Check explicit schema_version field
        if manifest.get("schema_version") == 2:
            return 2
        
        # Check version string
        version = manifest.get("version", "1.0.0")
        if version.startswith("2."):
            return 2
        
        # Check for v2-only fields
        for category in manifest.get("categories", {}).values():
            for tool in category.get("tools", []):
                # V2 fields
                if any(f in tool for f in ["depends_on", "capabilities", "destructive", 
                                            "rollback_supported", "input_schema", "security"]):
                    return 2
        
        return 1
    
    def migrate_to_v2(self, v1_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a v1 manifest to v2 format.
        
        Args:
            v1_manifest: V1 format manifest
            
        Returns:
            V2 format manifest with new fields populated
        """
        # Deep copy to avoid modifying original - handle datetime objects
        v2_manifest = self._deep_copy_manifest(v1_manifest)
        
        # Update version
        v2_manifest["version"] = "2.0.0"
        v2_manifest["schema_version"] = 2
        v2_manifest["last_updated"] = datetime.now().isoformat()
        
        # Process each tool
        for category_name, category in v2_manifest.get("categories", {}).items():
            tools = category.get("tools", [])
            for i, tool in enumerate(tools):
                tools[i] = self._migrate_tool(tool)
        
        return v2_manifest
    
    def _deep_copy_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy a manifest, handling datetime objects."""
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        return json.loads(json.dumps(manifest, default=serialize))
    
    def _migrate_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate a single tool definition to v2 format."""
        defaults = self.get_v2_defaults()
        
        # Add missing v2 fields with defaults
        for field_name, default_value in defaults.items():
            if field_name not in tool:
                tool[field_name] = default_value
        
        # Infer capabilities from name/description
        tool["capabilities"] = self._infer_capabilities(tool)
        
        # Infer destructive flag
        tool["destructive"] = self._infer_destructive(tool)
        
        # Set security based on requires_admin
        if tool.get("requires_admin"):
            tool["security"] = {
                "privilege_level": "admin",
                "audit_required": True
            }
        else:
            tool["security"] = {
                "privilege_level": "user",
                "audit_required": False
            }
        
        return tool
    
    def _infer_capabilities(self, tool: Dict[str, Any]) -> List[str]:
        """Infer capabilities from tool name and description."""
        capabilities = []
        
        name = tool.get("name", "").lower()
        description = tool.get("description", "").lower()
        text = f"{name} {description}"
        
        for capability, patterns in CAPABILITY_INFERENCE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    if capability not in capabilities:
                        capabilities.append(capability)
                    break
        
        return capabilities
    
    def _infer_destructive(self, tool: Dict[str, Any]) -> bool:
        """Infer whether a tool is destructive."""
        name = tool.get("name", "").lower()
        description = tool.get("description", "").lower()
        text = f"{name} {description}"
        
        for pattern in DESTRUCTIVE_PATTERNS:
            if pattern in text:
                return True
        
        return False
    
    def migrate_file(
        self, 
        source_path: Path,
        output_path: Optional[Path] = None,
        backup: bool = False
    ) -> Path:
        """
        Migrate a manifest file from v1 to v2.
        
        Args:
            source_path: Path to source manifest
            output_path: Path for output (defaults to same dir with -v2 suffix)
            backup: Whether to create backup of original
            
        Returns:
            Path to the migrated manifest file
        """
        source_path = Path(source_path)
        
        # Read source manifest
        content = source_path.read_text()
        manifest = yaml.safe_load(content)
        
        # Check if already v2
        if self.detect_version(manifest) == 2:
            return source_path
        
        # Create backup if requested
        if backup:
            backup_path = source_path.with_suffix(f".yaml.v1.backup")
            backup_path.write_text(content)
        
        # Migrate
        v2_manifest = self.migrate_to_v2(manifest)
        
        # Determine output path
        if output_path is None:
            output_path = source_path.parent / f"{source_path.stem}-v2.yaml"
        
        # Write v2 manifest
        output_path.write_text(yaml.dump(v2_manifest, default_flow_style=False, sort_keys=False))
        
        return output_path
    
    # =========================================================================
    # Default Values
    # =========================================================================
    
    def get_v2_defaults(self) -> Dict[str, Any]:
        """
        Get default values for v2 fields.
        
        Returns:
            Dictionary of field names to default values
        """
        return {
            "depends_on": [],
            "conflicts_with": [],
            "capabilities": [],
            "idempotent": True,
            "destructive": False,
            "rollback_supported": False,
            "input_schema": None,
            "output_schema": None,
            "rate_limit": {
                "max_calls_per_minute": 60
            },
            "security": {
                "privilege_level": "user",
                "audit_required": False
            }
        }
    
    def apply_defaults(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to a tool definition.
        
        Args:
            tool: Tool definition (may be missing optional fields)
            
        Returns:
            Tool definition with defaults applied
        """
        defaults = self.get_v2_defaults()
        result = tool.copy()
        
        for field_name, default_value in defaults.items():
            if field_name not in result:
                # Deep copy for mutable defaults
                if isinstance(default_value, (list, dict)):
                    result[field_name] = json.loads(json.dumps(default_value))
                else:
                    result[field_name] = default_value
        
        return result
