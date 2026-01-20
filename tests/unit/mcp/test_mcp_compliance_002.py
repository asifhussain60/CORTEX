"""
AC-MCP-COMPLIANCE-002: Tool Definition Standardization Test Suite.

Tests for standardized tool definitions across CORTEX system:
- Consistent naming conventions (snake_case)
- Uniform parameter documentation
- Standard tool metadata
- Documentation completeness
- Deprecation and versioning
"""

import pytest
from typing import Dict, Any
from dataclasses import dataclass

from cortex.mcp.protocol import (
    ToolDefinition,
    ToolParameter,
)


class ToolNameValidator:
    """Validates tool naming conventions."""
    
    @staticmethod
    def is_valid_tool_name(name: str) -> bool:
        """Check if tool name follows conventions (snake_case, lowercase)."""
        if not name:
            return False
        if not name.islower():
            return False
        if not all(c.isalnum() or c == '_' for c in name):
            return False
        if name.startswith('_') or name.endswith('_'):
            return False
        return True
    
    @staticmethod
    def is_valid_parameter_name(name: str) -> bool:
        """Check if parameter name follows conventions."""
        return ToolNameValidator.is_valid_tool_name(name)
    
    @staticmethod
    def is_valid_tool_id(tool_id: str) -> bool:
        """Check if tool ID follows conventions (usually tool_name_* format)."""
        if not tool_id:
            return False
        # Should be alphanumeric with underscores
        return all(c.isalnum() or c == '_' for c in tool_id)


class ToolDocumentationValidator:
    """Validates tool documentation completeness."""
    
    @staticmethod
    def is_description_complete(description: str) -> bool:
        """Check if description meets minimum requirements."""
        if not description:
            return False
        if len(description) < 10:
            return False
        return '.' in description or description.endswith(')')
    
    @staticmethod
    def is_parameter_documented(param: ToolParameter) -> bool:
        """Check if parameter is properly documented."""
        if not param.description or len(param.description) < 5:
            return False
        return True
    
    @staticmethod
    def all_parameters_documented(tool: ToolDefinition) -> bool:
        """Check if all parameters are documented."""
        for param in tool.parameters:
            if not ToolDocumentationValidator.is_parameter_documented(param):
                return False
        return True


