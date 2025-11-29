"""
JavaScriptAnalyzer - Regex-based JavaScript/TypeScript code analysis.

Analyzes JS/TS files to extract metrics and structure.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Dict, Any, List


class JavaScriptAnalyzer:
    """
    Analyze JavaScript/TypeScript source files using regex patterns.
    
    Extracts:
    - Function definitions
    - Class definitions
    - Import/export statements
    """
    
    def __init__(self):
        """Initialize JavaScriptAnalyzer."""
        # Regex patterns
        self.function_pattern = re.compile(
            r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\(.*?\)\s*=>))',
            re.MULTILINE
        )
        self.class_pattern = re.compile(
            r'class\s+(\w+)',
            re.MULTILINE
        )
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a JavaScript/TypeScript file.
        
        Args:
            file_path: Path to JS/TS file
            
        Returns:
            Dictionary containing analysis results
        """
        path = Path(file_path)
        language = 'typescript' if path.suffix in ['.ts', '.tsx'] else 'javascript'
        
        # Read source code
        try:
            source = path.read_text(encoding='utf-8')
        except Exception:
            return {
                'file_path': file_path,
                'language': language,
                'error': 'Failed to read file'
            }
        
        # Extract functions and classes
        functions = self._extract_functions(source)
        classes = self._extract_classes(source)
        
        return {
            'file_path': file_path,
            'language': language,
            'functions': functions,
            'classes': classes
        }
    
    def _extract_functions(self, source: str) -> List[str]:
        """Extract function names from source code."""
        matches = self.function_pattern.findall(source)
        # findall returns tuples due to multiple groups
        functions = []
        for match in matches:
            # Get first non-empty group
            name = match[0] if match[0] else match[1]
            if name:
                functions.append(name)
        return functions
    
    def _extract_classes(self, source: str) -> List[str]:
        """Extract class names from source code."""
        matches = self.class_pattern.findall(source)
        return matches
