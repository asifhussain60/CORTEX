"""
Language Detector

Auto-detects programming language from file extension and content.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from enum import Enum
from pathlib import Path
from typing import Optional


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"
    UNKNOWN = "unknown"


class LanguageDetector:
    """Detects programming language from file extension and content"""
    
    # Extension to language mapping
    EXTENSION_MAP = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.jsx': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.tsx': Language.TYPESCRIPT,
        '.cs': Language.CSHARP,
    }
    
    @classmethod
    def detect_from_file(cls, file_path: str) -> Language:
        """
        Detect language from file path
        
        Args:
            file_path: Path to source file
            
        Returns:
            Detected Language enum
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        return cls.EXTENSION_MAP.get(extension, Language.UNKNOWN)
    
    @classmethod
    def detect_from_extension(cls, extension: str) -> Language:
        """
        Detect language from file extension
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            Detected Language enum
        """
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        extension = extension.lower()
        return cls.EXTENSION_MAP.get(extension, Language.UNKNOWN)
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if file language is supported
        
        Args:
            file_path: Path to source file
            
        Returns:
            True if language is supported
        """
        language = cls.detect_from_file(file_path)
        return language != Language.UNKNOWN
