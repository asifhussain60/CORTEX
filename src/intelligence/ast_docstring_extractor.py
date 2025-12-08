"""
AST Docstring Extractor

Extracts docstrings from source code (Python, C#, TypeScript, JavaScript).
Identifies classes and functions with documentation, ranks by informativeness.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
License: Proprietary - Source-Available
"""

import ast
import logging
import re
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
    """Extract docstrings from source code (Python, C#, TypeScript, JavaScript)."""
    
    def __init__(self):
        """Initialize extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_from_file(
        self, 
        file_path: Path, 
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract docstrings from source file (Python, C#, TypeScript, JavaScript).
        
        Args:
            file_path: Path to source file (.py, .cs, .ts, .js)
            top_n: Maximum number of results to return (most informative)
        
        Returns:
            List of DocstringInfo objects, ranked by informativeness
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect language by extension
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.py':
                return self._extract_python_docstrings(file_path, top_n)
            elif suffix == '.cs':
                return self._extract_csharp_docstrings(file_path, top_n)
            elif suffix in ['.ts', '.js']:
                return self._extract_jsdoc_docstrings(file_path, top_n)
            else:
                # Unsupported file type
                self.logger.debug(f"Unsupported file type: {suffix}")
                return []
        
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
        Extract docstrings from all source files in directory (Python, C#, TypeScript, JavaScript).
        
        Args:
            directory: Directory to scan
            max_files: Maximum number of files to scan
            top_n: Maximum results per file
        
        Returns:
            Combined list of DocstringInfo objects, ranked by informativeness
        """
        all_docstrings = []
        
        # Find source files (Python, C#, TypeScript, JavaScript)
        source_files = []
        source_files.extend(directory.rglob('*.py'))
        source_files.extend(directory.rglob('*.cs'))
        source_files.extend(directory.rglob('*.ts'))
        source_files.extend(directory.rglob('*.js'))
        
        # Sort by file size (larger files likely more important)
        source_files.sort(key=lambda p: p.stat().st_size, reverse=True)
        
        # Limit to max_files
        source_files = source_files[:max_files]
        
        # Extract from each file
        for file_path in source_files:
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
    
    def _extract_python_docstrings(
        self,
        file_path: Path,
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract docstrings from Python file using AST.
        
        Args:
            file_path: Path to Python file
            top_n: Maximum number of results
        
        Returns:
            List of DocstringInfo objects
        """
        source_code = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(source_code, filename=str(file_path))
        docstrings = self._extract_docstrings(tree, str(file_path))
        ranked = self._rank_docstrings(docstrings)
        return ranked[:top_n]
    
    def _extract_csharp_docstrings(
        self,
        file_path: Path,
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract XML documentation comments from C# file using regex.
        
        Supports:
        - /// <summary>...</summary>
        - Multi-line XML doc comments
        
        Args:
            file_path: Path to C# file
            top_n: Maximum number of results
        
        Returns:
            List of DocstringInfo objects
        """
        source_code = file_path.read_text(encoding='utf-8', errors='ignore')
        docstrings = []
        
        # Pattern: XML doc comment followed by class/method declaration
        # Matches: /// <summary>...</summary> followed by class/interface/method
        pattern = r'///\s*<summary>(.*?)</summary>.*?(?:class|interface|struct|enum)\s+(\w+)'
        
        for match in re.finditer(pattern, source_code, re.DOTALL | re.MULTILINE):
            doc_text = match.group(1).strip()
            name = match.group(2)
            
            # Find line number
            line_number = source_code[:match.start()].count('\n') + 1
            
            docstrings.append(DocstringInfo(
                name=name,
                type='class',
                docstring=doc_text,
                line_number=line_number,
                file_path=str(file_path),
                informativeness_score=0.0
            ))
        
        # Also match method documentation
        method_pattern = r'///\s*<summary>(.*?)</summary>.*?(?:public|private|protected|internal)\s+\w+\s+(\w+)\s*\('
        
        for match in re.finditer(method_pattern, source_code, re.DOTALL | re.MULTILINE):
            doc_text = match.group(1).strip()
            name = match.group(2)
            
            line_number = source_code[:match.start()].count('\n') + 1
            
            docstrings.append(DocstringInfo(
                name=name,
                type='function',
                docstring=doc_text,
                line_number=line_number,
                file_path=str(file_path),
                informativeness_score=0.0
            ))
        
        ranked = self._rank_docstrings(docstrings)
        return ranked[:top_n]
    
    def _extract_jsdoc_docstrings(
        self,
        file_path: Path,
        top_n: int = 10
    ) -> List[DocstringInfo]:
        """
        Extract JSDoc comments from TypeScript/JavaScript file using regex.
        
        Supports:
        - /** ... */
        - Multi-line JSDoc comments
        - Class, function, and interface documentation
        
        Args:
            file_path: Path to TypeScript or JavaScript file
            top_n: Maximum number of results
        
        Returns:
            List of DocstringInfo objects
        """
        source_code = file_path.read_text(encoding='utf-8', errors='ignore')
        docstrings = []
        
        # Pattern: JSDoc comment followed by class/interface/function
        # Matches: /** ... */ followed by class/interface/function declaration
        
        # Class/Interface pattern
        class_pattern = r'/\*\*(.*?)\*/\s*(?:export\s+)?(?:class|interface)\s+(\w+)'
        
        for match in re.finditer(class_pattern, source_code, re.DOTALL | re.MULTILINE):
            doc_text = match.group(1).strip()
            # Remove leading * from each line
            doc_text = '\n'.join(line.lstrip('* ') for line in doc_text.split('\n'))
            doc_text = doc_text.strip()
            
            name = match.group(2)
            line_number = source_code[:match.start()].count('\n') + 1
            
            docstrings.append(DocstringInfo(
                name=name,
                type='class',
                docstring=doc_text,
                line_number=line_number,
                file_path=str(file_path),
                informativeness_score=0.0
            ))
        
        # Function pattern
        func_pattern = r'/\*\*(.*?)\*/\s*(?:export\s+)?(?:function|const|let|var)\s+(\w+)\s*[=(]'
        
        for match in re.finditer(func_pattern, source_code, re.DOTALL | re.MULTILINE):
            doc_text = match.group(1).strip()
            doc_text = '\n'.join(line.lstrip('* ') for line in doc_text.split('\n'))
            doc_text = doc_text.strip()
            
            name = match.group(2)
            line_number = source_code[:match.start()].count('\n') + 1
            
            docstrings.append(DocstringInfo(
                name=name,
                type='function',
                docstring=doc_text,
                line_number=line_number,
                file_path=str(file_path),
                informativeness_score=0.0
            ))
        
        ranked = self._rank_docstrings(docstrings)
        return ranked[:top_n]
