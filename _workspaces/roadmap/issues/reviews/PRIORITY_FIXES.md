# Priority Fixes for CORTEX Brittleness Issues

**Status:** IMMEDIATE ACTION REQUIRED  
**Priority:** CRITICAL  
**Timeline:** Complete within 1 week

---

## FIX #1: Database Connection Leak in ac_fix_001_06_regenerate.py

**Severity:** CRITICAL  
**File:** `cortex/tools/toolkit/ac_fix_001_06_regenerate.py`  
**Lines:** 43-66  
**Risk:** Connection exhaustion in long-running processes

### Current Code (BROKEN)
```python
# Line 43: Hardcoded path
db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/core/state/governance.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

# Line 46: Connection without cleanup guarantee
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# ... 20 lines of operations ...

conn.commit()

# PROBLEM: conn.close() not guaranteed to execute
# If any error occurs, connection leaks
```

### Fixed Code
```python
# Line 43: Use environment variable
import os
db_path = Path(
    os.environ.get(
        'CORTEX_DB_PATH',
        Path(__file__).parent.parent.parent / 'state' / 'governance.db'
    )
)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Line 46+: Use context manager
try:
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        
        # Create audit_log table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                ac_id TEXT,
                operation TEXT,
                timestamp TEXT,
                component TEXT,
                level TEXT,
                message TEXT,
                correlation_id TEXT,
                metadata TEXT,
                previous_hash TEXT,
                entry_hash TEXT
            )
        """)
        
        # Generate global hash chain entries
        print("Generating audit entries with GLOBAL hash chain...")
        entry_id = 1
        prev_hash = ""
        
        # Create entries for several ACs
        acs = ["AC-FIX-001-01", "AC-FIX-001-02", "AC-MCP-EXPOSURE-001", "AC-NFR-002-01"]
        
        for ac_id in acs:
            for operation in ["AC_START", "AC_EXECUTE", "AC_COMPLETE"]:
                # Simple hash: hash of (previous_hash + entry_id)
                entry_hash = hashlib.sha256(f"{prev_hash}{entry_id}".encode()).hexdigest()
                
                create_audit_entry(conn, entry_id, ac_id, operation, prev_hash, entry_hash)
                
                print(f"  Entry {entry_id}: {ac_id} {operation}")
                print(f"    previous_hash: {prev_hash[:16] if prev_hash else 'GENESIS'}...")
                print(f"    entry_hash:    {entry_hash[:16]}...")
                
                prev_hash = entry_hash
                entry_id += 1
        
        # Commit happens automatically on context manager exit
        
        # Verify the chain
        print("\nVerifying global hash chain...")
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total = cursor.fetchone()[0]
        print(f"Total entries: {total}")
        
        cursor.execute("SELECT id, ac_id, operation, previous_hash, entry_hash FROM audit_log ORDER BY id")
        entries = cursor.fetchall()
        
        violations = 0
        for i, (eid, ac_id, op, prev_hash, entry_hash) in enumerate(entries):
            if i > 0:
                prior_entry = entries[i-1]
                if prev_hash != prior_entry[4]:
                    print(f"❌ VIOLATION at entry {eid}: previous_hash doesn't match prior entry's hash")
                    violations += 1
        
        if violations == 0:
            print(f"✅ GLOBAL HASH CHAIN VERIFIED - All {total} entries linked correctly!")
        else:
            print(f"❌ Found {violations} violations")
        
except sqlite3.Error as e:
    print(f"❌ Database error: {e}")
    raise
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    raise

print("\n✅ AC-FIX-001-06 COMPLETE: Audit log regenerated with global hash chain")
```

**Changes Made:**
1. ✅ Replaced hardcoded path with environment variable
2. ✅ Wrapped connection in `with` statement for guaranteed cleanup
3. ✅ Added specific exception handling instead of silent failures
4. ✅ Added logging for all operations

**Verification:**
```bash
# Test locally
export CORTEX_DB_PATH=/tmp/test_governance.db
python cortex/tools/toolkit/ac_fix_001_06_regenerate.py
# Should succeed and print success message
```

---

## FIX #2: Bare Except in validate_consolidation.py

**Severity:** CRITICAL  
**File:** `cortex/brain/mcp/tools/validate_consolidation.py`  
**Lines:** 205  
**Risk:** Silent file read failures return magic string

### Current Code (BROKEN)
```python
def _compute_file_hash(self, file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        # PROBLEM: All errors return magic string
        return "ERROR_READING_FILE"
```

