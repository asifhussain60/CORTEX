# CORTEX TIER 1 - Acceptance Criteria & Project Governance

**Version:** 1.0 | **Updated:** 2026-01-22 | **Authority:** cortex_brain/tier1/governance (SQLite + YAML)

---

## 🧠 Overview

**TIER 1** is the **Project Governance Layer** that tracks and enforces acceptance criteria (AC-IDs), manages state across phases, and ensures all work is auditable and verifiable. While TIER 0 defines immutable rules, TIER 1 applies those rules to specific projects and tracks execution compliance.

**Key Characteristics:**
- **Semi-Immutable:** Rules can be modified, but changes are audited
- **High Precedence:** Overrides TIER 2 and TIER 3
- **State-Full:** Tracks AC-ID lifecycle and phase progress
- **Fully Auditable:** Every change logged with hash verification
- **Phase-Aware:** Enforces gates based on current execution phase

---

## 📋 Core Concepts

### 1. AC-ID (Acceptance Criteria Identifier)

An **AC-ID** is a unique identifier for a single acceptance criterion that must be verified:

**Format:** `AC-{PREFIX}-{NUMBER}-{SEQUENTIAL}`

**Examples:**
```
AC-FR-001-01    Feature Request 001, criteria 1
AC-FR-001-02    Feature Request 001, criteria 2
AC-NFR-003-01   Non-Functional Requirement 003, criteria 1
AC-REFACTOR-05-03  Refactoring task 05, criteria 3
AC-DOC-029-01   Documentation task 029, criteria 1
```

### 2. AC-ID Lifecycle

Every AC-ID passes through these states:

```
DEFINED → READY → IN_PROGRESS → COMPLETE → VERIFIED → LOCKED
   ↓
 (optional) BLOCKED (waiting for dependency)
```

**State Transitions:**

| From | To | Trigger | Audit Entry |
|------|----|---------|-----------  |
| DEFINED | READY | Dependencies satisfied | AC_READY |
| READY | IN_PROGRESS | Execution starts | AC_START |
| IN_PROGRESS | BLOCKED | Dependency found | AC_BLOCKED |
| BLOCKED | READY | Dependency resolved | AC_UNBLOCKED |
| IN_PROGRESS | COMPLETE | Work finished | AC_EXECUTE |
| COMPLETE | VERIFIED | Audit verified | AC_COMPLETE |
| VERIFIED | LOCKED | Phase locked | AC_LOCKED |

### 3. Audit Trail

Each AC-ID maintains a hash-chain audit trail:

```
AC-FR-001-01 Audit Trail:
├─ 2026-01-22 10:00:01 → AC_START [hash_001]
├─ 2026-01-22 10:15:32 → AC_EXECUTE [hash_002] (references hash_001)
├─ 2026-01-22 10:20:15 → AC_COMPLETE [hash_003] (references hash_002)
├─ 2026-01-22 10:25:00 → AC_VERIFIED [hash_004] (references hash_003)
└─ 2026-01-22 10:30:00 → AC_LOCKED [hash_005] (references hash_004)

Chain verified: hash_005 → hash_004 → hash_003 → hash_002 → hash_001 ✅
```

**Hash-Chain Verification:**
```python
def verify_hash_chain(ac_id: str) -> bool:
    """Verify audit trail integrity."""
    entries = load_audit_entries(ac_id)
    
    prev_hash = None
    for entry in entries:
        # Each entry must reference previous
        if entry.previous_hash != prev_hash:
            raise AuditIntegrityError(f"Chain broken at {entry}")
        prev_hash = entry.hash
    
    return True
```

---

## 🎯 Governance Gates

### Phase Gates

Each phase has specific governance gates:

**PHASE-0 (Planning):**
```
Gate: All AC-IDs have evidence attached
      All AC-IDs pass schema validation
      Dependency graph is acyclic
```

**PHASE-1 (Development):**
```
Gate: All AC-IDs in READY state
      No circular dependencies
      All type hints present (CORE-011)
      All docstrings present (CORE-012)
```

**PHASE-2 (Testing):**
```
Gate: All unit tests pass
      Code coverage ≥ 95%
      No bare except clauses (CORE-013)
      Error handling complete
```

**PHASE-3 (Validation):**
```
Gate: All AC-IDs marked VERIFIED
      Audit trail integrity confirmed
      Phase completion report generated
      All deliverables present
```

**PHASE-4 (Deployment):**
```
Gate: Phase 3 fully complete
      All gates passed
      No outstanding issues
      Rollback plan verified
```

