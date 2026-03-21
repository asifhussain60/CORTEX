# CORTEX Code Review Remediation — March 21, 2026

> Run this prompt in VS Code with CORTEX agent to fix all issues identified in the code review.
> Execute fixes in order — Critical first, then High, then Medium.

---

## Instructions

Apply the following fixes across the CORTEX codebase. For each fix:
1. Implement the change described
2. Run existing tests to confirm no regressions
3. Add or update tests where specified
4. Commit each fix category separately with conventional commit messages

---

## CRITICAL FIXES (3)

### FIX-001: Replace eval() in scaffolder_templates.py
**File:** `cortex/tools/scaffolder_templates.py` (lines 150-158)
**Problem:** `eval()` is used to evaluate template conditions. Even with safe_builtins and identifier allowlisting, this is exploitable if validation is bypassed.
**Action:** Replace the `eval()` call with `ast.literal_eval()` or implement a minimal safe expression parser using the `ast` module. Specifically:
- Parse the condition string into an AST using `ast.parse(condition, mode='eval')`
- Walk the AST and reject any node types beyond `Compare`, `BoolOp`, `Name`, `Constant`, `UnaryOp`
- Evaluate the safe AST manually instead of calling `eval()`
- Add a test in `tests/` that verifies malicious expressions like `__import__('os').system('whoami')` are rejected

### FIX-002: Remove silent exception swallowing in checkpoint_manager.py
**File:** `cortex/core/checkpoint_manager.py` (lines 441-442)
**Problem:** `except Exception: pass` silently swallows all errors. The comment says "Log error" but no logging exists.
**Action:**
- Replace `except Exception: pass` with proper error handling:
  ```python
  except Exception as e:
      logger.error("Failed to persist checkpoint %s: %s", checkpoint.id, e, exc_info=True)
      raise CheckpointPersistError(f"Checkpoint persistence failed: {e}") from e
  ```
- If `CheckpointPersistError` doesn't exist, create it in the appropriate exceptions module
- Ensure callers of `_persist_checkpoint` handle this exception gracefully

### FIX-003: Replace O(n) list operations in connection_pool.py
**File:** `cortex/infrastructure/connection_pool.py` (lines 169, 173, 239)
**Problem:** `list.remove()` is O(n) inside a retry loop, creating O(n²) behavior under concurrency.
**Action:**
- Replace `self._available_connections` (list) with `collections.deque`
- Use `popleft()` instead of filtering + `remove()` for acquiring connections
- Maintain a separate `set` of valid connection IDs for O(1) validity checks
- Keep the existing thread-safety mechanisms (locks) intact

---

## HIGH SEVERITY FIXES (4)

### FIX-004: Add exponential backoff to file_lock.py
**File:** `cortex/infrastructure/file_lock.py` (lines 117-162)
**Problem:** Busy-wait loop with flat 0.1s sleep wastes CPU and amplifies lock contention.
**Action:**
- Replace flat `time.sleep(self.check_interval)` with exponential backoff:
  ```python
  backoff = self.check_interval
  max_backoff = min(self.timeout / 4, 2.0)
  # Inside the loop, after failed acquire:
  time.sleep(backoff)
  backoff = min(backoff * 2, max_backoff)
  ```

### FIX-005: Add timeout protection to operation_lock.py
**File:** `cortex/infrastructure/collaboration/operation_lock.py` (lines 167-182)
**Problem:** `os.write()` and `os.ftruncate()` can block indefinitely on NFS/network drives.
**Action:**
- Wrap the file I/O operations with a timeout mechanism using `signal.alarm()` on Unix or a threading.Timer fallback
- Add a configurable `io_timeout` parameter (default 10 seconds)
- On timeout, close the file descriptor and raise a `FileLockIOTimeout` exception

### FIX-006: Remove shell=True from test_dashboard_server.py
**File:** `tests/tools/test_dashboard_server.py` (lines 25, 55, 64, 88)
**Problem:** `shell=True` with piped shell commands creates injection risk and establishes bad patterns.
**Action:**
- Replace shell commands with Python-native equivalents using `psutil`:
  ```python
  import psutil
  for proc in psutil.process_iter(['pid', 'connections']):
      for conn in (proc.info.get('connections') or []):
          if conn.laddr.port == 8080:
              proc.kill()
  ```
- If psutil is not available, use subprocess with list arguments instead of shell strings

