# Vacuum v2 Migration Strategy

**Date:** 2026-01-02  
**Purpose:** Define architecture and implementation strategy for Vacuum v2 migration

---

## 🎯 Migration Goals

Transform Vacuum from hybrid v0/v1 to **pure autonomous orchestrator** with:

1. **Merge V0 + V1 capabilities** (AST analysis + filesystem operations)
2. **BaseOrchestrator v4.1 compliance** (config-driven, phase management)
3. **Master Orchestrator integration** (pattern-based routing)
4. **Transactional safety** (atomic operations, rollback capability)
5. **CORTEX governance enforcement** (brain protection, file reorganization)

---

## 🏗️ Architecture Overview

### Component Hierarchy

```
VacuumOrchestratorV2(BaseOrchestratorV4_1)
│
├── config: vacuum-orchestrator-v2.yaml
│   ├── cleanup_categories (10 categories)
│   ├── safety_rules (critical patterns, thresholds)
│   ├── exclusions (patterns to skip)
│   └── output_templates (report templates)
│
├── FilesystemEngine
│   ├── DirectoryScanner
│   ├── FilesystemTransaction
│   ├── CheckpointManager
│   ├── DuplicateDetector
│   ├── OrphanDetector
│   └── SymlinkHandler
│
├── SafetyValidator
│   ├── CriticalFileDetector
│   ├── GitStatusChecker
│   ├── PermissionValidator
│   └── RiskClassifier
│
├── CleanupHandlers (5 categories)
│   ├── TempFileCleaner
│   ├── BuildArtifactCleaner
│   ├── IDEMetadataCleaner
│   ├── DuplicateRemover
│   └── OrphanHandler
│
└── ReportGenerator
    ├── DryRunReportGenerator
    ├── CompletionReportGenerator
    └── CheckpointManifestGenerator
```

### Data Flow

```
User Input
    ↓
Master Orchestrator (pattern: "vacuum [path]")
    ↓
VacuumOrchestratorV2.execute(target_path, dry_run=True, ...)
    ↓
Phase 1: DISCOVERY
    ├── DirectoryScanner.scan_directory()
    ├── Apply exclusion patterns
    ├── Categorize files (10 categories)
    └── Store in inventory: {temp_files: [], build_artifacts: [], ...}
    ↓
Phase 2: ANALYSIS
    ├── DuplicateDetector.find_duplicates() [hash-based]
    ├── OrphanDetector.find_orphaned_tests() [AST]
    ├── OrphanDetector.find_unused_imports() [AST]
    ├── Calculate disk space recovery
    └── Store in cleanup_plan: {delete: [], move: [], archive: []}
    ↓
Phase 3: PLANNING (Safety Validation)
    ├── SafetyValidator.validate_deletion() for each file
    ├── RiskClassifier.classify() → SAFE | LOW | MEDIUM | HIGH | CRITICAL
    ├── Block CRITICAL files (git, source, config, docs, brain)
    ├── Flag HIGH/MEDIUM for user confirmation
    └── Store in validated_plan: {safe: [], blocked: [], confirm: []}
    ↓
Phase 4: APPROVAL (if not auto-approved)
    ├── Generate dry-run report (if dry_run=True)
    ├── OR prompt user for confirmation (if dry_run=False)
    └── User approves/rejects
    ↓
Phase 5: EXECUTION (if approved)
    ├── CheckpointManager.create_checkpoint()
    ├── FilesystemTransaction.begin()
    ├── For each file in validated_plan:
    │   ├── delete_file() OR move_file() OR archive_file()
    │   ├── Log operation to transaction manifest
    │   └── Verify success
    ├── FilesystemTransaction.commit()
    └── CheckpointManager.finalize()
    ↓
Phase 6: COMPLETION
    ├── Re-scan filesystem (validation)
    ├── Generate completion report
    ├── Update .gitignore (if needed)
    └── Return results
```

---

## 🔄 Transactional Operations

### Transaction Design

**Goal:** Ensure atomic operations with rollback capability

#### Transaction Log Format

