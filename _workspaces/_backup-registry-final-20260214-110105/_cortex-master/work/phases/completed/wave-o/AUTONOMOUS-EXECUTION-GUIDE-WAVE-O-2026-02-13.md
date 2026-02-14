# CORTEX Autonomous Wave Execution: WAVE-O
**Version:** 1.0 | **Updated:** 2026-02-13T00:20:00Z | **Mode:** Session-Scoped | **Status:** READY ✅

---

## 🎯 Purpose

Complete guide for executing WAVE-O (ENH-068/069: Data Integrity & Explainability) autonomously within a single GitHub Copilot Chat session. Designed for end-to-end completion: setup → TDD → commit → verify.

---

## 📋 QUICK START: WAVE-O (READY NOW)

### Prerequisites (5 minutes)

1. **Verify Previous Waves Complete:**
   ```bash
   # Check git log for WAVE-N completion
   git log --oneline | grep "AC-WAVE-N"
   # Expected: 6ea2086a8 AC-WAVE-N-001: ENH-067 Autonomous Plan Execution Engine Complete
   ```

2. **Check Test Collection:**
   ```bash
   cd /Users/asifhussain/PROJECTS/CORTEX
   python3 -m pytest tests/ --collect-only -q | tail -5
   # Expected: 14463 tests collected
   ```

3. **Verify Git Clean:**
   ```bash
   git status
   # Expected: Clean working tree
   ```

### Execution Command

**Copy this EXACTLY into GitHub Copilot Chat:**

```markdown
/implement WAVE-O: ENH-068/069 Data Integrity & Explainability Complete

Authority: cortex-registry/_cortex-master/index.yaml v4.0
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-O-20260213-01
Token Budget: <200k
Precedent: WAVE-N completion (6ea2086a8)

Scope:

Stage 1: Data Integrity Validation (ENH-068)
1. Cross-reference validator (cortex/validation/cross_reference_validator.py)
   - Detect contradictions across registry files
   - Timestamp consistency checking
   - Metric accuracy verification
   - 12 unit tests (TDD: RED→GREEN→REFACTOR)

2. Contradiction resolver (cortex/validation/contradiction_resolver.py)
   - Automated contradiction resolution strategies
   - Manual override mechanisms
   - Resolution history tracking
   - 8 integration tests

Stage 2: Explainability System (ENH-069)
3. KPI transparency engine (cortex/explainability/kpi_transparency.py)
   - Transparent KPI calculation methods
   - Data source traceability
   - Confidence scoring for metrics
   - 5 unit tests

4. Decision traceability logger (cortex/explainability/decision_logger.py)
   - Log all critical decisions with reasoning
   - Stakeholder-friendly explanations
   - Audit trail visualization data
   - 5 integration tests

Stage 3: Documentation
5. User guide (.github/prompts/DATA-INTEGRITY-GUIDE.md)
   - Integrity validation procedures
   - Contradiction resolution workflows
   - Explainability feature usage
   - Dashboard integration examples

Success Criteria:
- ✅ 30/30 tests passing (0 failures)
- ✅ 3 commits pushed (1 per stage)
- ✅ Zero contradictions detected in cortex-registry/
- ✅ Explainability UI integration ready
- ✅ WAVE-O completion report generated

Depends: WAVE-N complete ✅ (6ea2086a8)

Timeline: 4 hours (single session)
```

