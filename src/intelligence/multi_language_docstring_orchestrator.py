"""
Multi-Language Docstring Orchestrator

Aggregates docstring extraction across Python, JavaScript, TypeScript, C#, and ColdFusion.
Part of Phase 1 Task 1.2 - Enhanced AST Docstring Extractor.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import logging

from .analyzers.python_analyzer import PythonAnalyzer
from .analyzers.javascript_analyzer import JavaScriptAnalyzer
from .analyzers.typescript_analyzer import TypeScriptAnalyzer
from .analyzers.csharp_analyzer import CSharpAnalyzer
from .analyzers.coldfusion_analyzer import ColdFusionAnalyzer
from .docstring_extractor import DocstringInfo


class MultiLanguageDocstringOrchestrator:
    """
    Orchestrates docstring extraction across multiple programming languages.
    
    Features:
    - Parallel processing for performance
    - Graceful degradation on individual file failures
    - Language auto-detection from file extension
    - Unified output schema across all languages
    """
    
    # Language to file extension mapping
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'csharp': ['.cs'],
        'coldfusion': ['.cfc', '.cfm']
    }
    
    def __init__(self):
        """Initialize analyzers for all supported languages"""
        self.logger = logging.getLogger(__name__)
        self.analyzers = {
            'python': PythonAnalyzer(),
            'javascript': JavaScriptAnalyzer(),
            'typescript': TypeScriptAnalyzer(),
            'csharp': CSharpAnalyzer(),
            'coldfusion': ColdFusionAnalyzer()
        }
    
    def extract_from_files(
        self,
        file_paths: List[Path],
        limit_per_file: int = 10,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Extract top docstrings from multiple files.
        
        Args:
            file_paths: List of file paths to analyze
            limit_per_file: Max docstrings to extract per file
            parallel: Use parallel processing (default: True)
            
        Returns:
            Dictionary with:
                - all_docstrings: List of all extracted docstrings
                - top_docstrings: Top N most informative across all files
                - by_language: Docstrings grouped by language
                - stats: Processing statistics
        """
        start_time = time.time()
        all_docstrings = []
        errors = []
        
        if parallel:
            all_docstrings, errors = self._extract_parallel(file_paths, limit_per_file)
        else:
            all_docstrings, errors = self._extract_sequential(file_paths, limit_per_file)
        
        elapsed_time = time.time() - start_time
        
        # Sort all docstrings by score
        ranked_docstrings = sorted(
            all_docstrings,
            key=lambda d: d.informativeness_score,
            reverse=True
        )
        
        # Group by language
        by_language = {}
        for doc in all_docstrings:
            lang = doc.language
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(doc)
        
        return {
            'all_docstrings': all_docstrings,
            'top_docstrings': ranked_docstrings[:limit_per_file],
            'by_language': by_language,
            'stats': {
                'total_files': len(file_paths),
                'total_docstrings': len(all_docstrings),
                'files_processed': len(file_paths) - len(errors),
                'errors': len(errors),
                'elapsed_seconds': round(elapsed_time, 2),
                'docstrings_per_second': round(len(all_docstrings) / elapsed_time, 2) if elapsed_time > 0 else 0
            },
            'errors': errors
        }
    
    def _extract_parallel(
        self,
        file_paths: List[Path],
        limit_per_file: int
    ) -> tuple[List[DocstringInfo], List[Dict[str, Any]]]:
        """Extract docstrings using parallel processing"""
        all_docstrings = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._extract_from_file, fp, limit_per_file): fp
                for fp in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    docstrings = future.result()
                    all_docstrings.extend(docstrings)
                except Exception as e:
                    errors.append({
                        'file': str(file_path),
                        'error': str(e)
                    })
                    self.logger.warning(f"Failed to extract from {file_path}: {e}")
        
        return all_docstrings, errors
    
    def _extract_sequential(
        self,
        file_paths: List[Path],
        limit_per_file: int
    ) -> tuple[List[DocstringInfo], List[Dict[str, Any]]]:
        """Extract docstrings sequentially"""
        all_docstrings = []
        errors = []
        
        for file_path in file_paths:
            try:
                docstrings = self._extract_from_file(file_path, limit_per_file)
                all_docstrings.extend(docstrings)
            except Exception as e:
                errors.append({
                    'file': str(file_path),
                    'error': str(e)
                })
                self.logger.warning(f"Failed to extract from {file_path}: {e}")
        
        return all_docstrings, errors
    
    def _extract_from_file(self, file_path: Path, limit: int) -> List[DocstringInfo]:
        """Extract docstrings from a single file"""
        language = self._detect_language(file_path)
        
        if not language:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        analyzer = self.analyzers.get(language)
        if not analyzer:
            raise ValueError(f"No analyzer available for language: {language}")
        
        return analyzer.get_top_docstrings(file_path, limit)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        suffix = file_path.suffix.lower()
        
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language
        
        return None
    
    def extract_from_directory(
        self,
        directory: Path,
        recursive: bool = True,
        limit_per_file: int = 10
    ) -> Dict[str, Any]:
        """
        Extract docstrings from all supported files in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Scan subdirectories (default: True)
            limit_per_file: Max docstrings per file
            
        Returns:
            Same format as extract_from_files()
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Collect all supported files
        file_paths = []
        all_extensions = []
        for extensions in self.LANGUAGE_EXTENSIONS.values():
            all_extensions.extend(extensions)
        
        if recursive:
            for ext in all_extensions:
                file_paths.extend(directory.rglob(f"*{ext}"))
        else:
            for ext in all_extensions:
                file_paths.extend(directory.glob(f"*{ext}"))
        
        self.logger.info(f"Found {len(file_paths)} files in {directory}")
        
        return self.extract_from_files(file_paths, limit_per_file, parallel=True)


# Convenience function for quick access
def extract_top_docstrings(
    paths: List[Path],
    limit: int = 10
) -> List[DocstringInfo]:
    """
    Extract top N most informative docstrings from files.
    
    Args:
        paths: List of file or directory paths
        limit: Maximum docstrings to return
        
    Returns:
        List of top N DocstringInfo objects
    """
    orchestrator = MultiLanguageDocstringOrchestrator()
    
    # Separate files and directories
    files = [p for p in paths if p.is_file()]
    dirs = [p for p in paths if p.is_dir()]
    
    # Extract from files
    result = orchestrator.extract_from_files(files, limit_per_file=limit)
    
    # Extract from directories
    for directory in dirs:
        dir_result = orchestrator.extract_from_directory(directory, limit_per_file=limit)
        result['all_docstrings'].extend(dir_result['all_docstrings'])
    
    # Re-rank all docstrings
    ranked = sorted(
        result['all_docstrings'],
        key=lambda d: d.informativeness_score,
        reverse=True
    )
    
    return ranked[:limit]