```json
{
  "transaction_id": "vacuum-2026-01-02-120000",
  "timestamp": "2026-01-02T12:00:00Z",
  "target_path": "/path/to/workspace",
  "operations": [
    {
      "id": 1,
      "type": "delete",
      "path": "/path/to/workspace/temp/cache.tmp",
      "backup_path": ".vacuum-checkpoint-2026-01-02/files/cache.tmp",
      "size_bytes": 1024,
      "hash": "a1b2c3...",
      "timestamp": "2026-01-02T12:00:01Z",
      "status": "completed"
    },
    {
      "id": 2,
      "type": "move",
      "source": "/path/to/workspace/misplaced/summary.md",
      "destination": "/path/to/workspace/cortex-brain/documents/summaries/summary.md",
      "timestamp": "2026-01-02T12:00:02Z",
      "status": "completed"
    },
    {
      "id": 3,
      "type": "archive",
      "source": "/path/to/workspace/logs/app-2025-01-01.log",
      "archive_path": "/path/to/workspace/logs/archive/2025-01/app-2025-01-01.log.gz",
      "compression": "gzip",
      "original_size": 5242880,
      "compressed_size": 524288,
      "timestamp": "2026-01-02T12:00:03Z",
      "status": "completed"
    }
  ],
  "summary": {
    "operations_total": 1010,
    "operations_completed": 1010,
    "operations_failed": 0,
    "space_saved_bytes": 550000000,
    "duration_seconds": 45.2
  }
}
```

#### Rollback Algorithm

```python
def rollback(transaction_log: Path) -> None:
    """
    Rollback vacuum operation by reversing all operations.
    
    Operations are reversed in LIFO order (last executed first).
    """
    with open(transaction_log, 'r') as f:
        transaction = json.load(f)
    
    # Reverse operations (LIFO)
    for operation in reversed(transaction['operations']):
        if operation['status'] != 'completed':
            continue  # Skip failed operations
        
        if operation['type'] == 'delete':
            # Restore from backup
            backup = Path(operation['backup_path'])
            original = Path(operation['path'])
            if backup.exists():
                shutil.copy2(backup, original)
                logger.info(f"Restored: {original}")
        
        elif operation['type'] == 'move':
            # Reverse move
            destination = Path(operation['destination'])
            source = Path(operation['source'])
            if destination.exists():
                destination.rename(source)
                logger.info(f"Reversed move: {destination} → {source}")
        
        elif operation['type'] == 'archive':
            # Decompress and restore
            archive = Path(operation['archive_path'])
            original = Path(operation['source'])
            if archive.exists():
                decompress_and_restore(archive, original)
                logger.info(f"Restored from archive: {original}")
```

### Atomic Operation Implementation

```python
class FilesystemTransaction:
    """
    Transactional filesystem operations with ACID guarantees.
    
    Properties:
        - Atomicity: All operations succeed or all fail
        - Consistency: Filesystem remains valid state
        - Isolation: Operations don't interfere with other processes
        - Durability: Changes persisted to disk
    """
    
    def __init__(self, checkpoint_dir: Path, state_db: PlanningStateDB):
        self.checkpoint_dir = checkpoint_dir
        self.state_db = state_db
        self.operations = []
        self.transaction_id = None
    
    def begin(self) -> str:
        """Start new transaction."""
        self.transaction_id = f"vacuum-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create transaction in database
        self.state_db.begin_transaction(self.transaction_id)
        
        return self.transaction_id
    
    def delete_file(self, path: Path) -> bool:
        """
        Delete file with checkpoint backup.
        
        Steps:
            1. Verify file exists
            2. Create backup in checkpoint directory
            3. Log operation to transaction
            4. Delete original file
            5. Verify deletion
        """
        if not path.exists():
            return False
        
        # Create backup
        backup_path = self.checkpoint_dir / "files" / path.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy with metadata preservation
            shutil.copy2(path, backup_path)
            
            # Verify backup hash matches original
            if not self._verify_hash(path, backup_path):
                logger.error(f"Backup verification failed: {path}")
                return False
        except OSError as e:
            logger.error(f"Backup creation failed: {path} - {e}")
            return False
        
        # Log operation
        operation = {
            'id': len(self.operations) + 1,
            'type': 'delete',
            'path': str(path),
            'backup_path': str(backup_path),
            'size_bytes': path.stat().st_size,
            'hash': self._compute_hash(path),
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Record in database
        self.state_db.log_operation(self.transaction_id, operation)
        
        # Delete file
        try:
            path.unlink()
            
            # Verify deletion
            if path.exists():
                logger.error(f"Deletion failed (file still exists): {path}")
                operation['status'] = 'failed'
                return False
            
            operation['status'] = 'completed'
            self.operations.append(operation)
            return True
        
        except OSError as e:
            logger.error(f"Deletion failed: {path} - {e}")
            operation['status'] = 'failed'
            return False
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        Move file atomically with rollback capability.
        
        Steps:
            1. Verify source exists
            2. Resolve destination conflict (if exists)
            3. Create destination directory
            4. Log operation
            5. Atomic rename (if same filesystem) OR copy + delete
            6. Verify move
        """
        if not source.exists():
            return False
        
        # Resolve conflict
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
        
        self.state_db.log_operation(self.transaction_id, operation)
        
        try:
            # Attempt atomic rename (same filesystem)
            source.rename(destination)
            
            operation['status'] = 'completed'
            self.operations.append(operation)
            return True
        
        except OSError:
            # Cross-filesystem move (copy + delete)
            try:
                shutil.copy2(source, destination)
                
                # Verify copy
                if self._verify_hash(source, destination):
                    source.unlink()
                    operation['status'] = 'completed'
                    self.operations.append(operation)
                    return True
                else:
                    # Copy failed verification
                    destination.unlink()
                    operation['status'] = 'failed'
                    return False
            
            except OSError as e:
                logger.error(f"Move failed: {source} → {destination} - {e}")
                operation['status'] = 'failed'
                return False
    
    def commit(self) -> None:
        """Finalize transaction."""
        # Write transaction manifest
        manifest = {
            'transaction_id': self.transaction_id,
            'timestamp': datetime.now().isoformat(),
            'operations': self.operations,
            'summary': {
                'operations_total': len(self.operations),
                'operations_completed': sum(1 for op in self.operations if op['status'] == 'completed'),
                'operations_failed': sum(1 for op in self.operations if op['status'] == 'failed')
            }
        }
        
        manifest_path = self.checkpoint_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Commit transaction in database
        self.state_db.commit_transaction(self.transaction_id)
        
        logger.info(f"Transaction committed: {self.transaction_id}")
    
    def rollback(self) -> None:
        """Rollback transaction (restore all files)."""
        # Implementation from rollback algorithm above
        pass
    
    def _verify_hash(self, path1: Path, path2: Path) -> bool:
        """Verify two files have identical hash."""
        hash1 = self._compute_hash(path1)
        hash2 = self._compute_hash(path2)
        return hash1 == hash2
    
    def _compute_hash(self, path: Path) -> str:
        """Compute SHA256 hash of file."""
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _resolve_conflict(self, path: Path) -> Path:
        """Resolve filename conflict by appending counter."""
        counter = 1
        while True:
            new_path = path.with_stem(f"{path.stem}_{counter}")
            if not new_path.exists():
                return new_path
            counter += 1
```

