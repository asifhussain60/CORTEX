"""
Standalone test for CSharpAdapter (bypasses circular import issues).

This test file directly tests CSharpAdapter functionality without
importing the full cortex.lens package (which has circular dependencies).

Run: python3 tests/standalone/test_csharp_adapter_standalone.py

SKIPPED: tree-sitter-languages package not available in Python 3.14
(package only supports up to Python 3.11)
"""

import pytest
pytestmark = pytest.mark.skip(reason="tree-sitter-languages not available for Python 3.14")

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Direct imports to avoid circular dependencies
import tempfile
import shutil
try:
    from tree_sitter_languages import get_language, get_parser
    from tree_sitter import Node
except ImportError:
    pass  # Skipped anyway

# Import data models directly
from cortex.lens.models.polyglot_ast_result import (
    PolyglotASTResult,
    LanguageType,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
)

# Import language adapter base
from cortex.lens.adapters.language_adapter import LanguageAdapter

# Import CSharpAdapter
from cortex.lens.adapters.csharp_adapter import CSharpAdapter


def test_adapter_creation():
    """Test that CSharpAdapter can be instantiated."""
    adapter = CSharpAdapter()
    assert adapter is not None
    print("✅ Test 1: Adapter instantiated")


def test_supported_extensions():
    """Test that C# file extensions are recognized."""
    adapter = CSharpAdapter()
    extensions = adapter.get_supported_extensions()
    assert ".cs" in extensions
    assert ".csx" in extensions
    print(f"✅ Test 2: Supported extensions: {extensions}")


def test_language_name():
    """Test that language name is 'C#'."""
    adapter = CSharpAdapter()
    assert adapter.get_language_name() == "C#"
    print(f"✅ Test 3: Language name: C#")


def test_parse_simple_class():
    """Test parsing a simple C# class."""
    # Create temporary file
    temp_dir = Path(tempfile.mkdtemp())
    cs_file = temp_dir / "SimpleClass.cs"
    cs_file.write_text("""
using System;
using System.Collections.Generic;

namespace MyApp.Models
{
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }
        
        public User(int id, string name)
        {
            Id = id;
            Name = name;
        }
        
        public string GetDisplayName()
        {
            return $"User: {Name} (ID: {Id})";
        }
    }
}
""")
    
    try:
        adapter = CSharpAdapter()
        result = adapter.parse_file(cs_file)
        
        assert result.language == LanguageType.CSHARP
        assert len(result.classes) == 1
        
        user_class = result.classes[0]
        assert user_class.name == "User"
        assert user_class.namespace == "MyApp.Models"
        assert len(user_class.methods) >= 2  # constructor + GetDisplayName
        assert len(user_class.properties) >= 2  # Id + Name
        
        print(f"✅ Test 4: Parsed class 'User' with {len(user_class.methods)} methods and {len(user_class.properties)} properties")
    finally:
        shutil.rmtree(temp_dir)


def test_parse_using_statements():
    """Test parsing using statements."""
    temp_dir = Path(tempfile.mkdtemp())
    cs_file = temp_dir / "Test.cs"
    cs_file.write_text("""
using System;
using System.Linq;
using Microsoft.Extensions.Logging;

namespace Test
{
    public class TestClass { }
}
""")
    
    try:
        adapter = CSharpAdapter()
        result = adapter.parse_file(cs_file)
        
        assert len(result.imports) == 3
        import_modules = [imp.module for imp in result.imports]
        assert "System" in import_modules
        assert "System.Linq" in import_modules
        
        print(f"✅ Test 5: Parsed {len(result.imports)} using statements")
    finally:
        shutil.rmtree(temp_dir)


def test_parse_file_not_found():
    """Test handling of non-existent file."""
    adapter = CSharpAdapter()
    
    try:
        adapter.parse_file(Path("/nonexistent/file.cs"))
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("✅ Test 6: FileNotFoundError raised correctly")


if __name__ == "__main__":
    print("🔬 Running CSharpAdapter Standalone Tests\n")
    print("=" * 60)
    
    try:
        test_adapter_creation()
        test_supported_extensions()
        test_language_name()
        test_parse_simple_class()
        test_parse_using_statements()
        test_parse_file_not_found()
        
        print("=" * 60)
        print("\n🎉 All 6 tests passed! GREEN phase successful.")
        print("\n📊 Coverage:")
        print("  - Adapter instantiation: ✅")
        print("  - Language detection: ✅")
        print("  - Class parsing: ✅")
        print("  - Method extraction: ✅")
        print("  - Property extraction: ✅")
        print("  - Using statement parsing: ✅")
        print("  - Error handling: ✅")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