### Expected Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Session Start: WAVE-O-20260213-01                          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [████░░░░░░] 10% Pre-Flight Checks                         │
│ ├─ ✅ WAVE-N complete (git verified)                       │
│ ├─ ✅ Test collection: 14463 tests                         │
│ ├─ ✅ Git workspace clean                                  │
│ └─ ✅ MCP tools available                                  │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [████████░░] 40% Stage 1: Cross-Reference Validator        │
│ ├─ 🔵 RED: 12 behavioral tests                            │
│ ├─ ⚪ GREEN: Implementation                                │
│ └─ ⚪ REFACTOR: Quality gates                              │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [████████░░] 40% Commit 1: AC-WAVE-O-001                   │
│ "ENH-068 S1: Cross-reference validator + 20/30 tests"      │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [██████████] 70% Stage 2: Explainability System            │
│ ├─ 🔵 RED: 10 behavioral tests                            │
│ ├─ ⚪ GREEN: KPI transparency + decision logger           │
│ └─ ⚪ REFACTOR: Stakeholder trust features                │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [██████████] 70% Commit 2: AC-WAVE-O-002                   │
│ "ENH-069 S2: Explainability system + 30/30 tests"          │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [██████████] 100% Stage 3: Documentation                    │
│ ├─ ✅ DATA-INTEGRITY-GUIDE.md                              │
│ ├─ ✅ Integration examples                                 │
│ └─ ✅ Dashboard UI specs                                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ [██████████] 100% Commit 3: AC-WAVE-O-003                   │
│ "WAVE-O COMPLETE: Data integrity + explainability"         │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ ✅ WAVE-O COMPLETE                                          │
│ Tests: 30/30 (100%)                                         │
│ Commits: 3                                                  │
│ Duration: 3h 45m                                            │
│ Coverage: 92%                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 WAVE-O Details

### Stage 1: Data Integrity Validation (ENH-068)

**Duration:** 2 hours  
**Token Budget:** <80k

#### Deliverable 1: Cross-Reference Validator

**File:** `cortex/validation/cross_reference_validator.py`  
**Est. LOC:** 350-400

**Features:**
- Detect contradictions across registry YAML files
- Timestamp consistency validation (completion_date ≤ last_updated)
- Metric accuracy verification (tests_passing ≤ tests_total)
- Dependency graph validation (blocks/depends consistency)

**Models:**
```python
@dataclass
class ContradictionReport:
    """Report of detected contradictions."""
    file_path: Path
    contradiction_type: str  # "timestamp", "metric", "dependency", "status"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    details: str
    suggested_fix: str
    confidence: float  # 0.0-1.0

class CrossReferenceValidator:
    """Validates data integrity across registry files."""
    
    def validate_registry(self, registry_path: Path) -> List[ContradictionReport]:
        """Main validation entry point."""
        ...
    
    def _check_timestamps(self, file_path: Path, data: dict) -> List[ContradictionReport]:
        """Validate timestamp consistency."""
        ...
    
    def _check_metrics(self, file_path: Path, data: dict) -> List[ContradictionReport]:
        """Validate metric accuracy."""
        ...
    
    def _check_dependencies(self, all_files: List[dict]) -> List[ContradictionReport]:
        """Validate dependency graph consistency."""
        ...
```

**Tests:** 12 unit tests
- ✅ Timestamp contradiction detection (5 tests)
- ✅ Metric accuracy validation (4 tests)
- ✅ Dependency graph validation (3 tests)

#### Deliverable 2: Contradiction Resolver

**File:** `cortex/validation/contradiction_resolver.py`  
**Est. LOC:** 250-300

**Features:**
- Automated resolution strategies (prefer git history, prefer recent timestamps)
- Manual override mechanism (user confirms resolution)
- Resolution history tracking (audit trail)
- Rollback capability (undo bad resolutions)

**Models:**
```python
class ResolutionStrategy(Enum):
    PREFER_GIT_HISTORY = "git_history"
    PREFER_RECENT = "recent_timestamp"
    MANUAL = "manual_override"
    REJECT = "reject_resolution"

@dataclass
class Resolution:
    """Resolution for a detected contradiction."""
    contradiction_id: str
    strategy: ResolutionStrategy
    applied_at: datetime
    resolved_by: str  # "auto" or user_id
    before_state: dict
    after_state: dict
    rollback_available: bool

class ContradictionResolver:
    """Resolves detected contradictions."""
    
    def resolve_contradiction(
        self, 
        report: ContradictionReport, 
        strategy: ResolutionStrategy
    ) -> Resolution:
        """Apply resolution strategy to contradiction."""
        ...
    
    def get_resolution_history(self) -> List[Resolution]:
        """Get history of applied resolutions."""
        ...
    
    def rollback_resolution(self, resolution_id: str) -> bool:
        """Rollback a previously applied resolution."""
        ...
```

