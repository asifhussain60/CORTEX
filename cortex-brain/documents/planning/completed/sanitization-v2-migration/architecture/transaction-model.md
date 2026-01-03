# Sanitization v2 - TransformationTransaction Model

**Created:** January 3, 2026  
**Phase:** 1 - Design Architecture  
**Version:** 1.0

---

## 🎯 Overview

The TransformationTransaction provides ACID-compliant operations for code sanitization, ensuring **atomicity** (all-or-nothing), **consistency** (valid states), **isolation** (no partial states visible), and **durability** (checkpoint-based recovery).

**Purpose:**
- Prevent partial transformations on failure
- Enable complete rollback to pre-transformation state
- Support multi-file atomic operations
- Provide audit trail for all transformations

---

## 🏗️ Transaction Architecture

### Components

```
TransformationTransaction (Main Controller)
├── CheckpointManager (Backup Creation/Restoration)
├── OperationLog (Audit Trail)
├── IntegrityVerifier (SHA256 Checksums)
└── RollbackEngine (Undo Operations)
```

---

## 📦 Data Structures

### TransformationOp

```python
@dataclass
class TransformationOp:
    """
    Single atomic transformation operation.
    
    Represents one unit of work within a transaction:
    - AST transformation (code changes)
    - File rename (filesystem operation)
    - Directory rename (recursive filesystem operation)
    """
    
    # Operation identity
    op_id: str  # UUID for traceability
    op_type: str  # 'ast_transform' | 'file_rename' | 'dir_rename'
    timestamp: datetime
    
    # Target information
    target: Path  # File or directory being transformed
    risk_level: RiskLevel  # Classification from risk assessment
    
    # AST transformation (op_type='ast_transform')
    old_content: Optional[str]  # Original file content
    new_content: Optional[str]  # Transformed file content
    ast_changes: List[ASTChange]  # Detailed AST node changes
    
    # Rename operation (op_type='file_rename' | 'dir_rename')
    old_path: Optional[Path]  # Original path
    new_path: Optional[Path]  # New path after rename
    
    # Integrity verification
    checksum_before: str  # SHA256 before transformation
    checksum_after: str  # SHA256 after transformation
    
    # Execution status
    executed: bool = False
    execution_time_ms: float = 0.0
    error: Optional[str] = None

@dataclass
class ASTChange:
    """Detailed AST node change for audit trail."""
    node_type: str  # 'FunctionDef', 'ClassDef', 'Name', etc.
    old_value: str  # Original identifier
    new_value: str  # Transformed identifier
    line_number: int
    column_offset: int
```

### TransformationTransaction

