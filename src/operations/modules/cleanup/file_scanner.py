"""
CORTEX Cleanup: Comprehensive File Scanner

Recursively scans repository to categorize all files by type, purpose, age, and usage.
Builds file inventory for intelligent cleanup decisions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import mimetypes
import hashlib

logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """File category classification"""
    DOCUMENTATION = "documentation"
    SOURCE_CODE = "source_code"
    TEST = "test"
    SCRIPT = "script"
    BACKUP = "backup"
    TEMPORARY = "temporary"
    CONFIGURATION = "configuration"
    DATA = "data"
    BUILD_ARTIFACT = "build_artifact"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"


class FilePurpose(Enum):
    """File purpose classification"""
    CORE = "core"  # Essential to system operation
    FEATURE = "feature"  # Feature implementation
    UTILITY = "utility"  # Helper/utility
    ARCHIVE = "archive"  # Historical/archived
    GENERATED = "generated"  # Auto-generated
    EXAMPLE = "example"  # Example/demo
    TEMPORARY = "temporary"  # Temporary/work-in-progress
    UNKNOWN = "unknown"


@dataclass
class FileMetadata:
    """Complete file metadata"""
    path: Path
    relative_path: str
    category: FileCategory
    purpose: FilePurpose
    
    # File properties
    size_bytes: int
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime
    
    # Content properties
    mime_type: str
    extension: str
    is_binary: bool
    line_count: Optional[int] = None
    content_hash: Optional[str] = None
    
    # Classification
    is_protected: bool = False
    is_duplicate: bool = False
    is_obsolete: bool = False
    
    # Relationships
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # Recommendations
    action: Optional[str] = None  # keep, delete, move, consolidate
    reason: Optional[str] = None
    destination: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path': str(self.path),
            'relative_path': self.relative_path,
            'category': self.category.value,
            'purpose': self.purpose.value,
            'size_bytes': self.size_bytes,
            'created_time': self.created_time.isoformat(),
            'modified_time': self.modified_time.isoformat(),
            'accessed_time': self.accessed_time.isoformat(),
            'mime_type': self.mime_type,
            'extension': self.extension,
            'is_binary': self.is_binary,
            'line_count': self.line_count,
            'content_hash': self.content_hash,
            'is_protected': self.is_protected,
            'is_duplicate': self.is_duplicate,
            'is_obsolete': self.is_obsolete,
            'dependencies': self.dependencies,
            'dependents': self.dependents,
            'action': self.action,
            'reason': self.reason,
            'destination': self.destination
        }


class FileScanner:
    """
    Comprehensive file scanner for cleanup orchestrator.
    
    Capabilities:
    - Recursive scanning from repository root
    - File categorization by type and purpose
    - Metadata extraction and analysis
    - Duplicate detection via content hashing
    - Protection validation
    - Relationship mapping (dependencies/dependents)
    """
    
    # Protected paths that should never be scanned/modified
    PROTECTED_PATHS = {
        '.git/', '.github/', '.vscode/', 'node_modules/', '__pycache__/',
        '.pytest_cache/', '.mypy_cache/', 'venv/', 'env/', '.env/'
    }
    
    # Protected file patterns
    PROTECTED_FILES = {
        'LICENSE', 'README.md', 'CHANGELOG.md', '.gitignore', '.gitattributes',
        'requirements.txt', 'optional-requirements.txt', 'package.json', 
        'tsconfig.json', 'pytest.ini', 'VERSION',
        'cortex.config.json', 'cortex.config.template.json', 'mkdocs.yml',
        'cortex-operations.yaml'
    }
    
    # Backup file patterns
    BACKUP_PATTERNS = {
        '*.bak', '*.backup', '*.old', '*_backup_*', '*_old_*',
        '*.orig', '*-BACKUP-*', '*BACKUP*', '*.tmp', '*.temp'
    }
    
    # Temporary file patterns
    TEMP_PATTERNS = {
        '*.tmp', '*.temp', '*.swp', '*.swo', '*~', '.DS_Store',
        'Thumbs.db', 'desktop.ini', '*.pyc', '*.pyo', '*.pyd'
    }
    
    # Documentation patterns
    DOC_PATTERNS = {
        '*.md', '*.rst', '*.txt', '*.doc', '*.docx', '*.pdf'
    }
    
    # Test patterns
    TEST_PATTERNS = {
        'test_*.py', '*_test.py', 'tests/', 'test/'
    }
    
    def __init__(self, project_root: Path, protected_paths: Optional[Set[str]] = None):
        """
        Initialize file scanner.
        
        Args:
            project_root: Root directory of project to scan
            protected_paths: Additional paths to protect (beyond defaults)
        """
        self.project_root = project_root
        self.protected_paths = self.PROTECTED_PATHS.copy()
        if protected_paths:
            self.protected_paths.update(protected_paths)
        
        # Scanning results
        self.files: Dict[str, FileMetadata] = {}
        self.duplicates: Dict[str, List[str]] = {}
        self.categories: Dict[FileCategory, List[str]] = {}
        self.purposes: Dict[FilePurpose, List[str]] = {}
        
        # Statistics
        self.total_files = 0
        self.total_size = 0
        self.protected_count = 0
        self.duplicate_count = 0
        self.obsolete_count = 0
    
    def scan(self, path: Optional[Path] = None) -> Dict[str, FileMetadata]:
        """
        Recursively scan directory and categorize all files.
        
        Args:
            path: Starting path (defaults to project_root)
            
        Returns:
            Dictionary of relative_path -> FileMetadata
        """
        start_path = path or self.project_root
        
        logger.info(f"Starting file scan from: {start_path}")
        logger.info(f"Protected paths: {len(self.protected_paths)}")
        
        try:
            self._scan_recursive(start_path)
            self._detect_duplicates()
            self._build_category_index()
            
            logger.info(f"Scan complete: {self.total_files} files, {self.total_size / 1024 / 1024:.2f}MB")
            logger.info(f"Protected: {self.protected_count}, Duplicates: {self.duplicate_count}")
            
            return self.files
            
        except Exception as e:
            logger.error(f"File scan failed: {e}", exc_info=True)
            raise
    
    def _scan_recursive(self, path: Path) -> None:
        """Recursively scan directory"""
        try:
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                return
            
            # Check if path is protected
            if self._is_protected_path(path):
                logger.debug(f"Skipping protected path: {path}")
                return
            
            # Scan directory
            if path.is_dir():
                try:
                    # First, process files in current directory (including root)
                    for item in path.iterdir():
                        if item.is_file():
                            self._process_file(item)
                    
                    # Then recursively scan subdirectories
                    for item in path.iterdir():
                        if item.is_dir():
                            self._scan_recursive(item)
                except PermissionError:
                    logger.warning(f"Permission denied: {path}")
                    return
            
            # Process file (for when path itself is a file)
            elif path.is_file():
                self._process_file(path)
        
        except Exception as e:
            logger.error(f"Error scanning {path}: {e}")
    
    def _process_file(self, file_path: Path) -> None:
        """Process and categorize a single file"""
        try:
            # Get relative path
            try:
                relative_path = str(file_path.relative_to(self.project_root))
            except ValueError:
                logger.warning(f"File outside project root: {file_path}")
                return
            
            # Check if protected
            is_protected = self._is_protected_file(file_path)
            
            # Get file stats
            stat = file_path.stat()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            mime_type = mime_type or 'application/octet-stream'
            
            # Check if binary
            is_binary = self._is_binary_file(file_path)
            
            # Count lines for text files
            line_count = None
            content_hash = None
            if not is_binary:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    line_count = content.count('\n') + 1
                    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                except Exception as e:
                    logger.debug(f"Could not read text file {file_path}: {e}")
            else:
                try:
                    content_bytes = file_path.read_bytes()
                    content_hash = hashlib.md5(content_bytes).hexdigest()
                except Exception as e:
                    logger.debug(f"Could not hash binary file {file_path}: {e}")
            
            # Categorize file
            category = self._categorize_file(file_path)
            purpose = self._determine_purpose(file_path, category)
            
            # Create metadata
            metadata = FileMetadata(
                path=file_path,
                relative_path=relative_path,
                category=category,
                purpose=purpose,
                size_bytes=stat.st_size,
                created_time=datetime.fromtimestamp(stat.st_ctime),
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                accessed_time=datetime.fromtimestamp(stat.st_atime),
                mime_type=mime_type,
                extension=file_path.suffix.lower(),
                is_binary=is_binary,
                line_count=line_count,
                content_hash=content_hash,
                is_protected=is_protected
            )
            
            # Store metadata
            self.files[relative_path] = metadata
            
            # Update statistics
            self.total_files += 1
            self.total_size += stat.st_size
            if is_protected:
                self.protected_count += 1
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    def _is_protected_path(self, path: Path) -> bool:
        """Check if path is protected"""
        try:
            relative_path = str(path.relative_to(self.project_root)).replace('\\', '/')
            
            # Check protected path prefixes
            for protected in self.protected_paths:
                if relative_path.startswith(protected):
                    return True
                if relative_path == protected.rstrip('/'):
                    return True
            
            return False
            
        except ValueError:
            # Path outside project root is protected
            return True
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected"""
        # Check filename
        if file_path.name in self.PROTECTED_FILES:
            return True
        
        # Check if in protected directory
        return self._is_protected_path(file_path)
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                if b'\x00' in chunk:
                    return True
                
                # Check for high proportion of non-text characters
                text_chars = bytes(range(32, 127)) + b'\n\r\t\b'
                non_text = sum(1 for byte in chunk if byte not in text_chars)
                return non_text / len(chunk) > 0.3 if chunk else False
                
        except Exception:
            return True
    
    def _categorize_file(self, file_path: Path) -> FileCategory:
        """Categorize file by type"""
        name = file_path.name.lower()
        path_str = str(file_path).lower()
        
        # Check backup patterns
        for pattern in self.BACKUP_PATTERNS:
            if self._matches_pattern(name, pattern):
                return FileCategory.BACKUP
        
        # Check temporary patterns
        for pattern in self.TEMP_PATTERNS:
            if self._matches_pattern(name, pattern):
                return FileCategory.TEMPORARY
        
        # Check documentation patterns
        for pattern in self.DOC_PATTERNS:
            if self._matches_pattern(name, pattern):
                return FileCategory.DOCUMENTATION
        
        # Check test patterns
        for pattern in self.TEST_PATTERNS:
            if self._matches_pattern(name, pattern) or '/tests/' in path_str or '/test/' in path_str:
                return FileCategory.TEST
        
        # Check by extension
        ext = file_path.suffix.lower()
        if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h']:
            return FileCategory.SOURCE_CODE
        elif ext in ['.sh', '.bash', '.ps1', '.cmd', '.bat']:
            return FileCategory.SCRIPT
        elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']:
            return FileCategory.CONFIGURATION
        elif ext in ['.db', '.sqlite', '.sqlite3', '.sql']:
            return FileCategory.DATA
        elif ext in ['.whl', '.egg', '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib']:
            return FileCategory.BUILD_ARTIFACT
        
        return FileCategory.UNKNOWN
    
    def _determine_purpose(self, file_path: Path, category: FileCategory) -> FilePurpose:
        """Determine file purpose"""
        name = file_path.name.lower()
        path_str = str(file_path).lower()
        
        # Check for core paths
        if any(core in path_str for core in ['src/tier0/', 'src/tier1/', 'src/cortex_agents/', 'cortex-brain/']):
            return FilePurpose.CORE
        
        # Check for archive/backup
        if 'archive' in path_str or 'backup' in path_str or category == FileCategory.BACKUP:
            return FilePurpose.ARCHIVE
        
        # Check for temporary
        if 'temp' in path_str or 'tmp' in path_str or category == FileCategory.TEMPORARY:
            return FilePurpose.TEMPORARY
        
        # Check for examples
        if 'example' in path_str or 'demo' in path_str or 'sample' in path_str:
            return FilePurpose.EXAMPLE
        
        # Check for generated files
        if 'generated' in path_str or '__pycache__' in path_str:
            return FilePurpose.GENERATED
        
        # Check for utilities
        if 'util' in path_str or 'helper' in path_str or 'tool' in path_str:
            return FilePurpose.UTILITY
        
        # Default to feature for source code/tests
        if category in [FileCategory.SOURCE_CODE, FileCategory.TEST]:
            return FilePurpose.FEATURE
        
        return FilePurpose.UNKNOWN
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern"""
        from fnmatch import fnmatch
        return fnmatch(filename, pattern)
    
    def _detect_duplicates(self) -> None:
        """Detect duplicate files by content hash"""
        hash_map: Dict[str, List[str]] = {}
        
        for relative_path, metadata in self.files.items():
            if metadata.content_hash:
                if metadata.content_hash not in hash_map:
                    hash_map[metadata.content_hash] = []
                hash_map[metadata.content_hash].append(relative_path)
        
        # Find duplicates (hash appears more than once)
        for content_hash, paths in hash_map.items():
            if len(paths) > 1:
                self.duplicates[content_hash] = paths
                self.duplicate_count += len(paths) - 1  # Don't count the original
                
                # Mark duplicates
                for path in paths[1:]:  # Keep first, mark others
                    self.files[path].is_duplicate = True
        
        logger.info(f"Found {len(self.duplicates)} duplicate file groups ({self.duplicate_count} duplicates)")
    
    def _build_category_index(self) -> None:
        """Build category and purpose indexes"""
        for relative_path, metadata in self.files.items():
            # Category index
            if metadata.category not in self.categories:
                self.categories[metadata.category] = []
            self.categories[metadata.category].append(relative_path)
            
            # Purpose index
            if metadata.purpose not in self.purposes:
                self.purposes[metadata.purpose] = []
            self.purposes[metadata.purpose].append(relative_path)
    
    def get_files_by_category(self, category: FileCategory) -> List[FileMetadata]:
        """Get all files in a category"""
        paths = self.categories.get(category, [])
        return [self.files[path] for path in paths]
    
    def get_files_by_purpose(self, purpose: FilePurpose) -> List[FileMetadata]:
        """Get all files with a purpose"""
        paths = self.purposes.get(purpose, [])
        return [self.files[path] for path in paths]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scanning statistics"""
        return {
            'total_files': self.total_files,
            'total_size_bytes': self.total_size,
            'total_size_mb': self.total_size / 1024 / 1024,
            'protected_count': self.protected_count,
            'duplicate_count': self.duplicate_count,
            'duplicate_groups': len(self.duplicates),
            'categories': {cat.value: len(paths) for cat, paths in self.categories.items()},
            'purposes': {purpose.value: len(paths) for purpose, paths in self.purposes.items()}
        }
