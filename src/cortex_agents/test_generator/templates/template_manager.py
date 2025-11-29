"""Test code templates."""

from typing import Dict, Any


class TemplateManager:
    """Manages test code templates for different scenarios."""
    
    def basic_function(self, func_info: Dict[str, Any]) -> str:
        """Template for basic function test."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_basic():',
            f'    """Test basic {func_name} functionality."""',
        ]
        
        # Generate function call
        if func_info["args"]:
            args = func_info["args"]
            args_str = ", ".join(f"mock_{a}" for a in args)
            test.append(f'    result = {func_name}({args_str})')
        else:
            test.append(f'    result = {func_name}()')
        
        # Add assertion
        if func_info.get("has_return"):
            test.append(f'    assert result is not None')
        
        return '\n'.join(test)
    
    def class_method(self, method_info: Dict[str, Any]) -> str:
        """Template for class method test."""
        return self.basic_function(method_info)
    
    def edge_cases(self, func_info: Dict[str, Any]) -> str:
        """Template for edge case tests."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_edge_cases():',
            f'    """Test {func_name} edge cases."""',
            f'    # Test with None',
            f'    result = {func_name}(None)',
            f'    assert result is not None',
            '',
            f'    # Test with empty values',
            f'    result = {func_name}("")',
            f'    assert result is not None',
        ]
        
        return '\n'.join(test)
    
    def error_handling(self, func_info: Dict[str, Any]) -> str:
        """Template for error handling tests."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_error_handling():',
            f'    """Test {func_name} error handling."""',
            f'    with pytest.raises(Exception):',
            f'        {func_name}(invalid_input)',
        ]
        
        return '\n'.join(test)
    
    def test_header(self, analysis: Dict[str, Any]) -> str:
        """Generate test file header with imports."""
        imports = [
            '"""',
            'Generated test file',
            '"""',
            '',
            'import pytest',
            'from unittest.mock import Mock, patch, MagicMock'
        ]
        
        if analysis.get("has_async"):
            imports.append('import asyncio')
        
        return '\n'.join(imports)
    
    def fixtures(self, analysis: Dict[str, Any]) -> str:
        """Generate pytest fixtures for classes."""
        fixtures = []
        
        for cls in analysis.get("classes", []):
            fixture_code = f'''@pytest.fixture
def {cls["name"].lower()}_instance():
    """Fixture for {cls["name"]} instance."""
    return {cls["name"]}()'''
            fixtures.append(fixture_code)
        
        return '\n\n'.join(fixtures) if fixtures else ""