```python
class TransformationTransaction:
    """
    ACID-compliant transaction for code transformations.
    
    Lifecycle:
    1. __init__: Create transaction with checkpoint
    2. add_operation: Add operations (not yet executed)
    3. commit: Execute all operations atomically
    4. rollback: Undo all operations, restore checkpoint
    
    Usage (Context Manager):
        with TransformationTransaction(checkpoint_id) as txn:
            txn.add_operation(op1)
            txn.add_operation(op2)
            # Auto-commit on success, auto-rollback on exception
    """
    
    def __init__(self, checkpoint_id: str, dry_run: bool = False):
        """
        Initialize transaction with checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier for rollback
            dry_run: If True, simulate operations without executing
        """
        self.transaction_id = str(uuid.uuid4())
        self.checkpoint_id = checkpoint_id
        self.dry_run = dry_run
        
        # Operation tracking
        self.operations: List[TransformationOp] = []
        self.executed_operations: List[TransformationOp] = []
        
        # Transaction state
        self.started_at: Optional[datetime] = None
        self.committed_at: Optional[datetime] = None
        self.rolled_back_at: Optional[datetime] = None
        self.committed = False
        self.rolled_back = False
        
        # Logging
        self.operation_log = OperationLog(self.transaction_id)
        self.logger = logging.getLogger(__name__)
    
    def add_operation(self, operation: TransformationOp) -> None:
        """
        Add operation to transaction (not executed yet).
        
        Args:
            operation: TransformationOp to add
        
        Raises:
            ValueError: If transaction already committed/rolled back
        """
        if self.committed or self.rolled_back:
            raise ValueError("Cannot add operation to completed transaction")
        
        self.operations.append(operation)
        self.operation_log.log_planned(operation)
        self.logger.debug(
            f"Added operation: {operation.op_type} on {operation.target}"
        )
    
    def commit(self) -> bool:
        """
        Execute all operations atomically.
        
        Execution Strategy:
        1. Validate all operations (pre-flight checks)
        2. Sort by risk level (SAFE first, CRITICAL last)
        3. Execute operations sequentially
        4. Verify integrity after each operation
        5. On error: Rollback all executed operations
        6. On success: Mark transaction committed
        
        Returns:
            True if all operations executed successfully
        
        Raises:
            TransactionError: If commit fails
        """
        if self.committed:
            raise ValueError("Transaction already committed")
        if self.rolled_back:
            raise ValueError("Cannot commit rolled-back transaction")
        
        self.started_at = datetime.now()
        self.logger.info(
            f"Committing transaction {self.transaction_id} "
            f"({len(self.operations)} operations)"
        )
        
        try:
            # Step 1: Validate all operations
            self._validate_operations()
            
            # Step 2: Sort by risk level (SAFE → CRITICAL)
            sorted_ops = sorted(
                self.operations, 
                key=lambda op: op.risk_level.value
            )
            
            # Step 3: Execute operations
            for operation in sorted_ops:
                if self.dry_run:
                    self._simulate_operation(operation)
                else:
                    self._execute_operation(operation)
                
                self.executed_operations.append(operation)
                self.operation_log.log_executed(operation)
            
            # Step 4: Mark committed
            self.committed = True
            self.committed_at = datetime.now()
            self.operation_log.log_committed()
            
            duration = (self.committed_at - self.started_at).total_seconds()
            self.logger.info(
                f"Transaction committed successfully "
                f"({len(self.executed_operations)} operations, {duration:.2f}s)"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Transaction commit failed: {e}")
            self.rollback()
            raise TransactionError(f"Commit failed: {e}") from e
    
    def rollback(self) -> bool:
        """
        Undo all executed operations, restore checkpoint.
        
        Rollback Strategy:
        1. Reverse operations in LIFO order
        2. For AST transforms: Restore original content
        3. For renames: Restore original paths
        4. Verify checksums match pre-transaction state
        5. Restore checkpoint if needed
        
        Returns:
            True if rollback successful
        """
        if self.rolled_back:
            self.logger.warning("Transaction already rolled back")
            return True
        
        self.logger.warning(
            f"Rolling back transaction {self.transaction_id} "
            f"({len(self.executed_operations)} operations)"
        )
        
        try:
            # Reverse operations in LIFO order
            for operation in reversed(self.executed_operations):
                if not self.dry_run:
                    self._reverse_operation(operation)
                
                self.operation_log.log_rolled_back(operation)
            
            # Restore checkpoint (filesystem-level restore)
            checkpoint_manager = CheckpointManager()
            checkpoint_manager.restore_checkpoint(self.checkpoint_id)
            
            self.rolled_back = True
            self.rolled_back_at = datetime.now()
            self.operation_log.log_rolled_back_all()
            
            self.logger.info("Transaction rolled back successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            raise TransactionError(f"Rollback failed: {e}") from e
    
    def _validate_operations(self) -> None:
        """Pre-flight validation of all operations."""
        for operation in self.operations:
            # Check target exists
            if not operation.target.exists():
                raise ValueError(f"Target does not exist: {operation.target}")
            
            # Check for file locks
            if self._is_file_locked(operation.target):
                raise ValueError(f"Target is locked: {operation.target}")
            
            # Validate checksums
            if operation.op_type == 'ast_transform':
                current_checksum = self._compute_checksum(operation.target)
                if current_checksum != operation.checksum_before:
                    raise ValueError(
                        f"Checksum mismatch (file modified during analysis): "
                        f"{operation.target}"
                    )
    
    def _execute_operation(self, operation: TransformationOp) -> None:
        """Execute single operation."""
        start_time = time.time()
        
        if operation.op_type == 'ast_transform':
            self._execute_ast_transform(operation)
        elif operation.op_type == 'file_rename':
            self._execute_file_rename(operation)
        elif operation.op_type == 'dir_rename':
            self._execute_dir_rename(operation)
        else:
            raise ValueError(f"Unknown operation type: {operation.op_type}")
        
        operation.executed = True
        operation.execution_time_ms = (time.time() - start_time) * 1000
        
        # Verify integrity
        self._verify_operation_integrity(operation)
    
    def _execute_ast_transform(self, operation: TransformationOp) -> None:
        """Execute AST transformation."""
        with open(operation.target, 'w', encoding='utf-8') as f:
            f.write(operation.new_content)
        
        self.logger.debug(f"AST transform: {operation.target}")
    
    def _execute_file_rename(self, operation: TransformationOp) -> None:
        """Execute file rename."""
        operation.old_path.rename(operation.new_path)
        self.logger.debug(f"File rename: {operation.old_path} → {operation.new_path}")
    
    def _execute_dir_rename(self, operation: TransformationOp) -> None:
        """Execute directory rename."""
        operation.old_path.rename(operation.new_path)
        self.logger.debug(f"Dir rename: {operation.old_path} → {operation.new_path}")
    
    def _reverse_operation(self, operation: TransformationOp) -> None:
        """Reverse single operation (undo)."""
        if operation.op_type == 'ast_transform':
            with open(operation.target, 'w', encoding='utf-8') as f:
                f.write(operation.old_content)
        
        elif operation.op_type == 'file_rename':
            operation.new_path.rename(operation.old_path)
        
        elif operation.op_type == 'dir_rename':
            operation.new_path.rename(operation.old_path)
        
        self.logger.debug(f"Reversed operation: {operation.op_type} on {operation.target}")
    
    def _verify_operation_integrity(self, operation: TransformationOp) -> None:
        """Verify operation integrity via checksums."""
        if operation.op_type == 'ast_transform':
            current_checksum = self._compute_checksum(operation.target)
            if current_checksum != operation.checksum_after:
                raise IntegrityError(
                    f"Checksum mismatch after transformation: {operation.target}"
                )
    
    def _compute_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _is_file_locked(self, file_path: Path) -> bool:
        """Check if file is locked by another process."""
        # Platform-specific implementation
        # For now, simple check
        try:
            with open(file_path, 'a'):
                pass
            return False
        except (IOError, OSError):
            return True
    
    def _simulate_operation(self, operation: TransformationOp) -> None:
        """Simulate operation for dry-run mode."""
        self.logger.info(f"[DRY-RUN] Would execute: {operation.op_type} on {operation.target}")
        operation.executed = True
        operation.execution_time_ms = 0.0
    
    # Context manager protocol
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with auto-rollback on exception."""
        if exc_type:
            self.logger.error(f"Exception during transaction: {exc_val}")
            self.rollback()
            return False  # Re-raise exception
        else:
            if not self.committed and not self.rolled_back:
                self.commit()
            return True
```

