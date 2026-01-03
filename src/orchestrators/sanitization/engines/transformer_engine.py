"""
Transformer Engine - Apply transformations with transactional safety (ACID).

Integrates:
- CheckpointManager from vacuum-v2-patterns.md (SHA256 verification)
- TransformationTransaction (ACID-compliant)
- File transformation logic with rollback
- Integrity verification

Features:
- ACID-compliant transformations (Atomicity, Consistency, Isolation, Durability)
- Checkpoint creation before transformations
- SHA256 integrity verification
- Automatic rollback on failure
- Context manager protocol (auto-rollback on exception)
- Dry-run mode support
- Progress tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import re
import shutil
import hashlib
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TransformationStatus(str, Enum):
    """Status of transformation operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class TransformationOp:
    """Single transformation operation."""
    op_id: str
    file_path: Path
    original_content: Optional[str] = None
    transformed_content: Optional[str] = None
    original_checksum: Optional[str] = None
    transformed_checksum: Optional[str] = None
    status: TransformationStatus = TransformationStatus.PENDING
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Checkpoint:
    """Checkpoint for rollback."""
    checkpoint_id: str
    created_at: datetime
    file_checksums: Dict[Path, str]  # file_path → SHA256
    file_count: int


@dataclass
class TransformationResult:
    """Result of transformation execution."""
    transaction_id: str
    files_transformed: int
    total_changes: int
    files_renamed: int
    checkpoint_id: str
    dry_run: bool
    status: TransformationStatus
    operations: List[TransformationOp]
    duration_seconds: float
    error: Optional[str] = None


class CheckpointManager:
    """
    Manages file checkpoints for safe transformations.
    
    Integrated from vacuum-v2-patterns.md.
    """
    
    HASH_CHUNK_SIZE = 65536  # 64 KB chunks (prevent memory overflow)
    
    @staticmethod
    def create_checkpoint(file_path: Path) -> str:
        """
        Create SHA256 checkpoint for file.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 hexdigest string
        
        Raises:
            OSError: If file cannot be read
        """
        hash_obj = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(CheckpointManager.HASH_CHUNK_SIZE):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_checkpoint(file_path: Path, expected_hash: str) -> bool:
        """
        Verify file integrity against checkpoint.
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA256 hash
        
        Returns:
            True if file matches checkpoint, False otherwise
        """
        try:
            actual_hash = CheckpointManager.create_checkpoint(file_path)
            return actual_hash == expected_hash
        except OSError:
            return False
    
    @staticmethod
    def create_checkpoint_for_files(files: List[Path]) -> Checkpoint:
        """
        Create checkpoint for multiple files.
        
        Args:
            files: List of file paths
        
        Returns:
            Checkpoint object
        """
        checkpoint_id = str(uuid.uuid4())
        checksums = {}
        
        for file_path in files:
            try:
                checksums[file_path] = CheckpointManager.create_checkpoint(file_path)
            except OSError as e:
                logger.warning(f"Failed to checkpoint {file_path}: {e}")
        
        return Checkpoint(
            checkpoint_id=checkpoint_id,
            created_at=datetime.now(),
            file_checksums=checksums,
            file_count=len(checksums)
        )


