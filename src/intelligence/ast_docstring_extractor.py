"""
AST Docstring Extractor

Extracts docstrings from Python source code using Abstract Syntax Trees (AST).
Identifies classes and functions with documentation, ranks by informativeness.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
License: Proprietary - Source-Available
"""

import ast
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class DocstringInfo:
    """Information about an extracted docstring."""
    name: str                      # Class or function name
    type: str                      # 'class' or 'function'
    docstring: str                 # Docstring content
    line_number: int               # Line number in file
    file_path: str                 # Source file path
    informativeness_score: float   # Ranking score (0.0-1.0)


class AstDocstringExtractor:
    """Extract docstrings from Python source code using AST parsing."""
    
    def __init__(self):
        """Initialize extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_from_file(
        self, 
        file_path: Path, 
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract docstrings from a Python file.
        
        Args:
            file_path: Path to Python source file
            top_n: Maximum number of results to return (most informative)
        
        Returns:
            List of DocstringInfo objects, ranked by informativeness
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Read source code
            source_code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse AST
            tree = ast.parse(source_code, filename=str(file_path))
            
            # Extract docstrings
            docstrings = self._extract_docstrings(tree, str(file_path))
            
            # Rank by informativeness
            ranked = self._rank_docstrings(docstrings)
            
            # Return top N
            return ranked[:top_n]
            
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return []
    
    def extract_from_directory(
        self,
        directory: Path,
        max_files: int = 20,
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract docstrings from all Python files in directory.
        
        Args:
            directory: Directory to scan
            max_files: Maximum number of files to scan
            top_n: Maximum results per file
        
        Returns:
            Combined list of DocstringInfo objects, ranked by informativeness
        """
        all_docstrings = []
        
        # Find Python files
        python_files = list(directory.rglob('*.py'))
        
        # Sort by file size (larger files likely more important)
        python_files.sort(key=lambda p: p.stat().st_size, reverse=True)
        
        # Limit to max_files
        python_files = python_files[:max_files]
        
        # Extract from each file
        for file_path in python_files:
            try:
                docstrings = self.extract_from_file(file_path, top_n=top_n)
                all_docstrings.extend(docstrings)
            except Exception as e:
                self.logger.warning(f"Skipping {file_path}: {e}")
                continue
        
        # Rank all results
        ranked = self._rank_docstrings(all_docstrings)
        
        return ranked[:top_n]
    
    def _extract_docstrings(
        self, 
        tree: ast.AST, 
        file_path: str
    ) -> List[DocstringInfo]:
        """
        Extract docstrings from AST tree.
        
        Args:
            tree: Parsed AST tree
            file_path: Source file path
        
        Returns:
            List of DocstringInfo objects (unranked)
        """
        docstrings = []
        
        for node in ast.walk(tree):
            # Extract from classes
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(DocstringInfo(
                        name=node.name,
                        type='class',
                        docstring=docstring,
                        line_number=node.lineno,
                        file_path=file_path,
                        informativeness_score=0.0  # Will be calculated later
                    ))
            
            # Extract from functions (top-level only for now)
            elif isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Check if it's a top-level function (not a method)
                    # Methods are children of ClassDef nodes
                    docstrings.append(DocstringInfo(
                        name=node.name,
                        type='function',
                        docstring=docstring,
                        line_number=node.lineno,
                        file_path=file_path,
                        informativeness_score=0.0
                    ))
        
        return docstrings
    
    def _rank_docstrings(
        self, 
        docstrings: List[DocstringInfo]
    ) -> List[DocstringInfo]:
        """
        Rank docstrings by informativeness.
        
        Scoring criteria:
        - Length (longer = more informative)
        - Keyword presence (Args, Returns, Examples, etc.)
        - Multi-line (structured documentation)
        
        Args:
            docstrings: List of unranked DocstringInfo objects
        
        Returns:
            List sorted by informativeness_score (descending)
        """
        for doc in docstrings:
            score = 0.0
            
            # Length score (0.0-0.5)
            # Normalize to reasonable range (50-500 characters)
            length = len(doc.docstring)
            length_score = min(length / 500.0, 0.5)
            score += length_score
            
            # Keyword bonus (0.0-0.3)
            keywords = ['args:', 'returns:', 'raises:', 'example:', 'note:']
            keyword_count = sum(1 for kw in keywords if kw in doc.docstring.lower())
            keyword_score = min(keyword_count * 0.1, 0.3)
            score += keyword_score
            
            # Multi-line bonus (0.0-0.2)
            line_count = len(doc.docstring.split('\n'))
            if line_count > 3:
                score += 0.2
            
            doc.informativeness_score = score
        
        # Sort by score (descending)
        return sorted(docstrings, key=lambda d: d.informativeness_score, reverse=True)
