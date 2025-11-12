# TEST SUITE OPTIMIZATION PLAN

**Created:** 2025-11-11  
**Priority:** 🔴 **HIGH PRIORITY** (User-Blocking Issue)  
**Status:** Planning Phase  
**Estimated Effort:** 16-20 hours  
**Target:** Reduce test execution from 6m 40s to <30s (unit tests)

---

## 🚨 Problem Statement

**Current State:**
- **Total Tests:** 2,088 tests (1,769 passing, 205 failing, 124 errors)
- **Execution Time:** 400.99 seconds (6 minutes 40 seconds)
- **Pass Rate:** 85% (target: 100%)
- **User Impact:** Tests run on every change, becoming development bottleneck

**Root Causes:**
1. **No Parallelization** - Tests run sequentially
2. **Real I/O Operations** - Actual file/database operations instead of mocking
3. **Obsolete Tests** - 50+ tests testing changed APIs
4. **Schema Drift** - Database schema changed, tests not updated
5. **Missing Dependencies** - scikit-learn marked required but is optional
6. **Windows File Locks** - Temp databases not properly closed

---

## 📊 Failure Analysis

### Category Breakdown

| Category | Count | Root Cause | Action Priority |
|----------|-------|------------|----------------|
| **YAML Loading** | 13 failures | Tests expect old YAML structure | HIGH - Update/Delete |
| **Entity Extractor** | 8 failures + 8 errors | Database schema changed | HIGH - Recreate |
| **FIFO Queue** | 5 failures | API signature changed | MEDIUM - Update |
| **Messages** | 7 failures + 7 errors | Column `timestamp` removed | HIGH - Fix schema |
| **Vision API** | 4 failures | Mock implementation incomplete | LOW - Enhancement |
| **ML Optimizer** | 17 errors | Missing `scikit-learn` | HIGH - Mark optional |
| **Agent Tests** | 12 errors | Constructor signature changed | HIGH - Update calls |
| **Tier3 Metrics** | 20+ errors | Wrong constructor arguments | MEDIUM - Fix init |
| **SKULL Tests** | 8 failures | Detection logic incomplete | MEDIUM - Enhance |
| **Workflow Engine** | 12 failures | Status enum issues | MEDIUM - Fix logic |
| **Plugin Tests** | 13 errors | Import path changes | HIGH - Fix imports |

### Slowest Tests (Top 20)

```
cortex-operations.yaml load: 0.197s (exceeds 100ms target)
brain-protection-rules.yaml: 0.125s (exceeds 100ms target)
Database connection: 121ms (target: <10ms)
Full optimization workflow: ~2s per test
Multi-day analysis: ~3s per test
```

---

## 🎯 Optimization Strategy

### Phase 1: Quick Fixes (2-3 hours)
**Goal:** Get to 90%+ pass rate fast

**Tasks:**
1. **Fix Import Paths** (30 min)
   - Fix relative imports in plugin tests
   - Update module import paths
   
2. **Mark Optional Dependencies** (30 min)
   - Add `@pytest.mark.skipif(not HAS_SKLEARN)` to ML tests
   - Create `HAS_SKLEARN` flag in conftest.py
   
3. **Fix Schema Issues** (1 hour)
   - Update `messages` table schema tests
   - Fix `entities` table constraint tests
   - Update FIFO queue API calls
   
4. **Fix Constructor Signatures** (1 hour)
   - Update Agent test instantiation
   - Fix Tier3 Metrics constructor calls
   - Update BaseOperationModule calls

**Expected Outcome:** 90%+ pass rate, still slow but working

---

### Phase 2: Parallel Execution (1 hour)
**Goal:** 50% time reduction via parallelization

**Tasks:**
1. **Install pytest-xdist** (5 min)
   ```bash
   pip install pytest-xdist
   ```