### Gate Enforcement

```python
class GovernanceGate:
    """Enforce phase-specific governance gates."""
    
    def can_enter_phase(self, phase: Phase, ac_ids: List[str]) -> Result[None]:
        """Check if phase entry conditions met."""
        
        required_gates = self.gates_for_phase(phase)
        
        for gate in required_gates:
            if not gate.validate(ac_ids):
                return Err(
                    f"Cannot enter {phase}: Gate '{gate.name}' not satisfied"
                )
        
        return Ok(None)
```

---

## 📊 Evidence Tracking

Each AC-ID collects **evidence** during execution:

### Evidence Types

| Type | Format | Example |
|------|--------|---------|
| **Code** | File path + line range | `cortex/brain/governance.py:1-50` |
| **Test** | Test name + result | `test_governance_core_rules: PASS` |
| **Commit** | Git commit SHA | `b99fb6c1c7a3f...` |
| **Audit** | Audit entry ID | `AE-2026-01-22-001` |
| **Review** | Reviewer + approval | `@asif-hussain: APPROVED` |
| **Performance** | Metric + benchmark | `Token efficiency: 95.2%` |

### Evidence Collection

```python
@dataclass
class Evidence:
    """Single piece of evidence for AC-ID."""
    
    evidence_id: str           # Unique identifier
    ac_id: str                 # Parent AC-ID
    evidence_type: EvidenceType
    content: str               # Evidence content
    timestamp: datetime
    submitter: str             # Who provided evidence
    verified: bool             # Manually verified
    hash: str                  # Content hash
    
    def verify_authenticity(self) -> bool:
        """Verify evidence hasn't been modified."""
        return compute_hash(self.content) == self.hash
```

### Evidence Validation

```python
def validate_evidence_complete(ac_id: str) -> Result[bool]:
    """Check if AC-ID has sufficient evidence."""
    
    evidence = load_evidence(ac_id)
    
    # Minimum evidence requirements
    required = {
        "code": 1,        # At least 1 code reference
        "test": 1,        # At least 1 test passing
        "commit": 1,      # At least 1 Git commit
    }
    
    by_type = group_by_type(evidence)
    
    for evidence_type, count_required in required.items():
        if len(by_type.get(evidence_type, [])) < count_required:
            return Err(f"Missing {evidence_type} evidence")
    
    return Ok(True)
```

---

## 🔄 State Persistence

### AC-ID State Storage

**Tier 1 maintains state in SQLite:**

```sql
-- AC-ID tracking table
CREATE TABLE ac_ids (
    ac_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20),           -- DEFINED, READY, IN_PROGRESS, etc.
    phase VARCHAR(20),            -- PHASE-0, PHASE-1, ...
    assigned_to VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    locked BOOLEAN DEFAULT FALSE,
    phase_lockable BOOLEAN,       -- Can this AC-ID be phase-locked?
    audit_verified BOOLEAN,       -- Has audit verified?
    
    CONSTRAINT valid_status CHECK (status IN 
        ('DEFINED', 'READY', 'IN_PROGRESS', 'BLOCKED', 'COMPLETE', 'VERIFIED', 'LOCKED'))
);

-- Audit trail table
CREATE TABLE audit_trail (
    audit_id VARCHAR(50) PRIMARY KEY,
    ac_id VARCHAR(50),
    operation VARCHAR(50),        -- AC_START, AC_EXECUTE, AC_COMPLETE, etc.
    timestamp TIMESTAMP,
    operator VARCHAR(100),
    previous_hash VARCHAR(64),    -- Hash of previous entry (for chain)
    current_hash VARCHAR(64),     -- SHA-256 hash of this entry
    details JSON,                 -- Additional context
    
    FOREIGN KEY (ac_id) REFERENCES ac_ids(ac_id)
);

-- Evidence table
CREATE TABLE evidence (
    evidence_id VARCHAR(50) PRIMARY KEY,
    ac_id VARCHAR(50),
    evidence_type VARCHAR(50),    -- code, test, commit, audit, review, performance
    content TEXT,
    timestamp TIMESTAMP,
    submitter VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    hash VARCHAR(64),
    
    FOREIGN KEY (ac_id) REFERENCES ac_ids(ac_id)
);
```

### State Consistency

