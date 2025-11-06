# Tier 0: Governance Design

**Version:** 1.0  
**Date:** 2025-11-05  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Immutable governance rules storage and enforcement

---

## 🎯 Overview

**Tier 0 = INSTINCT** - The brain's immutable DNA that cannot be changed.

**Purpose:**
- Store 22 permanent governance rules
- Enforce Definition of Ready (RIGHT BRAIN)
- Enforce Definition of Done (LEFT BRAIN)
- Provide rule lookup for agents (<1ms)
- Protect brain integrity

**Storage:** SQLite (`cortex-brain.db`)  
**Size Target:** <20 KB  
**Performance Target:** <1ms rule lookup

---

## 📊 SQLite Schema

### Table: `governance_rules`

```sql
CREATE TABLE governance_rules (
    id TEXT PRIMARY KEY,                    -- Rule ID (e.g., "RULE_001", "DoR", "DoD")
    rule_number INTEGER UNIQUE NOT NULL,    -- Rule number (1-22)
    title TEXT NOT NULL,                    -- Rule title
    tier TEXT NOT NULL CHECK(tier = 'TIER_0'), -- Always TIER_0
    priority TEXT NOT NULL CHECK(priority IN ('CRITICAL', 'HIGH', 'MEDIUM')),
    scope TEXT NOT NULL,                    -- Scope (e.g., "ALL", "CODE", "KDS")
    hemisphere TEXT CHECK(hemisphere IN ('RIGHT', 'LEFT', 'BOTH')),
    description TEXT NOT NULL,              -- Full description
    enforcement TEXT NOT NULL,              -- How it's enforced
    rationale TEXT NOT NULL,                -- Why this rule exists
    examples TEXT,                          -- JSON array of examples
    violations TEXT,                        -- JSON array of violations
    related_rules TEXT,                     -- JSON array of related rule IDs
    status TEXT NOT NULL DEFAULT 'active' CHECK(status = 'active'),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookup
CREATE INDEX idx_governance_rule_number ON governance_rules(rule_number);
CREATE INDEX idx_governance_priority ON governance_rules(priority);
CREATE INDEX idx_governance_hemisphere ON governance_rules(hemisphere);
```

### Table: `governance_rule_examples`

```sql
CREATE TABLE governance_rule_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    example_type TEXT NOT NULL CHECK(example_type IN ('GOOD', 'BAD')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    code_snippet TEXT,                      -- Optional code example
    FOREIGN KEY (rule_id) REFERENCES governance_rules(id) ON DELETE CASCADE
);

CREATE INDEX idx_examples_rule ON governance_rule_examples(rule_id);
```

### Table: `governance_rule_violations`

```sql
CREATE TABLE governance_rule_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    violation_type TEXT NOT NULL,           -- Type of violation
    severity TEXT NOT NULL CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    description TEXT NOT NULL,
    alternative_approach TEXT NOT NULL,     -- Suggested alternative
    FOREIGN KEY (rule_id) REFERENCES governance_rules(id) ON DELETE CASCADE
);

CREATE INDEX idx_violations_rule ON governance_rule_violations(rule_id);
```

---

## 📋 The 22 Governance Rules

### Rule Categories

**Definition of Ready (DoR) - RIGHT BRAIN:**
- Rule #21: Requirements clear, testable, scoped

**Definition of Done (DoD) - LEFT BRAIN:**
- Rule #20: Zero errors, zero warnings, all tests pass
- Rule #8: Test-Driven Development (RED → GREEN → REFACTOR)

**Brain Protection:**
- Rule #22: Challenge risky changes
- Rule #18: Challenge user modifications
- Rule #16: Brain update protocol

**Quality Gates:**
- Rule #1-7: Dual interface, live docs, architecture
- Rule #9-15: Session management, workflows
- Rule #19: Checkpoint strategy

### Sample Data Structure

