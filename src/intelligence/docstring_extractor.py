"""
Multi-Language Docstring Extractor

Unified interface for extracting and ranking the most informative docstrings
across Python, JavaScript, TypeScript, C#, and ColdFusion codebases.

Part of Phase 1 Task 1.2 - Enhanced AST Docstring Extractor

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum


class DocstringSource(str, Enum):
    """Types of docstring sources"""
    PYTHON_DOCSTRING = "python_docstring"
    JSDOC_COMMENT = "jsdoc_comment"
    CSHARP_XML_DOC = "csharp_xml_doc"
    COLDFUSION_HINT = "coldfusion_hint"
    COLDFUSION_COMMENT = "coldfusion_comment"
    MODULE_LEVEL = "module_level"
    CLASS_LEVEL = "class_level"
    FUNCTION_LEVEL = "function_level"
    METHOD_LEVEL = "method_level"


@dataclass
class DocstringInfo:
    """
    Unified docstring information across all languages.
    
    Attributes:
        source_file: Path to file containing the docstring
        object_name: Name of the documented item (class, function, method)
        object_type: Type of documented object (module, class, function, method)
        docstring_text: The actual documentation text
        line_number: Starting line number
        language: Programming language (python, javascript, typescript, csharp, coldfusion)
        source_type: How the docstring was extracted
        informativeness_score: Calculated score (0.0 to 1.0) indicating usefulness
        metadata: Additional language-specific information
    """
    source_file: Path
    object_name: str
    object_type: str
    docstring_text: str
    line_number: int
    language: str
    source_type: DocstringSource
    informativeness_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'source_file': str(self.source_file),
            'object_name': self.object_name,
            'object_type': self.object_type,
            'docstring_text': self.docstring_text,
            'line_number': self.line_number,
            'language': self.language,
            'source_type': self.source_type.value if isinstance(self.source_type, DocstringSource) else self.source_type,
            'informativeness_score': self.informativeness_score,
            'metadata': self.metadata
        }


class InformativenessScorer:
    """
    Calculates informativeness scores for docstrings.
    
    Scoring criteria (weighted):
    - Length (20%): Longer docstrings usually more informative (100-500 chars ideal)
    - Vocabulary richness (25%): Unique words vs total words
    - Technical keywords (20%): Presence of domain terms (API, database, service, controller, etc.)
    - Structure (15%): Presence of sections (Args, Returns, Examples, Notes)
    - Code examples (10%): Contains code blocks or usage examples
    - Type information (10%): Contains type hints or parameter descriptions
    """
    
    TECHNICAL_KEYWORDS = {
        'api', 'endpoint', 'service', 'controller', 'repository', 'model',
        'database', 'query', 'transaction', 'authentication', 'authorization',
        'validation', 'serialization', 'deserialization', 'middleware',
        'interface', 'abstract', 'implements', 'extends', 'override',
        'async', 'await', 'promise', 'callback', 'event', 'handler',
        'exception', 'error', 'logging', 'monitoring', 'cache', 'session',
        'request', 'response', 'http', 'rest', 'soap', 'graphql',
        'algorithm', 'optimization', 'performance', 'security', 'encryption'
    }
    
    STRUCTURE_INDICATORS = [
        'args:', 'arguments:', 'parameters:', 'params:',
        'returns:', 'return:', 'yields:', 'yield:',
        'raises:', 'throws:', 'exceptions:',
        'examples:', 'example:', 'usage:',
        'notes:', 'note:', 'warning:', 'caution:',
        'see also:', 'references:', 'todo:'
    ]
    
    @staticmethod
    def calculate_score(docstring: str) -> float:
        """
        Calculate informativeness score for a docstring.
        
        Args:
            docstring: The documentation text to score
            
        Returns:
            Score between 0.0 and 1.0 (higher = more informative)
        """
        if not docstring or not docstring.strip():
            return 0.0
            
        text = docstring.strip().lower()
        length = len(text)
        
        # Length score (0.0 to 1.0)
        # Optimal range: 100-500 characters
        if length < 50:
            length_score = length / 50.0
        elif length <= 500:
            length_score = 1.0
        else:
            # Penalize extremely long docstrings
            length_score = max(0.5, 1.0 - (length - 500) / 2000.0)
        
        # Vocabulary richness (unique words / total words)
        words = text.split()
        if not words:
            return 0.0
        unique_words = set(words)
        vocabulary_score = len(unique_words) / len(words)
        
        # Technical keywords (presence count / max expected)
        keyword_count = sum(1 for keyword in InformativenessScorer.TECHNICAL_KEYWORDS if keyword in text)
        keyword_score = min(1.0, keyword_count / 5.0)  # Max 5 keywords expected
        
        # Structure indicators
        structure_count = sum(1 for indicator in InformativenessScorer.STRUCTURE_INDICATORS if indicator in text)
        structure_score = min(1.0, structure_count / 3.0)  # Max 3 sections expected
        
        # Code examples (code blocks or backticks)
        has_code = '```' in text or '`' in text or 'example:' in text
        code_score = 1.0 if has_code else 0.0
        
        # Type information
        has_types = any(indicator in text for indicator in ['type:', 'str', 'int', 'float', 'bool', 'list', 'dict', 'optional'])
        type_score = 1.0 if has_types else 0.0
        
        # Weighted average
        final_score = (
            length_score * 0.20 +
            vocabulary_score * 0.25 +
            keyword_score * 0.20 +
            structure_score * 0.15 +
            code_score * 0.10 +
            type_score * 0.10
        )
        
        return round(final_score, 3)


class DocstringExtractor:
    """
    Base class for language-specific docstring extraction.
    
    Each language analyzer (Python, JS/TS, C#, ColdFusion) will implement
    the get_top_docstrings() method to extract and rank docstrings.
    """
    
    def __init__(self, language: str):
        self.language = language
        self.scorer = InformativenessScorer()
    
    def extract_and_rank(
        self,
        docstrings: List[DocstringInfo],
        limit: int = 10
    ) -> List[DocstringInfo]:
        """
        Calculate informativeness scores and return top N docstrings.
        
        Args:
            docstrings: List of extracted docstrings (scores may be 0)
            limit: Maximum number of results to return
            
        Returns:
            Top N most informative docstrings, sorted by score descending
        """
        # Calculate scores for any docstrings that don't have them
        for doc in docstrings:
            if doc.informativeness_score == 0.0:
                doc.informativeness_score = self.scorer.calculate_score(doc.docstring_text)
        
        # Sort by score descending
        ranked = sorted(docstrings, key=lambda d: d.informativeness_score, reverse=True)
        
        # Return top N
        return ranked[:limit]
