"""
CORTEX Tier 1: File Tracker
Tracks file modifications during conversations

Task 1.4: FileTracker
Duration: 1 hour
"""

import re
from typing import List, Set, Dict, Optional
from pathlib import Path
from datetime import datetime


class FileTracker:
    """
    Tracks file modifications during conversations
    
    Responsibilities:
    - Extract file paths from text
    - Normalize file paths
    - Track file modification patterns
    - Associate files with conversations
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize file tracker
        
        Args:
            workspace_root: Root directory of workspace (for path normalization)
        """
        self.workspace_root = workspace_root or Path.cwd()
        
        # File path patterns
        self.absolute_path_pattern = re.compile(
            r'(?:^|[\s\'"(])'
            r'(/[a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)'
            r'(?:$|[\s\'")\]])',
            re.MULTILINE
        )
        
        self.relative_path_pattern = re.compile(
            r'(?:^|[\s\'"(])'
            r'([a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*\.[a-zA-Z0-9]+)'
            r'(?:$|[\s\'")\]])',
            re.MULTILINE
        )
        
        # Common file extensions in CORTEX
        self.valid_extensions = {
            'py', 'md', 'yaml', 'yml', 'json', 'jsonl',
            'txt', 'sql', 'db', 'html', 'css', 'js',
            'ts', 'tsx', 'cs', 'csproj', 'ps1', 'sh',
            'bash', 'xml', 'config', 'template', 'example'
        }
    
    def extract_files_from_text(self, text: str) -> List[str]:
        """
        Extract file paths from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of normalized file paths
        """
        files = set()
        
        # Extract absolute paths
        absolute_matches = self.absolute_path_pattern.findall(text)
        for match in absolute_matches:
            if self._is_valid_file(match):
                normalized = self._normalize_path(match)
                if normalized:
                    files.add(normalized)
        
        # Extract relative paths
        relative_matches = self.relative_path_pattern.findall(text)
        for match in relative_matches:
            if self._is_valid_file(match):
                normalized = self._normalize_path(match)
                if normalized:
                    files.add(normalized)
        
        return sorted(files)
    
    def _is_valid_file(self, path: str) -> bool:
        """
        Check if path looks like a valid file
        
        Args:
            path: Potential file path
            
        Returns:
            True if valid
        """
        # Must have extension
        if '.' not in path:
            return False
        
        # Check extension
        parts = path.split('.')
        if len(parts) < 2:
            return False
        
        ext = parts[-1].lower()
        
        # Special case for compound extensions like .template.json
        if len(parts) > 2:
            compound_ext = f"{parts[-2]}.{parts[-1]}".lower()
            if compound_ext in {'template.json', 'example.json', 'test.py'}:
                return True
        
        return ext in self.valid_extensions
    
    def _normalize_path(self, path: str) -> Optional[str]:
        """
        Normalize file path
        
        Args:
            path: File path to normalize
            
        Returns:
            Normalized path or None if invalid
        """
        try:
            # Convert to Path object
            p = Path(path)
            
            # If absolute, try to make relative to workspace
            if p.is_absolute():
                try:
                    rel_path = p.relative_to(self.workspace_root)
                    return str(rel_path)
                except ValueError:
                    # Path not under workspace, keep absolute
                    return str(p)
            else:
                # Already relative
                return str(p)
        except Exception:
            return None
    
    def track_file_modifications(
        self,
        before_text: str,
        after_text: str
    ) -> List[str]:
        """
        Compare two texts to find newly mentioned files
        
        Args:
            before_text: Text before operation
            after_text: Text after operation
            
        Returns:
            List of newly mentioned files
        """
        before_files = set(self.extract_files_from_text(before_text))
        after_files = set(self.extract_files_from_text(after_text))
        
        new_files = after_files - before_files
        return sorted(new_files)
    
    def get_file_patterns(self, files: List[str]) -> Dict[str, List[str]]:
        """
        Group files by type/pattern and directory
        
        Args:
            files: List of file paths
            
        Returns:
            Dictionary mapping patterns to file lists
        """
        patterns = {
            'python': [],
            'documentation': [],
            'configuration': [],
            'database': [],
            'frontend': [],
            'scripts': [],
            'tests': [],
            'other': []
        }
        
        # Also track by directory patterns
        dir_patterns = {}
        
        for file in files:
            file_lower = file.lower()
            
            # Extract directory for pattern matching
            file_dir = str(Path(file).parent)
            if file_dir not in dir_patterns:
                dir_patterns[file_dir] = []
            dir_patterns[file_dir].append(file)
            
            if file_lower.endswith('.py'):
                if 'test' in file_lower:
                    patterns['tests'].append(file)
                else:
                    patterns['python'].append(file)
            elif file_lower.endswith(('.md', '.txt')):
                patterns['documentation'].append(file)
            elif file_lower.endswith(('.yaml', '.yml', '.json', '.config')):
                patterns['configuration'].append(file)
            elif file_lower.endswith(('.db', '.sql')):
                patterns['database'].append(file)
            elif file_lower.endswith(('.html', '.css', '.js', '.ts', '.tsx')):
                patterns['frontend'].append(file)
            elif file_lower.endswith(('.ps1', '.sh', '.bash')):
                patterns['scripts'].append(file)
            else:
                patterns['other'].append(file)
        
        # Remove empty patterns
        result = {k: v for k, v in patterns.items() if v}
        
        # Add directory patterns to results
        result.update(dir_patterns)
        
        return result
    
    def get_directory_hierarchy(self, files: List[str]) -> Dict[str, int]:
        """
        Get directory modification counts
        
        Args:
            files: List of file paths
            
        Returns:
            Dictionary mapping directories to file counts
        """
        dir_counts = {}
        
        for file in files:
            # Get directory
            directory = str(Path(file).parent)
            
            # Count
            dir_counts[directory] = dir_counts.get(directory, 0) + 1
        
        return dict(sorted(dir_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_file_statistics(self, files: List[str]) -> Dict:
        """
        Get statistics about files
        
        Args:
            files: List of file paths
            
        Returns:
            Statistics dictionary
        """
        patterns = self.get_file_patterns(files)
        directories = self.get_directory_hierarchy(files)
        
        # Count extensions
        by_extension = {}
        for file in files:
            ext = Path(file).suffix
            by_extension[ext] = by_extension.get(ext, 0) + 1
        
        return {
            'total_files': len(files),
            'total_directories': len(directories),
            'by_type': {k: len(v) for k, v in patterns.items()},
            'by_directory': directories,
            'by_extension': by_extension,
            'files_by_type': patterns
        }
    
    def format_file_list(self, files: List[str], max_files: int = 10) -> str:
        """
        Format file list for display
        
        Args:
            files: List of file paths
            max_files: Maximum files to display
            
        Returns:
            Formatted string
        """
        if not files:
            return "No files"
        
        if len(files) <= max_files:
            return '\n'.join(f"  - {f}" for f in files)
        else:
            shown = '\n'.join(f"  - {f}" for f in files[:max_files])
            remaining = len(files) - max_files
            return f"{shown}\n  ... and {remaining} more"