### FIX-007: Fix file descriptor leak in file_lock.py release()
**File:** `cortex/infrastructure/file_lock.py` (lines 200-215)
**Problem:** If unlock fails, the file descriptor is never closed.
**Action:**
- Add a `finally` block to ensure the file handle is always closed:
  ```python
  def release(self) -> None:
      if self.lock_file is None:
          return
      try:
          # existing unlock logic
      finally:
          try:
              self.lock_file.close()
          except Exception:
              pass
          self.lock_file = None
  ```

---

## MEDIUM SEVERITY FIXES (8)

### FIX-008: Add thread lock to lens_cache.py singleton
**File:** `cortex/lens/cache/lens_cache.py` (lines 194-206)
**Problem:** Race condition — two threads can both create cache instances simultaneously.
**Action:**
- Add a module-level lock and use it around instance creation:
  ```python
  _lens_cache_lock = threading.Lock()

  def get_lens_cache(backend_type: str = "memory", **kwargs) -> 'LENSCache':
      global _lens_cache_instance
      if _lens_cache_instance is None:
          with _lens_cache_lock:
              if _lens_cache_instance is None:  # double-check
                  # create instance
      return _lens_cache_instance
  ```

### FIX-009: Validate Anthropic API response structure
**File:** `cortex/intelligence/llm/anthropic_provider.py` (lines 99-113)
**Problem:** No validation that `response.content` is non-empty or `response.usage` exists.
**Action:**
- Add validation before accessing response fields:
  ```python
  if not response.content:
      raise LLMResponseError("Empty response content from Anthropic API")
  content = response.content[0].text
  if response.usage is None:
      raise LLMResponseError("Missing usage data in Anthropic API response")
  ```

### FIX-010: Add json.JSONDecodeError handling
**Files:**
- `cortex/tools/scaffolder_audit_logger.py` (line 336)
- `cortex/tools/debug_orchestrator/__init__.py` (line 585)
- `cortex/tools/cortex_sync.py` (line 388)
- `cortex/core/orchestrator_dependency_registry.py` (line 567)
**Problem:** `json.loads()` on database content without error handling.
**Action:** Wrap each `json.loads()` call:
```python
try:
    details = json.loads(row[4])
except (json.JSONDecodeError, TypeError) as e:
    logger.warning("Corrupted JSON in record: %s", e)
    details = {}
```

### FIX-011: Add path traversal protection to template_engine.py
**File:** `cortex/core/template_engine.py` (line 176)
**Problem:** User-supplied filenames not validated against `..` or absolute paths.
**Action:**
```python
resolved = (self.template_dir / filename).resolve()
if not str(resolved).startswith(str(self.template_dir.resolve())):
    raise TemplateSecurityError(f"Path traversal detected: {filename}")
filepath = resolved
```

### FIX-012: Add URL parameter encoding in dashboard_server.py
**File:** `cortex/tools/dashboard_server.py` (lines 267, 462, 542)
**Problem:** `repo` parameter passed directly into URL without encoding.
**Action:** Use `urllib.parse.quote()` on the repo parameter before URL construction.

### FIX-013: Implement lazy cache loading in storage_cache.py
**File:** `cortex/infrastructure/storage/storage_cache.py` (lines 116-138)
**Problem:** Eagerly loads all cache files from disk on init.
**Action:**
- Switch to lazy loading: only load a cache entry when requested
- Add a max cache size with LRU eviction
- Add a startup parameter `max_l2_entries` (default 1000) to cap loaded files

### FIX-014: Add recursion depth limit to repository_scanner.py
**File:** `cortex/orchestrators/support/repository_scanner.py` (lines 107-119)
**Problem:** `rglob("*.py")` with no depth limit, plus 3 separate `ast.walk()` calls per file.
**Action:**
- Add a `max_depth` parameter (default 10)
- Combine the 3 `ast.walk()` calls into a single pass
- Precompile exclude patterns into a set for O(1) lookup

### FIX-015: Fix type hints in lens_cache.py
**File:** `cortex/lens/cache/lens_cache.py` (lines 131-174)
**Problem:** `generate_key()` uses `object` type hints instead of `Union[str, Path]`.
**Action:** Change type hints to `Union[str, Path]` and add runtime validation.

---

## VALIDATION

After all fixes are applied, run:
```bash
python3 scripts/run_tests.py preflight
python3 scripts/run_tests.py smoke
```

Ensure all tests pass. If any new exception types were created, verify they are properly exported from their modules.

---

## COMMIT STRATEGY

Create separate commits for each severity tier:
1. `fix(security): resolve critical eval, silent-except, and O(n²) pool issues`
2. `fix(reliability): add backoff, timeouts, fd-leak, and shell-injection fixes`
3. `fix(correctness): thread-safety, null-checks, json-error-handling, and path-traversal`
