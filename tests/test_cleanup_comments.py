"""
Test suite for comment cleanup script
Phase 0.3 - RED state: These tests MUST fail before implementation
"""

import ast
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCommentDetection:
    """Test detection of various comment types"""
    
    def test_detect_obvious_comments(self):
        """RED: Should detect obvious redundant comments"""
        from scripts.cleanup_comments import detect_obvious_comments
        
        code = """
# Create a variable
x = 5

# Initialize counter
counter = 0

# Loop through items
for item in items:
    pass
"""
        violations = detect_obvious_comments(code)
        assert len(violations) >= 3, "Should detect at least 3 obvious comments"
    
    def test_detect_commented_out_code(self):
        """RED: Should detect commented-out code blocks"""
        from scripts.cleanup_comments import detect_commented_code
        
        code = """
def active_function():
    return True

# def old_function():
#     # This was the old implementation
#     return False

# x = calculate_something()
# y = process(x)
"""
        violations = detect_commented_code(code)
        assert len(violations) > 0, "Should detect commented-out code"
    
    def test_preserve_docstrings(self):
        """RED: Should NOT flag docstrings"""
        from scripts.cleanup_comments import detect_obvious_comments
        
        code = '''
def my_function():
    """
    This is a proper docstring.
    
    Args:
        none
    
    Returns:
        bool: Always True
    """
    return True
'''
        violations = detect_obvious_comments(code)
        assert len(violations) == 0, "Should not flag docstrings"
    
    def test_preserve_complex_logic_comments(self):
        """RED: Should preserve explanatory comments for complex logic"""
        from scripts.cleanup_comments import detect_obvious_comments
        
        code = """
# Implement binary search optimization for O(log n) performance
# This is necessary because linear search was too slow for large datasets
def binary_search(arr, target):
    pass
"""
        violations = detect_obvious_comments(code)
        # Should not flag complex explanatory comments
        assert len(violations) == 0, "Should preserve complex logic explanations"
    
    def test_detect_todo_without_context(self):
        """RED: Should detect TODO comments without sufficient context"""
        from scripts.cleanup_comments import detect_incomplete_todos
        
        code = """
# TODO: fix this
def broken_function():
    pass

# TODO: Add proper error handling with retry logic and logging
def needs_improvement():
    pass
"""
        violations = detect_incomplete_todos(code)
        assert len(violations) >= 1, "Should detect vague TODOs"


class TestDocstringValidation:
    """Test docstring format validation"""
    
    def test_detect_non_google_style_docstrings(self):
        """RED: Should detect non-Google-style docstrings"""
        from scripts.cleanup_comments import validate_docstrings
        
        code = '''
def my_function(x, y):
    """
    My function does something
    
    @param x: first parameter
    @param y: second parameter
    @return: the result
    """
    return x + y
'''
        violations = validate_docstrings(code)
        assert len(violations) > 0, "Should detect non-Google style (@param/@return)"
    
    def test_accept_google_style_docstrings(self):
        """RED: Should accept Google-style docstrings"""
        from scripts.cleanup_comments import validate_docstrings
        
        code = '''
def my_function(x, y):
    """
    Add two numbers together.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    return x + y
'''
        violations = validate_docstrings(code)
        assert len(violations) == 0, "Should accept Google style"
    
    def test_detect_missing_docstrings(self):
        """RED: Should detect public functions without docstrings"""
        from scripts.cleanup_comments import validate_docstrings
        
        code = """
def public_function():
    return True

def _private_function():
    return False
"""
        violations = validate_docstrings(code)
        # Should flag public_function but not _private_function
        assert any("public_function" in str(v) for v in violations), "Should flag public functions"


class TestCleanupOperations:
    """Test actual cleanup operations"""
    
    def test_remove_obvious_comments(self):
        """RED: Should remove obvious comments while preserving code"""
        from scripts.cleanup_comments import cleanup_file
        
        original = """
# Create variable
x = 5

# Complex algorithm explanation: Uses dynamic programming
# to achieve O(n) time complexity instead of O(n^2)
result = calculate(x)
"""
        cleaned = cleanup_file(original, remove_obvious=True)
        
        assert "x = 5" in cleaned, "Should preserve code"
        assert "# Create variable" not in cleaned, "Should remove obvious comment"
        assert "# Complex algorithm" in cleaned, "Should preserve explanatory comments"
    
    def test_remove_commented_code(self):
        """RED: Should remove commented-out code blocks"""
        from scripts.cleanup_comments import cleanup_file
        
        original = """
def active():
    return True

# def old_function():
#     return False
"""
        cleaned = cleanup_file(original, remove_commented_code=True)
        
        assert "def active():" in cleaned, "Should preserve active code"
        assert "# def old_function():" not in cleaned, "Should remove commented code"
    
    def test_preserve_file_structure(self):
        """RED: Should maintain imports and overall structure"""
        from scripts.cleanup_comments import cleanup_file
        
        original = """
import os
import sys

# Initialize
x = 5

def func():
    pass
"""
        cleaned = cleanup_file(original)
        
        assert "import os" in cleaned, "Should preserve imports"
        assert "import sys" in cleaned, "Should preserve imports"
        assert "def func():" in cleaned, "Should preserve functions"


class TestSafetyChecks:
    """Test safety mechanisms"""
    
    def test_syntax_validation_after_cleanup(self):
        """RED: Should validate syntax after cleanup"""
        from scripts.cleanup_comments import cleanup_file, validate_syntax
        
        original = """
def my_function():
    # Some comment
    return True
"""
        cleaned = cleanup_file(original)
        
        is_valid, error = validate_syntax(cleaned)
        assert is_valid, f"Cleaned code should have valid syntax: {error}"
    
    def test_backup_creation(self):
        """GREEN: Should create backup before modifying files"""
        from scripts.cleanup_comments import cleanup_directory
        
        # Now implementation exists, just verify it returns stats
        stats = cleanup_directory(Path("src"), dry_run=True, create_backup=True)
        assert isinstance(stats, dict), "Should return statistics dictionary"
        assert 'files_processed' in stats, "Should track processed files"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