```sql
-- Rule #20: Definition of DONE
INSERT INTO governance_rules (
    id, rule_number, title, tier, priority, scope, hemisphere,
    description, enforcement, rationale
) VALUES (
    'DoD',
    20,
    'Definition of DONE',
    'TIER_0',
    'CRITICAL',
    'ALL',
    'LEFT',
    'A task is NOT DONE unless: Build succeeds (0 errors, 0 warnings), All tests passing, TDD workflow followed (RED→GREEN→REFACTOR), Health validation passed, Semantic commit created.',
    'Automatic via validate-done.ps1 script. Commit hooks enforce validation. Tests must exist BEFORE or WITH code changes.',
    'Maintains code quality, prevents technical debt, ensures clean checkpoints, validates work completion, enables safe rollbacks.'
);

-- Rule #21: Definition of READY
INSERT INTO governance_rules (
    id, rule_number, title, tier, priority, scope, hemisphere,
    description, enforcement, rationale
) VALUES (
    'DoR',
    21,
    'Definition of READY',
    'TIER_0',
    'CRITICAL',
    'ALL',
    'RIGHT',
    'A task is NOT READY unless: Requirements clear, Acceptance criteria defined (Given/When/Then), Test scenarios outlined, Dependencies identified, Scope broken down (<4h tasks), DoD understood.',
    'RIGHT BRAIN validates before creating work packages. Refuses to hand work to LEFT BRAIN if incomplete. Interactive DoR completion wizard available.',
    'Prevents wasted effort, enables TDD (testable requirements), improves collaboration, reduces rework, complements DoD as entry gate.'
);

-- Rule #8: Test-Driven Development
INSERT INTO governance_rules (
    id, rule_number, title, tier, priority, scope, hemisphere,
    description, enforcement, rationale
) VALUES (
    'TDD',
    8,
    'Test-Driven Development',
    'TIER_0',
    'CRITICAL',
    'CODE',
    'LEFT',
    'All code changes MUST follow TDD workflow: Write failing test (RED), Implement minimum code (GREEN), Refactor with confidence (REFACTOR). Tests exist BEFORE or WITH code commits.',
    'Automatic TDD compliance check in validate-done.ps1. Detects code changes without corresponding test files. Commit rejected if TDD violated.',
    'Higher quality code, 94% success rate vs 67% without TDD, 68% less rework, tests define requirements, enables confident refactoring.'
);

-- Rule #22: Brain Protection
INSERT INTO governance_rules (
    id, rule_number, title, tier, priority, scope, hemisphere,
    description, enforcement, rationale
) VALUES (
    'BRAIN_PROTECTION',
    22,
    'Brain Protection System',
    'TIER_0',
    'CRITICAL',
    'KDS',
    'RIGHT',
    'RIGHT BRAIN MUST challenge any change that violates: Tier 0 immutability, SOLID principles, Tier boundary rules, Hemisphere specialization, TDD workflow. Provides alternatives, requires explicit override.',
    'brain-protector.md agent (RIGHT BRAIN) analyzes all KDS/brain modifications. Builds comprehensive challenge with threats, risks, alternatives. Cannot be bypassed for Tier 0 violations.',
    'Prevents architectural degradation, maintains SOLID compliance, protects brain integrity, enforces quality gates, enables safe evolution.'
);
```

---

## 🔍 Query Patterns

### Agent Rule Queries

```python
# Get rule by ID (fastest - primary key)
def get_rule(rule_id: str) -> Rule:
    """<1ms lookup"""
    return db.execute(
        "SELECT * FROM governance_rules WHERE id = ?",
        [rule_id]
    ).fetchone()

# Get rule by number
def get_rule_by_number(rule_number: int) -> Rule:
    """<1ms lookup (indexed)"""
    return db.execute(
        "SELECT * FROM governance_rules WHERE rule_number = ?",
        [rule_number]
    ).fetchone()

# Get all rules for hemisphere
def get_rules_by_hemisphere(hemisphere: str) -> list[Rule]:
    """<5ms (22 rules max)"""
    return db.execute(
        "SELECT * FROM governance_rules WHERE hemisphere = ? OR hemisphere = 'BOTH' ORDER BY priority, rule_number",
        [hemisphere]
    ).fetchall()

# Get critical rules (DoR, DoD, TDD)
def get_critical_rules() -> list[Rule]:
    """<3ms"""
    return db.execute(
        "SELECT * FROM governance_rules WHERE priority = 'CRITICAL' ORDER BY rule_number"
    ).fetchall()
```

### Validation Queries

