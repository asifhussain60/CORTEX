"""
Tests for CommentExtractor.

Authority: CORE-008 (TDD - Tests BEFORE code)
"""

from pathlib import Path
from typing import List

import pytest

from cortex.brain.analysis.comment_extractor import (
    CommentExtractor,
    Comment,
    DocstringInfo,
    CommentExtractionResult,
)


class TestComment:
    """Test Comment dataclass."""
    
    def test_comment_creation(self):
        """Test creating a Comment."""
        comment = Comment(
            line_number=10,
            content="TODO: Fix this",
            comment_type="inline",
        )
        assert comment.line_number == 10
        assert comment.content == "TODO: Fix this"
        assert comment.comment_type == "inline"


class TestDocstringInfo:
    """Test DocstringInfo dataclass."""
    
    def test_docstring_info_creation(self):
        """Test creating DocstringInfo."""
        docstring = DocstringInfo(
            target_name="my_function",
            target_type="function",
            content="This is a docstring.",
            line_number=5,
            style="google",
        )
        assert docstring.target_name == "my_function"
        assert docstring.target_type == "function"
        assert docstring.style == "google"


class TestCommentExtractor:
    """Test CommentExtractor functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return CommentExtractor()
    
    def test_extractor_initialization(self, extractor: CommentExtractor):
        """Test extractor initialization."""
        assert extractor is not None
    
    def test_extract_inline_comments(self, extractor: CommentExtractor):
        """Test extracting inline comments."""
        code = '''
x = 10  # This is an inline comment
y = 20  # Another comment
z = x + y
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.comments) == 2
        assert result.comments[0].content == "This is an inline comment"
        assert result.comments[0].comment_type == "inline"
        assert result.comments[1].line_number == 3
    
    def test_extract_block_comments(self, extractor: CommentExtractor):
        """Test extracting block comments."""
        code = '''
# This is a block comment
# spanning multiple lines
# with useful information
def my_function():
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        # Should have 3 comments (one per line)
        assert len(result.comments) >= 3
        assert all(c.comment_type == "block" for c in result.comments[:3])
    
    def test_extract_function_docstring(self, extractor: CommentExtractor):
        """Test extracting function docstring."""
        code = '''
def calculate(x, y):
    """
    Calculate the sum of two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        The sum of x and y
    """
    return x + y
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.docstrings) == 1
        assert result.docstrings[0].target_name == "calculate"
        assert result.docstrings[0].target_type == "function"
        assert "sum of two numbers" in result.docstrings[0].content.lower()
    
    def test_extract_class_docstring(self, extractor: CommentExtractor):
        """Test extracting class docstring."""
        code = '''
class Calculator:
    """A simple calculator class."""
    
    def add(self, x, y):
        """Add two numbers."""
        return x + y
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.docstrings) >= 1
        
        # Find class docstring
        class_docstrings = [d for d in result.docstrings if d.target_type == "class"]
        assert len(class_docstrings) == 1
        assert class_docstrings[0].target_name == "Calculator"
        assert "calculator class" in class_docstrings[0].content.lower()
    
    def test_extract_module_docstring(self, extractor: CommentExtractor):
        """Test extracting module-level docstring."""
        code = '''
"""
This is a module-level docstring.
It describes the entire module.
"""

def some_function():
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        # Should have module docstring
        module_docstrings = [d for d in result.docstrings if d.target_type == "module"]
        assert len(module_docstrings) == 1
        assert "module-level docstring" in module_docstrings[0].content.lower()
    
    def test_extract_todo_comments(self, extractor: CommentExtractor):
        """Test extracting TODO comments."""
        code = '''
# TODO: Implement this feature
def placeholder():
    pass  # FIXME: This is broken

# HACK: Temporary workaround
x = 10
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        
        # Should detect TODO/FIXME/HACK tags
        todo_comments = [c for c in result.comments if "TODO" in c.content]
        fixme_comments = [c for c in result.comments if "FIXME" in c.content]
        hack_comments = [c for c in result.comments if "HACK" in c.content]
        
        assert len(todo_comments) == 1
        assert len(fixme_comments) == 1
        assert len(hack_comments) == 1
    
    def test_extract_multiline_string_not_docstring(self, extractor: CommentExtractor):
        """Test that multiline strings that aren't docstrings are not extracted."""
        code = '''
def my_function():
    """This is a docstring."""
    text = """
    This is just a string variable,
    not a docstring.
    """
    return text
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        # Should only have one docstring (the function docstring)
        assert len(result.docstrings) == 1
        assert result.docstrings[0].target_name == "my_function"
    
    def test_detect_docstring_style_google(self, extractor: CommentExtractor):
        """Test detecting Google-style docstrings."""
        code = '''
