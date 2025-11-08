"""Tests for CodeExecutor validators."""

import tempfile
from pathlib import Path

from src.cortex_agents.code_executor.validators import SyntaxValidator


class TestSyntaxValidator:
    """Test SyntaxValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = SyntaxValidator()
        assert validator is not None
        assert len(validator.SYNTAX_CHECK_EXTENSIONS) > 0
    
    def test_should_validate_python(self):
        """Test Python files should be validated."""
        validator = SyntaxValidator()
        assert validator.should_validate("test.py") is True
        assert validator.should_validate("module.py") is True
    
    def test_should_validate_javascript(self):
        """Test JavaScript files should be validated."""
        validator = SyntaxValidator()
        assert validator.should_validate("script.js") is True
        assert validator.should_validate("component.jsx") is True
    
    def test_should_validate_typescript(self):
        """Test TypeScript files should be validated."""
        validator = SyntaxValidator()
        assert validator.should_validate("module.ts") is True
        assert validator.should_validate("component.tsx") is True
    
    def test_should_not_validate_other_files(self):
        """Test non-code files should not be validated."""
        validator = SyntaxValidator()
        assert validator.should_validate("readme.md") is False
        assert validator.should_validate("config.json") is False
        assert validator.should_validate("style.css") is False
    
    def test_validate_valid_python(self):
        """Test validation of valid Python code."""
        validator = SyntaxValidator()
        content = "def hello():\n    return 'world'"
        
        is_valid, error = validator.validate(content, "test.py")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_python(self):
        """Test validation of invalid Python code."""
        validator = SyntaxValidator()
        content = "def hello(\n    return 'world'"  # Missing closing paren
        
        is_valid, error = validator.validate(content, "test.py")
        
        assert is_valid is False
        assert error is not None
        assert "syntax error" in error.lower()
    
    def test_validate_empty_python(self):
        """Test validation of empty Python file."""
        validator = SyntaxValidator()
        content = ""
        
        is_valid, error = validator.validate(content, "test.py")
        
        # Empty file is valid Python
        assert is_valid is True
    
    def test_validate_python_with_imports(self):
        """Test validation of Python with imports."""
        validator = SyntaxValidator()
        content = """
import os
from pathlib import Path

def process_file(path):
    return Path(path).read_text()
"""
        
        is_valid, error = validator.validate(content, "test.py")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_python_indentation_error(self):
        """Test validation catches indentation errors."""
        validator = SyntaxValidator()
        content = """
def hello():
print('bad indentation')
"""
        
        is_valid, error = validator.validate(content, "test.py")
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_javascript_basic(self):
        """Test basic JavaScript validation."""
        validator = SyntaxValidator()
        content = "function hello() { return 'world'; }"
        
        is_valid, error = validator.validate(content, "test.js")
        
        # Basic validation passes
        assert is_valid is True
    
    def test_validate_empty_javascript(self):
        """Test validation of empty JavaScript file."""
        validator = SyntaxValidator()
        content = ""
        
        is_valid, error = validator.validate(content, "test.js")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_typescript_basic(self):
        """Test basic TypeScript validation."""
        validator = SyntaxValidator()
        content = "function hello(): string { return 'world'; }"
        
        is_valid, error = validator.validate(content, "test.ts")
        
        # Basic validation passes
        assert is_valid is True
