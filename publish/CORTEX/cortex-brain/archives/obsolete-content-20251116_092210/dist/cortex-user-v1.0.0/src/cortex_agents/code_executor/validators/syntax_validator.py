"""Syntax validation for code files."""

import os
import ast
from typing import Tuple, Optional


class SyntaxValidator:
    """Validates syntax of code files before execution."""
    
    # File extensions that require syntax validation
    SYNTAX_CHECK_EXTENSIONS = [".py", ".js", ".ts", ".jsx", ".tsx"]
    
    def should_validate(self, file_path: str) -> bool:
        """
        Check if file should have syntax validation.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if syntax should be validated
        """
        ext = os.path.splitext(file_path)[1]
        return ext in self.SYNTAX_CHECK_EXTENSIONS
    
    def validate(self, content: str, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate syntax of code content.
        
        Args:
            content: Code content to validate
            file_path: File path (for determining language)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        ext = os.path.splitext(file_path)[1]
        
        if ext == ".py":
            return self._validate_python(content)
        elif ext in [".js", ".jsx"]:
            return self._validate_javascript(content)
        elif ext in [".ts", ".tsx"]:
            return self._validate_typescript(content)
        
        # Default: no validation available
        return True, None
    
    def _validate_python(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python syntax.
        
        Args:
            content: Python code to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Python syntax error on line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Python validation error: {str(e)}"
    
    def _validate_javascript(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JavaScript syntax (basic check).
        
        Args:
            content: JavaScript code to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - could integrate with eslint or similar
        # For now, just check for obvious issues
        if not content.strip():
            return False, "Empty JavaScript file"
        
        # Could add more sophisticated checks here
        return True, None
    
    def _validate_typescript(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate TypeScript syntax (basic check).
        
        Args:
            content: TypeScript code to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - could integrate with tsc or similar
        # For now, just check for obvious issues
        if not content.strip():
            return False, "Empty TypeScript file"
        
        # Could add more sophisticated checks here
        return True, None
