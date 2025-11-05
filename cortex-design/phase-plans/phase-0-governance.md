# Phase 0: Tier 0 (Governance - Instinct Layer)

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** 4-6 hours + 1 hour holistic review  
**Dependencies:** None (first phase)  
**Storage:** SQLite (`cortex-brain.db` → `governance` schema)  
**Performance Target:** <1ms rule lookups, 100% indexed queries

---

## 🎯 Overview

**Purpose:** Build the immutable instinct layer that governs ALL CORTEX behavior. This tier stores 28 governance rules (from KDS) and provides enforcement mechanisms.

**Key Deliverables:**
- GovernanceEngine class with SQLite backend
- Migration from YAML → SQLite (`cortex-brain.db`)
- Rule query API (<1ms indexed lookups)
- Violation tracking system
- Pre-commit validation hooks
- Complete test coverage (15 unit tests)

---

## 📊 What We're Building

### Database Schema (already designed)
**File:** `cortex-design/architecture/unified-database-schema.sql`

```sql
CREATE TABLE governance_rules (
    id TEXT PRIMARY KEY,               -- 'TEST_FIRST_TDD', 'DEFINITION_OF_DONE', etc.
    number INTEGER UNIQUE NOT NULL,    -- 5, 20, 21, etc.
    severity TEXT NOT NULL,            -- CRITICAL, HIGH, MEDIUM, LOW
    category TEXT NOT NULL,            -- quality, protection, architecture
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    immutable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    version TEXT
);

CREATE TABLE governance_rule_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT REFERENCES governance_rules(id),
    requirement TEXT NOT NULL,
    priority INTEGER,
    category TEXT
);

CREATE TABLE governance_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT REFERENCES governance_rules(id),
    timestamp TIMESTAMP,
    context TEXT,
    severity TEXT,
    resolution TEXT,
    resolved_at TIMESTAMP
);
```

**Indexes:** All lookups <1ms via indexed queries

---

## 🏗️ Implementation Tasks

### Task 1: Setup Database & Schema
**File:** `CORTEX/src/tier0/governance_engine.py`
**Duration:** 1 hour  
**Tests:** 3 unit tests

**Description:**
Initialize SQLite database, create schema, establish connection pool.

**Implementation Details:**
```python
import sqlite3
from pathlib import Path
from typing import Optional

class GovernanceEngine:
    """Tier 0: Immutable governance rules with SQLite backend"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = Path(db_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and schema"""
        conn = sqlite3.connect(self.db_path)
        # Execute schema from unified-database-schema.sql (Tier 0 section)
        conn.close()
```

**Success Criteria:**
- [ ] Database created at `CORTEX/cortex-brain.db`
- [ ] All Tier 0 tables exist
- [ ] Indexes created and verified
- [ ] Connection pooling working

---

### Task 2: YAML → SQLite Migration
**File:** `CORTEX/src/tier0/migrate_governance.py`
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
One-time migration of 28 rules from `governance.yaml` → SQLite.

**Implementation Details:**
```python
import yaml
from typing import Dict, List

def migrate_governance_rules(yaml_path: str, engine: GovernanceEngine):
    """Migrate rules from YAML to SQLite"""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    
    for rule in data['rules']:
        # Insert into governance_rules table
        engine.create_rule(
            id=rule['id'],
            number=rule['number'],
            severity=rule['severity'],
            category=rule['category'],
            name=rule['name'],
            description=rule['description'],
            immutable=True
        )
        
        # Insert requirements (nested structure)
        for req in rule.get('requirements', []):
            engine.create_requirement(rule['id'], req)
```