2. **Configure pytest.ini** (15 min)
   ```ini
   [pytest]
   addopts = 
       -n auto              # Parallel execution (auto-detect CPUs)
       --durations=10       # Show 10 slowest tests
       --strict-markers
       --tb=short
       -v
   
   markers =
       slow: marks tests as slow (deselect with '-m "not slow"')
       integration: marks tests as integration tests
       unit: marks tests as unit tests (fast)
       requires_sklearn: marks tests requiring scikit-learn
       windows_only: marks Windows-specific tests
   ```

3. **Mark Slow Tests** (40 min)
   - Tag integration tests with `@pytest.mark.slow`
   - Tag unit tests with `@pytest.mark.unit`
   - Tag ML tests with `@pytest.mark.requires_sklearn`

**Expected Outcome:** 3-4 minutes total execution (parallel)

---

### Phase 3: Mock Heavy I/O (3-4 hours)
**Goal:** 70% time reduction for unit tests

**Tasks:**
1. **Database Mocking** (1.5 hours)
   - Create `@pytest.fixture` for in-memory SQLite
   - Mock database connections in tests
   - Use `unittest.mock.patch` for heavy queries
   
   ```python
   @pytest.fixture
   def mock_db(tmp_path):
       db_path = tmp_path / "test.db"
       conn = sqlite3.connect(":memory:")
       yield conn
       conn.close()
   ```

2. **File System Mocking** (1 hour)
   - Use `pytest.tmp_path` for temporary files
   - Mock file I/O operations
   - Clean up temp files properly (Windows fix)
   
   ```python
   @pytest.fixture
   def temp_workspace(tmp_path):
       workspace = tmp_path / "cortex"
       workspace.mkdir()
       yield workspace
       # Windows: Force cleanup
       import shutil
       shutil.rmtree(workspace, ignore_errors=True)
   ```

3. **YAML Loading Optimization** (30 min)
   - Cache parsed YAML in conftest.py
   - Load once, reuse across tests
   
   ```python
   @pytest.fixture(scope="session")
   def cached_yaml():
       return yaml.safe_load(Path("cortex-operations.yaml").read_text())
   ```

4. **Git Operations Mocking** (1 hour)
   - Mock `subprocess.run` for git commands
   - Use fixture for fake git repo
   - Avoid actual git operations in tests

**Expected Outcome:** Unit tests <10 seconds

---

### Phase 4: Delete Obsolete Tests (2-3 hours)
**Goal:** Remove tests that no longer apply

**Files to Review & Clean:**

1. **tests/test_yaml_conversion.py** (1 hour)
   - Delete tests for old YAML structure
   - Update or remove slash command tests
   - Fix operations config structure tests
   