def function():
    """
    Short description.
    
    Args:
        param: Description
    
    Returns:
        Return value
    """
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.docstrings) == 1
        assert result.docstrings[0].style == "google"
    
    def test_detect_docstring_style_numpy(self, extractor: CommentExtractor):
        """Test detecting NumPy-style docstrings."""
        code = '''
def function():
    """
    Short description.
    
    Parameters
    ----------
    param : type
        Description
    
    Returns
    -------
    type
        Description
    """
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.docstrings) == 1
        assert result.docstrings[0].style == "numpy"
    
    def test_detect_docstring_style_sphinx(self, extractor: CommentExtractor):
        """Test detecting Sphinx-style docstrings."""
        code = '''
def function():
    """
    Short description.
    
    :param param: Description
    :type param: type
    :return: Return value
    :rtype: type
    """
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert len(result.docstrings) == 1
        assert result.docstrings[0].style == "sphinx"
    
    def test_extract_from_file(self, extractor: CommentExtractor, tmp_path: Path):
        """Test extracting comments from a file."""
        file_path = tmp_path / "test.py"
        file_path.write_text('''
# File header comment
def hello():
    """Say hello."""
    return "Hello"  # Return greeting
''')
        
        result = extractor.extract_from_file(file_path)
        
        assert result.success is True
        assert len(result.comments) >= 1
        assert len(result.docstrings) == 1
    
    def test_extract_from_nonexistent_file(self, extractor: CommentExtractor):
        """Test extracting from non-existent file."""
        result = extractor.extract_from_file(Path("/nonexistent/file.py"))
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_extract_with_syntax_error(self, extractor: CommentExtractor):
        """Test extracting from code with syntax errors."""
        code = '''
def broken(
    # Missing closing parenthesis
'''
        result = extractor.extract_comments(code)
        
        # Should still extract the comment even with syntax error
        assert result.success is True
        assert len(result.comments) >= 1
    
    def test_count_comment_types(self, extractor: CommentExtractor):
        """Test counting different comment types."""
        code = '''
# Block comment
x = 10  # Inline comment
def func():
    """Docstring"""
    pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        assert "inline_count" in result.metadata
        assert "block_count" in result.metadata
        assert "docstring_count" in result.metadata
        assert result.metadata["inline_count"] == 1
        assert result.metadata["block_count"] == 1
        assert result.metadata["docstring_count"] == 1
    
    def test_extract_method_docstrings(self, extractor: CommentExtractor):
        """Test extracting method docstrings from classes."""
        code = '''
class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Constructor docstring."""
        pass
    
    def method(self):
        """Method docstring."""
        pass
'''
        result = extractor.extract_comments(code)
        
        assert result.success is True
        # Should have 3 docstrings: class + 2 methods
        assert len(result.docstrings) == 3
        
        method_docstrings = [d for d in result.docstrings if d.target_type == "function"]
        assert len(method_docstrings) == 2


class TestCommentIntegration:
    """Integration tests for comment extraction."""
    
    def test_extract_from_real_module(self, tmp_path: Path):
        """Test extracting from a complete module."""
        file_path = tmp_path / "module.py"
        file_path.write_text('''
"""
Module for data processing.

This module contains utilities for processing data.
"""

# Import required modules
import os
from typing import List

class DataProcessor:
    """Process data efficiently."""
    
    def __init__(self, data: List[str]):
        """
        Initialize the processor.
        
        Args:
            data: List of strings to process
        """
        self.data = data  # Store data
    
    def process(self) -> List[str]:
        """Process the stored data."""
        # TODO: Add more processing steps
        return [item.upper() for item in self.data]  # Convert to uppercase
''')
        
        extractor = CommentExtractor()
        result = extractor.extract_from_file(file_path)
        
        assert result.success is True
        # Should have module, class, and method docstrings
        assert len(result.docstrings) >= 3
        # Should have inline comments and TODO
        assert len(result.comments) >= 2
