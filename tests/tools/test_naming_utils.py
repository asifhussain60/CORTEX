"""
Tests for naming utility functions.

AC_START: AC-AUDIT-2026-02-12-002
Test: Naming utilities extracted to eliminate duplicates
"""

import pytest

from cortex.tools.naming_utils import to_class_name, to_module_name


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


# AC_COMPLETE: AC-AUDIT-2026-02-12-002 ✅ Tests added