---

## 🧠 Duplicate Detection Algorithm

### Three-Phase Detection

```python
class DuplicateDetector:
    """
    Efficient duplicate detection using three-phase algorithm.
    
    Phase 1: Group by size (O(n), instant)
    Phase 2: Quick hash first 8KB (O(n), fast)
    Phase 3: Full hash (O(n), slow but rare)
    """
    
    def find_duplicates(self, files: List[Path]) -> List[List[Path]]:
        """
        Find duplicate files in three phases.
        
        Returns:
            List of duplicate groups (each group = list of identical files)
        """
        # Phase 1: Group by size
        size_groups = defaultdict(list)
        for file_path in files:
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
            except OSError:
                continue
        
        # Filter groups with only 1 file (no duplicates)
        size_groups = {size: paths for size, paths in size_groups.items() if len(paths) > 1}
        
        logger.info(f"Phase 1: {len(files)} files → {len(size_groups)} size groups")
        
        # Phase 2: Quick hash (first 8KB)
        quick_hash_groups = defaultdict(list)
        for size, paths in size_groups.items():
            for path in paths:
                quick_hash = self._quick_hash(path, 8192)
                quick_hash_groups[(size, quick_hash)].append(path)
        
        # Filter groups with only 1 file
        quick_hash_groups = {key: paths for key, paths in quick_hash_groups.items() if len(paths) > 1}
        
        logger.info(f"Phase 2: {len(size_groups)} size groups → {len(quick_hash_groups)} quick-hash groups")
        
        # Phase 3: Full hash (only for remaining candidates)
        duplicate_groups = []
        for (size, quick_hash), paths in quick_hash_groups.items():
            full_hash_groups = defaultdict(list)
            for path in paths:
                full_hash = self._full_hash(path)
                full_hash_groups[full_hash].append(path)
            
            # Collect duplicate groups (hash collision = exact duplicates)
            for full_hash, group in full_hash_groups.items():
                if len(group) > 1:
                    duplicate_groups.append(group)
        
        logger.info(f"Phase 3: {len(quick_hash_groups)} quick-hash groups → {len(duplicate_groups)} duplicate groups")
        
        return duplicate_groups
```

### Optimization Strategies

1. **Hash Caching:**
   - Store full hashes in `.vacuum-hash-cache.json`
   - Invalidate cache if file mtime changed
   - Speeds up subsequent runs by 10x

2. **Parallel Processing:**
   - Use `ThreadPoolExecutor` for hashing
   - Hash multiple files concurrently
   - Target: 100 files/second

3. **Incremental Hashing:**
   - Hash in 64KB chunks
   - Avoid loading large files into memory
   - Works with files >1GB

