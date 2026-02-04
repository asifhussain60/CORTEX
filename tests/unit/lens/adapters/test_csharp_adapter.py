"""
Unit tests for CSharpAdapter (Phase 1).

Tests C# AST parsing using tree-sitter.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from cortex.lens.adapters.csharp_adapter import CSharpAdapter
from cortex.lens.models.polyglot_ast_result import PolyglotASTResult


@pytest.fixture
def temp_csharp_file():
    """Create temporary C# file for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def simple_csharp_class(temp_csharp_file):
    """Fixture for simple C# class."""
    cs_file = temp_csharp_file / "User.cs"
    cs_file.write_text("""using System;

public class User
{
    public string Name { get; set; }
    public int Age { get; set; }
    
    public void PrintInfo()
    {
        Console.WriteLine($"{Name} is {Age} years old");
    }
}
""")
    return cs_file


class TestCSharpAdapter:
    """Test CSharpAdapter parsing capabilities."""
    
    def test_adapter_creation(self):
        """Test that CSharpAdapter can be instantiated."""
        adapter = CSharpAdapter()
        assert adapter is not None
    
    def test_supported_extensions(self):
        """Test that C# file extensions are recognized."""
        adapter = CSharpAdapter()
        extensions = adapter.get_supported_extensions()
        assert ".cs" in extensions
        assert ".csx" in extensions
    
    def test_language_name(self):
        """Test that language name is C#."""
        adapter = CSharpAdapter()
        assert adapter.get_language_name() == "C#"
    
    def test_parse_simple_class(self, simple_csharp_class):
        """Test parsing a simple C# class."""
        adapter = CSharpAdapter()
        result = adapter.parse_file(simple_csharp_class)
        
        assert isinstance(result, PolyglotASTResult)
        assert len(result.classes) == 1
        assert result.classes[0].name == "User"
        assert len(result.classes[0].properties) >= 2  # Name, Age
        assert len(result.classes[0].methods) >= 1  # PrintInfo
    
    def test_parse_class_methods(self, simple_csharp_class):
        """Test parsing methods from a class."""
        adapter = CSharpAdapter()
        result = adapter.parse_file(simple_csharp_class)
        
        user_class = result.classes[0]
        method_names = [m.name for m in user_class.methods]
        assert "PrintInfo" in method_names
    
    def test_parse_class_properties(self, simple_csharp_class):
        """Test parsing properties from a class."""
        adapter = CSharpAdapter()
        result = adapter.parse_file(simple_csharp_class)
        
        user_class = result.classes[0]
        property_names = [p["name"] for p in user_class.properties]
        assert "Name" in property_names
        assert "Age" in property_names
    
    def test_parse_using_statements(self, simple_csharp_class):
        """Test parsing using statements (imports)."""
        adapter = CSharpAdapter()
        result = adapter.parse_file(simple_csharp_class)
        
        import_modules = [imp.module for imp in result.imports]
        assert "System" in import_modules
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent file."""
        adapter = CSharpAdapter()
        with pytest.raises(FileNotFoundError):
            adapter.parse_file(Path("/nonexistent/file.cs"))