**Success Criteria:**
- [ ] All 28 rules migrated
- [ ] Requirements extracted (Rule #5: TDD workflow, Rule #20: DoD criteria, etc.)
- [ ] Enforcement metadata preserved
- [ ] Migration idempotent (can run multiple times)

---

### Task 3: Rule Query API
**File:** `CORTEX/src/tier0/governance_engine.py` (extend)
**Duration:** 1 hour  
**Tests:** 4 unit tests

**Description:**
Fast rule lookups for agents to validate behavior.

**Implementation Details:**
```python
class GovernanceEngine:
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get rule by ID (<1ms with index)"""
        # SELECT * FROM governance_rules WHERE id = ?
        
    def get_rules_by_category(self, category: str) -> List[Rule]:
        """Get all rules in category"""
        # SELECT * FROM governance_rules WHERE category = ?
    
    def get_critical_rules(self) -> List[Rule]:
        """Get all CRITICAL severity rules"""
        # SELECT * FROM governance_rules WHERE severity = 'CRITICAL'
    
    def validate_action(self, action: str, context: Dict) -> ValidationResult:
        """Check if action violates any rules"""
        # Query relevant rules, check criteria
        
    def get_requirements(self, rule_id: str) -> List[str]:
        """Get all requirements for a rule"""
        # SELECT requirement FROM governance_rule_requirements WHERE rule_id = ?
```

**Success Criteria:**
- [ ] All queries <1ms (indexed)
- [ ] Rule lookup by ID works
- [ ] Category filtering works
- [ ] Severity filtering works
- [ ] Requirements nested properly

---

### Task 4: Violation Tracking
**File:** `CORTEX/src/tier0/violation_tracker.py`
**Duration:** 1 hour  
**Tests:** 3 unit tests

**Description:**
Log and track rule violations for anomaly detection.

**Implementation Details:**
```python
class ViolationTracker:
    """Track governance violations"""
    
    def log_violation(self, rule_id: str, context: str, severity: str):
        """Insert violation record"""
        # INSERT INTO governance_violations
        
    def get_unresolved_violations(self) -> List[Violation]:
        """Get all violations not yet resolved"""
        # SELECT * WHERE resolved_at IS NULL
    
    def resolve_violation(self, violation_id: int, resolution: str):
        """Mark violation as resolved"""
        # UPDATE governance_violations SET resolved_at = NOW()
    
    def get_violation_stats(self) -> Dict:
        """Aggregate violation metrics"""
        # Count by rule_id, severity, resolution status
```

**Success Criteria:**
- [ ] Violations logged successfully
- [ ] Unresolved violations queryable
- [ ] Resolution tracking works
- [ ] Stats aggregation accurate

---

### Task 5: Pre-Commit Validation Hook
**File:** `CORTEX/hooks/pre-commit-governance.py`
**Duration:** 0.5 hours  
**Tests:** 1 integration test

**Description:**
Git hook that validates commits against governance rules.

**Implementation Details:**
```python
#!/usr/bin/env python3
"""Pre-commit hook for governance validation"""

from tier0.governance_engine import GovernanceEngine

def validate_commit():
    """Check if commit violates governance"""
    engine = GovernanceEngine()
    
    # Check critical rules
    critical = engine.get_critical_rules()
    
    # Validate against Rule #20 (Definition of DONE)
    dod = engine.get_rule('DEFINITION_OF_DONE')
    # - Zero errors/warnings
    # - All tests pass
    # - Build succeeds
    
    # Block if violations found
```

**Success Criteria:**
- [ ] Hook executable
- [ ] Violations block commit
- [ ] Error messages helpful
- [ ] Bypass mechanism for emergencies

---

## 📋 Test Plan (15 Unit + 2 Integration = 17 Total)

### Unit Tests (15 tests)

**GovernanceEngine (7 tests):**
- [ ] `test_initialize_database()` - Database created with correct schema
- [ ] `test_get_rule_by_id()` - Rule lookup <1ms
- [ ] `test_get_rules_by_category()` - Category filtering works
- [ ] `test_get_critical_rules()` - Severity filtering works
- [ ] `test_get_requirements()` - Nested requirements returned
- [ ] `test_validate_action()` - Action validation logic
- [ ] `test_immutable_rules()` - Immutable flag enforced

**Migration (4 tests):**
- [ ] `test_migrate_governance_rules()` - All 28 rules migrated
- [ ] `test_migrate_requirements()` - Requirements extracted
- [ ] `test_migrate_enforcement()` - Enforcement metadata preserved
- [ ] `test_migration_idempotent()` - Can run multiple times

**ViolationTracker (4 tests):**
- [ ] `test_log_violation()` - Violation logged successfully
- [ ] `test_get_unresolved_violations()` - Unresolved queryable
- [ ] `test_resolve_violation()` - Resolution tracking works
- [ ] `test_get_violation_stats()` - Stats aggregation accurate

### Integration Tests (2 tests)
- [ ] `test_end_to_end_rule_query()` - YAML → SQLite → Query in <1ms
- [ ] `test_pre_commit_validation()` - Hook blocks violations

---

## ⚡ Performance Benchmarks

### Query Performance
```python
def test_rule_lookup_performance():
    """Ensure rule lookups meet <1ms target"""
    engine = GovernanceEngine()
    
    import time
    start = time.perf_counter()
    rule = engine.get_rule('TEST_FIRST_TDD')
    elapsed = (time.perf_counter() - start) * 1000  # ms
    
    assert elapsed < 1.0, f"Rule lookup took {elapsed}ms (target: <1ms)"
```

**Targets:**
- Rule lookup by ID: <1ms
- Category filter: <5ms
- Violation query: <10ms
- Migration time: <1 second

---

## 🎯 Success Criteria

**Phase 0 complete when:**
- ✅ All 15 unit tests passing
- ✅ All 2 integration tests passing
- ✅ Rule lookup <1ms (measured)
- ✅ 28 rules migrated from YAML
- ✅ Pre-commit hook blocks violations
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **API Documentation:** `CORTEX/docs/tier0-governance-api.md`
2. **Migration Guide:** `CORTEX/docs/tier0-migration-guide.md`
3. **Rule Reference:** `CORTEX/docs/governance-rules-reference.md` (generated from SQLite)

---

## 🔍 MANDATORY: Holistic Review (Phase 0 Complete)

**⚠️ DO NOT PROCEED TO PHASE 1 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 0 Section

#### 1. Design Alignment ✅
- [ ] Does SQLite storage match unified architecture design?
- [ ] Are all 28 governance rules preserved accurately?
- [ ] Does rule structure support future extensibility (Rule #28)?
- [ ] Is Tier 0 truly immutable (cannot be bypassed)?
- [ ] Does migration preserve semantic meaning?

#### 2. Implementation Quality ✅
- [ ] All 15 unit tests passing?
- [ ] All 2 integration tests passing?
- [ ] Code follows Python best practices?
- [ ] Type hints used consistently?
- [ ] Error handling comprehensive?
- [ ] Logging implemented?

#### 3. Performance Validation ✅
- [ ] Rule lookup <1ms achieved?
- [ ] Category queries <5ms achieved?
- [ ] Migration completes <1 second?
- [ ] Database file size <40KB?

#### 4. Integration with Previous Phases ✅
- [ ] N/A (Phase 0 is first)

#### 5. Integration Readiness for Next Phase ✅
- [ ] Phase 1 can query governance rules?
- [ ] API stable and documented?
- [ ] No blocking issues for conversation tracking?
- [ ] Database schema ready for Tier 1 tables?

#### 6. Adjustments Needed
- [ ] Should Rule #11 (FIFO) capacity be different?
- [ ] Should Rule #28 (Plugin) have more examples?
- [ ] Should pre-commit hook be more lenient during development?

### Review Output Document
**Create:** `cortex-design/reviews/phase-0-review.md`

**Template:**
```markdown
# Phase 0 Review Report

**Date:** 2025-11-05
**Phase:** Tier 0 (Governance - Instinct Layer)
**Status:** ✅ Pass / ⚠️ Pass with Adjustments / ❌ Fail

## Summary
[1-2 paragraphs on overall assessment]

## Design Alignment
- ✅ SQLite storage matches design
- ✅ All 28 rules preserved
- ⚠️ Consider adding more plugin examples (minor)

## Implementation Quality
- ✅ All tests passing (15 unit, 2 integration)
- ✅ Code quality high
- ✅ Type hints consistent
- ✅ Documentation complete

## Performance Validation
- ✅ Rule lookup: 0.7ms (target: <1ms) ✅
- ✅ Category query: 3.2ms (target: <5ms) ✅
- ✅ Migration: 0.8s (target: <1s) ✅
- ✅ Database size: 38KB (target: <40KB) ✅

## Integration Assessment
- ✅ API ready for Phase 1
- ✅ Database schema supports Tier 1 tables
- ✅ No blocking issues

## Adjustments Required
1. Add 2 more plugin architecture examples (Rule #28)
2. Update pre-commit hook to warn instead of block during dev branch
3. Add logging to migration script for debugging

## Plan Updates
- Phase 1 plan: Adjust conversation capacity to 50 (per Rule #11)
- Phase 4 plan: Add plugin registration examples (per Rule #28)

## Recommendation
⚠️ PASS WITH MINOR ADJUSTMENTS (implement above 3 items)
```

### Actions After Review

#### If Review PASSES ✅
1. **Commit review document:**
   ```bash
   git add cortex-design/reviews/phase-0-review.md
   git commit -m "docs(cortex): Phase 0 holistic review complete - PASS"
   ```

2. **Update next phase plan based on findings:**
   ```bash
   git add cortex-design/phase-plans/phase-1-working-memory.md
   git commit -m "docs(cortex): Update Phase 1 plan with Phase 0 learnings"
   ```

3. **THEN proceed to Phase 1 implementation**

#### If Review REQUIRES ADJUSTMENTS ⚠️
1. Document minor issues in review report
2. Create quick fix checklist:
   - Add plugin examples (10 min)
   - Update hook to warn mode (5 min)
   - Add migration logging (10 min)
3. Implement fixes
4. Re-run affected tests
5. Update review report with "PASS with adjustments"
6. Proceed to next phase

#### If Review FAILS ❌
1. Document critical issues in review report
2. Create detailed fix plan with estimates
3. Implement fixes
4. Re-run complete test suite
5. Re-run review checklist
6. Only proceed when PASS achieved

### Success Metrics for Phase 0
- ✅ All tests passing (17 total)
- ✅ All benchmarks met (<1ms, <5ms, <1s)
- ✅ All 28 rules migrated accurately
- ✅ Review report created and approved
- ✅ Phase 1 plan updated with learnings

### Learning Capture
**Document in review:**
- What worked well? (SQLite performance exceeded expectations)
- What was harder than expected? (YAML nested structure extraction)
- What assumptions were wrong? (Migration took 1.5h instead of 1h)
- What should change in next phases? (Allow more time for data structure complexity)

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 (DB Setup) + Task 2 (Migration) | 2.5 | 2.5 |
| 2 | Task 3 (Query API) + Task 4 (Violations) | 2 | 4.5 |
| 2 | Task 5 (Hook) + Tests + Docs | 2.5 | 7 |
| 3 | **Holistic Review** | 1 | 8 |

**Total Estimated:** 4-6 hours implementation + 1 hour review + 1 hour adjustments = 6-8 hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All 15 unit tests written and passing
- [ ] All 2 integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Phase 1 plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase 1 ready to start

---

**Status:** Ready for implementation  
**Next:** Phase 1 (Tier 1 - Working Memory)  
**Estimated Completion:** 6-8 hours  
**⚠️ CRITICAL:** Complete holistic review before Phase 1!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-1-working-memory.md` - Next phase
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
- `CORTEX-DNA.md` - Core design principles