4. **Early Termination:**
   - Stop at Phase 1 if no size matches
   - Stop at Phase 2 if no quick-hash matches
   - Only run expensive Phase 3 when necessary

---

## 🔍 Orphan Detection Strategy

### AST-Based Analysis

```python
class OrphanDetector:
    """Detect orphaned files using AST analysis."""
    
    def __init__(self, project_root: Path, ast_engine: ASTEngine):
        self.project_root = project_root
        self.ast_engine = ast_engine
    
    def find_orphaned_tests(self) -> List[Path]:
        """
        Find test files without corresponding source files.
        
        Algorithm:
            1. Find all test files (test_*.py, *_test.py)
            2. For each test, infer expected source file
            3. Check if source file exists
            4. If not, mark test as orphaned
        """
        orphaned_tests = []
        
        # Find all test files
        test_files = list(self.project_root.glob('**/test_*.py'))
        test_files += list(self.project_root.glob('**/*_test.py'))
        
        for test_file in test_files:
            # Infer source file name
            if test_file.name.startswith('test_'):
                source_name = test_file.name[5:]  # Remove 'test_' prefix
            elif test_file.name.endswith('_test.py'):
                source_name = test_file.name[:-8] + '.py'  # Remove '_test' suffix
            else:
                continue
            
            # Check if source file exists (same directory or src/)
            source_paths = [
                test_file.parent / source_name,
                self.project_root / 'src' / source_name,
                self.project_root / 'src' / test_file.parent.relative_to(self.project_root) / source_name
            ]
            
            if not any(path.exists() for path in source_paths):
                orphaned_tests.append(test_file)
        
        return orphaned_tests
    
    def find_unused_imports(self) -> List[Dict[str, Any]]:
        """
        Find files with unused import statements.
        
        Uses ASTEngine to parse Python files and detect unused imports.
        """
        return self.ast_engine.find_unused_imports()
```

---

## 📊 Progress Tracking

### Database Schema

Extend `PlanningStateDB` with vacuum-specific tables:

```sql
CREATE TABLE vacuum_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,  -- 'delete', 'move', 'archive'
    source_path TEXT NOT NULL,
    destination_path TEXT,
    backup_path TEXT,
    size_bytes INTEGER,
    hash TEXT,
    status TEXT NOT NULL,  -- 'pending', 'completed', 'failed'
    timestamp TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

CREATE TABLE vacuum_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    files_scanned INTEGER,
    files_deleted INTEGER,
    files_moved INTEGER,
    files_archived INTEGER,
    space_saved_bytes INTEGER,
    duration_seconds REAL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);
```

---

## 🎯 Implementation Order

### Phase 1: Core Infrastructure (Day 1-2)
1. `VacuumOrchestratorV2` base class
2. `FilesystemEngine` with scanning
3. `SafetyValidator` with critical file detection
4. Basic dry-run functionality

### Phase 2: Transactional Operations (Day 2-3)
1. `FilesystemTransaction` class
2. `CheckpointManager` class
3. Atomic delete/move/archive operations
4. Rollback implementation

### Phase 3: Cleanup Handlers (Day 3-4)
1. `TempFileCleaner`
2. `BuildArtifactCleaner`
3. `IDEMetadataCleaner`
4. `DuplicateDetector` (three-phase algorithm)
5. `OrphanDetector` (AST-based)

### Phase 4: Integration (Day 4-5)
1. Manifest creation (`vacuum-orchestrator-v2.yaml`)
2. Template creation (dry-run, completion reports)
3. Master Orchestrator routing
4. End-to-end testing

### Phase 5: Validation (Day 5)
1. Comprehensive test suite (60+ tests)
2. Edge case testing (symlinks, permissions, unicode)
3. Performance testing (100K+ files)
4. CORTEX brain protection validation

---

## ✅ Success Criteria

1. **Functionality:**
   - ✅ All 10 cleanup categories functional
   - ✅ Dry-run mode accurate
   - ✅ Transactional operations (rollback works)
   - ✅ Safety validation (critical files blocked)
   - ✅ Master Orchestrator routing

2. **Performance:**
   - ✅ <30 seconds for 100K files (dry-run)
   - ✅ <5 seconds per 10K files (execution)
   - ✅ <100MB memory for 1M files

3. **Safety:**
   - ✅ 0 critical file deletions
   - ✅ 100% checkpoint success rate
   - ✅ 100% rollback success rate

4. **Testing:**
   - ✅ 100% code coverage
   - ✅ 60+ test cases passing
   - ✅ All edge cases handled

5. **Integration:**
   - ✅ BaseOrchestrator v4.1 compliant
   - ✅ Master Orchestrator routes correctly
   - ✅ CORTEX brain protection enforced

---

**Next:** Begin Phase 1 implementation (VacuumOrchestratorV2 base class).