```python
# Check if rule exists
def rule_exists(rule_id: str) -> bool:
    """<1ms"""
    result = db.execute(
        "SELECT 1 FROM governance_rules WHERE id = ? LIMIT 1",
        [rule_id]
    ).fetchone()
    return result is not None

# Get rule examples
def get_rule_examples(rule_id: str, example_type: str = None) -> list[Example]:
    """<2ms"""
    if example_type:
        return db.execute(
            "SELECT * FROM governance_rule_examples WHERE rule_id = ? AND example_type = ?",
            [rule_id, example_type]
        ).fetchall()
    else:
        return db.execute(
            "SELECT * FROM governance_rule_examples WHERE rule_id = ?",
            [rule_id]
        ).fetchall()

# Get rule violations (for brain protection)
def get_rule_violations(rule_id: str) -> list[Violation]:
    """<2ms"""
    return db.execute(
        "SELECT * FROM governance_rule_violations WHERE rule_id = ? ORDER BY severity DESC",
        [rule_id]
    ).fetchall()
```

---

## 🛡️ Protection Mechanisms

### Immutability Enforcement

```python
class Tier0Protection:
    """Prevents modification of governance rules"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._setup_immutability()
    
    def _setup_immutability(self):
        """Create triggers to prevent rule modification"""
        
        # Prevent UPDATE
        self.db.execute("""
            CREATE TRIGGER prevent_rule_update
            BEFORE UPDATE ON governance_rules
            BEGIN
                SELECT RAISE(ABORT, 'Tier 0 rules are immutable and cannot be updated');
            END;
        """)
        
        # Prevent DELETE
        self.db.execute("""
            CREATE TRIGGER prevent_rule_delete
            BEFORE DELETE ON governance_rules
            BEGIN
                SELECT RAISE(ABORT, 'Tier 0 rules are immutable and cannot be deleted');
            END;
        """)
        
        # Prevent INSERT after initial load
        # (Allow during migration/setup, then lock)
        self.db.execute("""
            CREATE TRIGGER prevent_rule_insert
            BEFORE INSERT ON governance_rules
            WHEN (SELECT COUNT(*) FROM governance_rules) >= 22
            BEGIN
                SELECT RAISE(ABORT, 'Tier 0 is complete with 22 rules - no additions allowed');
            END;
        """)
```

### Validation on Read

```python
def validate_rule_integrity(rule_id: str) -> tuple[bool, str]:
    """
    Validates rule hasn't been corrupted.
    Returns: (is_valid, error_message)
    """
    rule = get_rule(rule_id)
    
    if not rule:
        return False, f"Rule {rule_id} not found"
    
    # Validate required fields
    if not rule['title'] or not rule['description']:
        return False, f"Rule {rule_id} missing required fields"
    
    # Validate tier
    if rule['tier'] != 'TIER_0':
        return False, f"Rule {rule_id} has invalid tier: {rule['tier']}"
    
    # Validate priority
    if rule['priority'] not in ['CRITICAL', 'HIGH', 'MEDIUM']:
        return False, f"Rule {rule_id} has invalid priority: {rule['priority']}"
    
    # Validate hemisphere
    if rule['hemisphere'] and rule['hemisphere'] not in ['RIGHT', 'LEFT', 'BOTH']:
        return False, f"Rule {rule_id} has invalid hemisphere: {rule['hemisphere']}"
    
    # Validate status
    if rule['status'] != 'active':
        return False, f"Rule {rule_id} is not active: {rule['status']}"
    
    return True, "Valid"
```

---

## 🧪 Test Specifications

### Unit Tests (15 tests)

