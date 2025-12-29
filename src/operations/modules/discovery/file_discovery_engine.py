"""
File Discovery Engine - Recursive Directory Traversal

Discovers files in a codebase with metadata collection, exclusion filtering,
and language detection.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Generator

from .models import DiscoveryScope, FileInfo, FileInventory
from .exclusion_engine import ExclusionEngine
from .language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class FileDiscoveryEngine:
    """
    Discovers and catalogs files in a directory tree.
    
    Features:
    - Recursive directory traversal
    - Exclusion pattern filtering
    - Language detection
    - Metadata collection (size, hash, lines, encoding)
    - Progress tracking
    """
    
    def __init__(self, exclusion_engine: ExclusionEngine):
        """
        Initialize file discovery engine.
        
        Args:
            exclusion_engine: Exclusion engine for filtering
        """
        self.exclusion_engine = exclusion_engine
        self.language_detector = LanguageDetector()
        logger.debug("FileDiscoveryEngine initialized")
    
    def discover(self, scope: DiscoveryScope) -> FileInventory:
        """
        Discover files within scope.
        
        Args:
            scope: Discovery scope defining root path and patterns
        
        Returns:
            FileInventory with discovered files and statistics
        
        Raises:
            ValueError: If scope is invalid
        """
        logger.info(f"Starting file discovery: {scope.root_path}")
        
        start_time = datetime.now()
        files: List[FileInfo] = []
        total_size = 0
        total_lines = 0
        languages = {}
        
        # Discover files
        for file_path in self._traverse_directory(scope):
            try:
                file_info = self._collect_metadata(file_path, scope.root_path)
                files.append(file_info)
                
                total_size += file_info.size_bytes
                total_lines += file_info.line_count
                languages[file_info.language] = languages.get(file_info.language, 0) + 1
                
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
                continue
        
        discovery_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Discovered {len(files)} files in {discovery_time:.2f}s")
        
        return FileInventory(
            files=files,
            total_files=len(files),
            total_size=total_size,
            total_lines=total_lines,
            languages=languages,
            discovery_time=discovery_time
        )
    
    def _traverse_directory(self, scope: DiscoveryScope) -> Generator[Path, None, None]:
        """
        Recursively traverse directory tree.
        
        Args:
            scope: Discovery scope
        
        Yields:
            Paths to discovered files
        """
        def _traverse_recursive(path: Path, current_depth: int = 0):
            """Recursive traversal helper."""
            try:
                # Check depth limit
                if scope.max_depth != -1 and current_depth > scope.max_depth:
                    return
                
                # Iterate directory contents
                for item in path.iterdir():
                    # Calculate relative path
                    try:
                        rel_path = item.relative_to(scope.root_path)
                    except ValueError:
                        continue
                    
                    # Check exclusions
                    if self.exclusion_engine.should_exclude(item, rel_path):
                        continue
                    
                    if item.is_file():
                        # Check include patterns
                        if self._matches_include_patterns(item, scope.include_patterns):
                            yield item
                    elif item.is_dir():
                        # Recurse into subdirectory
                        if scope.follow_symlinks or not item.is_symlink():
                            yield from _traverse_recursive(item, current_depth + 1)
            
            except PermissionError:
                logger.warning(f"Permission denied: {path}")
            except Exception as e:
                logger.warning(f"Error traversing {path}: {e}")
        
        yield from _traverse_recursive(scope.root_path, 0)
    
    def _collect_metadata(self, file_path: Path, root_path: Path) -> FileInfo:
        """
        Collect metadata for a file.
        
        Args:
            file_path: Path to file
            root_path: Root path for relative calculation
        
        Returns:
            FileInfo with metadata
        """
        # Calculate relative path
        relative_path = file_path.relative_to(root_path)
        
        # Get file stats
        stat = file_path.stat()
        size_bytes = stat.st_size
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        
        # Detect language
        language = self.language_detector.detect(file_path)
        
        # Count lines and calculate hash
        line_count = 0
        file_hash = ""
        encoding = "utf-8"
        
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        except UnicodeDecodeError:
            # Try binary read for hash
            try:
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                    file_hash = hashlib.sha256(content_bytes).hexdigest()[:16]
                    # Estimate line count
                    line_count = content_bytes.count(b'\n')
                encoding = "binary"
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {e}")
                file_hash = "error"
                encoding = "unknown"
        except Exception as e:
            logger.warning(f"Failed to process {file_path}: {e}")
            file_hash = "error"
        
        return FileInfo(
            path=file_path,
            relative_path=relative_path,
            language=language,
            size_bytes=size_bytes,
            line_count=line_count,
            modified_at=modified_at,
            hash=file_hash,
            encoding=encoding
        )
    
    def _matches_include_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """
        Check if file matches include patterns.
        
        Args:
            file_path: Path to check
            patterns: List of patterns to match
        
        Returns:
            True if file matches any pattern
        """
        import fnmatch
        
        # Default pattern "*" matches everything
        if "*" in patterns:
            return True
        
        filename = file_path.name
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
