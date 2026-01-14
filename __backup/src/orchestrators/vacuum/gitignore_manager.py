"""
GitIgnore Manager for Vacuum Orchestrator.

Parses .gitignore and identifies files/folders that are ignored and should be cleaned.
Handles recursive patterns and nested .gitignore files.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import List, Set, Tuple
import fnmatch


class GitIgnoreManager:
    """Manage .gitignore parsing and file matching."""
    
    # Essential files that should NEVER be deleted even if gitignored
    ESSENTIAL_PATTERNS = {
        '.env',  # Environment variables
        '.venv/',  # Virtual environment
        '__pycache__/',  # Python cache (can be regenerated but keep structure)
    }
    
    # Files that are safe to delete if gitignored
    SAFE_TO_DELETE_PATTERNS = {
        '*.pyc', '*.pyo', '*.pyd',  # Python bytecode
        '.coverage', 'coverage.xml', 'coverage.json',  # Coverage files
        '*.log', '*.logs',  # Log files
        '.pytest_cache/', '.mypy_cache/', '.ruff_cache/',  # Tool caches
        'htmlcov/',  # Coverage HTML report
        '*.tmp', '*.temp', '*.swp', '*.swo',  # Temporary files
        '.DS_Store', 'Thumbs.db',  # OS files
        'node_modules/',  # Dependencies
        'build/', 'dist/', '*.egg-info/',  # Build artifacts
    }
    
    def __init__(self, root_path: Path):
        """
        Initialize GitIgnore manager.
        
        Args:
            root_path: Repository root path
        """
        self.root_path = Path(root_path)
        self.ignore_patterns = []
        self.gitignore_files = []
        self._load_gitignore()
    
    def _load_gitignore(self):
        """Load and parse all .gitignore files in the repository."""
        # Load root .gitignore
        root_gitignore = self.root_path / '.gitignore'
        if root_gitignore.exists():
            self.gitignore_files.append(root_gitignore)
            self.ignore_patterns.extend(self._parse_gitignore(root_gitignore))
        
        # Load nested .gitignore files
        for gitignore_path in self.root_path.rglob('.gitignore'):
            if gitignore_path != root_gitignore:
                self.gitignore_files.append(gitignore_path)
                # Nested gitignore patterns are relative to their directory
                patterns = self._parse_gitignore(gitignore_path)
                base_dir = gitignore_path.parent.relative_to(self.root_path)
                for pattern in patterns:
                    self.ignore_patterns.append(f"{base_dir}/{pattern}")
    
    def _parse_gitignore(self, gitignore_path: Path) -> List[str]:
        """
        Parse .gitignore file and extract patterns.
        
        Args:
            gitignore_path: Path to .gitignore file
        
        Returns:
            List of ignore patterns
        """
        patterns = []
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Remove inline comments
                    if ' #' in line:
                        line = line[:line.index(' #')].strip()
                    
                    patterns.append(line)
        
        except Exception as e:
            print(f"Warning: Could not parse {gitignore_path}: {e}")
        
        return patterns
    
    def is_ignored(self, filepath: str) -> bool:
        """
        Check if file/folder matches any gitignore pattern.
        
        Args:
            filepath: Relative path from repository root
        
        Returns:
            True if file is gitignored
        """
        # Normalize path separators
        filepath = filepath.replace('\\', '/')
        
        for pattern in self.ignore_patterns:
            # Handle negation patterns (!)
            if pattern.startswith('!'):
                if self._match_pattern(pattern[1:], filepath):
                    return False
                continue
            
            if self._match_pattern(pattern, filepath):
                return True
        
        return False
    
    def _match_pattern(self, pattern: str, filepath: str) -> bool:
        """
        Match filepath against gitignore pattern.
        
        Args:
            pattern: Gitignore pattern
            filepath: File path to check
        
        Returns:
            True if pattern matches
        """
        # Directory patterns end with /
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            # Match directory name anywhere in path
            if f"/{pattern}/" in f"/{filepath}/":
                return True
            if filepath.startswith(f"{pattern}/"):
                return True
            return False
        
        # Pattern with / is relative to repo root
        if '/' in pattern:
            if fnmatch.fnmatch(filepath, pattern):
                return True
            # Try as directory prefix
            if filepath.startswith(f"{pattern}/"):
                return True
        else:
            # Pattern without / matches anywhere
            filename = filepath.split('/')[-1]
            if fnmatch.fnmatch(filename, pattern):
                return True
            # Also check full path
            if fnmatch.fnmatch(filepath, f"**/{pattern}"):
                return True
        
        return False
    
    def is_essential(self, filepath: str) -> bool:
        """
        Check if file is essential and should never be deleted.
        
        Args:
            filepath: Relative path from repository root
        
        Returns:
            True if file is essential
        """
        filepath = filepath.replace('\\', '/')
        
        for pattern in self.ESSENTIAL_PATTERNS:
            if pattern.endswith('/'):
                # Directory pattern
                if filepath.startswith(pattern) or f"/{pattern}" in filepath:
                    return True
            else:
                # File pattern
                if fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(filepath, f"**/{pattern}"):
                    return True
        
        return False
    
    def is_safe_to_delete(self, filepath: str) -> bool:
        """
        Check if gitignored file is safe to delete.
        
        Args:
            filepath: Relative path from repository root
        
        Returns:
            True if safe to delete
        """
        if self.is_essential(filepath):
            return False
        
        filepath = filepath.replace('\\', '/')
        
        for pattern in self.SAFE_TO_DELETE_PATTERNS:
            if pattern.endswith('/'):
                # Directory pattern
                if filepath.startswith(pattern) or f"/{pattern}" in filepath:
                    return True
            else:
                # File pattern
                if fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(filepath, f"**/{pattern}"):
                    return True
        
        return False
    
    def categorize_gitignored_file(self, filepath: str) -> Tuple[str, str]:
        """
        Categorize a gitignored file for action.
        
        Args:
            filepath: Relative path from repository root
        
        Returns:
            Tuple of (action, reason) where action is DELETE, ARCHIVE, or KEEP
        """
        if self.is_essential(filepath):
            return 'KEEP', 'Essential for functionality'
        
        if self.is_safe_to_delete(filepath):
            return 'DELETE', 'Temporary/cache file, can be regenerated'
        
        # Default to archive for safety
        return 'ARCHIVE', 'Gitignored but not confirmed safe to delete'
    
    def scan_gitignored_files(self) -> dict:
        """
        Scan repository for gitignored files and categorize them.
        
        Returns:
            Dictionary with categorized files
        """
        results = {
            'delete': [],
            'archive': [],
            'keep': [],
            'total_size_delete': 0,
            'total_size_archive': 0
        }
        
        # Scan all files
        for item in self.root_path.rglob('*'):
            # Skip .git directory
            if '.git' in item.parts:
                continue
            
            if not item.is_file():
                continue
            
            rel_path = str(item.relative_to(self.root_path)).replace('\\', '/')
            
            # Check if gitignored
            if self.is_ignored(rel_path):
                action, reason = self.categorize_gitignored_file(rel_path)
                
                file_size = item.stat().st_size
                
                file_info = {
                    'path': rel_path,
                    'size': file_size,
                    'size_mb': round(file_size / 1024 / 1024, 2),
                    'reason': reason
                }
                
                if action == 'DELETE':
                    results['delete'].append(file_info)
                    results['total_size_delete'] += file_size
                elif action == 'ARCHIVE':
                    results['archive'].append(file_info)
                    results['total_size_archive'] += file_size
                else:
                    results['keep'].append(file_info)
        
        # Convert total sizes to MB
        results['total_size_delete_mb'] = round(results['total_size_delete'] / 1024 / 1024, 2)
        results['total_size_archive_mb'] = round(results['total_size_archive'] / 1024 / 1024, 2)
        
        return results
