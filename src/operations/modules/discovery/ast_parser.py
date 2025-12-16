"""
Base AST parser for code intelligence
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from .models import ASTNode, CodeElement, ComplexityMetrics

logger = logging.getLogger(__name__)


class ASTParser(ABC):
    """Base class for language-specific AST parsing"""
    
    def __init__(self):
        """Initialize AST parser"""
        self.supported_languages = []
    
    @abstractmethod
    def parse(self, file_path: Path, content: str) -> Optional[ASTNode]:
        """
        Parse file content into AST
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            Root ASTNode or None if parsing fails
        """
        raise NotImplementedError("Subclasses must implement parse()")
    
    @abstractmethod
    def extract_elements(self, ast: ASTNode, file_path: Path) -> List[CodeElement]:
        """
        Extract code elements from AST
        
        Args:
            ast: Root AST node
            file_path: Path to the source file
            
        Returns:
            List of extracted CodeElements
        """
        raise NotImplementedError("Subclasses must implement extract_elements()")
    
    @abstractmethod
    def calculate_complexity(self, ast: ASTNode) -> ComplexityMetrics:
        """
        Calculate complexity metrics for AST node
        
        Args:
            ast: AST node to analyze
            
        Returns:
            ComplexityMetrics for the node
        """
        raise NotImplementedError("Subclasses must implement calculate_complexity()")
    
    def supports_language(self, language: str) -> bool:
        """
        Check if parser supports language
        
        Args:
            language: Language name
            
        Returns:
            True if language is supported
        """
        return language.lower() in self.supported_languages
