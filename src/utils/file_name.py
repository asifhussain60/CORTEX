"""
Filename validation and standardization utility.

This module enforces CORTEX v5 filename standards:
- Maximum 20 characters (excluding extension)
- Kebab-case format (lowercase with hyphens)
- No special characters except hyphens
- Descriptive but concise names

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Tuple, Optional


class FileNameValidator:
    """Validates and suggests filenames according to CORTEX v5 standards."""
    
    MAX_LENGTH = 20
    VALID_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    
    @staticmethod
    def validate_filename(name: str, max_len: int = MAX_LENGTH) -> Tuple[bool, str]:
        """
        Validate a filename against CORTEX v5 standards.
        
        Args:
            name: Filename to validate (without extension)
            max_len: Maximum allowed length (default: 20)
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if filename meets all standards
            - error_message: Empty string if valid, error description otherwise
            
        Examples:
            >>> FileNameValidator.validate_filename("plan-orch-v5")
            (True, "")
            >>> FileNameValidator.validate_filename("Planning_Orchestrator_V5")
            (False, "Must be kebab-case (lowercase with hyphens)")
        """
        if not name:
            return False, "Filename cannot be empty"
        
        # Check length
        if len(name) > max_len:
            return False, f"Filename exceeds {max_len} characters (current: {len(name)})"
        
        # Check for uppercase letters
        if any(c.isupper() for c in name):
            return False, "Must be kebab-case (lowercase with hyphens)"
        
        # Check for underscores
        if '_' in name:
            return False, "Use hyphens (-) instead of underscores (_)"
        
        # Check for leading/trailing hyphens (before pattern check)
        if name.startswith('-') or name.endswith('-'):
            return False, "Cannot start or end with hyphen"
        
        # Check for consecutive hyphens (before pattern check)
        if '--' in name:
            return False, "Cannot contain consecutive hyphens"
        
        # Check pattern (lowercase alphanumeric with hyphens)
        if not FileNameValidator.VALID_PATTERN.match(name):
            return False, "Invalid format. Use lowercase letters, numbers, and hyphens only"
        
        return True, ""
    
    @staticmethod
    def suggest_filename(long_name: str, max_len: int = MAX_LENGTH) -> str:
        """
        Suggest a valid filename based on a long or invalid name.
        
        Args:
            long_name: Original filename to convert
            max_len: Maximum allowed length (default: 20)
            
        Returns:
            Suggested valid filename
            
        Examples:
            >>> FileNameValidator.suggest_filename("Planning_Orchestrator_Version_5")
            "plan-orch-v5"
            >>> FileNameValidator.suggest_filename("MCPServer")
            "mcp-server"
        """
        # Convert to lowercase
        name = long_name.lower()
        
        # Replace underscores and spaces with hyphens
        name = name.replace('_', '-').replace(' ', '-')
        
        # Remove invalid characters
        name = re.sub(r'[^a-z0-9-]', '', name)
        
        # Replace consecutive hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        # If still too long, intelligently shorten
        if len(name) > max_len:
            name = FileNameValidator._intelligent_shorten(name, max_len)
        
        return name
    
    @staticmethod
    def _intelligent_shorten(name: str, max_len: int) -> str:
        """
        Intelligently shorten a name by abbreviating common words.
        
        Args:
            name: Name to shorten
            max_len: Target maximum length
            
        Returns:
            Shortened name
        """
        # Common abbreviations
        abbreviations = {
            'orchestrator': 'orch',
            'database': 'db',
            'configuration': 'config',
            'management': 'mgmt',
            'implementation': 'impl',
            'validation': 'val',
            'generation': 'gen',
            'execution': 'exec',
            'repository': 'repo',
            'application': 'app',
            'operation': 'op',
            'planning': 'plan',
            'version': 'v',
        }
        
        parts = name.split('-')
        shortened_parts = []
        
        for part in parts:
            # Try to abbreviate
            abbreviated = abbreviations.get(part, part)
            shortened_parts.append(abbreviated)
        
        result = '-'.join(shortened_parts)
        
        # If still too long, truncate vowels from middle words
        if len(result) > max_len:
            result = FileNameValidator._remove_vowels_from_middle(shortened_parts, max_len)
        
        # Last resort: truncate
        if len(result) > max_len:
            result = result[:max_len].rstrip('-')
        
        return result
    
    @staticmethod
    def _remove_vowels_from_middle(parts: list, max_len: int) -> str:
        """
        Remove vowels from middle parts to shorten name.
        
        Args:
            parts: List of name parts
            max_len: Target maximum length
            
        Returns:
            Shortened name
        """
        if len(parts) <= 2:
            return '-'.join(parts)
        
        # Keep first and last parts intact, remove vowels from middle
        first = parts[0]
        last = parts[-1]
        middle = parts[1:-1]
        
        shortened_middle = []
        for part in middle:
            # Remove vowels except at start
            shortened = part[0] + re.sub(r'[aeiou]', '', part[1:])
            shortened_middle.append(shortened)
        
        result = '-'.join([first] + shortened_middle + [last])
        
        # If still too long, keep only first and last
        if len(result) > max_len:
            result = f"{first}-{last}"
        
        return result
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Sanitize a filename to make it valid (best effort).
        
        Args:
            name: Filename to sanitize
            
        Returns:
            Sanitized filename that passes validation
            
        Examples:
            >>> FileNameValidator.sanitize_filename("My_File@Name!")
            "my-file-name"
        """
        is_valid, _ = FileNameValidator.validate_filename(name)
        
        if is_valid:
            return name
        
        return FileNameValidator.suggest_filename(name)
    
    @staticmethod
    def validate_path(file_path: str, max_len: int = MAX_LENGTH) -> Tuple[bool, str]:
        """
        Validate a file path's filename component.
        
        Args:
            file_path: Full file path
            max_len: Maximum allowed length (default: 20)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        stem = path.stem  # Filename without extension
        
        return FileNameValidator.validate_filename(stem, max_len)
    
    @staticmethod
    def suggest_path(file_path: str, max_len: int = MAX_LENGTH) -> str:
        """
        Suggest a valid path based on an invalid file path.
        
        Args:
            file_path: Original file path
            max_len: Maximum allowed length (default: 20)
            
        Returns:
            Suggested valid file path
        """
        path = Path(file_path)
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        suggested_stem = FileNameValidator.suggest_filename(stem, max_len)
        suggested_path = parent / f"{suggested_stem}{suffix}"
        
        return str(suggested_path)


# Convenience functions for module-level access
def validate_filename(name: str, max_len: int = 20) -> Tuple[bool, str]:
    """Validate a filename. See FileNameValidator.validate_filename()."""
    return FileNameValidator.validate_filename(name, max_len)


def suggest_filename(long_name: str, max_len: int = 20) -> str:
    """Suggest a valid filename. See FileNameValidator.suggest_filename()."""
    return FileNameValidator.suggest_filename(long_name, max_len)


def sanitize_filename(name: str) -> str:
    """Sanitize a filename. See FileNameValidator.sanitize_filename()."""
    return FileNameValidator.sanitize_filename(name)
