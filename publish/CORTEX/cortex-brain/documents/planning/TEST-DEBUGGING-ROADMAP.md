# CORTEX 3.0 Phase B Milestone 1: Test Debugging Roadmap

**Purpose:** Systematic plan to fix remaining test failures in conversation import suite  
**Session:** Next session (estimated 1-2 hours)  
**Goal:** 10/10 tests passing ✅

---

## 🎯 Current Status

**Test Results:** 8 failed, 2 errors (out of 10 total)

**Root Causes Identified:**
1. API method naming mismatch (`create_session` vs `detect_or_create_session`)
2. ConversationManager initialization issues in test fixtures
3. Schema alignment between test database and production database

---

## 🔍 Systematic Debugging Plan

### Step 1: Verify Test Database Schema (10 minutes)

**Goal:** Confirm test fixtures create the same schema as production

**Actions:**
```python
# In test fixture, after wm = WorkingMemory(db_path):
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check conversations table schema
cursor.execute("PRAGMA table_info(conversations)")
columns = cursor.fetchall()
print("Conversations columns:", columns)

# Verify new columns exist
expected = ['conversation_type', 'import_source', 'quality_score', 'semantic_elements']
actual_columns = [col[1] for col in columns]
for expected_col in expected:
    assert expected_col in actual_columns, f"Missing column: {expected_col}"
```

**Expected Outcome:** All 4 new columns present in test database

---

### Step 2: Fix Session Manager API Usage (15 minutes)

**Problem:** Tests use `create_session()` but API is `detect_or_create_session()`

**Solution:** Already partially fixed in `working_memory.py`, verify tests updated

**Files to Check:**
- `tests/tier1/test_conversation_import.py::test_import_links_to_existing_session`
- Any other test using `session_manager.create_session()`

**Fix Pattern:**
```python
# OLD (incorrect)
session_id = temp_db.session_manager.create_session(workspace_path)

# NEW (correct)
session = temp_db.session_manager.detect_or_create_session(workspace_path)
session_id = session.session_id
```

---

### Step 3: Verify ConversationManager Initialization (15 minutes)

**Problem:** `AttributeError: 'ConversationManager' object has no attribute 'create_conversation'`

**Hypothesis:** Test fixture may not be initializing WorkingMemory correctly

**Debug Steps:**
```python
def test_debug_conversation_manager(temp_db):
    """Debug test to verify ConversationManager."""
    print("WorkingMemory type:", type(temp_db))
    print("Has conversation_manager:", hasattr(temp_db, 'conversation_manager'))
    print("ConversationManager type:", type(temp_db.conversation_manager))
    print("Has create_conversation:", hasattr(temp_db.conversation_manager, 'create_conversation'))
    
    # List all methods
    methods = [m for m in dir(temp_db.conversation_manager) if not m.startswith('_')]
    print("Available methods:", methods)
```

**Expected:** `create_conversation` should be in methods list

---

### Step 4: Check Database Path Consistency (10 minutes)

**Problem:** WorkingMemory may be using different database than migration

**Debug:**
```python
def test_verify_migration_applied(temp_db):
    """Verify migration was applied to test database."""
    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT conversation_type, import_source FROM conversations LIMIT 1")
    # Should not raise error if columns exist
```

**If Error:** Migration not applied to test database

**Solution:** Run migration in test fixture setup:
```python
@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_import.db"
    wm = WorkingMemory(db_path)
    
    # Apply migration
    from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
    migrate_add_conversation_import(str(db_path))
    
    yield wm
```

---

### Step 5: Fix Context Parameter Format (15 minutes)

**Problem:** `create_conversation()` expects context as dict, may need specific format

**Check:**
```python
# In working_memory.py import_conversation()
conversation_id = self.conversation_manager.create_conversation(
    agent_id="manual_import",
    goal=f"Imported from {Path(import_source).name}",
    context={
        'conversation_type': 'imported',
        'import_source': import_source,
        'import_date': import_date.isoformat(),
        # ... more fields
    }
)
```

**Verify:** Context dict is JSON-serializable (no datetime objects, only strings/ints/bools)

---

### Step 6: Run Tests Individually (20 minutes)

**Strategy:** Run one test at a time to isolate issues

