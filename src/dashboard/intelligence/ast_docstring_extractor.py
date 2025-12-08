"""
AST Docstring Extractor

Extracts docstrings from Python source files to generate intelligent narratives
for executive summaries. Replaces generic template-based descriptions with
project-specific insights derived from actual code documentation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
License: Source-Available
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = logging.getLogger(__name__)


@dataclass
class DocstringInfo:
    """Represents extracted docstring information from a code entity"""
    file_path: str
    entity_type: str  # 'class', 'function', 'module'
    entity_name: str
    docstring: str
    line_number: int
    char_count: int
    summary: str  # First paragraph only
    
    def __post_init__(self):
        """Extract summary from full docstring"""
        if not self.summary and self.docstring:
            # Extract first paragraph (up to first blank line or period)
            lines = self.docstring.split('\n')
            summary_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped and summary_lines:
                    break  # Hit blank line
                if stripped:
                    summary_lines.append(stripped)
                    if stripped.endswith('.'):
                        break  # Hit period
            self.summary = ' '.join(summary_lines)[:200]  # Max 200 chars


@dataclass
class ExtractionResult:
    """Results from docstring extraction operation"""
    total_files_scanned: int
    successful_extractions: int
    failed_files: List[str]
    docstrings: List[DocstringInfo]
    top_docstrings: List[DocstringInfo]  # Ranked by informativeness
    

class ASTDocstringExtractor:
    """
    Extracts docstrings from Python source files using AST parsing.
    
    Focuses on top-level classes and functions to generate executive
    summaries with actual project-specific documentation rather than
    generic template text.
    """
    
    def __init__(self, min_docstring_length: int = 20, max_files: int = 50):
        """
        Initialize docstring extractor.
        
        Args:
            min_docstring_length: Minimum docstring length to consider (filters noise)
            max_files: Maximum number of files to scan (performance limit)
        """
        self.min_docstring_length = min_docstring_length
        self.max_files = max_files
        
    def extract_from_repository(
        self, 
        repo_path: Path,
        file_extensions: List[str] = None
    ) -> ExtractionResult:
        """
        Extract docstrings from all Python files in repository.
        
        Args:
            repo_path: Root path of repository
            file_extensions: File extensions to scan (default: ['.py'])
            
        Returns:
            ExtractionResult with all extracted docstrings ranked by quality
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        # Discover Python files, prioritize by size (larger = more important)
        python_files = self._discover_files(repo_path, file_extensions)
        
        # Limit to top N files for performance
        if len(python_files) > self.max_files:
            logger.info(f"Limiting scan to top {self.max_files} of {len(python_files)} files")
            python_files = python_files[:self.max_files]
        
        # Extract docstrings in parallel
        docstrings = []
        failed_files = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._extract_from_file, file_path): file_path
                for file_path in python_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_docstrings = future.result()
                    docstrings.extend(file_docstrings)
                except Exception as e:
                    logger.warning(f"Failed to extract from {file_path}: {e}")
                    failed_files.append(str(file_path))
        
        # Rank docstrings by informativeness
        top_docstrings = self._rank_docstrings(docstrings)
        
        return ExtractionResult(
            total_files_scanned=len(python_files),
            successful_extractions=len(python_files) - len(failed_files),
            failed_files=failed_files,
            docstrings=docstrings,
            top_docstrings=top_docstrings[:10]  # Top 10 most informative
        )
    
    def _discover_files(
        self, 
        repo_path: Path, 
        extensions: List[str]
    ) -> List[Path]:
        """
        Discover and prioritize source files.
        
        Prioritizes by:
        1. Controller/Service/Repository files (naming patterns)
        2. File size (larger files likely more important)
        3. Recent modification (active development areas)
        
        Args:
            repo_path: Repository root path
            extensions: File extensions to include
            
        Returns:
            Sorted list of file paths
        """
        files = []
        
        # Exclusion patterns
        excluded_dirs = {
            'node_modules', '.git', '.venv', 'venv', '__pycache__',
            'bin', 'obj', 'dist', 'build', 'packages', 'TestResults',
            'migrations', 'tests', 'test', 'spec'
        }
        
        for ext in extensions:
            for file_path in repo_path.rglob(f'*{ext}'):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in excluded_dirs):
                    continue
                
                # Skip test files
                if 'test' in file_path.stem.lower() or file_path.stem.startswith('test_'):
                    continue
                
                files.append(file_path)
        
        # Score files by importance
        scored_files = []
        for file_path in files:
            score = 0
            stem_lower = file_path.stem.lower()
            
            # Naming patterns (high priority)
            if any(pattern in stem_lower for pattern in ['controller', 'service', 'repository', 'manager', 'handler']):
                score += 100
            
            # File size (larger = more important, up to 10 points)
            try:
                size_kb = file_path.stat().st_size / 1024
                score += min(10, size_kb / 10)
            except:
                pass
            
            scored_files.append((score, file_path))
        
        # Sort by score descending
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return [file_path for _, file_path in scored_files]
    
    def _extract_from_file(self, file_path: Path) -> List[DocstringInfo]:
        """
        Extract docstrings from a single Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of DocstringInfo objects
        """
        docstrings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring and len(module_docstring) >= self.min_docstring_length:
                docstrings.append(DocstringInfo(
                    file_path=str(file_path),
                    entity_type='module',
                    entity_name=file_path.stem,
                    docstring=module_docstring,
                    line_number=1,
                    char_count=len(module_docstring),
                    summary=''  # Will be computed in __post_init__
                ))
            
            # Class and function docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_docstring = ast.get_docstring(node)
                    if class_docstring and len(class_docstring) >= self.min_docstring_length:
                        docstrings.append(DocstringInfo(
                            file_path=str(file_path),
                            entity_type='class',
                            entity_name=node.name,
                            docstring=class_docstring,
                            line_number=node.lineno,
                            char_count=len(class_docstring),
                            summary=''
                        ))
                
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions or class methods
                    func_docstring = ast.get_docstring(node)
                    if func_docstring and len(func_docstring) >= self.min_docstring_length:
                        # Skip private methods
                        if not node.name.startswith('_'):
                            docstrings.append(DocstringInfo(
                                file_path=str(file_path),
                                entity_type='function',
                                entity_name=node.name,
                                docstring=func_docstring,
                                line_number=node.lineno,
                                char_count=len(func_docstring),
                                summary=''
                            ))
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            raise
        
        return docstrings
    
    def _rank_docstrings(self, docstrings: List[DocstringInfo]) -> List[DocstringInfo]:
        """
        Rank docstrings by informativeness.
        
        Scoring criteria:
        - Length (longer = more informative, up to 500 chars)
        - Contains business terms (user, customer, payment, order, etc.)
        - Module-level docstrings ranked higher
        - Proper formatting (paragraphs, complete sentences)
        
        Args:
            docstrings: List of extracted docstrings
            
        Returns:
            Sorted list (most informative first)
        """
        business_terms = {
            'user', 'customer', 'payment', 'order', 'product', 'service',
            'account', 'transaction', 'employee', 'benefit', 'engagement',
            'parking', 'commute', 'reward', 'payroll', 'invoice'
        }
        
        scored = []
        for doc in docstrings:
            score = 0
            
            # Length score (0-30 points)
            score += min(30, doc.char_count / 500 * 30)
            
            # Business term presence (5 points per term, max 25)
            doc_lower = doc.docstring.lower()
            business_term_count = sum(1 for term in business_terms if term in doc_lower)
            score += min(25, business_term_count * 5)
            
            # Entity type bonus
            if doc.entity_type == 'module':
                score += 20  # Module docstrings are overview-level
            elif doc.entity_type == 'class':
                score += 15
            else:
                score += 5
            
            # Formatting quality (has paragraphs, sentences)
            if '\n\n' in doc.docstring:
                score += 10  # Multi-paragraph
            if doc.docstring.count('.') >= 2:
                score += 5  # Multiple sentences
            
            scored.append((score, doc))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for _, doc in scored]
    
    def generate_narrative(self, extraction_result: ExtractionResult) -> str:
        """
        Generate executive summary narrative from top docstrings.
        
        Args:
            extraction_result: Results from extract_from_repository
            
        Returns:
            Human-readable narrative (150-300 words)
        """
        if not extraction_result.top_docstrings:
            return "No documentation found. This appears to be an undocumented codebase."
        
        # Use top 3-5 docstrings
        top_docs = extraction_result.top_docstrings[:5]
        
        # Start with most informative summary
        narrative_parts = [top_docs[0].summary]
        
        # Add unique insights from other top docs (avoid repetition)
        used_words = set(top_docs[0].summary.lower().split())
        
        for doc in top_docs[1:]:
            # Check if this doc adds new information
            doc_words = set(doc.summary.lower().split())
            new_words = doc_words - used_words
            
            if len(new_words) > 5:  # At least 5 new words
                narrative_parts.append(doc.summary)
                used_words.update(new_words)
            
            if len(' '.join(narrative_parts)) > 250:
                break  # Target length reached
        
        narrative = ' '.join(narrative_parts)
        
        # Ensure proper ending
        if not narrative.endswith('.'):
            narrative += '.'
        
        return narrative


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ast_docstring_extractor.py <repo_path>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Extracting docstrings from: {repo_path}")
    
    extractor = ASTDocstringExtractor(max_files=50)
    result = extractor.extract_from_repository(repo_path)
    
    print(f"\n{'='*60}")
    print(f"Extraction Results")
    print(f"{'='*60}")
    print(f"Files scanned: {result.total_files_scanned}")
    print(f"Successful: {result.successful_extractions}")
    print(f"Failed: {len(result.failed_files)}")
    print(f"Total docstrings: {len(result.docstrings)}")
    
    print(f"\n{'='*60}")
    print(f"Top 10 Most Informative Docstrings")
    print(f"{'='*60}")
    for i, doc in enumerate(result.top_docstrings, 1):
        print(f"\n{i}. {doc.entity_type.upper()}: {doc.entity_name}")
        print(f"   File: {Path(doc.file_path).name}")
        print(f"   Summary: {doc.summary}")
    
    print(f"\n{'='*60}")
    print(f"Generated Narrative")
    print(f"{'='*60}")
    narrative = extractor.generate_narrative(result)
    print(narrative)


if __name__ == "__main__":
    main()