@dataclass
class StandardizedToolSpec:
    """Standard specification for a tool."""
    name: str
    description: str
    parameters: list
    version: str = "1.0.0"
    tags: list = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestToolDefinitionStandardization:
    """Test standardized tool definitions."""
    
    def test_tool_name_snake_case(self) -> None:
        """Test tool names use snake_case."""
        valid_names = [
            "process_text",
            "validate_input",
            "execute_query",
            "get_data",
            "analyze_results",
        ]
        
        for name in valid_names:
            assert ToolNameValidator.is_valid_tool_name(name), f"Name {name} should be valid"
    
    def test_tool_name_invalid_cases(self) -> None:
        """Test invalid tool names are rejected."""
        invalid_names = [
            "ProcessText",  # PascalCase
            "process-text",  # kebab-case
            "processText",  # camelCase
            "_process",  # starts with underscore
            "process_",  # ends with underscore
            "",  # empty
            "PROCESS",  # UPPERCASE
        ]
        
        for name in invalid_names:
            assert not ToolNameValidator.is_valid_tool_name(name), f"Name {name} should be invalid"
    
    def test_parameter_name_snake_case(self) -> None:
        """Test parameter names use snake_case."""
        valid_params = [
            "input_text",
            "max_length",
            "enable_cache",
            "retry_count",
            "timeout_ms",
        ]
        
        for param_name in valid_params:
            assert ToolNameValidator.is_valid_parameter_name(param_name)
    
    def test_tool_definition_standardization(self) -> None:
        """Test standardized tool definition structure."""
        tool = ToolDefinition(
            id="tool_001",
            name="process_data",
            description="Process and transform input data with validation.",
            parameters=[
                ToolParameter(
                    name="input_data",
                    type="string",
                    description="Input data to process",
                    required=True
                ),
                ToolParameter(
                    name="format_type",
                    type="string",
                    description="Output format type",
                    enum=["json", "csv", "xml"],
                    required=False
                )
            ],
            version="1.0.0",
            tags=["data", "processing", "validation"]
        )
        
        # Verify structure
        assert ToolNameValidator.is_valid_tool_name(tool.name)
        assert ToolNameValidator.is_valid_tool_id(tool.id)
        assert ToolDocumentationValidator.is_description_complete(tool.description)
        assert ToolDocumentationValidator.all_parameters_documented(tool)
        assert tool.version == "1.0.0"
        assert len(tool.tags) >= 1
    
    def test_parameter_naming_consistency(self) -> None:
        """Test parameter naming is consistent."""
        params = [
            ToolParameter("input_text", "string", "Input"),
            ToolParameter("output_format", "string", "Output format"),
            ToolParameter("retry_count", "number", "Retry count"),
            ToolParameter("enable_logging", "boolean", "Enable logging"),
        ]
        
        for param in params:
            assert ToolNameValidator.is_valid_parameter_name(param.name)
    
    def test_tool_version_format(self) -> None:
        """Test tool versions follow semantic versioning."""
        valid_versions = [
            "1.0.0",
            "2.1.0",
            "0.1.0",
            "1.2.3",
            "10.0.0",
        ]
        
        for version in valid_versions:
            tool = ToolDefinition(
                id="tool_001",
                name="test_tool",
                description="Test",
                version=version
            )
            assert tool.version == version
    
    def test_tool_description_requirements(self) -> None:
        """Test tool descriptions meet requirements."""
        # Good description
        good_desc = "Process input data and return formatted results."
        assert ToolDocumentationValidator.is_description_complete(good_desc)
        
        # Bad descriptions
        bad_descs = [
            "",  # empty
            "process",  # too short
            "a tool",  # too vague
        ]
        
        for desc in bad_descs:
            assert not ToolDocumentationValidator.is_description_complete(desc)
    
    def test_parameter_documentation_requirements(self) -> None:
        """Test parameters are properly documented."""
        good_param = ToolParameter(
            name="input_text",
            type="string",
            description="The input text to be processed",
            required=True
        )
        assert ToolDocumentationValidator.is_parameter_documented(good_param)
        
        bad_param = ToolParameter(
            name="x",
            type="string",
            description="x",  # too short
        )
        assert not ToolDocumentationValidator.is_parameter_documented(bad_param)
    
    def test_standardized_metadata(self) -> None:
        """Test tools have standardized metadata."""
        tool = ToolDefinition(
            id="tool_metadata",
            name="standardized_tool",
            description="A properly standardized tool implementation.",
            parameters=[],
            version="1.0.0",
            tags=["standard", "metadata"],
            deprecated=False,
            timeout_ms=30000
        )
        
        assert tool.version.count('.') == 2  # semantic versioning
        assert isinstance(tool.tags, list)
        assert isinstance(tool.deprecated, bool)
        assert isinstance(tool.timeout_ms, int)
        assert tool.timeout_ms > 0
    
    def test_parameter_type_consistency(self) -> None:
        """Test parameter types are consistent."""
        valid_types = ["string", "number", "boolean", "object", "array"]
        
        for ptype in valid_types:
            param = ToolParameter(
                name="test_param",
                type=ptype,
                description="Test parameter"
            )
            assert param.type == ptype
    
    def test_required_parameter_clarity(self) -> None:
        """Test required parameters are clearly marked."""
        tool = ToolDefinition(
            id="tool_required",
            name="test_required",
            description="Test required parameters.",
            parameters=[
                ToolParameter("required_field", "string", "Required", required=True),
                ToolParameter("optional_field", "string", "Optional", required=False),
            ]
        )
        
        required_params = [p for p in tool.parameters if p.required]
        optional_params = [p for p in tool.parameters if not p.required]
        
        assert len(required_params) == 1
        assert len(optional_params) == 1
    
    def test_default_value_specification(self) -> None:
        """Test default values are properly specified."""
        tool = ToolDefinition(
            id="tool_defaults",
            name="test_defaults",
            description="Test default values.",
            parameters=[
                ToolParameter(
                    "mode",
                    "string",
                    "Operation mode",
                    default="standard",
                    required=False
                ),
                ToolParameter(
                    "retries",
                    "number",
                    "Retry count",
                    default=3,
                    required=False
                ),
            ]
        )
        
        for param in tool.parameters:
            if not param.required:
                assert param.default is not None or param.enum is not None
    
    def test_enum_values_documented(self) -> None:
        """Test enum parameters have clear documentation."""
        param = ToolParameter(
            name="operation",
            type="string",
            description="The operation to perform: read, write, or delete.",
            enum=["read", "write", "delete"],
            required=True
        )
        
        assert param.enum is not None
        assert len(param.enum) >= 2
        # Description should mention enum values
        desc_lower = param.description.lower()
        for value in param.enum:
            assert value.lower() in desc_lower
    
    def test_numeric_constraints_documented(self) -> None:
        """Test numeric parameters have constraints."""
        param = ToolParameter(
            name="timeout_seconds",
            type="number",
            description="Timeout in seconds (1-3600)",
            min_value=1,
            max_value=3600,
            required=True
        )
        
        assert param.min_value is not None
        assert param.max_value is not None
        # Constraints should be mentioned in description
        assert "1-3600" in param.description or "seconds" in param.description.lower()
    
    def test_tool_tagging_consistency(self) -> None:
        """Test tools are consistently tagged."""
        tools = [
            ToolDefinition(
                id="tool_1",
                name="process_json",
                description="Process JSON data.",
                tags=["data", "json", "processing"]
            ),
            ToolDefinition(
                id="tool_2",
                name="validate_schema",
                description="Validate against schema.",
                tags=["validation", "schema"]
            ),
        ]
        
        for tool in tools:
            assert len(tool.tags) > 0
            assert all(isinstance(tag, str) for tag in tool.tags)
            assert all(tag.islower() for tag in tool.tags)
    
    def test_tool_deprecation_notice(self) -> None:
        """Test deprecated tools are marked."""
        deprecated_tool = ToolDefinition(
            id="old_tool",
            name="deprecated_process",
            description="DEPRECATED: Use process_v2 instead.",
            deprecated=True
        )
        
        active_tool = ToolDefinition(
            id="new_tool",
            name="process_v2",
            description="Process data with new algorithm.",
            deprecated=False
        )
        
        assert deprecated_tool.deprecated is True
        assert active_tool.deprecated is False
        assert "DEPRECATED" in deprecated_tool.description
    
    def test_timeout_specification(self) -> None:
        """Test tool timeouts are specified."""
        tools = [
            ToolDefinition(
                id="quick_tool",
                name="quick_check",
                description="Quick check.",
                timeout_ms=5000
            ),
            ToolDefinition(
                id="slow_tool",
                name="lengthy_process",
                description="Lengthy operation.",
                timeout_ms=120000
            ),
        ]
        
        for tool in tools:
            assert tool.timeout_ms > 0
            assert tool.timeout_ms <= 300000  # max 5 minutes
    
    def test_tool_return_schema(self) -> None:
        """Test tools specify return schema."""
        tool = ToolDefinition(
            id="schema_tool",
            name="process_with_schema",
            description="Process and return structured data.",
            returns={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"},
                    "errors": {"type": "array"}
                }
            }
        )
        
        assert tool.returns is not None
        assert "type" in tool.returns
        assert "properties" in tool.returns
    
    def test_consistent_tool_structure(self) -> None:
        """Test tools follow consistent structure."""
        tools = [
            ToolDefinition(
                id=f"tool_{i}",
                name=f"operation_{i}",
                description=f"Operation {i} description.",
                parameters=[
                    ToolParameter(f"input_{i}", "string", f"Input {i}"),
                ],
                version="1.0.0",
                tags=[f"category_{i}"],
                timeout_ms=30000
            )
            for i in range(3)
        ]
        
        for tool in tools:
            # All should have standard structure
            assert tool.id
            assert tool.name
            assert tool.description
            assert tool.version
            assert tool.tags
            assert tool.timeout_ms > 0
            # Names should follow convention
            assert ToolNameValidator.is_valid_tool_name(tool.name)
            assert ToolNameValidator.is_valid_tool_id(tool.id)


