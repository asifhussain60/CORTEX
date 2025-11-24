"""
Workspace Cleanup Operation
CORTEX 3.0 Phase 1.1 Week 3 - Monolithic MVP

Safely removes temporary files, old logs, and cache to free disk space.
Includes safety checks to never delete source code or critical files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum


class CleanupCategory(Enum):
    """Categories of files that can be cleaned."""
    TEMP_FILES = "temp_files"
    CACHE_DIRS = "cache_dirs"
    OLD_LOGS = "old_logs"
    BUILD_ARTIFACTS = "build_artifacts"


class CleanupResult:
    """Result of cleanup operation."""
    
    def __init__(self):
        self.files_removed: List[str] = []
        self.dirs_removed: List[str] = []
        self.space_freed_bytes: int = 0
        self.errors: List[str] = []
        self.skipped: List[Tuple[str, str]] = []  # (path, reason)
    
    def add_file(self, path: str, size: int):
        """Record file removal."""
        self.files_removed.append(path)
        self.space_freed_bytes += size
    
    def add_directory(self, path: str, size: int):
        """Record directory removal."""
        self.dirs_removed.append(path)
        self.space_freed_bytes += size
    
    def add_error(self, message: str):
        """Record error."""
        self.errors.append(message)
    
    def add_skip(self, path: str, reason: str):
        """Record skipped item."""
        self.skipped.append((path, reason))
    
    @property
    def total_items_removed(self) -> int:
        """Total files + directories removed."""
        return len(self.files_removed) + len(self.dirs_removed)
    
    @property
    def space_freed_mb(self) -> float:
        """Space freed in MB."""
        return self.space_freed_bytes / (1024 * 1024)


def is_safe_to_delete(path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Check if path is safe to delete.
    
    NEVER deletes:
        - Source code (.py, .js, .ts, .java, .cpp, etc.)
        - Configuration files (.yaml, .json, .toml, .ini)
        - Documentation (.md, .rst, .txt)
        - Git repository (.git/)
        - Brain databases (cortex-brain/*.db)
        - Package manifests (requirements.txt, package.json, etc.)
    
    Args:
        path: Path to check
        project_root: Project root directory
    
    Returns:
        (is_safe, reason)
    """
    # Protected extensions
    source_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala'
    }
    
    config_extensions = {
        '.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf'
    }
    
    doc_extensions = {
        '.md', '.rst', '.txt', '.pdf', '.doc', '.docx'
    }
    
    protected_extensions = source_extensions | config_extensions | doc_extensions
    
    # Protected directories
    protected_dirs = {
        '.git', '.github', 'src', 'docs', 'tests', 'prompts',
        'cortex-brain', 'scripts', 'workflows', 'examples'
    }
    
    # Protected filenames
    protected_files = {
        'requirements.txt', 'package.json', 'setup.py', 'pyproject.toml',
        'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', '.gitignore',
        'LICENSE', 'README.md', 'CHANGELOG.md'
    }
    
    path_str = str(path)
    path_name = path.name.lower()
    
    # Check if in protected directory
    try:
        rel_path = path.relative_to(project_root)
        parts = rel_path.parts
        if parts and parts[0] in protected_dirs:
            return False, f"Inside protected directory: {parts[0]}"
    except ValueError:
        # Path not relative to project_root
        return False, "Outside project root"
    
    # Check protected filenames
    if path.name in protected_files:
        return False, f"Protected file: {path.name}"
    
    # Check protected extensions
    if path.suffix.lower() in protected_extensions:
        return False, f"Protected extension: {path.suffix}"
    
    # Check for brain databases
    if '.db' in path_name and 'cortex-brain' in path_str:
        return False, "Brain database file"
    
    return True, "Safe to delete"