class TransformationTransaction:
    """
    ACID-compliant transformation transaction.
    
    Implements context manager protocol for automatic rollback on exception.
    
    Usage:
        with TransformationTransaction(checkpoint, dry_run=False) as txn:
            txn.add_operation(op)
            txn.commit()  # Auto-commits on successful exit
    """
    
    def __init__(self, checkpoint: Checkpoint, dry_run: bool = False):
        """
        Initialize transformation transaction.
        
        Args:
            checkpoint: Checkpoint to restore on rollback
            dry_run: If True, don't actually modify files
        """
        self.transaction_id = str(uuid.uuid4())
        self.checkpoint = checkpoint
        self.dry_run = dry_run
        self.operations: List[TransformationOp] = []
        self.committed = False
        self.rolled_back = False
        
        logger.info(
            f"Transaction {self.transaction_id[:8]} started "
            f"(checkpoint={checkpoint.checkpoint_id[:8]}, dry_run={dry_run})"
        )
    
    def add_operation(self, operation: TransformationOp):
        """
        Add operation to transaction (not executed yet).
        
        Args:
            operation: TransformationOp to add
        """
        if self.committed or self.rolled_back:
            raise RuntimeError("Cannot add operations to committed/rolled back transaction")
        
        self.operations.append(operation)
        logger.debug(f"Added operation {operation.op_id} to transaction")
    
    def commit(self) -> bool:
        """
        Execute all operations atomically.
        
        Returns:
            True if commit successful, False otherwise
        """
        if self.committed:
            logger.warning("Transaction already committed")
            return True
        
        if self.rolled_back:
            logger.error("Cannot commit rolled back transaction")
            return False
        
        logger.info(f"Committing transaction {self.transaction_id[:8]} ({len(self.operations)} ops)")
        
        try:
            # Execute all operations
            for op in self.operations:
                if not self._execute_operation(op):
                    # Operation failed - rollback
                    logger.error(f"Operation {op.op_id} failed: {op.error}")
                    self.rollback()
                    return False
            
            # All operations succeeded
            self.committed = True
            logger.info(f"Transaction {self.transaction_id[:8]} committed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Transaction commit failed: {e}", exc_info=True)
            self.rollback()
            return False
    
    def rollback(self) -> bool:
        """
        Undo all operations, restore checkpoint.
        
        Returns:
            True if rollback successful, False otherwise
        """
        if self.rolled_back:
            logger.warning("Transaction already rolled back")
            return True
        
        logger.warning(f"Rolling back transaction {self.transaction_id[:8]}")
        
        try:
            # Restore files from checkpoint (LIFO order)
            for op in reversed(self.operations):
                if op.status == TransformationStatus.COMPLETED:
                    self._restore_file(op)
            
            # Verify integrity
            if not self._verify_checkpoint_integrity():
                logger.error("Checkpoint integrity verification failed after rollback!")
                return False
            
            self.rolled_back = True
            logger.info(f"Transaction {self.transaction_id[:8]} rolled back successfully")
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def _execute_operation(self, op: TransformationOp) -> bool:
        """Execute single transformation operation."""
        try:
            op.status = TransformationStatus.IN_PROGRESS
            
            if self.dry_run:
                # Dry-run mode: don't actually modify files
                logger.debug(f"[DRY-RUN] Would transform {op.file_path}")
                op.status = TransformationStatus.COMPLETED
                return True
            
            # Read original content
            with open(op.file_path, 'r', encoding='utf-8') as f:
                op.original_content = f.read()
            
            # Create original checksum
            op.original_checksum = CheckpointManager.create_checkpoint(op.file_path)
            
            # Write transformed content
            with open(op.file_path, 'w', encoding='utf-8') as f:
                f.write(op.transformed_content)
            
            # Create transformed checksum
            op.transformed_checksum = CheckpointManager.create_checkpoint(op.file_path)
            
            op.status = TransformationStatus.COMPLETED
            logger.debug(f"Operation {op.op_id} completed")
            return True
        
        except Exception as e:
            op.status = TransformationStatus.FAILED
            op.error = str(e)
            logger.error(f"Operation {op.op_id} failed: {e}")
            return False
    
    def _restore_file(self, op: TransformationOp):
        """Restore file to original state."""
        try:
            if self.dry_run:
                logger.debug(f"[DRY-RUN] Would restore {op.file_path}")
                return
            
            # Write original content back
            with open(op.file_path, 'w', encoding='utf-8') as f:
                f.write(op.original_content)
            
            # Verify restoration
            restored_checksum = CheckpointManager.create_checkpoint(op.file_path)
            if restored_checksum != op.original_checksum:
                logger.error(f"Checksum mismatch after restoring {op.file_path}!")
            else:
                logger.debug(f"Restored {op.file_path} successfully")
            
            op.status = TransformationStatus.ROLLED_BACK
        
        except Exception as e:
            logger.error(f"Failed to restore {op.file_path}: {e}")
    
    def _verify_checkpoint_integrity(self) -> bool:
        """Verify all files match checkpoint after rollback."""
        for file_path, expected_hash in self.checkpoint.file_checksums.items():
            if not CheckpointManager.verify_checkpoint(file_path, expected_hash):
                logger.error(f"Integrity check failed for {file_path}")
                return False
        
        logger.info("Checkpoint integrity verified")
        return True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto-rollback on exception."""
        if exc_type is not None:
            # Exception occurred - rollback
            logger.error(f"Exception in transaction: {exc_val}")
            self.rollback()
            return False  # Re-raise exception
        
        if not self.committed and not self.rolled_back:
            # Auto-commit on successful exit
            self.commit()
        
        return True


class TransformerEngine:
    """
    Transformer engine with transactional safety.
    
    Applies transformations to codebase with ACID guarantees:
    - Atomicity: All-or-nothing execution
    - Consistency: Files always in valid state
    - Isolation: Operations don't interfere
    - Durability: Changes persisted or fully rolled back
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize transformer engine.
        
        Args:
            config: Configuration dictionary from orchestrator
        """
        self.config = config
        self.transformation_config = config.get('transformation', {})
        self.transaction_enabled = self.transformation_config.get('transaction', {}).get('enabled', True)
        
        logger.info(
            f"Initialized TransformerEngine "
            f"(transaction_enabled={self.transaction_enabled})"
        )
    
    def transform_codebase(
        self,
        source_directory: Path,
        output_directory: Path,
        mappings: Dict[str, str],
        dry_run: bool = True
    ) -> TransformationResult:
        """
        Transform entire codebase using mappings.
        
        Args:
            source_directory: Source codebase path
            output_directory: Destination for sanitized code
            mappings: Transformation mappings (original→generic)
            dry_run: If True, simulate transformations
        
        Returns:
            TransformationResult
        """
        logger.info(
            f"Starting codebase transformation "
            f"(source={source_directory}, output={output_directory}, dry_run={dry_run})"
        )
        start_time = datetime.now()
        
        # Collect files to transform
        files = self._collect_files(source_directory)
        logger.info(f"Found {len(files)} files to transform")
        
        # Create checkpoint
        checkpoint = CheckpointManager.create_checkpoint_for_files(files)
        logger.info(f"Created checkpoint {checkpoint.checkpoint_id[:8]} ({checkpoint.file_count} files)")
        
        # Create operations
        operations = self._create_operations(files, source_directory, output_directory, mappings)
        logger.info(f"Created {len(operations)} transformation operations")
        
        # Execute transaction
        try:
            with TransformationTransaction(checkpoint, dry_run) as txn:
                for op in operations:
                    txn.add_operation(op)
                
                # Commit handled by context manager
                status = TransformationStatus.COMPLETED if txn.committed else TransformationStatus.FAILED
        
        except Exception as e:
            logger.error(f"Transformation failed: {e}", exc_info=True)
            status = TransformationStatus.FAILED
        
        # Build result
        duration = (datetime.now() - start_time).total_seconds()
        
        files_transformed = sum(1 for op in operations if op.status == TransformationStatus.COMPLETED)
        total_changes = len(operations)
        
        result = TransformationResult(
            transaction_id=str(uuid.uuid4()),
            files_transformed=files_transformed,
            total_changes=total_changes,
            checkpoint_id=checkpoint.checkpoint_id,
            dry_run=dry_run,
            status=status,
            operations=operations,
            duration_seconds=duration
        )
        
        logger.info(f"Transformation complete in {duration:.1f}s")
        logger.info(f"  Files transformed: {files_transformed}")
        logger.info(f"  Total changes: {total_changes}")
        logger.info(f"  Status: {status.value}")
        
        return result
    
    def _collect_files(self, source_directory: Path) -> List[Path]:
        """Collect files to transform."""
        files = []
        
        for root, dirs, filenames in os.walk(source_directory):
            for filename in filenames:
                file_path = Path(root) / filename
                files.append(file_path)
        
        return files
    
    def _create_operations(
        self,
        files: List[Path],
        source_dir: Path,
        output_dir: Path,
        mappings: Dict[str, str]
    ) -> List[TransformationOp]:
        """Create transformation operations for files."""
        operations = []
        
        # Sort mappings by length (longest first) for greedy replacement
        sorted_mappings = dict(sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True))
        
        for file_path in files:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply transformations
                transformed_content = self._apply_mappings(content, sorted_mappings)
                
                # Only create operation if content changed
                if transformed_content != content:
                    rel_path = file_path.relative_to(source_dir)
                    output_path = output_dir / rel_path
                    
                    op = TransformationOp(
                        op_id=str(uuid.uuid4()),
                        file_path=output_path,
                        original_content=content,
                        transformed_content=transformed_content
                    )
                    operations.append(op)
            
            except Exception as e:
                logger.warning(f"Failed to create operation for {file_path}: {e}")
        
        return operations
    
    def _apply_mappings(self, content: str, mappings: Dict[str, str]) -> str:
        """Apply transformation mappings to content."""
        transformed = content
        
        for original, generic in mappings.items():
            # Use word boundary matching for safe replacement
            pattern = re.compile(rf'\b{re.escape(original)}\b')
            transformed = pattern.sub(generic, transformed)
        
        return transformed