### Fixed Code
```python
def _compute_file_hash(self, file_path: Path) -> str:
    """
    Compute SHA256 hash of file content.
    
    Args:
        file_path: Path to file
        
    Returns:
        SHA256 hexdigest
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If cannot read file
        IOError: If I/O error occurs
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        self.logger.error(f"File not found during hash: {file_path}")
        raise
    except PermissionError:
        self.logger.error(f"Permission denied reading file: {file_path}")
        raise
    except IOError as e:
        self.logger.error(f"I/O error reading file {file_path}: {e}")
        raise
    except Exception as e:
        self.logger.error(f"Unexpected error hashing file {file_path}: {e}", exc_info=True)
        raise
```

**Changes Made:**
1. ✅ Replaced bare `except:` with specific exception types
2. ✅ Added parameter validation
3. ✅ Added logging with context for each error path
4. ✅ Added docstring documenting exceptions
5. ✅ Raises exceptions instead of returning magic string

**Verification:**
```python
# Test cases
def test_hash_nonexistent_file():
    validator = ConsolidationValidator()
    with pytest.raises(FileNotFoundError):
        validator._compute_file_hash(Path("/nonexistent/file.txt"))

def test_hash_unreadable_file():
    with tempfile.NamedTemporaryFile() as f:
        # Make unreadable
        os.chmod(f.name, 0o000)
        validator = ConsolidationValidator()
        with pytest.raises(PermissionError):
            validator._compute_file_hash(Path(f.name))

def test_hash_valid_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"test content")
        f.flush()
        validator = ConsolidationValidator()
        hash_value = validator._compute_file_hash(Path(f.name))
        assert hash_value.startswith("e3b0c")  # Known hash prefix
```

---

## FIX #3: Bare Except in import validation tests

**Severity:** CRITICAL  
**File:** `tests/test_ac_ar_010_03_imports.py`  
**Lines:** 42, 66, 385  
**Risk:** Test failures silently suppressed

### Current Code (BROKEN)
```python
# Line 42
try:
    content = py_file.read_text(encoding='utf-8', errors='ignore')
    for pattern in old_patterns:
        if pattern in content and '__pycache__' not in str(py_file):
            found_old.append((py_file.name, pattern))
except:
    pass  # PROBLEM: Errors silently ignored

# Line 66
try:
    content = py_file.read_text(encoding='utf-8', errors='ignore')
    for pattern in new_patterns:
        if pattern in content and '__pycache__' not in str(py_file):
            found_new[pattern] = found_new.get(pattern, 0) + 1
except:
    pass  # PROBLEM: Errors silently ignored
```

### Fixed Code
```python
# Line 42
for py_file in cortex.rglob("*.py"):
    try:
        content = py_file.read_text(encoding='utf-8', errors='ignore')
    except FileNotFoundError:
        logging.warning(f"File disappeared during scan: {py_file}")
        continue
    except (UnicodeDecodeError, PermissionError) as e:
        logging.warning(f"Cannot read {py_file}: {e}")
        continue
    except Exception as e:
        logging.error(f"Unexpected error reading {py_file}: {e}", exc_info=True)
        raise
    
    try:
        for pattern in old_patterns:
            if pattern in content and '__pycache__' not in str(py_file):
                found_old.append((py_file.name, pattern))
    except Exception as e:
        logging.error(f"Error scanning {py_file} for old patterns: {e}")
        raise

# Line 66 - Similar pattern
for py_file in cortex.rglob("*.py"):
    try:
        content = py_file.read_text(encoding='utf-8', errors='ignore')
    except FileNotFoundError:
        continue
    except (UnicodeDecodeError, PermissionError) as e:
        logging.warning(f"Cannot read {py_file}: {e}")
        continue
    except Exception as e:
        logging.error(f"Unexpected error reading {py_file}: {e}")
        raise
    
    try:
        for pattern in new_patterns:
            if pattern in content and '__pycache__' not in str(py_file):
                found_new[pattern] = found_new.get(pattern, 0) + 1
    except Exception as e:
        logging.error(f"Error scanning {py_file} for new patterns: {e}")
        raise
```

**Changes Made:**
1. ✅ Separated file read from pattern matching
2. ✅ Specific exception handling for file operations
3. ✅ Logging for transient errors (continue)
4. ✅ Error logging for unexpected conditions (raise)

---

## FIX #4: Connection Pool Exception Suppression

**Severity:** CRITICAL  
**File:** `cortex/infrastructure/connection_pool.py`  
**Lines:** 300, 383  
**Risk:** Dead connections remain in pool

### Current Code (BROKEN)
```python
def _close_connection(self, wrapper: _ConnectionWrapper) -> None:
    """Close a connection and remove from pool."""
    try:
        wrapper.connection.close()
    except Exception:
        pass  # PROBLEM: Error silently ignored
    
    conn_id = id(wrapper.connection)
    if conn_id in self._all_connections:
        del self._all_connections[conn_id]
```