---

## 🗃️ Supporting Components

### CheckpointManager

```python
class CheckpointManager:
    """Manages checkpoint creation and restoration."""
    
    def create_checkpoint(self, directory: Path) -> str:
        """
        Create backup checkpoint of directory.
        
        Returns:
            checkpoint_id: Unique identifier for checkpoint
        """
        
    def restore_checkpoint(self, checkpoint_id: str) -> None:
        """Restore directory to checkpoint state."""
        
    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Delete checkpoint (after successful commit)."""
```

### OperationLog

```python
class OperationLog:
    """Audit trail for transaction operations."""
    
    def log_planned(self, operation: TransformationOp) -> None:
        """Log operation planned."""
        
    def log_executed(self, operation: TransformationOp) -> None:
        """Log operation executed."""
        
    def log_rolled_back(self, operation: TransformationOp) -> None:
        """Log operation rolled back."""
        
    def log_committed(self) -> None:
        """Log transaction committed."""
        
    def export_to_json(self, output_path: Path) -> None:
        """Export log to JSON for audit."""
```

---

## 🔄 Transaction Lifecycle

```
1. INITIALIZATION
   ├─→ Create transaction with checkpoint_id
   ├─→ Initialize operation log
   └─→ Ready to accept operations

2. OPERATION ACCUMULATION
   ├─→ add_operation(op1)
   ├─→ add_operation(op2)
   ├─→ add_operation(op3)
   └─→ All operations staged, none executed

3. COMMIT PHASE
   ├─→ Validate all operations
   ├─→ Sort by risk level (SAFE → CRITICAL)
   ├─→ Execute operations sequentially
   ├─→ Verify integrity after each
   └─→ Mark committed OR rollback on error

4. ROLLBACK PHASE (if error)
   ├─→ Reverse executed operations (LIFO)
   ├─→ Restore original content/paths
   ├─→ Restore checkpoint (filesystem-level)
   └─→ Mark rolled back

5. CLEANUP
   ├─→ Export operation log
   ├─→ Delete checkpoint (if committed successfully)
   └─→ Release resources
```

