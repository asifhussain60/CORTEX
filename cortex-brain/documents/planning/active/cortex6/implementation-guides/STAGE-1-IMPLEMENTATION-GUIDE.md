# CORTEX 6.0 - Stage 1 Implementation Guide

**Status:** NOT_STARTED  
**Duration:** Week 1 (5-6 days)  
**Effort:** 40-48 hours  
**Owner:** Development Team  
**Last Updated:** 2026-01-09

---

## Quick Start

```bash
# Navigate to CORTEX workspace
cd /Users/asifhussain/PROJECTS/CORTEX

# Verify prerequisites
python3 --version  # Should be 3.9+
pytest --version   # Should be installed

# Create working branch
git checkout -b feature/stage-1-foundation

# Start with Phase 1.1
cd cortex-brain/documents/planning/active/cortex6/implementation-guides
```

---

## Phase 1.1: Audit Logger Infrastructure (16-20 hours)

### Overview
Implement comprehensive audit logging system that enables evidence-based validation for all 390+ acceptance criteria.

### Task 1.1.1: Design audit.db Schema (2 hours)

**Location:** `cortex-brain/database/audit_schema.sql`

```sql
-- Example schema structure
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    ac_id TEXT,
    category TEXT NOT NULL CHECK(category IN ('governance', 'orchestrator', 'validation', 'infrastructure', 'mcp', 'brain', 'integration')),
    operation TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('success', 'failure', 'warning')),
    duration_ms INTEGER,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ac_id ON audit_logs(ac_id);
CREATE INDEX idx_category ON audit_logs(category);
CREATE INDEX idx_timestamp ON audit_logs(timestamp);
```

**Acceptance Criteria:**
- ✅ Supports 7 audit categories
- ✅ Includes ac_id, operation_type, status, timestamp, metadata columns
- ✅ Efficient querying by ac_id, timestamp, category

**Validation:**
```bash
sqlite3 cortex-brain/database/audit.db < cortex-brain/database/audit_schema.sql
sqlite3 cortex-brain/database/audit.db ".schema audit_logs"
```

---

### Task 1.1.2: Implement AuditLogger Class (6 hours)

**Location:** `src/infrastructure/audit_logger.py`

**Design Pattern:** Thread-safe Singleton

```python
# Key interfaces to implement
class AuditLogger:
    def __init__(self, db_path: str, jsonl_path: str):
        """Initialize with SQLite DB and JSONL backup."""
        
    def log_governance(self, operation: str, status: str, ac_id: Optional[str] = None, **metadata):
        """Log governance-related operations."""
        
    def log_orchestrator(self, operation: str, status: str, ac_id: Optional[str] = None, **metadata):
        """Log orchestrator execution."""
        
    def log_validation(self, operation: str, status: str, ac_id: str, **metadata):
        """Log AC validation operations."""
        
    # ... other category methods
    
    def _write_entry(self, category: str, operation: str, status: str, ac_id: Optional[str], metadata: dict):
        """Internal: Write to both SQLite and JSONL."""
```

**Key Requirements:**
- Thread-safe (use threading.Lock)
- Singleton pattern (one instance per process)
- Dual storage: SQLite + JSONL
- Performance: <5ms per log entry
- Self-audit: Log own initialization

**Validation:**
```python
# In tests/unit/test_audit_logger.py
@pytest.mark.ac_id("AC-F01-005")
def test_audit_logger_initialization():
    logger = AuditLogger()
    # Verify logger logged its own initialization
    entries = logger.query(operation="audit_logger_init")
    assert len(entries) == 1
    assert entries[0]["status"] == "success"
```

---

### Task 1.1.3: Implement MCP Audit Query Tools (4 hours)

**Location:** `src/mcp/audit_query.py`

**MCP Tools to Implement:**

```python
def mcp_audit_validate(ac_id: str) -> dict:
    """
    Validate AC with audit evidence.
    Returns: {
        "ac_id": "AC-F01-005",
        "validated": True,
        "test_evidence": {...},
        "audit_evidence": {...}
    }
    """
    
def mcp_audit_search(category: str, operation: str) -> list:
    """Search audit logs by category and operation."""
    
def mcp_audit_coverage() -> dict:
    """Generate AC coverage report."""
    
def mcp_audit_timeline(ac_id: str) -> list:
    """Show execution timeline for AC."""
```

**Validation:**
```bash
# Manual test via MCP
python3 -m src.main "audit validate AC-F01-005"
```

---

### Task 1.1.4: Write Comprehensive Tests (4 hours)

**Locations:**
- `tests/unit/test_audit_logger.py`
- `tests/integration/test_audit_mcp.py`

