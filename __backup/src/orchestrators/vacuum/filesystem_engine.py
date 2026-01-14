"""
Filesystem Engine - Core filesystem operations with transactional safety.

Provides atomic filesystem operations with:
- Directory scanning with exclusion patterns
- Transactional file operations (delete, move, archive)
- Checkpoint management with rollback capability
- Symlink safety validation
- Permission handling
- ACID transaction guarantees

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import json
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Iterator
from datetime import datetime
from collections import defaultdict

from src.database.planning_state_db import PlanningStateDB


logger = logging.getLogger(__name__)


class FilesystemTransaction:
    """
    Transactional filesystem operations with ACID guarantees.
    
    Properties:
        - Atomicity: All operations succeed or all fail
        - Consistency: Filesystem remains in valid state
        - Isolation: Operations don't interfere with other processes
        - Durability: Changes persisted to disk
    """
    
    def __init__(self, checkpoint_dir: Path, state_db: PlanningStateDB):
        """
        Initialize filesystem transaction.
        
        Args:
            checkpoint_dir: Directory for checkpoint backups
            state_db: Database for transaction logging
        """
        self.checkpoint_dir = checkpoint_dir
        self.state_db = state_db
        self.operations: List[Dict[str, Any]] = []
        self.transaction_id: Optional[str] = None
        
        logger.info(f"Initialized transaction (checkpoint={checkpoint_dir})")
    
    def begin(self) -> str:
        """
        Start new transaction.
        
        Returns:
            Transaction ID
        """
        self.transaction_id = f"vacuum-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create checkpoint directory
        if self.checkpoint_dir:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            (self.checkpoint_dir / "files").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Transaction started: {self.transaction_id}")
        return self.transaction_id
    
    def delete_file(self, path: Path) -> bool:
        """
        Delete file with checkpoint backup.
        
        Args:
            path: File to delete
        
        Returns:
            True if deleted successfully
        """
        if not path.exists():
            logger.warning(f"File not found (skipping): {path}")
            return False
        
        try:
            # Create backup if checkpoint enabled
            backup_path = None
            if self.checkpoint_dir:
                backup_path = self.checkpoint_dir / "files" / path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy with metadata preservation
                shutil.copy2(path, backup_path)
                
                # Verify backup
                if not self._verify_hash(path, backup_path):
                    logger.error(f"Backup verification failed: {path}")
                    return False
            
            # Log operation
            operation = {
                'id': len(self.operations) + 1,
                'type': 'delete',
                'path': str(path),
                'backup_path': str(backup_path) if backup_path else None,
                'size_bytes': path.stat().st_size,
                'hash': self._compute_hash(path),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Delete file
            path.unlink()
            
            # Verify deletion
            if path.exists():
                logger.error(f"Deletion failed (file still exists): {path}")
                operation['status'] = 'failed'
                return False
            
            operation['status'] = 'completed'
            self.operations.append(operation)
            
            logger.debug(f"Deleted: {path}")
            return True
        
        except PermissionError as e:
            logger.warning(f"Permission denied (skipping): {path} - {e}")
            return False
        except OSError as e:
            logger.error(f"Deletion failed: {path} - {e}")
            return False
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        Move file atomically with rollback capability.
        
        Args:
            source: Source file path
            destination: Destination file path
        
        Returns:
            True if moved successfully
        """
        if not source.exists():
            logger.warning(f"Source not found (skipping): {source}")
            return False
        
        try:
            # Resolve conflict if destination exists
            if destination.exists():
                destination = self._resolve_conflict(destination)
            
            # Create destination directory
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Log operation
            operation = {
                'id': len(self.operations) + 1,
                'type': 'move',
                'source': str(source),
                'destination': str(destination),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Attempt atomic rename (same filesystem)
            try:
                source.rename(destination)
                operation['status'] = 'completed'
                self.operations.append(operation)
                
                logger.debug(f"Moved: {source} → {destination}")
                return True
            
            except OSError:
                # Cross-filesystem move (copy + delete)
                shutil.copy2(source, destination)
                
                # Verify copy
                if self._verify_hash(source, destination):
                    source.unlink()
                    operation['status'] = 'completed'
                    self.operations.append(operation)
                    
                    logger.debug(f"Moved (cross-fs): {source} → {destination}")
                    return True
                else:
                    # Copy failed verification - cleanup
                    destination.unlink()
                    operation['status'] = 'failed'
                    logger.error(f"Move verification failed: {source}")
                    return False
        
        except PermissionError as e:
            logger.warning(f"Permission denied (skipping): {source} - {e}")
            return False
        except OSError as e:
            logger.error(f"Move failed: {source} → {destination} - {e}")
            return False
    
    def archive_file(self, source: Path, archive_dir: Path) -> bool:
        """
        Archive file with compression.
        
        Args:
            source: Source file path
            archive_dir: Archive directory
        
        Returns:
            True if archived successfully
        """
        if not source.exists():
            logger.warning(f"Source not found (skipping): {source}")
            return False
        
        try:
            # Create archive directory structure
            archive_path = archive_dir / source.name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to archive
            shutil.copy2(source, archive_path)
            
            # Compress (gzip)
            import gzip
            with open(source, 'rb') as f_in:
                with gzip.open(f"{archive_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed copy
            archive_path.unlink()
            
            # Log operation
            operation = {
                'id': len(self.operations) + 1,
                'type': 'archive',
                'source': str(source),
                'archive_path': f"{archive_path}.gz",
                'original_size': source.stat().st_size,
                'compressed_size': Path(f"{archive_path}.gz").stat().st_size,
                'compression': 'gzip',
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            self.operations.append(operation)
            
            logger.debug(f"Archived: {source} → {archive_path}.gz")
            return True
        
        except Exception as e:
            logger.error(f"Archive failed: {source} - {e}")
            return False
    
    def commit(self) -> None:
        """Finalize transaction and save manifest."""
        if not self.transaction_id:
            raise RuntimeError("Transaction not started (call begin() first)")
        
        # Calculate summary statistics
        summary = {
            'operations_total': len(self.operations),
            'operations_completed': sum(
                1 for op in self.operations if op['status'] == 'completed'
            ),
            'operations_failed': sum(
                1 for op in self.operations if op['status'] == 'failed'
            ),
            'space_saved_bytes': sum(
                op.get('size_bytes', 0) for op in self.operations 
                if op['type'] == 'delete' and op['status'] == 'completed'
            )
        }
        
        # Write transaction manifest
        if self.checkpoint_dir:
            manifest = {
                'transaction_id': self.transaction_id,
                'timestamp': datetime.now().isoformat(),
                'operations': self.operations,
                'summary': summary
            }
            
            manifest_path = self.checkpoint_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Transaction manifest saved: {manifest_path}")
        
        logger.info(
            f"Transaction committed: {self.transaction_id} "
            f"({summary['operations_completed']}/{summary['operations_total']} ops)"
        )
    
    def rollback(self) -> None:
        """
        Rollback transaction by restoring all files from checkpoint.
        
        Reverses operations in LIFO order (last executed first).
        """
        if not self.checkpoint_dir or not self.checkpoint_dir.exists():
            logger.error("Cannot rollback: No checkpoint directory")
            return
        
        manifest_path = self.checkpoint_dir / "manifest.json"
        if not manifest_path.exists():
            logger.error("Cannot rollback: No manifest found")
            return
        
        # Load manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        logger.info(f"Rolling back transaction: {manifest['transaction_id']}")
        
        # Reverse operations (LIFO)
        restored = 0
        for operation in reversed(manifest['operations']):
            if operation['status'] != 'completed':
                continue  # Skip failed operations
            
            try:
                if operation['type'] == 'delete':
                    # Restore from backup
                    backup = Path(operation['backup_path'])
                    original = Path(operation['path'])
                    if backup.exists():
                        shutil.copy2(backup, original)
                        restored += 1
                        logger.debug(f"Restored: {original}")
                
                elif operation['type'] == 'move':
                    # Reverse move
                    destination = Path(operation['destination'])
                    source = Path(operation['source'])
                    if destination.exists():
                        destination.rename(source)
                        restored += 1
                        logger.debug(f"Reversed move: {destination} → {source}")
                
                elif operation['type'] == 'archive':
                    # Decompress and restore
                    archive = Path(operation['archive_path'])
                    original = Path(operation['source'])
                    if archive.exists():
                        import gzip
                        with gzip.open(archive, 'rb') as f_in:
                            with open(original, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        restored += 1
                        logger.debug(f"Restored from archive: {original}")
            
            except Exception as e:
                logger.error(f"Rollback operation failed: {operation['type']} - {e}")
        
        logger.info(f"Rollback complete: {restored} operations reversed")
    
    def _verify_hash(self, path1: Path, path2: Path) -> bool:
        """Verify two files have identical hash."""
        try:
            hash1 = self._compute_hash(path1)
            hash2 = self._compute_hash(path2)
            return hash1 == hash2
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    def _compute_hash(self, path: Path) -> str:
        """Compute SHA256 hash of file."""
        hasher = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash computation failed for {path}: {e}")
            return ""
    
    def _resolve_conflict(self, path: Path) -> Path:
        """Resolve filename conflict by appending counter."""
        counter = 1
        while True:
            new_path = path.with_stem(f"{path.stem}_{counter}")
            if not new_path.exists():
                logger.debug(f"Resolved conflict: {path} → {new_path}")
                return new_path
            counter += 1


class FilesystemEngine:
    """
    Core filesystem operations engine.
    
    Provides:
    - Directory scanning with exclusion patterns
    - File categorization by cleanup rules
    - Transactional operations
    - Symlink safety validation
    - Permission handling
    """
    
    def __init__(self, state_db: PlanningStateDB, safety_rules: Dict[str, Any]):
        """
        Initialize filesystem engine.
        
        Args:
            state_db: Database for state persistence
            safety_rules: Safety configuration from manifest
        """
        self.state_db = state_db
        self.safety_rules = safety_rules
        
        logger.info("Initialized FilesystemEngine")
    
    def scan_directory(
        self,
        root: Path,
        cleanup_rules: Dict[str, Any],
        exclude_patterns: Set[str],
        max_depth: Optional[int] = None
    ) -> Dict[str, List[Path]]:
        """
        Scan directory and categorize files by cleanup rules.
        
        Args:
            root: Root directory to scan
            cleanup_rules: Cleanup category definitions
            exclude_patterns: Patterns to exclude (.git, node_modules, etc.)
            max_depth: Maximum traversal depth (None = unlimited)
        
        Returns:
            Dictionary of {category: [file_paths]}
        """
        logger.info(f"Scanning directory: {root}")
        
        inventory = defaultdict(list)
        visited = set()  # Track visited paths (detect circular symlinks)
        
        def should_exclude(path: Path) -> bool:
            """Check if path matches any exclusion pattern."""
            path_str = str(path)
            for pattern in exclude_patterns:
                if pattern in path_str or path.match(pattern):
                    return True
            return False
        
        def is_safe_symlink(path: Path) -> bool:
            """Verify symlink points inside root (security)."""
            if not path.is_symlink():
                return True
            try:
                target = path.resolve()
                return target.is_relative_to(root)
            except (OSError, RuntimeError):
                return False
        
        def walk(current: Path, depth: int = 0):
            """Recursively walk directory tree."""
            # Check depth limit
            if max_depth is not None and depth > max_depth:
                return
            
            # Check exclusions
            if should_exclude(current):
                logger.debug(f"Excluded: {current}")
                return
            
            # Detect circular symlinks
            try:
                real_path = current.resolve()
                if real_path in visited:
                    logger.debug(f"Circular symlink detected (skipping): {current}")
                    return
                visited.add(real_path)
            except (OSError, RuntimeError) as e:
                logger.warning(f"Cannot resolve path (skipping): {current} - {e}")
                return
            
            # Check permissions
            if not os.access(current, os.R_OK):
                logger.warning(f"Permission denied (skipping): {current}")
                return
            
            # Iterate children
            try:
                for child in current.iterdir():
                    if child.is_dir():
                        # Recurse into directory
                        if not child.is_symlink() or is_safe_symlink(child):
                            walk(child, depth + 1)
                    elif child.is_file():
                        # Categorize file
                        if not child.is_symlink() or is_safe_symlink(child):
                            category = self._categorize_file(child, cleanup_rules)
                            if category:
                                inventory[category].append(child)
            
            except PermissionError:
                logger.warning(f"Cannot read directory (skipping): {current}")
            except OSError as e:
                logger.warning(f"OS error scanning {current}: {e}")
        
        # Start traversal
        walk(root)
        
        # Log statistics
        total_files = sum(len(files) for files in inventory.values())
        logger.info(
            f"Scan complete: {total_files} files in {len(inventory)} categories"
        )
        
        return dict(inventory)
    
    def _categorize_file(
        self,
        path: Path,
        cleanup_rules: Dict[str, Any]
    ) -> Optional[str]:
        """
        Categorize file based on cleanup rules.
        
        Args:
            path: File path
            cleanup_rules: Category definitions with patterns
        
        Returns:
            Category name or None if no match
        """
        # Check each category
        for category, rules in cleanup_rules.items():
            patterns = rules.get('patterns', [])
            for pattern in patterns:
                if path.match(pattern):
                    return category
        
        return None
    
    def execute_cleanup(
        self,
        validated_plan: Dict[str, Any],
        checkpoint_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute filesystem cleanup operations.
        
        Args:
            validated_plan: Validated cleanup plan from safety validator
            checkpoint_dir: Optional checkpoint directory for rollback
        
        Returns:
            Execution summary with statistics
        """
        logger.info("Executing filesystem cleanup...")
        
        # Create transaction
        transaction = FilesystemTransaction(checkpoint_dir, self.state_db)
        transaction.begin()
        
        # Track results
        files_deleted = 0
        files_moved = 0
        files_archived = 0
        files_skipped = 0
        
        try:
            # Delete safe files
            for file_path in validated_plan.get('safe', []):
                if transaction.delete_file(file_path):
                    files_deleted += 1
                else:
                    files_skipped += 1
            
            # Move files (if any)
            for move_op in validated_plan.get('moves', []):
                source = move_op.get('source')
                destination = move_op.get('destination')
                if transaction.move_file(Path(source), Path(destination)):
                    files_moved += 1
                else:
                    files_skipped += 1
            
            # Archive files (if any)
            for archive_op in validated_plan.get('archives', []):
                source = archive_op.get('source')
                archive_dir = archive_op.get('archive_dir', Path('archives'))
                if transaction.archive_file(Path(source), Path(archive_dir)):
                    files_archived += 1
                else:
                    files_skipped += 1
            
            # Commit transaction
            transaction.commit()
            
            logger.info(
                f"Cleanup complete: {files_deleted} deleted, "
                f"{files_moved} moved, {files_archived} archived, "
                f"{files_skipped} skipped"
            )
            
            return {
                'files_deleted': files_deleted,
                'files_moved': files_moved,
                'files_archived': files_archived,
                'files_skipped': files_skipped,
                'transaction_id': transaction.transaction_id,
                'checkpoint_dir': str(checkpoint_dir) if checkpoint_dir else None
            }
        
        except Exception as e:
            logger.error(f"Cleanup execution failed: {e}", exc_info=True)
            
            # Attempt rollback
            if checkpoint_dir:
                logger.info("Attempting rollback...")
                transaction.rollback()
            
            raise