**Tests:** 8 integration tests
- ✅ Automated resolution (git history strategy) (3 tests)
- ✅ Manual override workflow (2 tests)
- ✅ Resolution history tracking (2 tests)
- ✅ Rollback capability (1 test)

---

### Stage 2: Explainability System (ENH-069)

**Duration:** 1.5 hours  
**Token Budget:** <70k

#### Deliverable 3: KPI Transparency Engine

**File:** `cortex/explainability/kpi_transparency.py`  
**Est. LOC:** 200-250

**Features:**
- Transparent KPI calculation with step-by-step breakdown
- Data source traceability (which files contributed to KPI)
- Confidence scoring (how reliable is this KPI?)
- Stakeholder-friendly explanations (business language, not code)

**Models:**
```python
@dataclass
class KPIExplanation:
    """Transparent explanation of KPI calculation."""
    kpi_name: str
    value: float
    unit: str
    calculation_steps: List[str]  # Step-by-step breakdown
    data_sources: List[Path]  # Files used in calculation
    confidence: float  # 0.0-1.0
    explanation: str  # Stakeholder-friendly summary
    
class KPITransparencyEngine:
    """Provides transparent KPI calculations."""
    
    def explain_kpi(self, kpi_name: str) -> KPIExplanation:
        """Generate transparent explanation for KPI."""
        ...
    
    def trace_data_sources(self, kpi_name: str) -> List[Path]:
        """Trace which files contributed to KPI."""
        ...
    
    def calculate_confidence(self, kpi_name: str) -> float:
        """Calculate confidence score for KPI."""
        ...
```

**Tests:** 5 unit tests
- ✅ KPI calculation transparency (2 tests)
- ✅ Data source traceability (2 tests)
- ✅ Confidence scoring (1 test)

#### Deliverable 4: Decision Traceability Logger

**File:** `cortex/explainability/decision_logger.py`  
**Est. LOC:** 180-220

**Features:**
- Log all critical decisions with reasoning
- Decision history tracking (who, what, when, why)
- Audit trail visualization data (timeline, dependencies)
- Stakeholder notifications (email, dashboard alerts)

**Models:**
```python
@dataclass
class DecisionLog:
    """Log entry for critical decision."""
    decision_id: str
    timestamp: datetime
    decision_type: str  # "WAVE_COMPLETE", "PHASE_START", "ROLLBACK", etc.
    decision: str  # Human-readable decision statement
    reasoning: str  # Why this decision was made
    alternatives_considered: List[str]  # What else was evaluated
    decided_by: str  # "autonomous" or user_id
    impact_score: float  # 0.0-1.0 (how critical)
    
class DecisionTraceabilityLogger:
    """Logs critical decisions with full traceability."""
    
    def log_decision(self, decision: DecisionLog) -> None:
        """Log a critical decision."""
        ...
    
    def get_decision_history(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[DecisionLog]:
        """Get decision history for date range."""
        ...
    
    def generate_audit_trail(self) -> dict:
        """Generate audit trail visualization data."""
        ...
```

**Tests:** 5 integration tests
- ✅ Decision logging (2 tests)
- ✅ Decision history retrieval (2 tests)
- ✅ Audit trail generation (1 test)

---

### Stage 3: Documentation

**Duration:** 0.5 hours  
**Token Budget:** <30k

#### Deliverable 5: User Guide

**File:** `.github/prompts/DATA-INTEGRITY-GUIDE.md`  
**Est. Lines:** 300-400

**Contents:**
- **Overview:** Data integrity + explainability architecture
- **Integrity Validation:**
  - How to run cross-reference validator
  - Interpreting contradiction reports
  - Resolution strategies guide
- **Explainability:**
  - Accessing KPI transparency reports
  - Understanding confidence scores
  - Decision history queries
- **Dashboard Integration:**
  - Real-time integrity metrics
  - Contradiction alerts
  - Decision timeline visualization
