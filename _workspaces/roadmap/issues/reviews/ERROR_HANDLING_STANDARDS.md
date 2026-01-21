# CORTEX Error Handling Standards & Code Review Checklist

## Overview

This document establishes standards for error handling across the CORTEX codebase to eliminate brittleness and improve production reliability.

---

## Code Review Checklist

Use this checklist for all code reviews. **Any item marked as FAILED should block merge.**

### Exception Handling

- [ ] **No bare `except:` clauses**
  - ❌ FAIL: `except:` with nothing or `pass`
  - ✅ PASS: `except SpecificException as e:` with handling

- [ ] **No `except Exception:` with silent pass**
  - ❌ FAIL: `except Exception: pass`
  - ✅ PASS: `except Exception: logger.error(...); raise`

- [ ] **All exception paths logged or raised**
  - ❌ FAIL: Silent failure without logging
  - ✅ PASS: `logger.error(...)` or `raise` in handler

- [ ] **Specific exception types used**
  - ❌ FAIL: `except Exception:` for all errors
  - ✅ PASS: `except FileNotFoundError:`, `except ValueError:`, etc.

- [ ] **Context included in error messages**
  - ❌ FAIL: `logger.error("Error occurred")`
  - ✅ PASS: `logger.error(f"Failed to read {filepath}: {e}")`

### Resource Management

- [ ] **All context managers use `with` statement**
  - ❌ FAIL: `conn = sqlite3.connect(...); conn.close()`
  - ✅ PASS: `with sqlite3.connect(...) as conn:`

- [ ] **All try blocks have finally for cleanup**
  - ❌ FAIL: No finally block with close/cleanup
  - ✅ PASS: `finally: resource.close()`

- [ ] **File operations use `with` statement**
  - ❌ FAIL: `f = open(...); data = f.read()`
  - ✅ PASS: `with open(...) as f: data = f.read()`

- [ ] **Database connections properly closed**
  - ❌ FAIL: `conn = db.connect(...); cursor.execute(...)`
  - ✅ PASS: `with db.connection() as conn: cursor = conn.cursor()`

- [ ] **Lock releases are guaranteed**
  - ❌ FAIL: Lock acquire without finally block
  - ✅ PASS: `try: acquire_lock() finally: release_lock()`

### Input Validation

- [ ] **Function parameters validated at entry**
  - ❌ FAIL: No type checking on parameters
  - ✅ PASS: `if not isinstance(data, dict): raise TypeError(...)`

- [ ] **Required parameters checked for None**
  - ❌ FAIL: `def func(path): path.exists()`  # May be None
  - ✅ PASS: `if path is None: raise ValueError("path required")`

- [ ] **String parameters validated for empty**
  - ❌ FAIL: No check for empty string
  - ✅ PASS: `if not name or not isinstance(name, str): raise ValueError(...)`

- [ ] **Numeric parameters validated for range**
  - ❌ FAIL: `timeout` parameter not validated
  - ✅ PASS: `if timeout <= 0: raise ValueError("timeout must be positive")`

### Documentation

- [ ] **Function docstring documents all exceptions**
  ```python
  def risky_operation(self):
      """
      Raises:
          FileNotFoundError: If config file missing
          ValueError: If config invalid
          IOError: If file unreadable
      """
  ```

- [ ] **Error conditions explained in comments**
  - ❌ FAIL: `except IOError: pass  # ??`
  - ✅ PASS: `except IOError: pass  # File locked, will retry next cycle`

- [ ] **TODO/FIXME/HACK comments have owners and dates**
  - ❌ FAIL: `# TODO: Implement validation`
  - ✅ PASS: `# TODO(john, 2025-02-15): Implement validation`

- [ ] **Deferred work tracked with AC-IDs**
  - ❌ FAIL: `# TODO: Fix this bug`
  - ✅ PASS: `# TODO(owner, date): Implement AC-FIX-001-01 - Fix bug`

### Logging

- [ ] **Error logging includes exception info when needed**
  - ❌ FAIL: `logger.error("Error occurred")`
  - ✅ PASS: `logger.error("Operation failed", exc_info=True)`

- [ ] **Different log levels used appropriately**
  - debug: Expected conditions, detailed diagnostics
  - info: Normal operations, state changes
  - warning: Degraded operation, expected errors
  - error: Unexpected errors, needs investigation
  - critical: System failure, immediate action needed

- [ ] **Correlation IDs included for distributed tracing**
  - ❌ FAIL: No correlation ID in logs
  - ✅ PASS: `logger.error(..., extra={"correlation_id": cid})`

### Testing

