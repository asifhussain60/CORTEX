# Filesystem Operations Patterns

**Date:** 2026-01-02  
**Purpose:** Document safe, atomic, and transactional filesystem operation patterns for Vacuum v2

---

## 🎯 Core Principles

### 1. **Atomic Operations**
Every filesystem operation must be atomic (all-or-nothing):
- ✅ Transaction log BEFORE executing
- ✅ Verify success AFTER executing
- ✅ Rollback on failure

### 2. **Safety First**
Preserve data integrity at all costs:
- ✅ Dry-run by default
- ✅ Checkpoints before modifications
- ✅ Never follow symlinks outside target
- ✅ Validate permissions before operations

### 3. **Performance**
Optimize for large-scale operations:
- ✅ Parallel processing (thread pools)
- ✅ Streaming (don't load all in memory)
- ✅ Caching (hash values, git status)
- ✅ Batching (delete 100 files per syscall)

### 4. **Cross-Platform**
Work consistently on Windows, Linux, macOS:
- ✅ Use `pathlib.Path` (not `os.path`)
- ✅ Handle case-sensitive/insensitive filesystems
- ✅ Normalize path separators
- ✅ UTF-8 encoding throughout

---

## 📁 Filesystem Traversal

### Pattern: Safe Directory Scanning

**Goal:** Traverse directory tree, catalog files, handle edge cases

#### Implementation

```python
from pathlib import Path
from typing import Iterator, Set
import os

def scan_directory(
    root: Path,
    exclude_patterns: Set[str],
    follow_symlinks: bool = False,
    max_depth: int | None = None
) -> Iterator[Path]:
    """
    Safely traverse directory tree with exclusion support.
    
    Args:
        root: Starting directory
        exclude_patterns: Glob patterns to exclude (.git, node_modules)
        follow_symlinks: Whether to follow symlinks (DANGEROUS)
        max_depth: Maximum traversal depth (None = unlimited)
        
    Yields:
        Path objects for each file
        
    Edge Cases:
        - Symlinks: Never follow outside root (security)
        - Permissions: Skip inaccessible directories (log warning)
        - Large directories: Stream results (don't load all in memory)
        - Unicode: Handle emoji, non-ASCII characters
        - Circular: Detect circular symlinks (infinite loop)
    """
    def _should_exclude(path: Path) -> bool:
        """Check if path matches exclusion patterns."""
        for pattern in exclude_patterns:
            if path.match(pattern):
                return True
        return False
    
    def _is_safe_symlink(path: Path) -> bool:
        """Verify symlink points inside root (security)."""
        if not path.is_symlink():
            return True
        try:
            target = path.resolve()
            return target.is_relative_to(root)
        except (OSError, RuntimeError):
            return False
    
    visited = set()  # Detect circular symlinks
    
    def _walk(current: Path, depth: int = 0):
        # Check depth limit
        if max_depth is not None and depth > max_depth:
            return
        
        # Check exclusions
        if _should_exclude(current):
            return
        
        # Detect circular symlinks
        try:
            real_path = current.resolve()
            if real_path in visited:
                return  # Circular reference
            visited.add(real_path)
        except (OSError, RuntimeError):
            return  # Cannot resolve
        
        # Check permissions
        if not os.access(current, os.R_OK):
            logger.warning(f"Permission denied: {current}")
            return
        
        # Iterate children
        try:
            for child in current.iterdir():
                if child.is_dir():
                    # Recurse into directory
                    if follow_symlinks or not child.is_symlink():
                        _walk(child, depth + 1)
                elif child.is_file():
                    # Yield file
                    if follow_symlinks or _is_safe_symlink(child):
                        yield child
        except PermissionError:
            logger.warning(f"Cannot read directory: {current}")
        except OSError as e:
            logger.warning(f"OS error scanning {current}: {e}")
    
    yield from _walk(root)
```

#### Usage

```python
# Exclude common patterns
exclude_patterns = {
    '.git', '.github',
    'node_modules', 'venv',
    '__pycache__', '.pytest_cache',
    '*.pyc', '*.pyo'
}

# Scan directory
for file_path in scan_directory(Path('/path/to/target'), exclude_patterns):
    print(f"Found: {file_path}")
```

#### Edge Cases Handled

1. **Symlinks:**
   - Never follow symlinks by default (security)
   - If following, verify target inside root (prevent path traversal)
   - Use `lstat()` to detect symlinks (not `stat()`)

2. **Permissions:**
   - Check `os.access(path, os.R_OK)` before reading
   - Skip inaccessible directories (log warning)
   - Handle `PermissionError` gracefully

3. **Circular References:**
   - Track visited paths via `resolve()`
   - Detect infinite loops
   - Skip circular symlinks

4. **Large Directories:**
   - Use `iterdir()` (streaming, not `listdir()`)
   - Yield results (don't load all in memory)
   - Process in batches if needed

5. **Unicode:**
   - Use UTF-8 encoding throughout
   - Handle emoji, non-ASCII characters
   - Normalize Unicode (NFC)

---

## 🗑️ Safe Deletion

### Pattern: Transactional File Deletion

**Goal:** Delete files with rollback capability

#### Implementation

```python
from pathlib import Path
from typing import List
import shutil
import json
from datetime import datetime

class FilesystemTransaction:
    """
    Transactional filesystem operations with rollback support.
    
    Operations are logged to a transaction file before execution.
    On failure, rollback restores original state.
    """
    
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifest_path = checkpoint_dir / "manifest.json"
        self.operations = []
        
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete file with checkpoint backup.
        
        Args:
            file_path: File to delete
            
        Returns:
            True if deleted, False if failed
            
        Safety:
            - Backs up file to checkpoint directory
            - Logs operation to manifest
            - Validates file exists before deletion
        """
        if not file_path.exists():
            return False
        
        # Backup file
        backup_path = self.checkpoint_dir / "files" / file_path.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(file_path, backup_path)
        except OSError as e:
            logger.error(f"Backup failed for {file_path}: {e}")
            return False
        
        # Log operation
        operation = {
            'type': 'delete',
            'original_path': str(file_path),
            'backup_path': str(backup_path),
            'timestamp': datetime.now().isoformat(),
            'size': file_path.stat().st_size
        }
        self.operations.append(operation)
        
        # Delete file
        try:
            file_path.unlink()
            return True
        except OSError as e:
            logger.error(f"Deletion failed for {file_path}: {e}")
            return False
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        Move file with rollback capability.
        
        Args:
            source: Source file
            destination: Destination path
            
        Returns:
            True if moved, False if failed
            
        Safety:
            - Checks destination doesn't exist (or resolves conflict)
            - Atomic rename (if same filesystem)
            - Logs operation for rollback
        """
        if not source.exists():
            return False
        
        # Resolve conflict (destination exists)
        if destination.exists():
            # Rename source to avoid collision
            destination = self._resolve_conflict(destination)
        
        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Log operation
        operation = {
            'type': 'move',
            'source': str(source),
            'destination': str(destination),
            'timestamp': datetime.now().isoformat()
        }
        self.operations.append(operation)
        
        # Move file (atomic if same filesystem)
        try:
            source.rename(destination)
            return True
        except OSError:
            # Cross-filesystem move (copy + delete)
            try:
                shutil.copy2(source, destination)
                source.unlink()
                return True
            except OSError as e:
                logger.error(f"Move failed {source} → {destination}: {e}")
                return False
    
    def commit(self) -> None:
        """Save transaction manifest."""
        with open(self.manifest_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'operations': self.operations
            }, f, indent=2)
    
    def rollback(self) -> None:
        """Restore files from checkpoint."""
        if not self.manifest_path.exists():
            return
        
        with open(self.manifest_path, 'r') as f:
            data = json.load(f)
        
        # Reverse operations
        for operation in reversed(data['operations']):
            if operation['type'] == 'delete':
                # Restore from backup
                backup = Path(operation['backup_path'])
                original = Path(operation['original_path'])
                if backup.exists():
                    shutil.copy2(backup, original)
            elif operation['type'] == 'move':
                # Reverse move
                source = Path(operation['source'])
                destination = Path(operation['destination'])
                if destination.exists():
                    destination.rename(source)
    
    def _resolve_conflict(self, path: Path) -> Path:
        """Resolve filename conflict by appending number."""
        counter = 1
        while True:
            new_path = path.with_stem(f"{path.stem}_{counter}")
            if not new_path.exists():
                return new_path
            counter += 1
```

#### Usage

```python
# Create transaction
checkpoint_dir = Path('.vacuum-checkpoint-2025-12-31-100000')
transaction = FilesystemTransaction(checkpoint_dir)

# Delete files with backup
for file_path in files_to_delete:
    transaction.delete_file(file_path)

# Move files
for source, dest in files_to_move:
    transaction.move_file(source, dest)

# Commit changes
transaction.commit()

# Or rollback on error
transaction.rollback()
```

#### Safety Features

1. **Checkpoint Backup:**
   - Copy file before deletion
   - Preserve metadata (timestamps, permissions)
   - Store in checkpoint directory

2. **Transaction Log:**
   - JSON manifest with all operations
   - Timestamp each operation
   - Reversible operations only

3. **Atomic Operations:**
   - Use `Path.rename()` for same-filesystem moves (atomic)
   - Fallback to copy + delete for cross-filesystem
   - All-or-nothing per file

4. **Conflict Resolution:**
   - Detect destination exists
   - Append counter to filename (`file_1.txt`)
   - Never overwrite existing files

5. **Rollback:**
   - Reverse operations in order
   - Restore from checkpoints
   - Handle partial failures

---

## 🔍 Duplicate Detection

### Pattern: Hash-Based Duplicate Detection

**Goal:** Find duplicate files efficiently (byte-for-byte identical)

#### Implementation

```python
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import hashlib

class DuplicateDetector:
    """
    Efficient duplicate file detection using hashing.
    
    Algorithm:
        1. Group by size (fast, eliminates most files)
        2. Hash first 8KB (fast, eliminates most size matches)
        3. Full hash (slow, only for remaining candidates)
    """
    
    def __init__(self, cache_path: Path | None = None):
        self.cache_path = cache_path
        self.hash_cache: Dict[Path, str] = {}
        
        if cache_path and cache_path.exists():
            self._load_cache()
    
    def find_duplicates(
        self,
        files: List[Path],
        quick_hash_size: int = 8192
    ) -> List[List[Path]]:
        """
        Find duplicate files.
        
        Args:
            files: List of file paths to check
            quick_hash_size: Bytes to hash for quick check
            
        Returns:
            List of duplicate groups (each group = list of identical files)
            
        Example:
            [
                [Path('file1.txt'), Path('copy1.txt'), Path('copy2.txt')],
                [Path('image.jpg'), Path('backup/image.jpg')]
            ]
        """
        # Phase 1: Group by size
        size_groups = defaultdict(list)
        for file_path in files:
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
            except OSError:
                continue
        
        # Phase 2: Quick hash (first 8KB)
        quick_hash_groups = defaultdict(list)
        for size, paths in size_groups.items():
            if len(paths) == 1:
                continue  # No duplicates
            
            for path in paths:
                quick_hash = self._quick_hash(path, quick_hash_size)
                quick_hash_groups[(size, quick_hash)].append(path)
        
        # Phase 3: Full hash (only for remaining candidates)
        duplicate_groups = []
        for (size, quick_hash), paths in quick_hash_groups.items():
            if len(paths) == 1:
                continue
            
            full_hash_groups = defaultdict(list)
            for path in paths:
                full_hash = self._full_hash(path)
                full_hash_groups[full_hash].append(path)
            
            # Collect duplicate groups
            for full_hash, group in full_hash_groups.items():
                if len(group) > 1:
                    duplicate_groups.append(group)
        
        return duplicate_groups
    
    def _quick_hash(self, path: Path, size: int) -> str:
        """Hash first N bytes (fast)."""
        try:
            with open(path, 'rb') as f:
                data = f.read(size)
            return hashlib.sha256(data).hexdigest()
        except OSError:
            return ''
    
    def _full_hash(self, path: Path) -> str:
        """Hash entire file (slow, cached)."""
        # Check cache
        if path in self.hash_cache:
            return self.hash_cache[path]
        
        try:
            hash_obj = hashlib.sha256()
            with open(path, 'rb') as f:
                # Read in chunks (64KB)
                while chunk := f.read(65536):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            self.hash_cache[path] = file_hash
            return file_hash
        except OSError:
            return ''
    
    def _load_cache(self) -> None:
        """Load hash cache from disk."""
        # Implementation: Load JSON cache of {path: hash}
        pass
    
    def save_cache(self) -> None:
        """Save hash cache to disk."""
        # Implementation: Save JSON cache
        pass
```

#### Usage

```python
detector = DuplicateDetector(cache_path=Path('.vacuum-hash-cache.json'))

# Find duplicates
duplicate_groups = detector.find_duplicates(list_of_files)

# Process duplicates
for group in duplicate_groups:
    newest = max(group, key=lambda p: p.stat().st_mtime)
    print(f"Keep: {newest}")
    
    for duplicate in group:
        if duplicate != newest:
            print(f"Delete: {duplicate}")

# Save cache for next run
detector.save_cache()
```

#### Optimizations

1. **Three-Phase Algorithm:**
   - Phase 1: Group by size (O(n), instant)
   - Phase 2: Quick hash first 8KB (O(n), fast)
   - Phase 3: Full hash (O(n), slow but rare)

2. **Hash Caching:**
   - Cache full hashes to disk
   - Invalidate cache if file modified (check mtime)
   - Avoid rehashing on subsequent runs

3. **Chunked Reading:**
   - Read files in 64KB chunks
   - Avoid loading large files into memory
   - Works with files >1GB

4. **Parallel Processing:**
   - Hash multiple files in parallel (thread pool)
   - CPU-bound operation (GIL not an issue for I/O)

---

## 🔗 Symlink Handling

### Pattern: Safe Symlink Operations

**Goal:** Handle symlinks safely without security vulnerabilities

#### Implementation

```python
from pathlib import Path

class SymlinkHandler:
    """Safe symlink operations with security validation."""
    
    def __init__(self, root: Path):
        self.root = root.resolve()
    
    def is_safe_symlink(self, path: Path) -> bool:
        """
        Check if symlink is safe (points inside root).
        
        Security: Prevents path traversal attacks where symlink
        points to /etc/passwd or other system files.
        """
        if not path.is_symlink():
            return True
        
        try:
            target = path.resolve()
            return target.is_relative_to(self.root)
        except (OSError, RuntimeError):
            return False
    
    def delete_symlink(self, path: Path) -> bool:
        """
        Delete symlink (NOT its target).
        
        Important: Use unlink(), not remove() to delete
        the symlink itself, not what it points to.
        """
        if not path.is_symlink():
            return False
        
        try:
            path.unlink()  # Delete symlink, not target
            return True
        except OSError:
            return False
    
    def create_symlink(self, source: Path, link: Path) -> bool:
        """
        Create symlink with validation.
        
        Args:
            source: File to link to
            link: Symlink path to create
        """
        if not source.exists():
            return False
        
        if link.exists():
            return False  # Don't overwrite
        
        try:
            link.symlink_to(source)
            return True
        except OSError:
            return False
```

#### Safety Rules

1. **Never Follow Symlinks Outside Root:**
   - Validate symlink target with `resolve()` + `is_relative_to()`
   - Prevents path traversal attacks

2. **Use `lstat()` Not `stat()`:**
   - `lstat()` returns info about symlink itself
   - `stat()` follows symlink (dangerous)

3. **Delete Symlink, Not Target:**
   - Use `path.unlink()` (deletes symlink)
   - NOT `path.unlink(missing_ok=True)` (could follow and delete target)

4. **Detect Circular Symlinks:**
   - Track visited paths
   - Abort if cycle detected

---

## 🔐 Permission Handling

### Pattern: Permission-Aware Operations

**Goal:** Handle permission errors gracefully

#### Implementation

```python
import os
from pathlib import Path

def check_permissions(path: Path) -> Dict[str, bool]:
    """
    Check file/directory permissions.
    
    Returns:
        Dict with readable, writable, executable flags
    """
    return {
        'readable': os.access(path, os.R_OK),
        'writable': os.access(path, os.W_OK),
        'executable': os.access(path, os.X_OK),
        'exists': path.exists()
    }

def safe_delete_with_permissions(path: Path) -> bool:
    """
    Delete file, handling permission issues.
    
    Returns:
        True if deleted, False if failed
    """
    perms = check_permissions(path)
    
    if not perms['exists']:
        return True  # Already gone
    
    if not perms['writable']:
        logger.warning(f"Permission denied: {path}")
        return False
    
    try:
        path.unlink()
        return True
    except PermissionError:
        logger.warning(f"Cannot delete (locked?): {path}")
        return False
    except OSError as e:
        logger.error(f"OS error deleting {path}: {e}")
        return False
```

---

## 🎯 Summary

### Key Patterns

1. **Traversal:** Stream-based, exclusion-aware, symlink-safe
2. **Deletion:** Transactional, checkpoint backup, rollback
3. **Duplication:** Three-phase hashing, caching, parallel
4. **Symlinks:** Validate targets, never follow outside root
5. **Permissions:** Check before operations, handle errors

### Implementation Checklist

For Vacuum v2, implement:
- ✅ `FilesystemEngine` - Traversal + operations
- ✅ `FilesystemTransaction` - Atomic operations + rollback
- ✅ `DuplicateDetector` - Hash-based detection
- ✅ `SymlinkHandler` - Safe symlink operations
- ✅ `PermissionValidator` - Permission checks

**Next:** Document safe deletion strategies (critical file protection).
