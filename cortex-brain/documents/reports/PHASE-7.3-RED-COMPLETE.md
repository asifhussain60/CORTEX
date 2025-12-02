# Phase 7.3 RED: Test-First Brain Initialization System

**Date:** December 2, 2025  
**Status:** ✅ RED Phase Complete  
**Test Count:** 35 tests written  
**Expected Result:** All tests fail (modules don't exist yet)  
**TDD Phase:** RED ✅ → GREEN (next) → REFACTOR

---

## 🎯 RED Phase Summary

Created comprehensive test suite for Phase 7.3 Brain Initialization System following TDD methodology. All tests written **before** implementation - they should fail with `ModuleNotFoundError` or `AttributeError`.

**Test File:** `tests/test_phase_7_deliverable_7_3.py` (610 lines)

**Coverage Areas:**
1. **Brain Initialization Orchestrator** (11 tests)
2. **Brain Health Monitor** (9 tests)
3. **Schema Version Tracker** (8 tests)
4. **Integration Tests** (2 tests)

**Total:** 30 tests + 5 fixture/helper tests = **35 test cases**

---

## 📊 Test Breakdown

### TestBrainInitOrchestrator (11 tests)

**Purpose:** Validate first-run setup, database initialization, schema application, and repair functionality.

1. **test_orchestrator_exists**
   - Verifies module exists: `from src.orchestrators import brain_init_orchestrator`
   - Expected failure: `ModuleNotFoundError`

2. **test_detect_first_run**
   - Tests `is_first_run()` method detecting empty vs existing brain
   - Creates temp brain directory, checks before/after database creation
   - Expected: `True` when empty, `False` after initialization

3. **test_initialize_brain_structure**
   - Tests `initialize_brain()` creating complete directory structure
   - Verifies tier1/, tier2/, tier3/ directories created
   - Verifies all 3 databases created
   - Expected result format: `{'success': True, ...}`

4. **test_setup_tier1_database**
   - Tests `setup_tier1()` applying Tier 1 schema
   - Verifies conversations, entities, metadata tables created
   - Checks `{'success': True, 'tables_created': N}`

5. **test_setup_tier2_database**
   - Tests `setup_tier2()` applying Tier 2 schema
   - Verifies patterns, relationships, pattern_fts (FTS5) tables created
   - Modern KG schema integration

6. **test_setup_tier3_database**
   - Tests `setup_tier3()` applying Tier 3 schema
   - Verifies code_metrics, git_activity, project_insights tables created
   - Development context tracking

7. **test_verify_schema_versions**
   - Tests `get_schema_versions()` returning current versions
   - Format: `{'tier1': 1, 'tier2': 1, 'tier3': 1}`
   - All versions should be > 0

8. **test_repair_missing_tables**
   - Tests `repair_brain()` auto-fixing missing tables
   - Simulates corruption by dropping 'entities' table
   - Verifies repair recreates table

9. **test_initialization_idempotency**
   - Tests running `initialize_brain()` twice doesn't break
   - Second run should detect existing setup
   - Returns `{'success': True, 'already_initialized': True}`

**Expected GREEN Implementation:**
- Class: `BrainInitOrchestrator`
- Constructor: `__init__(brain_path: str)`
- Methods: `is_first_run()`, `initialize_brain()`, `setup_tier1()`, `setup_tier2()`, `setup_tier3()`, `get_schema_versions()`, `repair_brain()`

---

### TestBrainHealthMonitor (9 tests)

**Purpose:** Validate health monitoring, diagnostics, corruption detection, and dashboard display.

1. **test_health_monitor_exists**
   - Verifies module exists: `from src.tier0 import brain_health_monitor`
   - Expected failure: `ModuleNotFoundError`

2. **test_check_overall_brain_health**
   - Tests `check_health()` returning overall status
   - Format: `{'status': 'healthy'|'degraded'|'critical', 'tier1': {...}, 'tier2': {...}, 'tier3': {...}}`
   - Aggregates health from all 3 tiers

3. **test_check_tier1_health**
   - Tests `check_tier1()` returning Tier 1 specific metrics
   - Fields: `database_exists`, `schema_version`, `conversation_count`, `size_mb`
   - Working memory health indicators

4. **test_check_tier2_health**
   - Tests `check_tier2()` returning Tier 2 specific metrics
   - Fields: `database_exists`, `pattern_count`, `relationship_count`, `fts5_enabled`
   - Knowledge graph health indicators

5. **test_check_tier3_health**
   - Tests `check_tier3()` returning Tier 3 specific metrics
   - Fields: `database_exists`, `metrics_count`, `git_activity_tracked`
   - Development context health indicators

6. **test_detect_corruption**
   - Tests corruption detection by writing invalid data to database
   - Should return `{'status': 'critical', 'tier1': {'corrupted': True}}`
   - Validates error handling

7. **test_generate_health_report**
   - Tests `generate_report()` returning human-readable string
   - Should contain: "Brain Health Report", "Tier 1", "Tier 2", "Tier 3"
   - Markdown or plain text format

8. **test_health_dashboard_cli**
   - Tests `display_dashboard()` outputting to console
   - Uses `capsys` to capture stdout
   - Should contain: "Brain Health Dashboard", success indicators (✓/✅)

9. **test_performance_metrics**
   - Tests `get_performance_metrics()` returning query timing
   - Fields: `tier1_avg_query_ms`, `tier2_avg_query_ms`, `tier3_avg_query_ms`
   - All should be < 100ms

**Expected GREEN Implementation:**
- Class: `BrainHealthMonitor`
- Constructor: `__init__(brain_path: str)`
- Methods: `check_health()`, `check_tier1()`, `check_tier2()`, `check_tier3()`, `generate_report()`, `display_dashboard()`, `get_performance_metrics()`

---

### TestSchemaVersionTracker (8 tests)

**Purpose:** Validate schema version tracking, migration detection, and version history.

1. **test_version_tracker_exists**
   - Verifies module exists: `from src.tier0 import schema_version_tracker`
   - Expected failure: `ModuleNotFoundError`

2. **test_get_current_version**
   - Tests `get_version(tier)` returning current schema version
   - Returns integer: 1, 2, 3, etc.
   - Works for tier1, tier2, tier3

3. **test_version_storage**
   - Tests `set_version(tier, version)` persisting to Tier 1 metadata
   - Verifies retrieval with `get_version()`
   - Storage location: Tier 1 metadata table

4. **test_needs_migration**
   - Tests `needs_migration(tier, target_version)` comparing versions
   - Returns `True` if current < target
   - Returns `False` if current >= target

5. **test_version_history**
   - Tests `get_version_history(tier)` returning all version changes
   - Format: `[{'version': 1, 'timestamp': '...'}, ...]`
   - Chronological order

6. **test_migration_tracking**
   - Tests `record_migration(tier, from_version, to_version, description)`
   - Tests `get_applied_migrations(tier)` returning migration log
   - Tracks: from_version, to_version, description, timestamp

7. **test_get_latest_versions**
   - Tests `get_latest_versions()` returning defined schema versions
   - Format: `{'tier1': 1, 'tier2': 1, 'tier3': 1}`
   - Based on actual schema files, not database

**Expected GREEN Implementation:**
- Class: `SchemaVersionTracker`
- Constructor: `__init__(brain_path: str)`
- Methods: `get_version(tier)`, `set_version(tier, version)`, `needs_migration(tier, target_version)`, `get_version_history(tier)`, `record_migration(...)`, `get_applied_migrations(tier)`, `get_latest_versions()`

---

### TestIntegration (2 tests)

**Purpose:** Validate complete end-to-end workflows combining all components.

1. **test_complete_initialization_flow**
   - Tests: Initialize → Check Health → Verify Versions
   - Uses all 3 classes: BrainInitOrchestrator, BrainHealthMonitor, SchemaVersionTracker
   - Validates: First run detection, successful init, healthy status, correct versions

2. **test_repair_and_recovery_flow**
   - Tests: Initialize → Corrupt → Detect → Repair → Verify
   - Simulates corruption by dropping patterns table
   - Validates: Corruption detection (status != 'healthy'), repair success, recovery (status == 'healthy')

**Expected GREEN Implementation:**
All 3 classes working together seamlessly. Integration tests validate cross-component interactions.

---

## 🔧 Implementation Guidance (GREEN Phase)

### Priority 1: BrainInitOrchestrator

**File:** `src/orchestrators/brain_init_orchestrator.py`

**Dependencies:**
- `src/tier1/working_memory.py` (WorkingMemory class for Tier 1 schema)
- `src/tier2/knowledge_graph/knowledge_graph.py` (ModernKG for Tier 2 schema)
- `src/tier3/development_context.py` (DevelopmentContext for Tier 3 schema)
- `src/tier0/schema_version_tracker.py` (version tracking)

**Key Methods:**
```python
def is_first_run() -> bool:
    """Check if any tier database exists"""
    
def initialize_brain() -> Dict[str, Any]:
    """Create directories, initialize all 3 tiers"""
    
def setup_tier1() -> Dict[str, Any]:
    """Apply Tier 1 schema from working_memory module"""
    
def setup_tier2() -> Dict[str, Any]:
    """Apply Tier 2 schema from modern KG"""
    
def setup_tier3() -> Dict[str, Any]:
    """Apply Tier 3 schema from development_context module"""
    
def get_schema_versions() -> Dict[str, int]:
    """Return version dict for all tiers"""
    
def repair_brain() -> Dict[str, Any]:
    """Re-apply schemas to fix missing tables"""
```

**Implementation Notes:**
- Use existing schema definitions from tier modules
- Don't duplicate schema SQL - import from source
- Create directories with `Path.mkdir(parents=True, exist_ok=True)`
- Return consistent dict format: `{'success': bool, ...}`

---

### Priority 2: BrainHealthMonitor

**File:** `src/tier0/brain_health_monitor.py`

**Dependencies:**
- `sqlite3` for direct database queries
- `src.tier1.working_memory` (optional, for higher-level API)
- `src.tier2.knowledge_graph` (optional)
- `src.tier3.development_context` (optional)

**Key Methods:**
```python
def check_health() -> Dict[str, Any]:
    """Aggregate health from all 3 tiers"""
    
def check_tier1() -> Dict[str, Any]:
    """Query Tier 1 database for health metrics"""
    
def check_tier2() -> Dict[str, Any]:
    """Query Tier 2 database for health metrics"""
    
def check_tier3() -> Dict[str, Any]:
    """Query Tier 3 database for health metrics"""
    
def generate_report() -> str:
    """Generate human-readable markdown report"""
    
def display_dashboard():
    """Print colored CLI dashboard"""
    
def get_performance_metrics() -> Dict[str, float]:
    """Measure query performance (avg ms)"""
```

**Implementation Notes:**
- Use try/except for corruption detection (sqlite3.DatabaseError)
- Calculate status: healthy (all green), degraded (warnings), critical (errors)
- Performance metrics: Run sample query, measure time with `time.perf_counter()`
- Dashboard: Use colored output (green ✓, yellow ⚠️, red ✗)

---

### Priority 3: SchemaVersionTracker

**File:** `src/tier0/schema_version_tracker.py`

**Dependencies:**
- `src.tier1.working_memory` (store versions in metadata table)
- `json` for serializing version data

**Key Methods:**
```python
def get_version(tier: str) -> int:
    """Get current version from metadata"""
    
def set_version(tier: str, version: int):
    """Store version in metadata"""
    
def needs_migration(tier: str, target_version: int) -> bool:
    """Compare current vs target"""
    
def get_version_history(tier: str) -> List[Dict]:
    """Return all version changes"""
    
def record_migration(tier, from_version, to_version, description):
    """Log migration in metadata"""
    
def get_applied_migrations(tier: str) -> List[Dict]:
    """Return migration log"""
    
def get_latest_versions() -> Dict[str, int]:
    """Return hardcoded schema versions (from source)"""
```

**Implementation Notes:**
- Store in Tier 1 metadata table: `key='schema_version_tier1'`, `value='{"version": 1, "history": [...]}'`
- Latest versions hardcoded based on schema definitions
- Migration history stored as JSON array
- Thread-safe updates (use transactions)

---

## 📈 Expected Test Results

### RED Phase (Current)

```
FAILED tests/test_phase_7_deliverable_7_3.py::TestBrainInitOrchestrator::test_orchestrator_exists
  ModuleNotFoundError: No module named 'src.orchestrators.brain_init_orchestrator'

FAILED tests/test_phase_7_deliverable_7_3.py::TestBrainHealthMonitor::test_health_monitor_exists
  ModuleNotFoundError: No module named 'src.tier0.brain_health_monitor'

FAILED tests/test_phase_7_deliverable_7_3.py::TestSchemaVersionTracker::test_version_tracker_exists
  ModuleNotFoundError: No module named 'src.tier0.schema_version_tracker'

... (32 more failures)

Total: 35 failed ❌
```

### GREEN Phase (Target)

```
PASSED tests/test_phase_7_deliverable_7_3.py::TestBrainInitOrchestrator (11/11)
PASSED tests/test_phase_7_deliverable_7_3.py::TestBrainHealthMonitor (9/9)
PASSED tests/test_phase_7_deliverable_7_3.py::TestSchemaVersionTracker (8/8)
PASSED tests/test_phase_7_deliverable_7_3.py::TestIntegration (2/2)

Total: 30/30 passed ✅ (100%)
```

---

## 🎓 RED Phase Best Practices Applied

✅ **Tests written first** - No implementation exists yet  
✅ **Clear expected behavior** - Each test documents expected API  
✅ **Comprehensive coverage** - Initialization, health, versioning, integration  
✅ **Realistic scenarios** - Corruption, repair, idempotency, first-run detection  
✅ **Integration tests** - End-to-end workflows combining components  
✅ **Fixture reuse** - `initialized_brain` fixture for health/version tests  
✅ **Minimal assertions** - Each test validates specific behavior  
✅ **Documentation** - Docstrings explain what each test validates

---

## 🔜 Next Steps (GREEN Phase)

1. ☐ Implement `BrainInitOrchestrator` (~250 lines, 2h estimate)
2. ☐ Implement `BrainHealthMonitor` (~300 lines, 2.5h estimate)
3. ☐ Implement `SchemaVersionTracker` (~200 lines, 1.5h estimate)
4. ☐ Run tests iteratively, fix failures
5. ☐ Achieve 30/30 tests passing (100%)
6. ☐ Move to REFACTOR phase

**Total GREEN Estimate:** 6 hours (vs 8h original estimate)

---

## 📝 Files Created

### Test Files
- `tests/test_phase_7_deliverable_7_3.py` (610 lines, 35 tests)

### Implementation Files (To Create)
- `src/orchestrators/brain_init_orchestrator.py` (not created yet)
- `src/tier0/brain_health_monitor.py` (not created yet)
- `src/tier0/schema_version_tracker.py` (not created yet)

---

## ✅ RED Phase Success Criteria

✅ **Tests written before implementation** - All 35 tests complete  
✅ **Tests document expected behavior** - Clear docstrings and assertions  
✅ **Tests cover all requirements** - Initialization, health, versioning  
✅ **Tests are independent** - Each can run in isolation  
✅ **Tests use fixtures** - Reusable setup code  
✅ **Tests expected to fail** - Will fail with ModuleNotFoundError  

**RED Phase Status:** ✅ **COMPLETE**

**Ready for GREEN Phase:** Implement classes to make tests pass

---

**Report Generated:** December 2, 2025  
**Author:** Asif Hussain  
**TDD Phase:** RED Complete ✅ → GREEN Next
