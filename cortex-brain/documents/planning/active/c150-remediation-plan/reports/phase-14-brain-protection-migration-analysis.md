# Phase 14: Brain Protection Rules Migration - Analysis

**Date:** January 4, 2026  
**Plan:** C150 Remediation Plan  
**Status:** 🔄 IN PROGRESS

## Executive Summary

**Requirement:** Complete YAML→SQLite migration for brain-protection-rules.yaml

**Current Status:**
- ✅ SQLite schema exists (`cortex-brain/tier0/governance-schema.sql`)
- ✅ Database populated with 83 rules (13 protection layers)
- ⚠️ Middleware still using YAML file (not database)
- ⚠️ YAML file has parsing errors (line 261)
- ⚠️ No database access layer implemented

**Time:** 4 hours estimated

## Current State Analysis

### 1. Database Status

**Location:** `cortex-brain/tier0/governance.db`

**Tables:**
- `schema_version` - Version tracking
- `protection_layers` - 13 layers populated
- `governance_rules` - 83 rules populated
- `rule_detection` - Detection patterns
- `rule_test_requirements` - Test requirements
- `rule_alternatives` - Alternative patterns
- `rule_documentation` - Documentation
- `tier0_instincts` - Core instincts
- `critical_paths` - Critical file paths
- `application_paths` - Application paths
- `brain_state_files` - Brain state tracking
- `rule_violations` - Violation history
- `rule_usage_stats` - Usage statistics
- `governance_metadata` - Metadata

**Status:** ✅ Schema complete, ✅ Data populated

### 2. YAML File Status

**Location:** `cortex-brain/brain-protection-rules.yaml`

**Issues:**
- ❌ YAML parsing error at line 261
- ⚠️ File still being used by middleware
- ⚠️ May be out of sync with database (83 vs unknown count)

**Structure:**
```yaml
schema_version: "5.0"
categories: [...]
---
- rule_id: SETUP_VERIFICATION
  category: orchestration_lifecycle
  severity: blocked
  ...
```

### 3. Middleware Status

**File:** `src/orchestrators/middleware/governance_checkpoint.py`

**Current Implementation:**
```python
self.rules_path = self.workspace_path / "cortex-brain" / "brain-protection-rules.yaml"

def _load_rules(self):
    """Load SKULL rules from brain-protection-rules.yaml"""
    # Loads from YAML file
```

**Issues:**
- ❌ Still reading YAML file
- ❌ No SQLite integration
- ❌ No database access layer
- ❌ YAML parsing will fail (line 261 error)

### 4. Integration Points

**Files Using Brain Protection Rules:**

1. **governance_checkpoint.py** (PRIMARY)
   - Lines 108, 118
   - Loads rules from YAML
   - Used by all orchestrators

2. **planning/governance_integrator.py**
   - Uses governance_checkpoint
   - Indirect YAML dependency

3. **Other orchestrators**
   - Use governance_checkpoint for SKULL rule validation
   - Indirect YAML dependency

## Gap Analysis

### Gap 1: No Database Access Layer
**Status:** ❌ MISSING

**Required:**
- `GovernanceDB` class with CRUD operations
- Query methods for rules, layers, violations
- Connection pooling
- Error handling

**Location:** `src/database/governance_db.py` (needs creation)

### Gap 2: Middleware Not Using Database
**Status:** ❌ MISSING

**Required:**
- Update `governance_checkpoint.py` to use `GovernanceDB`
- Remove YAML file loading
- Update rule validation logic
- Test all checkpoint methods

### Gap 3: YAML File Parsing Error
**Status:** ❌ BROKEN

**Issue:** Line 261 parsing error prevents YAML loading

**Impact:** Current middleware WILL FAIL if YAML is still in use