- [ ] **Error cases tested explicitly**
  - ❌ FAIL: Only happy path tested
  - ✅ PASS: Test for FileNotFoundError, ValueError, etc.

- [ ] **Exception messages validated in tests**
  ```python
  with pytest.raises(ValueError, match="must be positive"):
      process_data(timeout=-1)
  ```

- [ ] **Resource cleanup tested**
  - ❌ FAIL: No test for connection close
  - ✅ PASS: Test verifies connection released to pool

- [ ] **Test isolation for singletons**
  - ❌ FAIL: Tests pollute global state
  - ✅ PASS: Fixtures reset singletons between tests

### Performance & Scalability

- [ ] **No unbounded loops without timeout**
  - ❌ FAIL: `while True: retry_operation()`
  - ✅ PASS: `while time.time() < deadline: retry_operation()`

- [ ] **External API calls have timeout**
  - ❌ FAIL: `response = requests.get(url)`
  - ✅ PASS: `response = requests.get(url, timeout=5.0)`

- [ ] **No resource exhaustion under load**
  - ❌ FAIL: Connections leak, files not closed
  - ✅ PASS: Resources released promptly

### Security & Reliability

- [ ] **No hardcoded paths or credentials**
  - ❌ FAIL: `db_path = "/home/user/project/db.sqlite"`
  - ✅ PASS: `db_path = Path(os.environ.get('DB_PATH', DEFAULT_PATH))`

- [ ] **No sensitive data in logs**
  - ❌ FAIL: `logger.info(f"User password: {pwd}")`
  - ✅ PASS: `logger.info(f"Authentication attempt for user: {user_id}")`

- [ ] **Error messages don't leak sensitive info**
  - ❌ FAIL: Exception shows database password
  - ✅ PASS: Generic error message with detailed logging

---

## Error Handling Pattern Examples

### Pattern 1: File Operations

```python
# ✅ CORRECT - Guaranteed cleanup
def read_config(config_path: Path) -> Dict[str, Any]:
    """
    Read configuration from YAML file.
    
    Args:
        config_path: Path to YAML file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is invalid
        IOError: If file cannot be read
    """
    if not isinstance(config_path, Path):
        raise TypeError(f"config_path must be Path, got {type(config_path)}")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
    except PermissionError:
        logger.error(f"Permission denied reading config: {config_path}")
        raise
    except IOError as e:
        logger.error(f"Cannot read config file {config_path}: {e}")
        raise
    
    try:
        config = yaml.safe_load(content)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_path}: {e}")
        raise ValueError(f"Invalid config format at line {e.problem_mark.line}")
    
    return config
```

### Pattern 2: Database Operations

```python
# ✅ CORRECT - Proper transaction handling
def execute_transaction(self, operations: List[Operation]) -> Result:
    """
    Execute multiple database operations as transaction.
    
    Raises:
        ValueError: If operations invalid
        DatabaseError: If operation fails
        ConnectionError: If connection lost
    """
    if not operations:
        raise ValueError("operations list cannot be empty")
    
    try:
        with self.db.connection() as conn:
            try:
                for op in operations:
                    op.execute(conn)
                conn.commit()
                logger.info(f"Transaction committed: {len(operations)} operations")
                return Result(success=True)
            except sqlite3.IntegrityError as e:
                conn.rollback()
                logger.warning(f"Transaction rolled back: integrity violation: {e}")
                raise ValueError(f"Data constraint violation: {e}")
            except sqlite3.OperationalError as e:
                conn.rollback()
                logger.error(f"Database operational error: {e}")
                raise DatabaseError(f"Database operation failed: {e}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed unexpectedly: {e}", exc_info=True)
                raise
    except ConnectionError as e:
        logger.error(f"Database connection lost: {e}")
        raise
```

### Pattern 3: REST API Integration

```python
# ✅ CORRECT - Proper timeout and retry
def fetch_data_with_retry(
    self, 
    url: str, 
    timeout: float = 5.0,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Dict[str, Any]:
    """
    Fetch data from API with exponential backoff retry.
    
    Args:
        url: API endpoint URL
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        backoff_factor: Backoff multiplier per retry
        
    Raises:
        ValueError: If URL invalid
        requests.ConnectTimeout: If connection times out
        requests.HTTPError: If HTTP error returned
        requests.RequestException: For other request errors
    """
    if not url or not isinstance(url, str):
        raise ValueError(f"url must be non-empty string, got {url}")
    
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "CORTEX/1.0"}
            )
            response.raise_for_status()
            logger.info(f"Fetched {url}: {response.status_code}")
            return response.json()
            
        except requests.ConnectTimeout as e:
            wait_time = timeout * (backoff_factor ** attempt)
            if attempt < max_retries - 1:
                logger.warning(
                    f"Connection timeout to {url}, retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Connection timeout to {url} after {max_retries} retries: {e}")
                raise
        except requests.HTTPError as e:
            if response.status_code in (429, 503):  # Retryable
                wait_time = timeout * (backoff_factor ** attempt)
                logger.warning(f"HTTP {response.status_code}, retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error {response.status_code} from {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}", exc_info=True)
            raise
```

