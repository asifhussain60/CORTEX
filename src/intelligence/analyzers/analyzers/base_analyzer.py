"""
Base Analyzer

Abstract base class for language-agnostic AST analysis.
Defines common interface for code smell detection across all languages.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Optional


class SmellType(Enum):
    """Types of code smells"""
    # Performance smells (from TDD Mastery)
    SLOW_FUNCTION = "slow_function"
    HOT_PATH = "hot_path"
    BOTTLENECK = "bottleneck"
    
    # Structural smells (AST-based)
    LONG_METHOD = "long_method"
    COMPLEX_METHOD = "complex_method"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    MAGIC_NUMBER = "magic_number"
    DEEP_NESTING = "deep_nesting"
    LONG_PARAMETER_LIST = "long_parameter_list"
    FEATURE_ENVY = "feature_envy"


@dataclass
class CodeSmell:
    """Detected code smell"""
    smell_type: SmellType
    function_name: str
    line_number: int
    confidence: float
    message: str
    suggestion: str
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAnalyzer(ABC):
    """Abstract base class for language-specific analyzers"""
    
    def __init__(self, language: str):
        """
        Initialize analyzer
        
        Args:
            language: Programming language name
        """
        self.language = language
        self.base_confidence = self._get_base_confidence()
    
    @abstractmethod
    def _get_base_confidence(self) -> float:
        """Get base confidence score for this language"""
        pass
    
    @abstractmethod
    def analyze(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """
        Analyze AST for code smells
        
        Args:
            ast_tree: Parsed AST tree
            code: Original source code
            
        Returns:
            List of detected code smells
        """
        pass
    
    @abstractmethod
    def detect_long_methods(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect methods exceeding line count threshold"""
        pass
    
    @abstractmethod
    def detect_complex_methods(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect methods with high cyclomatic complexity"""
        pass
    
    @abstractmethod
    def detect_deep_nesting(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect deeply nested code blocks"""
        pass
    
    @abstractmethod
    def detect_long_parameter_lists(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect functions with too many parameters"""
        pass
    
    @abstractmethod
    def detect_magic_numbers(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect unexplained numeric literals"""
        pass
    
    def adjust_confidence(self, base_confidence: float) -> float:
        """
        Adjust confidence based on language-specific factors
        
        Args:
            base_confidence: Base confidence score
            
        Returns:
            Adjusted confidence score
        """
        return min(1.0, base_confidence * self.base_confidence)
