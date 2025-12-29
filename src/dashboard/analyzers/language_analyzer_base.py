"""
Base class for language-specific analyzers.
Provides common interface and utilities for all analyzers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Standard result format for language analysis."""
    file_path: str
    language: str
    classes: List[Dict[str, Any]]
    methods: List[Dict[str, Any]]
    complexity: Dict[str, float]
    dependencies: List[str]
    patterns: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: List[str]


class LanguageAnalyzer(ABC):
    """
    Abstract base class for language-specific analyzers.
    
    All language analyzers (C#, TypeScript, ColdFusion, SQL) inherit from this class
    and implement the analyze() method.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize language analyzer.
        
        Args:
            encoding: File encoding (default: utf-8)
        """
        self.encoding = encoding
        self.errors = []
    
    @abstractmethod
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze a source file and extract language-specific metrics.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            AnalysisResult with extracted data
        """
        pass
    
    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this analyzer supports the given file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if analyzer supports this file type
        """
        pass
    
    def read_file(self, file_path: Path) -> str:
        """
        Read file content with error handling.
        
        Args:
            file_path: Path to read
            
        Returns:
            File content as string, empty string if error
        """
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {str(e)}")
            return ""
    
    def calculate_cyclomatic_complexity(self, content: str, language: str) -> int:
        """
        Calculate cyclomatic complexity for given content.
        
        Args:
            content: Source code content
            language: Programming language
            
        Returns:
            Cyclomatic complexity value
        """
        # Basic pattern-based complexity calculation
        # Override in subclasses for more accurate language-specific calculation
        
        complexity_keywords = {
            'csharp': ['if', 'else', 'for', 'foreach', 'while', 'case', 'catch', '&&', '||', '??'],
            'typescript': ['if', 'else', 'for', 'while', 'case', 'catch', '&&', '||', '?'],
            'javascript': ['if', 'else', 'for', 'while', 'case', 'catch', '&&', '||', '?'],
            'sql': ['IF', 'ELSE', 'CASE', 'WHEN', 'WHILE', 'FOR', 'AND', 'OR'],
            'coldfusion': ['cfif', 'cfelseif', 'cfloop', 'cfcase', 'cfcatch']
        }
        
        keywords = complexity_keywords.get(language.lower(), [])
        count = 1  # Base complexity
        
        content_lower = content.lower()
        for keyword in keywords:
            count += content_lower.count(keyword.lower())
        
        return count
    
    def extract_imports(self, content: str, language: str) -> List[str]:
        """
        Extract import/using statements.
        
        Args:
            content: Source code content
            language: Programming language
            
        Returns:
            List of imported modules/namespaces
        """
        # Basic import extraction - override in subclasses
        imports = []
        
        import_patterns = {
            'csharp': 'using',
            'typescript': 'import',
            'javascript': 'import',
            'coldfusion': 'cfimport'
        }
        
        pattern = import_patterns.get(language.lower())
        if pattern:
            for line in content.split('\n'):
                if pattern in line:
                    imports.append(line.strip())
        
        return imports
    
    def detect_patterns(self, content: str, patterns: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Detect code patterns by keywords.
        
        Args:
            content: Source code content
            patterns: Dict of pattern name to keyword list
            
        Returns:
            Dict of pattern name to occurrence count
        """
        results = {}
        content_lower = content.lower()
        
        for pattern_name, keywords in patterns.items():
            count = 0
            for keyword in keywords:
                count += content_lower.count(keyword.lower())
            results[pattern_name] = count
        
        return results
