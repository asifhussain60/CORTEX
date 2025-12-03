"""
Naming convention enforcer for CORTEX governance.

Automatically detects file types and applies appropriate naming conventions.
"""

import re
from pathlib import Path
from typing import Union, Dict
from src.governance.file_naming_validator import FileNameValidator


class NamingConventionEnforcer:
    """
    Enforces naming conventions based on file type.
    
    Usage:
        enforcer = NamingConventionEnforcer()
        if enforcer.check("userService.py"):
            print("Valid")
        else:
            print("Suggested:", enforcer.suggest_name("userService.py"))
    """
    
    # File type mapping
    FILE_TYPE_MAP = {
        '.py': 'python',
        '.md': 'markdown',
        '.yaml': 'config',
        '.yml': 'config',
        '.json': 'config',
        '.txt': 'text'
    }
    
    # Convention per file type
    CONVENTION_MAP = {
        'python': 'snake_case',
        'markdown': 'kebab-case',
        'config': 'kebab-case',
        'text': 'kebab-case'
    }
    
    def __init__(self):
        """Initialize enforcer with validator."""
        self.validator = FileNameValidator()
    
    def check(self, filename: Union[str, Path]) -> bool:
        """
        Check if filename follows correct naming convention.
        
        Args:
            filename: Filename or path to check
            
        Returns:
            True if valid, False otherwise
        """
        # Use validator which handles all rules
        return self.validator.validate(filename)
    
    def get_file_type(self, filename: Union[str, Path]) -> str:
        """
        Detect file type from extension.
        
        Args:
            filename: Filename or path
            
        Returns:
            File type string (python, markdown, config, text, unknown)
        """
        if isinstance(filename, str):
            filename = Path(filename)
        
        ext = filename.suffix.lower()
        return self.FILE_TYPE_MAP.get(ext, 'unknown')
    
    def get_expected_convention(self, filename: Union[str, Path]) -> str:
        """
        Get expected naming convention for file.
        
        Args:
            filename: Filename or path
            
        Returns:
            Convention name (snake_case, kebab-case, unknown)
        """
        file_type = self.get_file_type(filename)
        return self.CONVENTION_MAP.get(file_type, 'unknown')
    
    def suggest_name(self, filename: Union[str, Path]) -> str:
        """
        Suggest correct name for invalid filename.
        
        Args:
            filename: Invalid filename
            
        Returns:
            Suggested corrected filename
        """
        if isinstance(filename, Path):
            filename = str(filename)
        
        path = Path(filename)
        name = path.stem
        ext = path.suffix
        
        convention = self.get_expected_convention(filename)
        
        if convention == 'snake_case':
            # Convert to snake_case
            # Handle camelCase: userService → user_service
            name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
            # Handle PascalCase: UserService → user_service
            name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', name)
            name = name.lower()
            # Replace hyphens with underscores
            name = name.replace('-', '_')
            
        elif convention == 'kebab-case':
            # Convert to kebab-case
            # Handle camelCase
            name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
            # Handle PascalCase
            name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1-\2', name)
            name = name.lower()
            # Replace underscores with hyphens
            name = name.replace('_', '-')
        
        return name + ext
    
    def check_batch(self, filenames: list) -> Dict[str, dict]:
        """
        Check multiple files at once.
        
        Args:
            filenames: List of filenames to check
            
        Returns:
            Dict mapping filename to validation result with details
        """
        results = {}
        
        for filename in filenames:
            is_valid = self.check(filename)
            
            result = {
                'valid': is_valid,
                'file_type': self.get_file_type(filename),
                'expected_convention': self.get_expected_convention(filename)
            }
            
            if not is_valid:
                result['suggested_name'] = self.suggest_name(filename)
                result['violations'] = self.validator.get_violations(filename)
            
            results[str(filename)] = result
        
        return results