### Fixed Code
```python
def _close_connection(self, wrapper: _ConnectionWrapper) -> None:
    """
    Close a connection and remove from pool.
    
    Raises:
        sqlite3.Error: If close fails (logged but re-raised for diagnostics)
    """
    conn_id = id(wrapper.connection)
    try:
        wrapper.connection.close()
        self.logger.debug(f"Closed connection {conn_id}")
    except sqlite3.Error as e:
        self.logger.error(
            f"Failed to close connection {conn_id}: {e}",
            extra={"connection_id": conn_id}
        )
        # Still remove from pool even if close failed
        if conn_id in self._all_connections:
            del self._all_connections[conn_id]
        raise
    except Exception as e:
        self.logger.error(
            f"Unexpected error closing connection {conn_id}: {e}",
            exc_info=True,
            extra={"connection_id": conn_id}
        )
        # Still cleanup
        if conn_id in self._all_connections:
            del self._all_connections[conn_id]
        raise
    else:
        # Only remove if successfully closed
        if conn_id in self._all_connections:
            del self._all_connections[conn_id]
```

**Changes Made:**
1. ✅ Specific exception types for SQLite errors
2. ✅ Mandatory logging before any suppression
3. ✅ Cleanup guaranteed even on error
4. ✅ Connection still removed from pool

---

## FIX #5: Database Exception Suppression

**Severity:** CRITICAL  
**File:** `cortex/infrastructure/database.py`  
**Lines:** 89, 105, 270  
**Risk:** Database errors invisible to caller

### Current Code (BROKEN)
```python
# Line 89
try:
    yield conn
except Exception:
    conn.rollback()
    raise
else:
    conn.commit()

# Line 105
try:
    self._local.connection.close()
except Exception:
    pass  # PROBLEM: Close errors silently ignored
```

### Fixed Code
```python
# Line 89 - This one is OK, add logging
try:
    yield conn
except Exception as e:
    self.logger.error(
        f"Transaction failed, rolling back: {e}",
        exc_info=True
    )
    try:
        conn.rollback()
    except Exception as rb_error:
        self.logger.error(f"Rollback also failed: {rb_error}", exc_info=True)
    raise
else:
    try:
        conn.commit()
    except Exception as e:
        self.logger.error(f"Commit failed: {e}", exc_info=True)
        raise

# Line 105 - Add logging
if hasattr(self._local, 'connection') and self._local.connection is not None:
    try:
        self._local.connection.close()
        self.logger.debug("Database connection closed")
    except sqlite3.Error as e:
        self.logger.warning(f"Error closing database connection: {e}")
    except Exception as e:
        self.logger.error(f"Unexpected error closing connection: {e}", exc_info=True)
    finally:
        self._local.connection = None
```

**Changes Made:**
1. ✅ Added logging to all exception handlers
2. ✅ Specific exception types
3. ✅ Guaranteed cleanup in finally block
4. ✅ Connection set to None regardless

---

## Fix Implementation Checklist

- [ ] FIX #1: ac_fix_001_06_regenerate.py (1-2 hours)
  - [ ] Replace hardcoded path
  - [ ] Add context manager
  - [ ] Add exception handling
  - [ ] Test locally

- [ ] FIX #2: validate_consolidation.py (1-2 hours)
  - [ ] Replace bare except
  - [ ] Add parameter validation
  - [ ] Add logging
  - [ ] Write unit tests

- [ ] FIX #3: test_ac_ar_010_03_imports.py (1-2 hours)
  - [ ] Separate read from parsing
  - [ ] Add specific exception handling
  - [ ] Add logging
  - [ ] Run all tests

- [ ] FIX #4: connection_pool.py (2-3 hours)
  - [ ] Add logging to handlers
  - [ ] Ensure cleanup guaranteed
  - [ ] Add unit tests for error paths
  - [ ] Test connection leak scenario

- [ ] FIX #5: database.py (2-3 hours)
  - [ ] Add logging to all handlers
  - [ ] Add finally blocks
  - [ ] Test transaction rollback
  - [ ] Test connection cleanup

**Total Estimated Effort:** 8-12 hours  
**Recommended Timeline:** Complete by end of January 22, 2025

---

## Testing After Fixes

### Unit Tests Required
```python
# For each fix, add tests for:
def test_error_cases():
    """Verify error handling."""

def test_resource_cleanup():
    """Verify resources cleanup on error."""

def test_error_logging():
    """Verify errors are logged."""

def test_no_silent_failures():
    """Verify no silent exception suppression."""
```

### Integration Tests Required
```python
# Run full test suite
pytest cortex/ -v --tb=short

# Check for new warnings
python -m pylint cortex/ --disable=all --enable=bare-except
```

---

## Sign-Off

- [ ] Code review approved
- [ ] All tests passing
- [ ] No new brittleness issues introduced
- [ ] PR merged to main branch

**Due Date:** January 22, 2025 End of Day