**Options:**
1. Fix YAML (but we're migrating away)
2. Remove YAML dependency first (recommended)

### Gap 4: Migration Validation
**Status:** ❌ MISSING

**Required:**
- Verify all 83 DB rules are valid
- Check for missing rules from YAML
- Validate rule integrity
- Test performance (YAML vs SQLite)

## Implementation Plan

### Task 1: Create Database Access Layer (1 hour)

**File:** `src/database/governance_db.py`

**Methods:**
```python
class GovernanceDB:
    def __init__(self, db_path: str):
        """Initialize connection to governance.db"""
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get rule by ID"""
    
    def get_rules_by_severity(self, severity: str) -> List[Dict]:
        """Get all rules by severity level"""
    
    def get_rules_by_layer(self, layer_id: str) -> List[Dict]:
        """Get all rules in a protection layer"""
    
    def get_all_rules(self) -> List[Dict]:
        """Get all governance rules"""
    
    def log_violation(self, violation: Dict) -> int:
        """Log a rule violation"""
    
    def get_violations(self, rule_id: Optional[str] = None) -> List[Dict]:
        """Get violation history"""
    
    def update_rule_stats(self, rule_id: str, validated: bool):
        """Update rule usage statistics"""
```

### Task 2: Update Governance Checkpoint Middleware (1.5 hours)

**File:** `src/orchestrators/middleware/governance_checkpoint.py`

**Changes:**
```python
# OLD:
self.rules_path = self.workspace_path / "cortex-brain" / "brain-protection-rules.yaml"

def _load_rules(self):
    """Load SKULL rules from brain-protection-rules.yaml"""
    with open(self.rules_path) as f:
        docs = yaml.safe_load_all(f)
        ...

# NEW:
from src.database.governance_db import GovernanceDB

self.governance_db = GovernanceDB(
    db_path=str(self.workspace_path / "cortex-brain" / "tier0" / "governance.db")
)

def _load_rules(self):
    """Load SKULL rules from governance.db"""
    return self.governance_db.get_all_rules()
```

**Additional Changes:**
- Update `_validate_rule()` to work with DB rule format
- Update `_log_checkpoint()` to use DB logging
- Add rule statistics tracking
- Remove YAML dependencies

### Task 3: Create Migration Validation Script (0.5 hours)

**File:** `scripts/validate_governance_migration.py`

**Purpose:**
- Compare YAML rules (if parseable) with DB rules
- Validate DB schema integrity
- Test all CRUD operations
- Performance benchmark (YAML vs SQLite)

**Output:**
- Migration validation report
- Performance comparison
- Missing/extra rules list

### Task 4: Update Planning Orchestrator Integration (0.5 hours)

**File:** `src/orchestrators/planning/governance_integrator.py`

**Changes:**
- Verify compatibility with new database backend
- Test SKULL rule validation
- Update any direct YAML references

### Task 5: Integration Testing (0.5 hours)

**Tests:**
1. Checkpoint phase start with DB rules
2. Checkpoint operation with DB rules
3. Checkpoint phase complete with DB rules
4. Violation logging to database
5. Rule statistics updates
6. Performance comparison

## Database Schema Review

### Key Tables for Middleware

#### 1. governance_rules
```sql
CREATE TABLE governance_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('blocked', 'warning', 'info')),
    description TEXT NOT NULL,
    layer_id TEXT NOT NULL,
    minimum_coverage INTEGER DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns Needed:**
- `rule_id` - Unique identifier (SETUP_VERIFICATION, TDD_ENFORCEMENT, etc.)
- `name` - Human-readable name
- `severity` - blocked/warning/info
- `description` - Rule description
- `enabled` - Active/inactive flag

#### 2. rule_violations
```sql
CREATE TABLE rule_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    orchestrator TEXT NOT NULL,
    phase INTEGER,
    operation TEXT,
    severity TEXT NOT NULL,
    context_json TEXT,
    recommendation TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Use Case:** Log all violations during checkpoints

#### 3. rule_usage_stats
```sql
CREATE TABLE rule_usage_stats (
    rule_id TEXT PRIMARY KEY,
    total_validations INTEGER DEFAULT 0,
    total_violations INTEGER DEFAULT 0,
    last_validated TIMESTAMP,
    last_violated TIMESTAMP
);
```

**Use Case:** Track rule effectiveness and usage

## Migration Benefits

### 1. Performance

**YAML Loading:**
- Parses entire file every time
- Multi-document YAML parsing
- ~100-200ms per load

**SQLite:**
- Indexed queries
- Selective loading (only needed rules)
- ~1-5ms per query

**Improvement:** 20-200x faster

### 2. Scalability

**YAML:**
- Linear growth with rule count
- File locks on write
- No concurrent access

**SQLite:**
- Indexed queries (O(log n))
- Multi-reader support
- Concurrent read access

**Improvement:** Scales to 1000+ rules

### 3. Auditability

**YAML:**
- No violation history
- No usage statistics
- External logging only

**SQLite:**
- Built-in violation log
- Usage statistics
- Query violation history

**Improvement:** Full audit trail

### 4. Reliability

**YAML:**
- Parsing errors block ALL rules
- No validation
- Manual integrity checks

**SQLite:**
- Schema validation
- Foreign key constraints
- ACID compliance

**Improvement:** Data integrity guaranteed

## Backward Compatibility

### Option 1: Immediate Cutover (Recommended)
- Remove YAML dependency immediately
- All orchestrators use SQLite
- YAML file becomes read-only reference

**Pros:**
- Clean break
- No dual-mode complexity
- Forces validation

**Cons:**
- Requires all orchestrators update
- No fallback

### Option 2: Dual Mode (Not Recommended)
- Support both YAML and SQLite
- Gradual migration
- Fallback to YAML on DB error

**Pros:**
- Safer transition
- Fallback available

**Cons:**
- Complex code
- Sync issues
- Technical debt

**Decision:** IMMEDIATE CUTOVER (Option 1)

## Validation Criteria

### Pre-Migration Checks
- [ ] Database exists and is accessible
- [ ] Schema version matches expected (v1)
- [ ] All 83 rules are valid
- [ ] All 13 layers are populated
- [ ] No missing foreign keys

### Post-Migration Checks
- [ ] Middleware loads rules from DB
- [ ] Checkpoint validation works
- [ ] Violations log to database
- [ ] Statistics update correctly
- [ ] Performance is ≥20x faster
- [ ] No YAML file dependencies

### Integration Tests
- [ ] Planning v5 governance validation
- [ ] ADO v2 governance validation
- [ ] All 5 orchestrators checkpoint successfully
- [ ] Phase start/complete checkpoints work
- [ ] Operation checkpoints work

## Risk Assessment

### Risk 1: Database Corruption
**Probability:** Low  
**Impact:** High  
**Mitigation:** 
- Database backup before migration
- Schema validation on startup
- Read-only mode on corruption

### Risk 2: Missing Rules
**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Validation script compares YAML vs DB
- Manual review of all 83 rules
- Test suite validates critical rules

### Risk 3: Performance Regression
**Probability:** Very Low  
**Impact:** Low  
**Mitigation:**
- Benchmark before/after
- Index optimization
- Query profiling

### Risk 4: Integration Breakage
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Comprehensive integration tests
- Orchestrator validation suite
- Rollback plan (keep YAML backup)

## Rollback Plan

**If migration fails:**

1. **Revert middleware changes:**
   ```bash
   git checkout HEAD~1 src/orchestrators/middleware/governance_checkpoint.py
   ```

2. **Fix YAML parsing error:**
   - Investigate line 261 issue
   - Restore YAML loading

3. **Test orchestrators:**
   - Validate all 5 orchestrators work
   - Check governance checkpoints

4. **Re-plan migration:**
   - Identify failure cause
   - Update migration plan
   - Retry with fixes

## Success Criteria

### Phase 14 Complete When:
- ✅ GovernanceDB class created and tested
- ✅ Middleware updated to use SQLite
- ✅ All YAML dependencies removed
- ✅ Integration tests pass
- ✅ Performance improvement validated (≥20x)
- ✅ Violation logging works
- ✅ Statistics tracking works
- ✅ All 5 orchestrators validated

## Next Steps

1. **Create GovernanceDB** (Task 1 - 1 hour)
2. **Update Middleware** (Task 2 - 1.5 hours)
3. **Validation Script** (Task 3 - 0.5 hours)
4. **Integration Testing** (Task 5 - 0.5 hours)
5. **Documentation** (Task 4 - 0.5 hours)

**Total:** 4 hours estimated

---

*Generated by C150 Remediation Plan - Phase 14*  
*Analysis completed: January 4, 2026*  
*Next: Implementation*
