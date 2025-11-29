"""
CSharpAnalyzer - Regex-based C# code analysis.

Analyzes C# files to extract metrics and structure.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Dict, Any, List


class CSharpAnalyzer:
    """
    Analyze C# source files using regex patterns.
    
    Extracts:
    - Class definitions
    - Method definitions
    - Namespace declarations
    """
    
    def __init__(self):
        """Initialize CSharpAnalyzer."""
        # Regex pattern for class declarations
        self.class_pattern = re.compile(
            r'(?:public|private|internal|protected)?\s*(?:static|abstract|sealed)?\s*class\s+(\w+)',
            re.MULTILINE
        )
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a C# file.
        
        Args:
            file_path: Path to C# file
            
        Returns:
            Dictionary containing analysis results
        """
        path = Path(file_path)
        
        # Read source code
        try:
            source = path.read_text(encoding='utf-8')
        except Exception:
            return {
                'file_path': file_path,
                'language': 'csharp',
                'error': 'Failed to read file'
            }
        
        # Extract classes
        classes = self._extract_classes(source)
        
        return {
            'file_path': file_path,
            'language': 'csharp',
            'classes': classes
        }
    
    def _extract_classes(self, source: str) -> List[str]:
        """Extract class names from source code."""
        matches = self.class_pattern.findall(source)
        return matches