```python
@dataclass
class ACIDState:
    """Current state of an AC-ID."""
    
    ac_id: str
    status: ACIDStatus
    phase: Phase
    evidence: List[Evidence]
    audit_trail: List[AuditEntry]
    locked: bool
    verified: bool
    
    def is_complete(self) -> bool:
        """Check if AC-ID is complete and audited."""
        return (
            self.status == ACIDStatus.COMPLETE and
            self.verified and
            self.audit_trail_valid()
        )
    
    def audit_trail_valid(self) -> bool:
        """Verify audit trail integrity."""
        return verify_hash_chain(self.audit_trail)
```

---

## 🔐 Compliance Rules (TIER 1-Specific)

### Rule: AC-ID Dependency Management

**Purpose:** Prevent circular dependencies and ensure logical ordering.

**Rule:**
- AC-IDs may depend on other AC-IDs
- Dependencies MUST be acyclic
- Blocked AC-IDs cannot progress until dependency resolves

**Validation:**
```python
def validate_dependency_graph(ac_ids: List[str]) -> Result[None]:
    """Check for circular dependencies."""
    
    graph = build_dependency_graph(ac_ids)
    
    if has_cycle(graph):
        return Err("Circular dependency detected")
    
    # Check all can eventually complete
    for ac_id in ac_ids:
        if not has_topological_order(graph, ac_id):
            return Err(f"AC-ID {ac_id} cannot be ordered")
    
    return Ok(None)
```

### Rule: Evidence Coherence

**Purpose:** Ensure evidence is consistent and verifiable.

**Rule:**
- Evidence must reference actual code/tests/commits
- All referenced items must exist and be verifiable
- Evidence timestamps must be ordered correctly
- Evidence cannot be modified after submission

**Validation:**
```python
def validate_evidence_coherence(evidence: Evidence) -> Result[None]:
    """Validate evidence against actual artifacts."""
    
    match evidence.type:
        case "code":
            file, lines = parse_code_reference(evidence.content)
            if not file_exists(file) or lines_missing(file, lines):
                return Err(f"Code reference invalid: {evidence.content}")
        
        case "test":
            test_name = evidence.content
            if not test_exists(test_name) or not test_passes(test_name):
                return Err(f"Test not passing: {test_name}")
        
        case "commit":
            commit_sha = evidence.content
            if not commit_exists(commit_sha):
                return Err(f"Commit not found: {commit_sha}")
    
    return Ok(None)
```

### Rule: Phase Lock Requirements

**Purpose:** Ensure phases only lock when ready.

**Rule:**
- AC-IDs must be VERIFIED before phase lock
- All evidence must be attached and coherent
- Audit trail must be complete
- No outstanding issues

**Validation:**
```python
def can_lock_phase(phase: Phase, ac_ids: List[str]) -> Result[None]:
    """Check if phase can be locked."""
    
    for ac_id in ac_ids:
        state = get_ac_id_state(ac_id)
        
        # Must be complete
        if not state.is_complete():
            return Err(f"AC-ID {ac_id} not complete")
        
        # Evidence must be coherent
        for evidence in state.evidence:
            if not validate_evidence_coherence(evidence).is_ok():
                return Err(f"Evidence incoherent for {ac_id}")
        
        # Audit trail must be valid
        if not state.audit_trail_valid():
            return Err(f"Audit trail invalid for {ac_id}")
    
    return Ok(None)
```

---

## 🎯 Governance Compliance Rules

TIER 1 enforces all TIER 0 rules PLUS project-specific rules:

### TIER 1-Specific Rules

**Rule: AC-ID Tracking Mandatory**
- Every piece of work MUST have an AC-ID
- AC-IDs track evidence from start to completion
- No work can progress without AC-ID

**Rule: Evidence-Based Verification**
- Completion verified by evidence, not by assumption
- Evidence attached to AC-IDs during execution
- Evidence coherence validated before phase lock

**Rule: Audit Trail Immutability**
- Audit entries cannot be modified or deleted
- Hash-chain prevents tampering
- Missing entries detected immediately

**Rule: Phase-Based Governance**
- Each phase has specific gates
- Gates must be passed to progress
- Phase completion requires audit verification

---

## 📊 Tier 1 State Management

### Checkpoint System