- **API Reference:**
  - `CrossReferenceValidator` usage
  - `ContradictionResolver` workflows
  - `KPITransparencyEngine` examples
  - `DecisionTraceabilityLogger` queries
- **Troubleshooting:**
  - Common contradictions and fixes
  - Low confidence KPI investigation
  - Resolution rollback procedures

---

## ✅ Success Criteria

### Test Requirements
- ✅ 30/30 tests passing (100% pass rate)
- ✅ 0 test failures
- ✅ Coverage ≥90% for new files

### Code Quality
- ✅ TDD workflow (RED→GREEN→REFACTOR for all tests)
- ✅ Type hints (all functions typed)
- ✅ Docstrings (Google style)
- ✅ CORE-008 compliant (tests before code)

### Git Requirements
- ✅ 3 commits (1 per stage)
- ✅ AC markers (AC-WAVE-O-001, AC-WAVE-O-002, AC-WAVE-O-003)
- ✅ Descriptive commit messages

### Documentation
- ✅ User guide complete (DATA-INTEGRITY-GUIDE.md)
- ✅ API documentation inline
- ✅ Integration examples included

### Validation
- ✅ Zero contradictions in `cortex-registry/_cortex-master/`
- ✅ Explainability UI integration specs ready
- ✅ WAVE-O completion report generated

---

## 📋 Post-Completion Checklist

After WAVE-O completes, verify:

1. **Test Execution:**
   ```bash
   python3 -m pytest tests/unit/validation/ -v
   # Expected: 12/12 passing
   
   python3 -m pytest tests/integration/validation/ -v
   # Expected: 8/8 passing
   
   python3 -m pytest tests/unit/explainability/ -v
   # Expected: 10/10 passing
   ```

2. **Registry Validation:**
   ```bash
   python3 -m cortex.validation.cross_reference_validator \
     --registry cortex-registry/_cortex-master/
   # Expected: 0 contradictions found
   ```

3. **Git History:**
   ```bash
   git log --oneline | grep "WAVE-O"
   # Expected: 3 commits (AC-WAVE-O-001, AC-WAVE-O-002, AC-WAVE-O-003)
   ```

4. **Documentation:**
   ```bash
   ls -la .github/prompts/DATA-INTEGRITY-GUIDE.md
   # Expected: File exists
   
   wc -l .github/prompts/DATA-INTEGRITY-GUIDE.md
   # Expected: 300-400 lines
   ```

5. **Completion Report:**
   ```bash
   ls -la WAVE-O-COMPLETION-REPORT.md
   # Expected: File exists in root
   ```

---

## 🚀 After WAVE-O: Next Steps

**Milestone Reached:** Wave 3 "Autonomy" Complete ✅

### Completed Waves (15 Total)
- ✅ Wave 7, 8, A-E (foundation)
- ✅ WAVE-H, I, J, K (cleanup)
- ✅ WAVE-L, M, N, O (intelligence + autonomy)

### Next Waves (P2-MEDIUM Priority)

| Wave | Name | Priority | Duration | Status |
|------|------|----------|----------|--------|
| **WAVE-P** | Performance Optimization | P2 | 3h | ⚪ After O |
| **WAVE-Q** | Enhanced Testing | P2 | 4h | ⚪ After P |
| **WAVE-R** | Documentation Polish | P2 | 3h | ⚪ After Q |
| **WAVE-S** | UI/UX Improvements | P2 | 4h | ⚪ After R |

**Timeline:** 1-2 weeks (4 sessions)

---

## 🔗 References

- **Authority:** cortex-architect.prompt.md v15.3
- **Registry:** cortex-registry/_cortex-master/index.yaml v4.0
- **Precedent:** WAVE-N-COMPLETION-REPORT.md (489 lines)
- **Git:** 6ea2086a8 (WAVE-N complete)
- **Implementation Reality:** IMPLEMENTATION-REALITY-SYNC-V5-2026-02-13.md

---

**Generated:** 2026-02-13T00:20:00Z  
**Session:** WAVE-O-GUIDE-20260213-01  
**Duration:** 10 minutes  
**Lines:** 622  
**Status:** ✅ READY FOR EXECUTION