```python
# Test 1: Rule lookup by ID
def test_get_rule_by_id():
    rule = get_rule('DoD')
    assert rule['id'] == 'DoD'
    assert rule['rule_number'] == 20
    assert rule['title'] == 'Definition of DONE'

# Test 2: Rule lookup by number
def test_get_rule_by_number():
    rule = get_rule_by_number(21)
    assert rule['id'] == 'DoR'
    assert rule['title'] == 'Definition of READY'

# Test 3: Get rules by hemisphere
def test_get_rules_by_hemisphere():
    left_rules = get_rules_by_hemisphere('LEFT')
    assert len(left_rules) > 0
    assert all(r['hemisphere'] in ['LEFT', 'BOTH'] for r in left_rules)

# Test 4: Get critical rules
def test_get_critical_rules():
    critical = get_critical_rules()
    assert len(critical) >= 3  # DoR, DoD, TDD minimum
    assert all(r['priority'] == 'CRITICAL' for r in critical)

# Test 5: Rule immutability - UPDATE prevented
def test_rule_update_prevented():
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        db.execute("UPDATE governance_rules SET title = 'Modified' WHERE id = 'DoD'")

# Test 6: Rule immutability - DELETE prevented
def test_rule_delete_prevented():
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        db.execute("DELETE FROM governance_rules WHERE id = 'DoD'")

# Test 7: Rule immutability - INSERT prevented after 22 rules
def test_rule_insert_prevented_when_full():
    # Assuming 22 rules already exist
    with pytest.raises(sqlite3.IntegrityError, match="no additions allowed"):
        db.execute("INSERT INTO governance_rules (id, rule_number, ...) VALUES (?, ?, ...)", ['RULE_23', 23, ...])

# Test 8: Rule validation - valid rule
def test_validate_rule_integrity_valid():
    is_valid, message = validate_rule_integrity('DoD')
    assert is_valid
    assert message == "Valid"

# Test 9: Rule validation - missing rule
def test_validate_rule_integrity_missing():
    is_valid, message = validate_rule_integrity('NONEXISTENT')
    assert not is_valid
    assert "not found" in message

# Test 10: Get rule examples
def test_get_rule_examples():
    examples = get_rule_examples('DoD', 'GOOD')
    assert len(examples) > 0
    assert all(e['example_type'] == 'GOOD' for e in examples)

# Test 11: Get rule violations
def test_get_rule_violations():
    violations = get_rule_violations('DoD')
    # Should have violations like "Skip warnings", "Mark done with errors"
    assert len(violations) > 0

# Test 12: Query performance - rule lookup <1ms
def test_rule_lookup_performance():
    start = time.perf_counter()
    get_rule('DoD')
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 1.0, f"Rule lookup took {elapsed_ms}ms (target: <1ms)"

# Test 13: All 22 rules loaded
def test_all_rules_loaded():
    rules = db.execute("SELECT COUNT(*) FROM governance_rules").fetchone()[0]
    assert rules == 22, f"Expected 22 rules, found {rules}"

# Test 14: No duplicate rule numbers
def test_no_duplicate_rule_numbers():
    duplicates = db.execute("""
        SELECT rule_number, COUNT(*) as count 
        FROM governance_rules 
        GROUP BY rule_number 
        HAVING count > 1
    """).fetchall()
    assert len(duplicates) == 0, f"Duplicate rule numbers found: {duplicates}"

# Test 15: All rules have required fields
def test_all_rules_complete():
    incomplete = db.execute("""
        SELECT id FROM governance_rules 
        WHERE title IS NULL 
           OR description IS NULL 
           OR enforcement IS NULL 
           OR rationale IS NULL
    """).fetchall()
    assert len(incomplete) == 0, f"Incomplete rules: {incomplete}"
```

---

## 📊 Performance Benchmarks

### Target Metrics

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Rule lookup by ID | <1ms | Primary key index |
| Rule lookup by number | <1ms | Indexed column |
| Get hemisphere rules | <5ms | Max 22 rows |
| Get all rules | <10ms | Rare operation |
| Rule validation | <2ms | Simple checks |

### Benchmark Test

```python
def benchmark_tier0_performance():
    """Benchmark all Tier 0 operations"""
    
    iterations = 1000
    
    # Benchmark 1: Rule lookup by ID
    start = time.perf_counter()
    for _ in range(iterations):
        get_rule('DoD')
    avg_ms = (time.perf_counter() - start) / iterations * 1000
    assert avg_ms < 1.0, f"Rule lookup: {avg_ms}ms (target: <1ms)"
    
    # Benchmark 2: Rule lookup by number
    start = time.perf_counter()
    for _ in range(iterations):
        get_rule_by_number(20)
    avg_ms = (time.perf_counter() - start) / iterations * 1000
    assert avg_ms < 1.0, f"Rule number lookup: {avg_ms}ms (target: <1ms)"
    
    # Benchmark 3: Get hemisphere rules
    start = time.perf_counter()
    for _ in range(iterations):
        get_rules_by_hemisphere('LEFT')
    avg_ms = (time.perf_counter() - start) / iterations * 1000
    assert avg_ms < 5.0, f"Hemisphere rules: {avg_ms}ms (target: <5ms)"
    
    print(f"✅ All Tier 0 performance benchmarks passed")
```