**Test Coverage Requirements:**
- ✅ ≥95% code coverage
- ✅ All 7 audit categories tested
- ✅ Thread safety (concurrent logging)
- ✅ JSONL format parsing
- ✅ Performance (<5ms latency)

**Run Tests:**
```bash
pytest tests/unit/test_audit_logger.py -v --cov=src.infrastructure.audit_logger --cov-report=html
pytest tests/integration/test_audit_mcp.py -v
```

---

### Task 1.1.5: Integration and Validation (4 hours)

**Deliverable:** `cortex-brain/audit-logs/bootstrap.jsonl`

**Steps:**
1. Run full test suite
2. Verify AuditLogger logs its own initialization
3. Test MCP tools return valid audit evidence
4. Generate coverage report
5. Validate AC-F01-005 is marked as validated

**Validation Command:**
```bash
pytest tests/unit/test_audit_logger.py tests/integration/test_audit_mcp.py -v --cov
python3 -c "from src.infrastructure.audit_logger import AuditLogger; logger = AuditLogger(); print('Bootstrap successful' if logger.query(operation='audit_logger_init') else 'Failed')"
```

---

## Phase 1.2: SKULL Rules Migration (4-6 hours)

### Overview
Migrate 61 SKULL rules to CORE-* numbering system for unified governance.

### Task 1.2.1: Design CORE-* Numbering (1 hour)

**Location:** `cortex-brain/tier0/governance/CORE-NUMBERING-SPEC.yaml`

**Mapping Strategy:**
- SKULL-001 → CORE-001 (Maintain sequence)
- Add category prefixes in metadata
- Preserve backward compatibility

---

### Task 1.2.2: Migrate to core-rules.yaml (2 hours)

**Location:** `cortex-brain/tier0/governance/core-rules.yaml`

**Migration Script:**
```python
# scripts/migrate_skull_to_core.py
import yaml

def migrate_skull_rules():
    # Load brain-protection-rules.yaml
    # Transform SKULL-* to CORE-*
    # Preserve metadata
    # Write to core-rules.yaml
    # Add deprecation header to original file
```

---

### Task 1.2.3: Validation Tests (1.5 hours)

**Location:** `tests/governance/test_skull_migration.py`

```python
@pytest.mark.ac_id("AC-GOV-001")
def test_all_61_rules_migrated():
    core_rules = load_yaml("cortex-brain/tier0/governance/core-rules.yaml")
    assert len(core_rules["rules"]) == 61
```

---

### Task 1.2.4: Update References (1.5 hours)

**Find and Replace:**
```bash
# Find all SKULL-* references
grep -r "SKULL-" src/ cortex-brain/ .github/

# Replace with CORE-*
# Manual review required for context-specific replacements
```

---

## Phase 1.3: AC-ID Traceability System (8-10 hours)

### Overview
Link tests to acceptance criteria for coverage tracking and gap detection.

### Task 1.3.1: Design System (2 hours)

**Location:** `docs/architecture/ac-traceability-design.yaml`

**Key Components:**
- @pytest.mark.ac_id() marker
- Coverage matrix YAML schema
- Gap detection algorithm
- MCP query interface

---

### Task 1.3.2: Implement ACTraceabilitySystem (4 hours)

**Location:** `src/infrastructure/ac_traceability.py`

```python
class ACTraceabilitySystem:
    def scan_tests(self) -> dict:
        """Extract ac_id markers from all test files."""
        
    def generate_coverage_matrix(self) -> dict:
        """Create AC → Test mapping."""
        
    def detect_gaps(self) -> dict:
        """Find AC without tests, tests without AC."""
        
    def validate_ac(self, ac_id: str) -> bool:
        """Check if AC has test coverage."""
```

---

### Task 1.3.3: Update pytest Configuration (1 hour)

**Files:**
- `tests/conftest.py`
- `pytest.ini`

```python
# In conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "ac_id(id): Mark test with acceptance criteria ID"
    )
```

---

### Task 1.3.4: MCP Tools (2 hours)

**Location:** `src/mcp/ac_traceability_query.py`

**Tools:**
- `mcp_ac_coverage()`
- `mcp_ac_tests(ac_id)`
- `mcp_ac_gaps()`
- `mcp_test_acs(test_file)`

---

### Task 1.3.5: Generate Initial Report (1 hour)

**Deliverable:** `cortex-brain/registry/ac-test-coverage.yaml`

```bash
python3 -m src.infrastructure.ac_traceability generate_coverage_matrix
```

---

## Phase 1.4: Housekeeping Orchestrator (12-16 hours)

### Overview
Autonomous brain health monitoring and maintenance system.

### Task 1.4.1: Design Workflow (3 hours)

**Location:** `cortex-brain/manifests/orchestrators/housekeeping.yaml`

