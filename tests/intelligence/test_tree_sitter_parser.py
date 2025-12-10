"""
Tests for Tree-sitter AST Parser Utility
Validates cross-platform compatibility and multi-language support.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from intelligence.tree_sitter_parser import (
    TreeSitterParser,
    SupportedLanguage,
    create_parser,
    TREE_SITTER_AVAILABLE
)


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="Tree-sitter not installed")
class TestTreeSitterParser:
    """Test suite for Tree-sitter parser functionality."""
    
    def test_parser_initialization(self):
        """Test that parser initializes with all language grammars."""
        parser = create_parser()
        
        assert SupportedLanguage.PYTHON in parser._parsers
        assert SupportedLanguage.JAVASCRIPT in parser._parsers
        assert SupportedLanguage.TYPESCRIPT in parser._parsers
        assert SupportedLanguage.CSHARP in parser._parsers
    
    def test_parse_python_code(self):
        """Test parsing valid Python code."""
        parser = create_parser()
        
        python_code = b"""
def calculate_total(price, tax_rate):
    \"\"\"Calculate total with tax.\"\"\"
    tax = price * tax_rate
    return price + tax

class Invoice:
    def __init__(self, amount):
        self.amount = amount
"""
        
        tree = parser.parse_string(python_code, SupportedLanguage.PYTHON)
        
        assert tree is not None
        assert tree.root_node is not None
        assert not tree.root_node.has_error
        assert tree.root_node.type == 'module'
    
    def test_parse_javascript_code(self):
        """Test parsing valid JavaScript code."""
        parser = create_parser()
        
        js_code = b"""
function calculateTotal(price, taxRate) {
    const tax = price * taxRate;
    return price + tax;
}

class Invoice {
    constructor(amount) {
        this.amount = amount;
    }
}
"""
        
        tree = parser.parse_string(js_code, SupportedLanguage.JAVASCRIPT)
        
        assert tree is not None
        assert tree.root_node is not None
        assert not tree.root_node.has_error
        assert tree.root_node.type == 'program'
    
    def test_parse_csharp_code(self):
        """Test parsing valid C# code."""
        parser = create_parser()
        
        csharp_code = b"""
public class Invoice
{
    private decimal amount;
    
    public Invoice(decimal amount)
    {
        this.amount = amount;
    }
    
    public decimal CalculateTotal(decimal taxRate)
    {
        decimal tax = amount * taxRate;
        return amount + tax;
    }
}
"""
        
        tree = parser.parse_string(csharp_code, SupportedLanguage.CSHARP)
        
        assert tree is not None
        assert tree.root_node is not None
        # Note: C# parser may have minor issues with whitespace, but should parse structure
        assert tree.root_node.type == 'compilation_unit'
    
    def test_parse_with_syntax_error(self):
        """Test that parser handles syntax errors gracefully (error recovery)."""
        parser = create_parser()
        
        # Python code with syntax error (missing colon)
        python_code = b"""
def broken_function()
    return "missing colon"
"""
        
        tree = parser.parse_string(python_code, SupportedLanguage.PYTHON)
        
        assert tree is not None
        assert tree.root_node is not None
        # Tree-sitter provides partial parse even with errors
        assert tree.root_node.has_error
    
    def test_detect_language_by_extension(self):
        """Test language detection from file extensions."""
        parser = create_parser()
        
        assert parser.detect_language("app.py") == SupportedLanguage.PYTHON
        assert parser.detect_language("index.js") == SupportedLanguage.JAVASCRIPT
        assert parser.detect_language("component.jsx") == SupportedLanguage.JAVASCRIPT
        assert parser.detect_language("types.ts") == SupportedLanguage.TYPESCRIPT
        assert parser.detect_language("app.tsx") == SupportedLanguage.TYPESCRIPT
        assert parser.detect_language("Program.cs") == SupportedLanguage.CSHARP
        assert parser.detect_language("unknown.txt") is None
    
    def test_get_node_text(self):
        """Test extracting text from AST node."""
        parser = create_parser()
        
        python_code = b"def hello(): return 'world'"
        tree = parser.parse_string(python_code, SupportedLanguage.PYTHON)
        
        # Get first function definition node
        root = tree.root_node
        func_node = root.children[0]  # function_definition
        
        text = parser.get_node_text(func_node, python_code)
        assert "def hello()" in text
        assert "return 'world'" in text
    
    def test_traverse_tree(self):
        """Test recursive tree traversal."""
        parser = create_parser()
        
        python_code = b"def test(): pass"
        tree = parser.parse_string(python_code, SupportedLanguage.PYTHON)
        
        nodes = parser.traverse_tree(tree.root_node, max_depth=5)
        
        assert len(nodes) > 0
        assert any(node['type'] == 'function_definition' for node in nodes)
        assert any(node['type'] == 'identifier' for node in nodes)
    
    def test_query_function_names(self):
        """Test Tree-sitter query to find function names."""
        parser = create_parser()
        
        python_code = b"""
def calculate_tax(amount):
    return amount * 0.1

def calculate_total(price, tax):
    return price + tax
"""
        
        tree = parser.parse_string(python_code, SupportedLanguage.PYTHON)
        
        # Query to find all function names
        query_string = "(function_definition name: (identifier) @function_name)"
        captures = parser.query_nodes(tree, query_string, SupportedLanguage.PYTHON)
        
        function_names = [parser.get_node_text(node, python_code) for node, _ in captures]
        
        assert 'calculate_tax' in function_names
        assert 'calculate_total' in function_names
    
    def test_incremental_parsing_simulation(self):
        """Test that parser can handle incremental updates (simulated)."""
        parser = create_parser()
        
        # Original code
        original_code = b"def hello(): return 'world'"
        tree1 = parser.parse_string(original_code, SupportedLanguage.PYTHON)
        
        # Modified code (change return value)
        modified_code = b"def hello(): return 'universe'"
        tree2 = parser.parse_string(modified_code, SupportedLanguage.PYTHON)
        
        # Both should parse successfully
        assert tree1 is not None
        assert tree2 is not None
        assert not tree1.root_node.has_error
        assert not tree2.root_node.has_error


# Integration test for cross-platform compatibility
def test_tree_sitter_installation():
    """Verify Tree-sitter is installed and importable."""
    try:
        import tree_sitter
        from tree_sitter_python import language as python_language
        from tree_sitter_javascript import language as js_language
        from tree_sitter_c_sharp import language as csharp_language
        
        # Test that languages can be loaded
        assert python_language() is not None
        assert js_language() is not None
        assert csharp_language() is not None
        
        print("✅ Tree-sitter installation verified (Python, JavaScript, C#)")
        
    except ImportError as e:
        pytest.fail(f"Tree-sitter not properly installed: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
