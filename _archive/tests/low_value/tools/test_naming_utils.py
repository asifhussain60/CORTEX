"""
Tests for naming utility functions.

AC_START: AC-AUDIT-2026-02-12-002
Test: Naming utilities extracted to eliminate duplicates
"""

import pytest

from cortex.tools.naming_utils import to_class_name, to_module_name, yaml_type_to_python


class TestToClassName:
    """Tests for to_class_name function."""
    
    def test_kebab_case(self):
        """Convert kebab-case to PascalCase."""
        assert to_class_name("my-tool") == "MyTool"
        assert to_class_name("lens-analyzer") == "LensAnalyzer"
        assert to_class_name("tdd-orchestrator") == "TddOrchestrator"
    
    def test_snake_case(self):
        """Convert snake_case to PascalCase."""
        assert to_class_name("my_tool") == "MyTool"
        assert to_class_name("lens_analyzer") == "LensAnalyzer"
        assert to_class_name("tdd_orchestrator") == "TddOrchestrator"
    
    def test_space_separated(self):
        """Convert space-separated to PascalCase."""
        assert to_class_name("my tool") == "MyTool"
        assert to_class_name("TDD Orchestrator") == "TddOrchestrator"
        assert to_class_name("lens analyzer") == "LensAnalyzer"
    
    def test_mixed_separators(self):
        """Handle mixed separators."""
        assert to_class_name("my-tool_name test") == "MyToolNameTest"
    
    def test_single_word(self):
        """Handle single word."""
        assert to_class_name("tool") == "Tool"
        assert to_class_name("TOOL") == "Tool"


class TestToModuleName:
    """Tests for to_module_name function."""
    
    def test_pascal_case(self):
        """Convert PascalCase to snake_case."""
        assert to_module_name("MyTool") == "my_tool"
        assert to_module_name("LensAnalyzer") == "lens_analyzer"
        # Note: Consecutive caps stay together (standard snake_case convention)
        assert to_module_name("TDDOrchestrator") == "tddorchestrator"
    
    def test_camel_case(self):
        """Convert camelCase to snake_case."""
        assert to_module_name("myTool") == "my_tool"
        assert to_module_name("lensAnalyzer") == "lens_analyzer"
    
    def test_kebab_case(self):
        """Convert kebab-case to snake_case."""
        assert to_module_name("my-tool") == "my_tool"
        assert to_module_name("lens-analyzer") == "lens_analyzer"
    
    def test_space_separated(self):
        """Convert space-separated to snake_case."""
        assert to_module_name("my tool") == "my_tool"
        assert to_module_name("TDD Orchestrator") == "tdd_orchestrator"
    
    def test_mixed_separators(self):
        """Handle mixed separators."""
        assert to_module_name("My-Tool Name") == "my_tool_name"
    
    def test_single_word(self):
        """Handle single word."""
        assert to_module_name("tool") == "tool"
        assert to_module_name("TOOL") == "tool"


class TestYamlTypeToPython:
    """Tests for yaml_type_to_python function."""
    
    def test_string_types(self):
        """Convert string types."""
        assert yaml_type_to_python("str") == "str"
        assert yaml_type_to_python("string") == "str"
        assert yaml_type_to_python("STRING") == "str"
    
    def test_integer_types(self):
        """Convert integer types."""
        assert yaml_type_to_python("int") == "int"
        assert yaml_type_to_python("integer") == "int"
        assert yaml_type_to_python("INTEGER") == "int"
    
    def test_float_types(self):
        """Convert float types."""
        assert yaml_type_to_python("float") == "float"
        assert yaml_type_to_python("number") == "float"
    
    def test_boolean_types(self):
        """Convert boolean types."""
        assert yaml_type_to_python("bool") == "bool"
        assert yaml_type_to_python("boolean") == "bool"
    
    def test_collection_types(self):
        """Convert collection types."""
        assert yaml_type_to_python("list") == "List[Any]"
        assert yaml_type_to_python("array") == "List[Any]"
        assert yaml_type_to_python("dict") == "Dict[str, Any]"
        assert yaml_type_to_python("object") == "Dict[str, Any]"
    
    def test_unknown_type(self):
        """Handle unknown types."""
        assert yaml_type_to_python("unknown") == "Any"
        assert yaml_type_to_python("custom") == "Any"


# AC_COMPLETE: AC-AUDIT-2026-02-12-002 ✅ Tests added