2. **tests/tier1/entities/** (45 min)
   - Recreate schema-dependent tests
   - Update entity extractor API calls
   
3. **tests/tier1/fifo/** (30 min)
   - Update queue manager API
   - Fix status return structure
   
4. **tests/tier1/messages/** (30 min)
   - Fix message schema tests
   - Update timestamp handling
   
5. **tests/plugins/test_command_expansion.py** (15 min)
   - Fix import paths or delete if feature removed

**Expected Outcome:** 100% pass rate on remaining tests

---

### Phase 5: Test Organization (2 hours)
**Goal:** Clear separation of fast vs slow tests

**Directory Structure:**
```
tests/
├── unit/                    # Fast tests (<100ms each)
│   ├── tier0/
│   ├── tier1/
│   ├── tier2/
│   └── tier3/
├── integration/             # Slower tests (100ms-1s)
│   ├── operations/
│   ├── workflows/
│   └── agents/
├── e2e/                     # End-to-end tests (1s+)
│   └── full_workflows/
└── fixtures/                # Shared test data
    └── mock_data.py
```

**Tasks:**
1. Move integration tests to `tests/integration/`
2. Move unit tests to `tests/unit/`
3. Update `pytest.ini` paths
4. Create `conftest.py` hierarchy

**Expected Outcome:** Clear test organization, easy to run subset

---

### Phase 6: Continuous Optimization (Ongoing)
**Goal:** Maintain fast tests going forward

**Practices:**
1. **New Test Guidelines:**
   - Unit tests MUST use mocking
   - Integration tests marked `@pytest.mark.integration`
   - E2E tests marked `@pytest.mark.slow`
   - Max unit test time: 100ms

2. **Pre-Commit Hook:**
   ```bash
   # Run only unit tests pre-commit
   pytest -m "unit" --maxfail=1
   ```

3. **CI Pipeline:**
   ```yaml
   # Fast feedback (unit tests)
   - name: Unit Tests
     run: pytest -m "unit" -n auto
   
   # Comprehensive (all tests)
   - name: Full Test Suite
     run: pytest -n auto
     if: github.event_name == 'pull_request'
   ```

4. **Test Metrics Dashboard:**
   - Track test execution time over time
   - Alert on tests exceeding time budget
   - Report coverage per module

---

## 📋 Implementation Checklist

### Phase 1: Quick Fixes (High Priority)
- [ ] Fix plugin import paths
- [ ] Mark scikit-learn as optional dependency
- [ ] Fix messages table schema tests
- [ ] Fix entities table constraint tests
- [ ] Update FIFO queue API calls
- [ ] Update Agent constructor calls
- [ ] Fix Tier3 Metrics initialization
- [ ] Update BaseOperationModule calls

### Phase 2: Parallel Execution (High Priority)
- [ ] Install pytest-xdist
- [ ] Update pytest.ini configuration
- [ ] Mark slow tests with decorators
- [ ] Mark integration tests
- [ ] Mark optional dependency tests
- [ ] Verify parallel execution works

### Phase 3: Mock Heavy I/O (Medium Priority)
- [ ] Create in-memory database fixture
- [ ] Mock database connections
- [ ] Add temp_workspace fixture
- [ ] Fix Windows file cleanup
- [ ] Cache YAML loading
- [ ] Mock git operations

### Phase 4: Delete Obsolete Tests (Medium Priority)
- [ ] Review and update test_yaml_conversion.py
- [ ] Recreate entity extractor tests
- [ ] Update FIFO queue tests
- [ ] Update message store tests
- [ ] Fix or remove command expansion tests

### Phase 5: Test Organization (Low Priority)
- [ ] Create unit/integration/e2e directories
- [ ] Move tests to appropriate directories
- [ ] Update pytest.ini paths
- [ ] Create conftest.py hierarchy
- [ ] Update CI configuration

### Phase 6: Continuous Optimization (Ongoing)
- [ ] Document new test guidelines
- [ ] Add pre-commit hook
- [ ] Update CI pipeline
- [ ] Create test metrics dashboard

---

## 🎯 Success Metrics

**Targets:**

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| **Pass Rate** | 85% | 100% | Phase 1 (Day 1) |
| **Total Execution** | 6m 40s | 2m 0s | Phase 2 (Day 1) |
| **Unit Tests** | N/A | <30s | Phase 3 (Day 2) |
| **Integration Tests** | N/A | <1m | Phase 3 (Day 2) |
| **Test Organization** | Mixed | Separated | Phase 5 (Day 3) |

**Key Performance Indicators:**
- ✅ All tests pass (100%)
- ✅ Unit tests run in <30 seconds
- ✅ Full suite runs in <2 minutes
- ✅ Parallel execution working
- ✅ No Windows file lock issues
- ✅ Optional dependencies handled correctly

---

## 🔧 Technical Details

### pytest-xdist Configuration

```ini
# pytest.ini
[pytest]
addopts = 
    -n auto                          # Auto-detect CPU count
    --dist loadscope                 # Distribute by module
    --durations=10
    --strict-markers
    --tb=short
    -v

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests (fast)
    requires_sklearn: marks tests requiring scikit-learn
    windows_only: marks Windows-specific tests
    linux_only: marks Linux-specific tests
    mac_only: marks macOS-specific tests
```

### Fixture Examples

```python
# conftest.py

import pytest
import sqlite3
from pathlib import Path
import yaml

# Session-scoped (loaded once)
@pytest.fixture(scope="session")
def cached_operations_yaml():
    """Load operations YAML once for all tests"""
    path = Path("cortex-operations.yaml")
    return yaml.safe_load(path.read_text())

@pytest.fixture(scope="session")
def cached_brain_protection_yaml():
    """Load brain protection rules once"""
    path = Path("cortex-brain/brain-protection-rules.yaml")
    return yaml.safe_load(path.read_text())

# Function-scoped (per test)
@pytest.fixture
def mock_db():
    """In-memory SQLite database"""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

@pytest.fixture
def temp_workspace(tmp_path):
    """Temporary workspace directory"""
    workspace = tmp_path / "cortex"
    workspace.mkdir()
    yield workspace
    # Windows-safe cleanup
    import shutil
    try:
        shutil.rmtree(workspace)
    except PermissionError:
        pass  # Best effort cleanup

# Skip conditionals
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_sklearn: mark test as requiring scikit-learn"
    )

def pytest_collection_modifyitems(config, items):
    """Auto-skip tests based on missing dependencies"""
    try:
        import sklearn
        HAS_SKLEARN = True
    except ImportError:
        HAS_SKLEARN = False
    
    if not HAS_SKLEARN:
        skip_sklearn = pytest.mark.skip(reason="scikit-learn not installed")
        for item in items:
            if "requires_sklearn" in item.keywords:
                item.add_marker(skip_sklearn)
```

### Mock Examples

```python
# tests/unit/tier1/test_messages.py

import pytest
from unittest.mock import Mock, patch
from src.tier1.messages import MessageStore

@pytest.fixture
def mock_message_store(mock_db):
    """Mocked message store with in-memory DB"""
    return MessageStore(db_path=":memory:")

def test_add_message_fast(mock_message_store):
    """Fast test using mocked database"""
    # This should complete in <10ms
    msg = mock_message_store.add_message(
        conversation_id="test",
        role="user",
        content="Hello"
    )
    assert msg.content == "Hello"

@patch('subprocess.run')
def test_git_operations_mocked(mock_run):
    """Mock git operations to avoid real subprocess calls"""
    mock_run.return_value = Mock(stdout="commit abc123", returncode=0)
    
    # Test code that calls git
    result = run_git_command("status")
    
    assert "abc123" in result
    mock_run.assert_called_once()
```

---

## 📅 Timeline

**Day 1 (4-5 hours):**
- Phase 1: Quick Fixes (2-3 hours)
- Phase 2: Parallel Execution (1 hour)
- **Goal:** 90%+ pass rate, 2-minute execution

**Day 2 (4-5 hours):**
- Phase 3: Mock Heavy I/O (3-4 hours)
- Phase 4 (partial): Delete obvious obsolete tests (1 hour)
- **Goal:** 100% pass rate, <1 minute for unit tests

**Day 3 (4-5 hours):**
- Phase 4 (complete): Clean up remaining obsolete tests
- Phase 5: Test Organization (2 hours)
- **Goal:** Clean test structure, documented process

**Ongoing:**
- Phase 6: Continuous Optimization
- Monitor test metrics
- Enforce guidelines

---

## 🚦 Approval & Next Steps

**Requires Approval:**
- [ ] User confirms plan approach
- [ ] User approves deleting obsolete tests
- [ ] User approves test reorganization

**Ready to Execute:**
Once approved, execute phases in order:
1. Phase 1 → Immediate pass rate improvement
2. Phase 2 → Immediate speed improvement
3. Phase 3 → Major speed improvement for unit tests
4. Phase 4 → Clean up technical debt
5. Phase 5 → Long-term maintainability

**Communication:**
- Progress updates after each phase
- Test metrics before/after comparison
- Documentation of deleted tests (for audit)

---

## 📚 References

**Related Documents:**
- `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` - Overall project status
- `cortex-brain/brain-protection-rules.yaml` - SKULL-007 test requirements
- `pytest.ini` - Current pytest configuration
- `.github/copilot-instructions.md` - Development guidelines

**External Resources:**
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Author:** CORTEX Design Sync  
**Last Updated:** 2025-11-11  
**Status:** 🔴 HIGH PRIORITY - Awaiting User Approval