---

## 🎯 ACID Properties

### Atomicity
- **All-or-nothing:** Either all operations execute or none
- **Rollback on failure:** Any error triggers full rollback
- **No partial states:** Transaction completes fully or not at all

### Consistency
- **Valid states only:** Pre-commit validation ensures operations are valid
- **Checksum verification:** Integrity checks after each operation
- **Risk-based ordering:** SAFE operations first minimize failure impact

### Isolation
- **File locking:** Detect concurrent modifications before commit
- **Checksum validation:** Detect external changes during transaction
- **Single-threaded execution:** Operations execute sequentially

### Durability
- **Checkpoint backups:** Filesystem-level backup before transformation
- **Operation log:** Persistent audit trail
- **Idempotent rollback:** Rollback can be executed multiple times safely

---

## 📊 Performance Characteristics

| Operation | Overhead | Notes |
|-----------|----------|-------|
| Checkpoint creation | O(n) files | One-time cost, full directory copy |
| Operation validation | O(n) ops | Lightweight, checksum computation |
| Operation execution | O(n) ops | Sequential, no parallelization |
| Rollback | O(n) ops | LIFO reversal + checkpoint restore |
| Integrity verification | O(n) ops | SHA256 checksums |

**Optimization:**
- Checkpoint uses hardlinks where possible (COW filesystems)
- Checksums computed during analysis phase (cached)
- Dry-run mode skips all I/O operations

---

## 🧪 Testing Strategy

### Unit Tests
- Test operation execution (AST transform, rename)
- Test rollback logic (LIFO reversal)
- Test integrity verification (checksum mismatches)
- Test validation (file locks, missing targets)

### Integration Tests
- Test transaction lifecycle (init → commit → cleanup)
- Test rollback scenarios (mid-transaction failures)
- Test concurrent modification detection
- Test checkpoint restoration

### Edge Cases
- Transaction with 0 operations
- Transaction with duplicate operations
- Rollback after partial rollback (idempotency)
- Checkpoint restoration with missing checkpoint

---

## 🎯 Success Criteria

**Transaction Model Complete When:**
- ✅ TransformationOp data structure defined
- ✅ TransformationTransaction interface specified
- ✅ ACID properties documented
- ✅ Rollback strategy detailed
- ✅ Context manager protocol defined
- ✅ Supporting components specified (CheckpointManager, OperationLog)
- ✅ Performance characteristics analyzed

---

**Next:** Workflow diagram (visual representation of 5-phase flow with transactions)
