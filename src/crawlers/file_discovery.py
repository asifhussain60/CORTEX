"""
AC-CRAWLER-005: File Discovery and Filtering
Discover files with include/exclude patterns, respect .gitignore, size limits
"""
import os
import fnmatch
from pathlib import Path
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FileStats:
    """Statistics about discovered files"""
    total_files: int
    total_size_bytes: int
    by_extension: Dict[str, int]
    excluded_count: int
    excluded_size_bytes: int


class GitignoreParser:
    """Parse and respect .gitignore patterns"""

    def __init__(self, gitignore_path: str):
        """Load patterns from .gitignore file"""
        self.patterns: List[str] = []
        self.negation_patterns: List[str] = []

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("!"):
                        self.negation_patterns.append(line[1:])
                    else:
                        self.patterns.append(line)

    def should_ignore(self, file_path: str) -> bool:
        """Check if file matches ignore patterns"""
        # Check negation patterns first (exceptions)
        for pattern in self.negation_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return False

        # Check ignore patterns
        for pattern in self.patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True

        return False


class FileDiscovery:
    """
    File discovery with include/exclude patterns.
    
    AC-CRAWLER-005 Requirements:
    - Glob pattern support for includes/excludes
    - .gitignore parsing and respect
    - Size limits
    - Language detection by extension
    """

    # Supported language extensions
    LANGUAGE_EXTENSIONS = {
        "python": [".py"],
        "javascript": [".js", ".mjs", ".cjs"],
        "typescript": [".ts", ".tsx"],
        "csharp": [".cs"],
        "java": [".java"],
        "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
        "c": [".c", ".h"],
        "go": [".go"],
        "rust": [".rs"],
        "ruby": [".rb"],
        "php": [".php"],
        "sql": [".sql"],
        "oracle": [".sql", ".plsql"],
        "angular": [".ts", ".html"],
        "vue": [".vue"],
        "react": [".jsx", ".tsx"],
        "bash": [".sh"],
        "json": [".json"],
        "yaml": [".yaml", ".yml"],
        "xml": [".xml"],
        "html": [".html", ".htm"],
        "css": [".css", ".scss", ".sass", ".less"],
    }

    def __init__(
        self,
        root_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_file_size_mb: float = 50,
        respect_gitignore: bool = True,
    ):
        """
        Initialize file discoverer.

        Args:
            root_path: Root directory to scan
            include_patterns: Glob patterns to include (default: all)
            exclude_patterns: Glob patterns to exclude
            max_file_size_mb: Skip files larger than this
            respect_gitignore: Honor .gitignore patterns
        """
        self.root_path = Path(root_path)
        self.include_patterns = include_patterns or ["**/*"]
        self.exclude_patterns = exclude_patterns or []
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.respect_gitignore = respect_gitignore
        self.gitignore = None

        if self.respect_gitignore:
            gitignore_path = self.root_path / ".gitignore"
            if gitignore_path.exists():
                self.gitignore = GitignoreParser(str(gitignore_path))

    def discover(self) -> List[str]:
        """
        Discover files matching patterns.

        Returns:
            List of absolute file paths
        """
        discovered = set()

        for include_pattern in self.include_patterns:
            for match in self.root_path.glob(include_pattern):
                if not match.is_file():
                    continue

                # Check file size
                if match.stat().st_size > self.max_file_size_bytes:
                    logger.debug(
                        f"Skipping {match}: exceeds size limit"
                    )
                    continue

                # Check exclude patterns
                rel_path = match.relative_to(self.root_path)
                if self.exclude_patterns and self._matches_patterns(
                    str(rel_path), self.exclude_patterns
                ):
                    logger.debug(
                        f"Skipping {match}: matches exclude pattern"
                    )
                    continue

                # Check .gitignore
                if self.gitignore and self.gitignore.should_ignore(
                    str(rel_path)
                ):
                    logger.debug(
                        f"Skipping {match}: matches .gitignore"
                    )
                    continue

                discovered.add(str(match))

        return sorted(list(discovered))

    def discover_by_language(self, language: str) -> List[str]:
        """Discover files for specific language"""
        extensions = self.LANGUAGE_EXTENSIONS.get(
            language.lower(), []
        )
        if not extensions:
            logger.warning(f"Unknown language: {language}")
            return []

        all_files = self.discover()
        return [
            f for f in all_files
            if Path(f).suffix.lower() in extensions
        ]

    def get_statistics(self) -> FileStats:
        """Get discovery statistics"""
        files = self.discover()
        by_extension: Dict[str, int] = {}
        total_size = 0

        for file_path in files:
            path = Path(file_path)
            ext = path.suffix.lower() or "no_extension"
            by_extension[ext] = by_extension.get(ext, 0) + 1
            total_size += path.stat().st_size

        return FileStats(
            total_files=len(files),
            total_size_bytes=total_size,
            by_extension=by_extension,
            excluded_count=0,  # Would track manually excluded
            excluded_size_bytes=0,
        )

    @staticmethod
    def _matches_patterns(path: str, patterns: List[str]) -> bool:
        """Check if path matches any pattern"""
        import glob as glob_module
        
        for pattern in patterns:
            # Handle ** (globstar) patterns
            if "**" in pattern:
                # Convert to fnmatch-compatible pattern
                pattern_normalized = pattern.replace("**/", "")
                pattern_normalized = pattern_normalized.replace("**", "*")
            else:
                pattern_normalized = pattern
            
            if fnmatch.fnmatch(path, pattern_normalized):
                return True
            
            # Also try with trailing wildcards
            if fnmatch.fnmatch(path, pattern_normalized + "*"):
                return True
        
        return False
