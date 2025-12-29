"""
Recursive File Scanner Utility for Dashboard Collectors.

Provides language-agnostic file scanning that starts from project root and
recursively scans all folders/subfolders, avoiding hardcoded 'src/' assumptions.

Author: CORTEX
Created: 2025-12-05
Purpose: Fix hardcoded path issues in dashboard collectors
"""

import logging
from pathlib import Path
from typing import List, Dict, Set, Any, Optional


class RecursiveScanner:
    """
    Universal file scanner that recursively traverses from project root.
    
    Avoids hardcoded assumptions about folder structure (e.g., 'src/').
    Works with Python, .NET, JavaScript, Java, Go, Rust, and other projects.
    """
    
    # Directories to always skip (performance + relevance)
    SKIP_DIRS: Set[str] = {
        'venv', 'env', '.venv', '__pycache__', '.git', '.svn', '.hg',
        'node_modules', 'bower_components', 'jspm_packages',
        'bin', 'obj', 'packages', 'vendor', 'dist', 'build',
        '.pytest_cache', '.mypy_cache', '.tox', 'htmlcov',
        'coverage', '.coverage', '.idea', '.vscode', '.vs'
    }
    
    # Multi-language file patterns
    FILE_PATTERNS: Dict[str, List[str]] = {
        'python': ['*.py'],
        'dotnet': ['*.cs', '*.vb', '*.fs', '*.csproj', '*.vbproj', '*.fsproj'],
        'javascript': ['*.js', '*.jsx', '*.mjs', '*.cjs'],
        'typescript': ['*.ts', '*.tsx'],
        'java': ['*.java', '*.kt', '*.scala', '*.groovy'],
        'cpp': ['*.c', '*.cpp', '*.cc', '*.cxx', '*.h', '*.hpp'],
        'go': ['*.go'],
        'rust': ['*.rs'],
        'php': ['*.php'],
        'ruby': ['*.rb'],
        'swift': ['*.swift', '*.m', '*.mm'],
        'shell': ['*.sh', '*.bash', '*.ps1'],
        'sql': ['*.sql'],
        'other': ['*.r', '*.R', '*.lua', '*.dart', '*.pl', '*.pm']
    }
    
    def __init__(self, project_root: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize scanner.
        
        Args:
            project_root: Absolute path to project root directory
            logger: Optional logger instance
        """
        self.project_root = Path(project_root).resolve()
        self.logger = logger or logging.getLogger(__name__)
        
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {self.project_root}")
    
    def scan_files(
        self,
        patterns: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        include_dirs: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Recursively scan for files from project root.
        
        Args:
            patterns: Custom glob patterns (e.g., ['*.py', '*.cs']). If None, uses all language patterns.
            languages: Language keys from FILE_PATTERNS (e.g., ['python', 'dotnet']). Ignored if patterns provided.
            include_dirs: Only scan these directories (relative to project_root). If None, scan all.
            exclude_dirs: Additional directories to skip beyond SKIP_DIRS.
        
        Returns:
            List of Path objects for matching files
        """
        # Determine patterns to use
        if patterns:
            search_patterns = patterns
        elif languages:
            search_patterns = []
            for lang in languages:
                if lang in self.FILE_PATTERNS:
                    search_patterns.extend(self.FILE_PATTERNS[lang])
        else:
            # Default: all patterns
            search_patterns = []
            for lang_patterns in self.FILE_PATTERNS.values():
                search_patterns.extend(lang_patterns)
        
        # Build exclusion set
        exclusions = self.SKIP_DIRS.copy()
        if exclude_dirs:
            exclusions.update(exclude_dirs)
        
        # Determine search roots
        if include_dirs:
            search_roots = [self.project_root / d for d in include_dirs]
            search_roots = [r for r in search_roots if r.exists()]
        else:
            search_roots = [self.project_root]
        
        # Collect files
        found_files = []
        for root in search_roots:
            for pattern in search_patterns:
                for file_path in root.rglob(pattern):
                    # Check if any parent directory is in exclusion set
                    if self._should_skip(file_path, exclusions):
                        continue
                    
                    if file_path.is_file():
                        found_files.append(file_path)
        
        # Deduplicate (glob patterns may overlap)
        return list(set(found_files))
    
    def scan_by_language(self, language: str, **kwargs) -> List[Path]:
        """
        Convenience method to scan for specific language.
        
        Args:
            language: Language key from FILE_PATTERNS
            **kwargs: Additional arguments for scan_files()
        
        Returns:
            List of Path objects
        """
        return self.scan_files(languages=[language], **kwargs)
    
    def scan_python_files(self, **kwargs) -> List[Path]:
        """Scan for Python files."""
        return self.scan_by_language('python', **kwargs)
    
    def scan_dotnet_files(self, **kwargs) -> List[Path]:
        """Scan for .NET files."""
        return self.scan_by_language('dotnet', **kwargs)
    
    def scan_javascript_files(self, **kwargs) -> List[Path]:
        """Scan for JavaScript files."""
        return self.scan_by_language('javascript', **kwargs)
    
    def get_file_stats(self, files: List[Path]) -> Dict[str, Any]:
        """
        Get statistics about scanned files.
        
        Args:
            files: List of file paths
        
        Returns:
            Dict with statistics
        """
        stats = {
            'total_files': len(files),
            'by_extension': {},
            'by_directory': {},
            'total_size_kb': 0
        }
        
        for file_path in files:
            # Extension stats
            ext = file_path.suffix or 'no_extension'
            stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
            
            # Directory stats
            try:
                rel_dir = str(file_path.parent.relative_to(self.project_root))
            except ValueError:
                rel_dir = 'external'
            stats['by_directory'][rel_dir] = stats['by_directory'].get(rel_dir, 0) + 1
            
            # Size stats
            try:
                stats['total_size_kb'] += file_path.stat().st_size / 1024
            except Exception:
                pass
        
        stats['total_size_kb'] = round(stats['total_size_kb'], 2)
        return stats
    
    def _should_skip(self, file_path: Path, exclusions: Set[str]) -> bool:
        """
        Check if file should be skipped based on parent directories.
        
        Args:
            file_path: Path to check
            exclusions: Set of directory names to exclude
        
        Returns:
            True if should skip
        """
        path_str = str(file_path)
        
        # Check each parent directory name
        for parent in file_path.parents:
            if parent.name in exclusions:
                return True
        
        # Additional check: full path contains excluded directory
        for excluded in exclusions:
            if f"\\{excluded}\\" in path_str or f"/{excluded}/" in path_str:
                return True
        
        return False
    
    def find_source_directories(self) -> List[Path]:
        """
        Intelligently detect source code directories.
        
        Looks for directories containing code files but avoids build/vendor dirs.
        
        Returns:
            List of directories that likely contain source code
        """
        all_files = self.scan_files()
        
        # Group files by directory
        dir_file_counts = {}
        for file_path in all_files:
            parent = file_path.parent
            dir_file_counts[parent] = dir_file_counts.get(parent, 0) + 1
        
        # Sort by file count (descending)
        source_dirs = sorted(dir_file_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return directories with significant file counts
        return [d for d, count in source_dirs if count >= 3]