class TestToolDefinitionStandardizationIntegration:
    """Integration tests for standardized tools."""
    
    def test_tool_registry_standardization(self) -> None:
        """Test tool registry maintains standards."""
        tool_registry = {}
        
        # Register tools
        for i in range(3):
            tool = ToolDefinition(
                id=f"tool_{i:03d}",
                name=f"standard_operation_{i}",
                description=f"Standard operation number {i}.",
                version="1.0.0"
            )
            tool_registry[tool.name] = tool
        
        # Verify all are standardized
        for name, tool in tool_registry.items():
            assert ToolNameValidator.is_valid_tool_name(tool.name)
            assert ToolDocumentationValidator.is_description_complete(tool.description)
    
    def test_migration_to_standard_format(self) -> None:
        """Test migrating tools to standard format."""
        # Old format (non-standard)
        old_tool_data = {
            "id": "old_001",
            "name": "OldProcessName",  # PascalCase
            "description": "Process",  # too short
            "params": {},  # non-standard field name
        }
        
        # Migrate to standard
        standard_tool = ToolDefinition(
            id=old_tool_data["id"],
            name="old_process_name",  # converted to snake_case
            description="Process data according to old specification.",  # enhanced
            parameters=[]  # standardized field name
        )
        
        # Verify result is standard
        assert ToolNameValidator.is_valid_tool_name(standard_tool.name)
        assert ToolDocumentationValidator.is_description_complete(standard_tool.description)
    
    def test_batch_standardization_check(self) -> None:
        """Test checking multiple tools for standardization."""
        tools = [
            ToolDefinition(
                id="batch_001",
                name="batch_process",
                description="Batch process operation.",
                parameters=[
                    ToolParameter("items", "array", "Items to process")
                ]
            ),
            ToolDefinition(
                id="batch_002",
                name="batch_validate",
                description="Batch validation operation.",
                parameters=[
                    ToolParameter("schema", "object", "Schema definition")
                ]
            ),
        ]
        
        # Check all are standardized
        for tool in tools:
            assert ToolNameValidator.is_valid_tool_name(tool.name)
            for param in tool.parameters:
                assert ToolNameValidator.is_valid_parameter_name(param.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