**9 Phases:**
1. Governance rule validation
2. Test coverage analysis
3. Audit log health check
4. Brain tier synchronization
5. Cache cleanup
6. Git isolation verification
7. Orchestrator manifest validation
8. AC gap detection
9. Health report generation

---

### Task 1.4.2: Implement Orchestrator (6 hours)

**Location:** `src/orchestrators/housekeeping_orchestrator.py`

```python
class HousekeepingOrchestrator:
    def execute(self) -> OrchestratorResult:
        """Execute all 9 phases with audit logging."""
        
    def _run_phase(self, phase_number: int, phase_name: str):
        """Execute single phase with error handling."""
```

---

### Task 1.4.3: Implement 9 Phases (4 hours)

**Location:** `src/operations/housekeeping/*.py`

**Files:**
- `governance_validation_phase.py`
- `test_coverage_phase.py`
- `audit_health_phase.py`
- ... (9 files total)

---

### Task 1.4.4: Write Tests (3 hours)

**Location:** `tests/orchestrators/test_housekeeping.py`

```python
@pytest.mark.ac_id("AC-ORC-HOUSE-001")
def test_governance_validation_phase():
    orchestrator = HousekeepingOrchestrator()
    result = orchestrator._run_phase(1, "governance_validation")
    assert result["status"] == "success"
```

---

## Progress Tracking

### Daily Checklist

**Day 1:**
- [ ] Task 1.1.1: Design audit.db schema
- [ ] Task 1.1.2: Implement AuditLogger class (start)

**Day 2:**
- [ ] Task 1.1.2: Complete AuditLogger class
- [ ] Task 1.1.3: Implement MCP audit tools

**Day 3:**
- [ ] Task 1.1.4: Write comprehensive tests
- [ ] Task 1.1.5: Integration and validation
- [ ] Phase 1.1 COMPLETE ✅

**Day 4:**
- [ ] Task 1.2.1-1.2.4: Complete SKULL migration
- [ ] Phase 1.2 COMPLETE ✅
- [ ] Task 1.3.1-1.3.3: Start AC traceability

**Day 5:**
- [ ] Task 1.3.4-1.3.5: Complete AC traceability
- [ ] Phase 1.3 COMPLETE ✅
- [ ] Task 1.4.1: Design housekeeping workflow

**Day 6:**
- [ ] Task 1.4.2-1.4.3: Implement housekeeping orchestrator
- [ ] Task 1.4.4: Write tests
- [ ] Phase 1.4 COMPLETE ✅
- [ ] **STAGE 1 COMPLETE** 🎉

---

## Validation Checklist

### Stage 1 Completion Criteria

- [ ] All 4 blocking issues resolved
- [ ] AuditLogger operational (self-audit successful)
- [ ] 61 SKULL rules migrated to CORE-*
- [ ] AC traceability generating coverage reports
- [ ] Housekeeping Orchestrator running health checks
- [ ] Stage 1 tests: 100% passing, ≥95% coverage

### Validation Commands

```bash
# Run all Stage 1 tests
pytest tests/unit/test_audit_logger.py tests/governance/test_skull_migration.py tests/architecture/test_ac_traceability.py tests/orchestrators/test_housekeeping.py -v --cov

# Validate AC coverage
python3 -m src.main "audit coverage"

# Run housekeeping orchestrator
python3 -m src.main "housekeeping"

# Generate Stage 1 completion report
python3 -m src.operations.stage_completion_report stage=1
```

---

## Troubleshooting

### Issue: AuditLogger not initializing

**Solution:**
```bash
# Check database permissions
ls -la cortex-brain/database/audit.db

# Verify schema
sqlite3 cortex-brain/database/audit.db ".schema"

# Check logs
tail -f cortex-brain/audit-logs/bootstrap.jsonl
```

### Issue: Test coverage below 95%

**Solution:**
```bash
# Generate coverage report
pytest --cov=src.infrastructure.audit_logger --cov-report=html

# Open report
open htmlcov/index.html

# Identify untested lines and add tests
```

### Issue: SKULL migration conflicts

**Solution:**
```bash
# Validate both files exist
ls -la cortex-brain/tier0/governance/*.yaml

# Check for duplicate IDs
python3 scripts/validate_core_rules.py
```

---

## Next Steps

After Stage 1 completion:
1. Generate completion report: `cortex-brain/documents/reports/stage1-completion-report.yaml`
2. Update tracking: `cortex-brain/documents/planning/active/cortex6/tracking/stage1-status.md`
3. Review with team
4. Proceed to Stage 2: Quality (Week 2)

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-09  
**Author:** Asif Hussain (Generated by GitHub Copilot)
