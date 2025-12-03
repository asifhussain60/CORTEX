"""
File naming validator for CORTEX governance.

Enforces consistent file naming conventions:
- snake_case for Python files (.py)
- kebab-case for markdown files (.md, .txt, .yaml, .json)
- No spaces allowed
- Max length 100 characters
- Allowed characters: [a-z0-9_-.]
- Common exceptions: LICENSE, VERSION, README.md, etc.
"""

import re
from pathlib import Path
from typing import Union, List


class FileNameValidator:
    """
    Validates file names against CORTEX naming conventions.
    
    Usage:
        validator = FileNameValidator()
        if validator.validate("user_service.py"):
            print("Valid filename")
        else:
            print("Violations:", validator.get_violations("user_service.py"))
    """
    
    # Naming convention patterns
    SNAKE_CASE_PATTERN = re.compile(r'^[a-z0-9_]+$')
    KEBAB_CASE_PATTERN = re.compile(r'^[a-z0-9-]+$')
    
    # File extension to naming convention mapping
    SNAKE_CASE_EXTENSIONS = {'.py'}
    KEBAB_CASE_EXTENSIONS = {'.md', '.txt', '.yaml', '.yml', '.json'}
    
    # Common exception filenames (case-sensitive)
    ALLOWED_EXCEPTIONS = {
        'LICENSE', 'VERSION', 'README.md', 'CHANGELOG.md',
        'Makefile', '.gitignore', '.gitattributes',
        'Dockerfile', 'Procfile'
    }
    
    # Max filename length (including extension)
    MAX_FILENAME_LENGTH = 100
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate(self, filename: Union[str, Path]) -> bool:
        """
        Validate a filename against naming conventions.
        
        Args:
            filename: Filename or path to validate (only filename is checked)
            
        Returns:
            True if valid, False otherwise
        """
        # Extract just the filename from path
        if isinstance(filename, Path):
            filename = filename.name
        else:
            filename = Path(filename).name
        
        # Check if it's an allowed exception
        if filename in self.ALLOWED_EXCEPTIONS:
            return True
        
        # Get violations
        violations = self.get_violations(filename)
        
        return len(violations) == 0
    
    def get_violations(self, filename: Union[str, Path]) -> List[str]:
        """
        Get list of naming violations for a filename.
        
        Args:
            filename: Filename or path to check
            
        Returns:
            List of violation messages (empty if valid)
        """
        # Extract just the filename from path
        if isinstance(filename, Path):
            filename = filename.name
        else:
            filename = Path(filename).name
        
        violations = []
        
        # Check if it's an allowed exception
        if filename in self.ALLOWED_EXCEPTIONS:
            return []
        
        # Check for spaces
        if ' ' in filename:
            violations.append("Filename contains spaces (use snake_case or kebab-case)")
        
        # Check length
        if len(filename) > self.MAX_FILENAME_LENGTH:
            violations.append(f"Filename exceeds {self.MAX_FILENAME_LENGTH} characters (length: {len(filename)})")
        
        # Get extension
        path = Path(filename)
        extension = path.suffix.lower()
        name_without_ext = path.stem
        
        # Check naming convention based on extension
        if extension in self.SNAKE_CASE_EXTENSIONS:
            # Python files: should be snake_case
            if not self.SNAKE_CASE_PATTERN.match(name_without_ext):
                violations.append(f"Python files must use snake_case (found: {name_without_ext})")
        
        elif extension in self.KEBAB_CASE_EXTENSIONS:
            # Markdown/config files: should be kebab-case
            # Allow uppercase for special files like README
            name_lower = name_without_ext.lower()
            if not self.KEBAB_CASE_PATTERN.match(name_lower):
                violations.append(f"Markdown/config files must use kebab-case (found: {name_without_ext})")
        
        # Check for special characters (except allowed ones)
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-.')
        for char in filename.lower():
            if char not in allowed_chars:
                violations.append(f"Filename contains invalid character: '{char}' (allowed: a-z, 0-9, _, -, .)")
                break
        
        return violations
