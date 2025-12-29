"""
Language Detector - Programming Language Detection

Detects programming language from file extensions and content.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Detects programming language from file characteristics.
    
    Uses extension-based detection with fallback to content analysis.
    """
    
    # Extension to language mapping
    EXTENSION_MAP: Dict[str, str] = {
        ".py": "python",
        ".cs": "csharp",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sql": "sql",
        ".sh": "shell",
        ".bash": "shell",
        ".ps1": "powershell",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".md": "markdown",
        ".txt": "text",
    }
    
    def detect(self, file_path: Path) -> str:
        """
        Detect language from file path.
        
        Args:
            file_path: Path to file
        
        Returns:
            Language identifier (lowercase)
        """
        # Get extension (lowercase)
        extension = file_path.suffix.lower()
        
        # Look up in extension map
        language = self.EXTENSION_MAP.get(extension)
        
        if language:
            return language
        
        # Unknown extension
        return "unknown"