```python
class Tier1Checkpoint:
    """Save and restore TIER 1 state at checkpoints."""
    
    @staticmethod
    def create_checkpoint(phase: Phase) -> Result[str]:
        """Create checkpoint before phase entry."""
        
        checkpoint_id = f"CP-{phase}-{timestamp()}"
        
        # Save all AC-ID states
        state_snapshot = {
            "phase": phase,
            "ac_ids": serialize_all_ac_ids(),
            "audit_trail": serialize_audit_trail(),
            "evidence": serialize_evidence(),
            "timestamp": datetime.now(),
            "hash": compute_state_hash(),
        }
        
        # Persist checkpoint
        save_checkpoint(checkpoint_id, state_snapshot)
        
        # Log checkpoint
        audit_logger.record(
            operation="CHECKPOINT_CREATE",
            checkpoint_id=checkpoint_id,
            phase=phase,
        )
        
        return Ok(checkpoint_id)
    
    @staticmethod
    def restore_checkpoint(checkpoint_id: str) -> Result[None]:
        """Restore state from checkpoint."""
        
        checkpoint = load_checkpoint(checkpoint_id)
        
        # Verify checkpoint integrity
        if not verify_checkpoint_hash(checkpoint):
            return Err("Checkpoint corrupted")
        
        # Restore state
        restore_ac_ids(checkpoint["ac_ids"])
        restore_audit_trail(checkpoint["audit_trail"])
        restore_evidence(checkpoint["evidence"])
        
        audit_logger.record(
            operation="CHECKPOINT_RESTORE",
            checkpoint_id=checkpoint_id,
        )
        
        return Ok(None)
```

---

## 📈 Metrics & Dashboard

### AC-ID Metrics

```python
@dataclass
class Tier1Metrics:
    """TIER 1 operational metrics."""
    
    total_ac_ids: int
    ac_defined: int
    ac_ready: int
    ac_in_progress: int
    ac_blocked: int
    ac_complete: int
    ac_verified: int
    ac_locked: int
    
    phase_completion: float      # 0.0 to 1.0
    evidence_quality: float      # Ratio of coherent evidence
    audit_trail_integrity: bool  # All chains valid
    average_ac_duration: timedelta
    
    @property
    def phase_progress(self) -> str:
        """Visual progress indicator."""
        filled = int(self.phase_completion * 20)
        return "█" * filled + "░" * (20 - filled)
```

### Dashboard Display

```
PHASE-1 Progress: ███████████░░░░░░░░░ 65%

AC-ID Status:
├─ ✅ COMPLETE:  23/35 (66%)
├─ ⏳ IN_PROGRESS: 5/35 (14%)
├─ 🟡 BLOCKED:   3/35 (9%)
├─ ⏸️  READY:     4/35 (11%)
└─ ⭕ VERIFIED:   15/23 (85%)

Evidence Quality: 94/98 coherent (96%)
Audit Trail Integrity: ✅ All chains valid
Average AC Duration: 2h 15m
```

---

## 🔗 Integration with Other Tiers

### TIER 0 → TIER 1

- TIER 1 enforces all TIER 0 rules
- AC-ID evidence validated against CORE rules
- Phase gates check TIER 0 compliance
- Violations escalate immediately

### TIER 1 → TIER 2

- AC-ID status determines response template type
- Phase affects response verbosity level
- Evidence informs composite request generation

### TIER 1 → TIER 3

- AC-ID context passed to knowledge retrieval
- Domain knowledge retrieved based on AC-ID type
- Retrieved knowledge validated against TIER 1 compliance

---

## ✅ Compliance Checklist (TIER 1)

Before phase lock:

- [ ] All AC-IDs have evidence
- [ ] Evidence is coherent (references valid)
- [ ] Audit trails valid (hash-chain intact)
- [ ] No outstanding blocked AC-IDs
- [ ] All AC-IDs verified or locked
- [ ] Dependencies acyclic
- [ ] Phase gates all passed
- [ ] No TIER 0 rule violations

---

## 📈 Implementation Status

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| AC-ID State Machine | ✅ Complete | 45 | 100% |
| Audit Trail | ✅ Complete | 50 | 100% |
| Evidence Tracking | ✅ Complete | 40 | 100% |
| Hash-Chain Verification | ✅ Complete | 25 | 100% |
| Governance Gates | ✅ Complete | 35 | 100% |
| **Total** | ✅ **Complete** | **195** | **100%** |

---

## 🔗 Related Documentation

- [Brain Index](00-brain-index.md) - System overview
- [TIER 0 Governance](01-tier0-governance.md) - Immutable rules
- [TIER 2 Templates](03-tier2-response-templates.md) - Response formatting
- [TIER 3 Knowledge](04-tier3-knowledge.md) - Domain knowledge
- [State Manager](../../cortex/brain/core/state_manager.py) - Implementation

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