def find_temp_files(project_root: Path) -> List[Path]:
    """
    Find temporary files in project.
    
    Targets:
        - *.tmp, *.temp
        - __pycache__ directories
        - *.pyc, *.pyo, *.pyd files
        - .pytest_cache directories
        - *.log files in temp locations
    
    Args:
        project_root: Project root directory
    
    Returns:
        List of temporary file/directory paths
    """
    temp_items = []
    
    # Patterns to find
    temp_patterns = ['*.tmp', '*.temp', '*.pyc', '*.pyo', '*.pyd']
    temp_dirs = ['__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache']
    
    # Search for files
    for pattern in temp_patterns:
        for item in project_root.rglob(pattern):
            safe, _ = is_safe_to_delete(item, project_root)
            if safe:
                temp_items.append(item)
    
    # Search for directories
    for dirname in temp_dirs:
        for item in project_root.rglob(dirname):
            if item.is_dir():
                safe, _ = is_safe_to_delete(item, project_root)
                if safe:
                    temp_items.append(item)
    
    return temp_items


def find_old_logs(project_root: Path, days_old: int = 30) -> List[Path]:
    """
    Find log files older than specified days.
    
    Args:
        project_root: Project root directory
        days_old: Consider files older than this many days
    
    Returns:
        List of old log file paths
    """
    old_logs = []
    cutoff_time = datetime.now() - timedelta(days=days_old)
    
    logs_dir = project_root / 'logs'
    if not logs_dir.exists():
        return old_logs
    
    for log_file in logs_dir.rglob('*.log'):
        if log_file.is_file():
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_time:
                    safe, _ = is_safe_to_delete(log_file, project_root)
                    if safe:
                        old_logs.append(log_file)
            except (OSError, ValueError):
                # Skip files we can't read
                continue
    
    return old_logs


def find_large_cache_files(project_root: Path, min_size_mb: int = 10) -> List[Path]:
    """
    Find large cache files (>10MB by default).
    
    Args:
        project_root: Project root directory
        min_size_mb: Minimum file size in MB
    
    Returns:
        List of large cache file paths
    """
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024
    
    cache_patterns = ['*.cache', '*.pkl', '*.pickle', '*.dat']
    
    for pattern in cache_patterns:
        for item in project_root.rglob(pattern):
            if item.is_file():
                try:
                    if item.stat().st_size >= min_size_bytes:
                        safe, _ = is_safe_to_delete(item, project_root)
                        if safe:
                            large_files.append(item)
                except OSError:
                    continue
    
    return large_files


def get_size(path: Path) -> int:
    """
    Get total size of file or directory in bytes.
    
    Args:
        path: File or directory path
    
    Returns:
        Total size in bytes
    """
    if path.is_file():
        return path.stat().st_size
    
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except (OSError, PermissionError):
        pass
    
    return total