**Commands:**
```bash
# Test 1: Basic import (most fundamental)
pytest tests/tier1/test_conversation_import.py::TestConversationImport::test_import_basic_conversation -v -s

# Test 2: Quality detection
pytest tests/tier1/test_conversation_import.py::TestConversationImport::test_import_high_quality_conversation -v -s

# Test 3: Metadata storage
pytest tests/tier1/test_conversation_import.py::TestConversationImport::test_import_stores_quality_metadata -v -s

# Continue with remaining tests...
```

**Log:** Document which tests pass vs fail after each fix

---

### Step 7: Update Test Fixtures If Needed (15 minutes)

**If:** Tests still fail after API fixes

**Then:** Update fixture to match production initialization:

```python
@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database matching production setup."""
    db_path = tmp_path / "test_import.db"
    
    # Initialize WorkingMemory (creates base schema)
    wm = WorkingMemory(db_path)
    
    # Apply conversation import migration
    from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
    success = migrate_add_conversation_import(str(db_path))
    
    if not success:
        pytest.fail("Migration failed in test setup")
    
    # Verify migration applied
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    required_columns = ['conversation_type', 'import_source', 'quality_score', 'semantic_elements']
    for col in required_columns:
        assert col in columns, f"Migration incomplete: missing {col}"
    
    yield wm
    # Cleanup handled by tmp_path
```

---

### Step 8: Validate Session Linking (10 minutes)

**Test:** `test_import_links_to_existing_session`

**Check:**
1. Session creation works: `detect_or_create_session()`
2. Session ID returned correctly
3. Import links to that session
4. Database has correct session_id in conversations table

---

### Step 9: Test Quality Scoring Integration (10 minutes)

**Verify:**
- ConversationQualityAnalyzer imported correctly
- Quality scores calculated correctly
- semantic_elements JSON serialization works
- Database stores quality_score as INTEGER

---

### Step 10: Final Validation (10 minutes)

**Run Full Suite:**
```bash
pytest tests/tier1/test_conversation_import.py -v
```

**Expected:** 10/10 tests passing ✅

---

## 📋 Debugging Checklist

- [ ] Test database has all 4 new columns
- [ ] Migration applied in test fixtures
- [ ] SessionManager API usage correct (`detect_or_create_session`)
- [ ] ConversationManager has `create_conversation` method
- [ ] Context dict is JSON-serializable
- [ ] All datetime objects converted to ISO strings
- [ ] Session linking works correctly
- [ ] Quality scoring calculates correctly
- [ ] Database queries succeed
- [ ] All 10 tests pass

---

## 🎯 Success Criteria

**Must Achieve:**
- ✅ 10/10 tests passing
- ✅ No errors, no failures
- ✅ Quality scores accurate (EXCELLENT for planning, LOW for simple)
- ✅ Session linking verified
- ✅ Metadata stored correctly

**Validation Command:**
```bash
pytest tests/tier1/test_conversation_import.py -v --tb=short
```

---

## 🚀 Post-Debugging: Next Steps

**Once Tests Pass:**

1. **Vault Storage (1-2 hours)**
   - Create `cortex-brain/conversation-vault/` directory
   - Implement index metadata file
   - Add file naming convention
   - Test storage workflow

2. **Documentation (1 hour)**
   - CopilotChats.md export guide
   - Import tutorial
   - Quality scoring examples

3. **E2E Validation (1 hour)**
   - Export real conversation
   - Import and verify
   - Test narrative generation

**Total Remaining:** 3-4 hours to Milestone 1 completion

---

## 💡 Tips for Next Session

1. **Start with simplest test** - `test_import_empty_conversation`
2. **Use -s flag** - See print statements for debugging
3. **Use --pdb** - Drop into debugger on failure
4. **Run individually** - Isolate failures
5. **Check database directly** - Use sqlite3 CLI to inspect

**Quick Debug Command:**
```bash
# Run one test with full output and debugger
pytest tests/tier1/test_conversation_import.py::TestConversationImport::test_import_basic_conversation -v -s --pdb
```

---

**Estimated Debug Time:** 1-2 hours  
**Confidence Level:** High (root causes identified, fixes are straightforward)

---

*Roadmap Created: 2025-11-13*  
*Ready for Next Session*