### Pattern 4: Long-Running Operations with Cancellation

```python
# ✅ CORRECT - Cancellation support and cleanup
class DataProcessor:
    def process_large_dataset(
        self,
        dataset: Iterator[Record],
        cancellation_token: Optional[CancellationToken] = None
    ) -> ProcessResult:
        """
        Process large dataset with cancellation support.
        
        Args:
            dataset: Iterator of records to process
            cancellation_token: Token to signal cancellation
            
        Raises:
            OperationCancelledError: If cancelled
            ProcessingError: If processing fails
        """
        result = ProcessResult()
        
        try:
            for record in dataset:
                # Check for cancellation
                if cancellation_token and cancellation_token.is_cancelled:
                    logger.info("Processing cancelled by user")
                    raise OperationCancelledError("User requested cancellation")
                
                try:
                    processed = self._process_record(record)
                    result.add_success(processed)
                except ValidationError as e:
                    logger.warning(f"Record validation failed: {e}")
                    result.add_error(record.id, str(e))
                except Exception as e:
                    logger.error(f"Unexpected error processing record: {e}", exc_info=True)
                    result.add_error(record.id, str(e))
        finally:
            # Cleanup is always executed
            self._cleanup_resources()
            result.finalize()
        
        return result
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Bare Except
```python
try:
    do_something()
except:
    pass
```

### ✅ Correct Approach
```python
try:
    do_something()
except SpecificError as e:
    handle_specific_error(e)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

---

### ❌ Mistake 2: Silent Suppression
```python
try:
    risky_operation()
except Exception:
    pass  # What went wrong?
```

### ✅ Correct Approach
```python
try:
    risky_operation()
except SomeError:
    logger.warning("Expected condition occurred")
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

---

### ❌ Mistake 3: No Resource Cleanup
```python
conn = db.connect()
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
# connection never closed
```

### ✅ Correct Approach
```python
with db.connection() as conn:
    cursor = conn.cursor()
    cursor.execute(sql)
conn.commit()  # Automatic close
```

---

### ❌ Mistake 4: Hardcoded Paths
```python
config_path = "/home/user/projects/cortex/config.yaml"
```

### ✅ Correct Approach
```python
config_path = Path(
    os.environ.get(
        'CORTEX_CONFIG',
        Path(__file__).parent / 'config.yaml'
    )
)
```

---

### ❌ Mistake 5: No Parameter Validation
```python
def process_data(data, timeout=30):
    # Assume data is dict and timeout > 0
    client.query(data, timeout=timeout)
```

### ✅ Correct Approach
```python
def process_data(data: Dict[str, Any], timeout: float = 30.0) -> Result:
    if not isinstance(data, dict):
        raise TypeError(f"data must be dict, got {type(data)}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")
    
    client.query(data, timeout=timeout)
```

---

## Testing for Error Conditions

### ✅ Good Error Test
```python
def test_process_data_with_invalid_timeout():
    """Should raise ValueError for non-positive timeout."""
    processor = DataProcessor()
    
    with pytest.raises(ValueError, match="timeout must be positive"):
        processor.process_data({"key": "value"}, timeout=-1)
```

### ✅ Good Resource Cleanup Test
```python
def test_database_connection_cleanup():
    """Connection should be released to pool even on error."""
    pool = ConnectionPool(max_connections=2)
    
    with pytest.raises(ValueError):
        with pool.connection() as conn:
            raise ValueError("Simulated error")
    
    # Connection should be available again
    with pool.connection() as conn:
        assert conn is not None
```

---

## Enforcement

### Automated Checks
- ✅ Pre-commit hooks will fail on bare except
- ✅ CI/CD pipeline will run static analysis
- ✅ Code review bot will flag pattern violations

### Manual Review
- Code reviewer uses this checklist for every PR
- Failed checklist items block merge
- Team training on error handling standards

---

## Questions?

For questions about these standards, create issue with label `error-handling-standards` or contact the architecture team.

**Last Updated:** January 21, 2025  
**Version:** 1.0
