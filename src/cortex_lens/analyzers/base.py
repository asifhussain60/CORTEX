"""
Base protocol for language analyzers.

All analyzer implementations must follow this protocol.
"""

from typing import Protocol, Dict, Any, List
from pathlib import Path


class BaseAnalyzer(Protocol):
    """
    Protocol for language analyzers.
    
    Analyzers extract structured information from source code using
    AST parsing (Python) or regex patterns (C#, JavaScript, SQL).
    
    Example:
        >>> analyzer = PythonAnalyzer()
        >>> result = analyzer.analyze(Path('src/app.py'))
        >>> print(result['functions'])
    """
    
    @property
    def language(self) -> str:
        """
        Get the language this analyzer supports.
        
        Returns:
            Language name (e.g., 'python', 'csharp', 'javascript')
        """
        ...
    
    @property
    def file_extensions(self) -> List[str]:
        """
        Get file extensions this analyzer handles.
        
        Returns:
            List of extensions (e.g., ['.py', '.pyx'])
        """
        ...
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a source file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Dictionary containing:
                - functions: List of function definitions
                - classes: List of class definitions
                - imports: List of imported modules
                - complexity: Cyclomatic complexity metrics
                - loc: Lines of code count
                - comments: Extracted comments
                
        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors (optional)
        """
        ...
    
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if this analyzer can handle the given file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file extension matches
        """
        ...