def cleanup_workspace(
    project_root: Path = None,
    dry_run: bool = True,
    categories: List[CleanupCategory] = None,
    confirm: bool = True
) -> Dict[str, Any]:
    """
    Clean workspace by removing temporary files, old logs, and cache.
    
    Args:
        project_root: Project root directory (auto-detected if None)
        dry_run: If True, only show what would be deleted
        categories: List of cleanup categories (all by default)
        confirm: If True, prompt for confirmation before deleting
    
    Returns:
        Dictionary with cleanup results
    """
    # Auto-detect project root
    if project_root is None:
        project_root = Path.cwd()
        while project_root != project_root.parent:
            if (project_root / '.git').exists():
                break
            project_root = project_root.parent
    
    if not project_root.exists():
        return {
            'success': False,
            'error': f'Project root not found: {project_root}'
        }
    
    # Default to all categories
    if categories is None:
        categories = list(CleanupCategory)
    
    result = CleanupResult()
    items_to_delete = []
    
    # Find items to clean
    print(f"\n🔍 Scanning workspace: {project_root}")
    print("━" * 80)
    
    if CleanupCategory.TEMP_FILES in categories:
        print("Searching for temporary files...")
        temp_items = find_temp_files(project_root)
        items_to_delete.extend([(item, CleanupCategory.TEMP_FILES) for item in temp_items])
        print(f"  Found {len(temp_items)} temporary items")
    
    if CleanupCategory.OLD_LOGS in categories:
        print("Searching for old log files (>30 days)...")
        old_logs = find_old_logs(project_root, days_old=30)
        items_to_delete.extend([(item, CleanupCategory.OLD_LOGS) for item in old_logs])
        print(f"  Found {len(old_logs)} old log files")
    
    if CleanupCategory.CACHE_DIRS in categories:
        print("Searching for large cache files (>10MB)...")
        large_caches = find_large_cache_files(project_root, min_size_mb=10)
        items_to_delete.extend([(item, CleanupCategory.CACHE_DIRS) for item in large_caches])
        print(f"  Found {len(large_caches)} large cache files")
    
    print("━" * 80)
    
    if not items_to_delete:
        print("\n✨ Workspace is clean! Nothing to remove.")
        return {
            'success': True,
            'dry_run': dry_run,
            'items_removed': 0,
            'space_freed_mb': 0.0,
            'message': 'Workspace already clean'
        }
    
    # Calculate total size
    total_size = sum(get_size(item[0]) for item in items_to_delete)
    total_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 Cleanup Summary:")
    print(f"  Items to remove: {len(items_to_delete)}")
    print(f"  Space to free: {total_mb:.2f} MB")
    print()
    
    # Show what will be deleted
    if dry_run or confirm:
        print("Items to be removed:")
        for item, category in items_to_delete[:10]:  # Show first 10
            size_mb = get_size(item) / (1024 * 1024)
            print(f"  [{category.value}] {item.name} ({size_mb:.2f} MB)")
        
        if len(items_to_delete) > 10:
            print(f"  ... and {len(items_to_delete) - 10} more items")
        print()
    
    # Dry run - stop here
    if dry_run:
        print("🔒 DRY RUN - No files deleted")
        print("   Run without --dry-run to actually remove files")
        return {
            'success': True,
            'dry_run': True,
            'items_found': len(items_to_delete),
            'space_would_free_mb': total_mb,
            'message': 'Dry run complete'
        }
    
    # Confirm before deletion
    if confirm:
        response = input(f"\n⚠️  Delete {len(items_to_delete)} items ({total_mb:.2f} MB)? [y/N]: ")
        if response.lower() != 'y':
            print("❌ Cleanup cancelled")
            return {
                'success': False,
                'cancelled': True,
                'message': 'User cancelled cleanup'
            }
    
    # Perform cleanup
    print("\n🗑️  Removing items...")
    for item, category in items_to_delete:
        try:
            size = get_size(item)
            
            if item.is_dir():
                shutil.rmtree(item)
                result.add_directory(str(item), size)
            else:
                item.unlink()
                result.add_file(str(item), size)
            
            print(f"  ✓ Removed: {item.name}")
        
        except Exception as e:
            result.add_error(f"Failed to remove {item}: {e}")
            print(f"  ✗ Error: {item.name} - {e}")
    
    # Final report
    print("\n━" * 80)
    print("✅ Cleanup Complete!")
    print(f"  Files removed: {len(result.files_removed)}")
    print(f"  Directories removed: {len(result.dirs_removed)}")
    print(f"  Space freed: {result.space_freed_mb:.2f} MB")
    
    if result.errors:
        print(f"\n⚠️  Errors: {len(result.errors)}")
        for error in result.errors[:5]:
            print(f"  - {error}")
    
    print("━" * 80)
    
    return {
        'success': True,
        'dry_run': False,
        'items_removed': result.total_items_removed,
        'files_removed': len(result.files_removed),
        'dirs_removed': len(result.dirs_removed),
        'space_freed_mb': result.space_freed_mb,
        'errors': result.errors,
        'message': f"Removed {result.total_items_removed} items, freed {result.space_freed_mb:.2f} MB"
    }


def main():
    """CLI entry point for cleanup operation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Workspace Cleanup - Remove temporary files and free disk space'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt (use with caution!)'
    )
    parser.add_argument(
        '--category',
        choices=['temp', 'logs', 'cache', 'all'],
        default='all',
        help='What to clean (default: all)'
    )
    
    args = parser.parse_args()
    
    # Map category argument to enum
    category_map = {
        'temp': [CleanupCategory.TEMP_FILES],
        'logs': [CleanupCategory.OLD_LOGS],
        'cache': [CleanupCategory.CACHE_DIRS],
        'all': list(CleanupCategory)
    }
    
    categories = category_map.get(args.category, list(CleanupCategory))
    
    # Run cleanup
    result = cleanup_workspace(
        project_root=args.project_root,
        dry_run=args.dry_run,
        categories=categories,
        confirm=not args.no_confirm
    )
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