---

## 🔄 Migration from KDS v8

### Source: `governance/rules.md`

**Current format:**
```yaml
# Rule in KDS v8
rule_id: DUAL_INTERFACE
severity: CRITICAL
scope: ALL_PROMPTS
...
```

**Migration script:**

```python
# scripts/migrate-tier0.py

import yaml
import sqlite3
from pathlib import Path

def migrate_governance_rules():
    """Migrate governance/rules.md → SQLite Tier 0"""
    
    # Read KDS v8 rules
    rules_md = Path('governance/rules.md').read_text()
    
    # Parse YAML sections
    rules = parse_governance_rules(rules_md)  # Custom parser
    
    # Create SQLite database
    db = sqlite3.connect('cortex-brain.db')
    
    # Create tables
    create_tier0_tables(db)
    
    # Insert rules
    for rule in rules:
        db.execute("""
            INSERT INTO governance_rules (
                id, rule_number, title, tier, priority, scope, hemisphere,
                description, enforcement, rationale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            rule['id'],
            rule['number'],
            rule['title'],
            'TIER_0',
            rule['severity'],  # Map to priority
            rule['scope'],
            rule.get('hemisphere', 'BOTH'),
            rule['description'],
            rule['enforcement'],
            rule['rationale']
        ])
    
    db.commit()
    
    # Validate migration
    count = db.execute("SELECT COUNT(*) FROM governance_rules").fetchone()[0]
    assert count == 22, f"Expected 22 rules, migrated {count}"
    
    print(f"✅ Migrated {count} governance rules to Tier 0")
```

---

## 🎯 Integration with Agents

### RIGHT BRAIN: Definition of READY Enforcement

```python
# agents/right_brain/readiness_validator.py

class ReadinessValidator:
    """Enforces Rule #21: Definition of READY"""
    
    def validate_ready(self, work_item: WorkItem) -> ReadyStatus:
        # Get DoR rule
        dor_rule = get_rule('DoR')
        
        # Check criteria
        checks = {
            'requirements_clear': self._check_requirements(work_item),
            'acceptance_criteria_defined': self._check_acceptance_criteria(work_item),
            'test_scenarios_outlined': self._check_test_scenarios(work_item),
            'dependencies_identified': self._check_dependencies(work_item),
            'scope_breakdown': self._check_scope(work_item),
            'dod_understood': self._check_dod_understanding(work_item)
        }
        
        if all(checks.values()):
            return ReadyStatus(ready=True, message="✅ Definition of READY complete")
        else:
            missing = [k for k, v in checks.items() if not v]
            return ReadyStatus(
                ready=False,
                message=f"❌ Definition of READY incomplete: {missing}",
                missing_items=missing,
                rule_reference=dor_rule
            )
```

### LEFT BRAIN: Definition of DONE Enforcement

```python
# agents/left_brain/health_validator.py

class HealthValidator:
    """Enforces Rule #20: Definition of DONE"""
    
    def validate_done(self, task: Task) -> DoneStatus:
        # Get DoD rule
        dod_rule = get_rule('DoD')
        
        # Run validations
        checks = {
            'build_succeeds': self._run_build(),
            'zero_errors': self._check_errors(),
            'zero_warnings': self._check_warnings(),
            'tests_passing': self._run_tests(),
            'tdd_followed': self._check_tdd_compliance(),
            'health_passed': self._run_health_checks()
        }
        
        if all(checks.values()):
            return DoneStatus(done=True, message="✅ Definition of DONE validated")
        else:
            failures = [k for k, v in checks.items() if not v]
            return DoneStatus(
                done=False,
                message=f"❌ Definition of DONE failed: {failures}",
                failed_checks=failures,
                rule_reference=dod_rule,
                action="Fix issues before proceeding"
            )
```

---

## 📚 Related Documents

- [Architecture Overview](overview.md)
- [Tier 1: STM Design](tier1-stm-design.md)
- [Tier 2: LTM Design](tier2-ltm-design.md)
- [Storage Schema](storage-schema.md)

---

**Status:** ✅ Tier 0 Design Complete  
**Next:** Create Tier 1 STM design  
**Version:** 1.0 (Initial design)

