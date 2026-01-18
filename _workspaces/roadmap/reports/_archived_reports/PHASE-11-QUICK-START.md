# PHASE-11 Quick Start Guide

## 📋 Overview
**Phase:** PHASE-11-HALLUCINATION-PREVENTION (Hallucination Prevention System)  
**Status:** ✅ READY TO START  
**Prerequisites:** ✅ PHASE-09-GOVERNANCE-TOOLS (locked), PHASE-10-ADAPTIVE-EXECUTION (locked)  
**Estimated Duration:** 28 hours (3.5 days)  
**Acceptance Criteria:** 6

---

## 🚀 Getting Started (First 5 Minutes)

### 1. Verify Prerequisites
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
grep "PHASE-09" .github/roadmap/cortex-master.yaml | grep -i "locked: true"
# Should show: ✅ PHASE-09 locked
```

### 2. Read Executive Summary
```bash
cat docs/PHASE-11-EXECUTIVE-SUMMARY.md
# Review AC breakdown (HP-001-01 through HP-003-02)
```

### 3. Review Phase Specifications
```bash
cat docs/phases/phase-11.yaml
# Understand each AC's requirements
```

---

## 📝 AC Implementation Order

### Week 1, Day 1: Intent & Boundaries (2 ACs)
```
HP-001-01: Intent Canonicalization Engine (6 hours)
HP-001-02: Behavioral Boundary Rules (8 hours)
```

**Command to start HP-001-01:**
```bash
# This will initiate TDD workflow for intent canonicalization
cd /Users/asifhussain/PROJECTS/CORTEX
python -m pytest tests/unit/test_intent_canonicalizer.py -v 2>&1 | grep -E "PASSED|FAILED|ERROR"
```

### Week 1, Day 2: Sandbox & Detection (2 ACs)
```
HP-002-01: Agent Execution Sandbox (8 hours)
HP-002-02: Hallucination Detection & Recovery (8 hours)
```

### Week 1, Day 2.5: Mutations & Confidence (2 ACs)
```
HP-003-01: Vision Mutation Tracking (6 hours)
HP-003-02: Agent Confidence Scoring (6 hours)
```

---

## 🏗️ Module Structure to Create

```bash
# Create the hallucination prevention module structure
mkdir -p src/hallucination_prevention/{
    intent_canonicalization,
    behavioral_boundaries,
    execution_sandbox,
    hallucination_detection,
    mutation_tracking,
    confidence_scoring
}

# Create __init__.py files for each submodule
touch src/hallucination_prevention/__init__.py
touch src/hallucination_prevention/intent_canonicalization/__init__.py
touch src/hallucination_prevention/behavioral_boundaries/__init__.py
touch src/hallucination_prevention/execution_sandbox/__init__.py
touch src/hallucination_prevention/hallucination_detection/__init__.py
touch src/hallucination_prevention/mutation_tracking/__init__.py
touch src/hallucination_prevention/confidence_scoring/__init__.py

# Create test files
touch tests/unit/test_intent_canonicalizer.py
touch tests/unit/test_boundary_enforcer.py
touch tests/unit/test_execution_sandbox.py
touch tests/unit/test_ssot_validator.py
touch tests/unit/test_mutation_tracker.py
touch tests/unit/test_confidence_scorer.py
```

---

## 🔧 TDD Workflow for Each AC

Follow this pattern for each acceptance criterion:

### Step 1: Create Test File
```bash
# Example for HP-001-01
cat > tests/unit/test_intent_canonicalizer.py << 'EOF'
"""Tests for IntentCanonicalizer - AC-HP-001-01"""
import pytest
from cortex.hallucination_prevention.intent_canonicalization import IntentCanonicalizer

class TestIntentCanonicalizer:
    def test_extract_ac_id_from_standard_format(self):
        """Extract AC-ID from standard AC-XX-YYY-ZZ format"""
        canonicalizer = IntentCanonicalizer()
        intent = "Please implement AC-EX-001-01"
        result = canonicalizer.canonicalize(intent)
        assert result.ac_id == "AC-EX-001-01"
    
    # ... more tests
EOF
```

### Step 2: Run Tests (All Fail - Expected)
```bash
pytest tests/unit/test_intent_canonicalizer.py -v
# Result: All tests FAIL (no implementation yet)
```

### Step 3: Implement Minimum Code
```bash
# Create the implementation file
cat > src/hallucination_prevention/intent_canonicalization/intent_canonicalizer.py << 'EOF'
"""Intent canonicalization engine - AC-HP-001-01"""

class IntentCanonicalizer:
    """Canonicalizes agent intents into structured format"""
    
    def canonicalize(self, intent: str):
        """Convert varied intent formats to canonical form"""
        pass
EOF
```

### Step 4: Run Tests Again
```bash
pytest tests/unit/test_intent_canonicalizer.py -v
# Result: Incrementally implement until all pass
```

### Step 5: Commit When Complete
```bash
git add -A
git commit -m "HP-001-01: Intent Canonicalization Engine - 20+ tests passing"
```

---

## 🔑 Key Classes to Implement

### HP-001-01: IntentCanonicalizer
```python
class IntentCanonicalizer:
    """Extracts AC-ID, phase, and action type from varied formats"""
    
    def canonicalize(self, intent: str) -> CanonicalIntent:
        """Convert varied intent formats to canonical structure"""
        
    def extract_ac_id(self, text: str) -> Optional[str]:
        """Extract AC-ID from text (handles: AC-XX-YYY-ZZ, ACXXYYYZZZ, descriptions)"""
        
    def identify_phase(self, ac_id: str, context: str) -> str:
        """Identify phase from AC-ID or explicit specification"""
        
    def classify_action(self, intent: str) -> ActionType:
        """Classify action type (CREATE, MODIFY, DELETE, QUERY, EXECUTE, ROLLBACK)"""
```

### HP-001-02: BoundaryEnforcer
```python
class BoundaryEnforcer:
    """Enforces behavioral boundaries on agent operations"""
    
    def check_operation(self, operation: Operation) -> OperationResult:
        """Validate operation against boundary rules"""
        
    def prevent_locked_phase_modification(self, ac_id: str) -> bool:
        """Block modifications to locked phases"""
        
    def prevent_ac_deletion(self, ac_id: str) -> bool:
        """Require approval for AC deletion"""
        
    def detect_governance_bypass(self, operation: Operation) -> List[ViolationLog]:
        """Detect attempts to bypass governance rules"""
```

### HP-002-01: ExecutionSandbox
```python
class ExecutionSandbox:
    """Isolated execution environment with rollback"""
    
    def execute_in_sandbox(self, action, dry_run=False):
        """Execute action in isolated sandbox"""
        
    def record_side_effect(self, effect: SideEffect):
        """Capture file/DB modifications"""
        
    def commit(self):
        """Persist changes atomically"""
        
    def rollback(self):
        """Restore pre-execution state"""
```

### HP-002-02: SSOTValidator
```python
class SSOTValidator:
    """Validates Single Source of Truth integrity"""
    
    def verify_integrity(self) -> ValidationResult:
        """Check SSOT for corruption patterns"""
        
    def detect_corruption(self) -> Optional[CorruptionReport]:
        """Identify corruption (phase state, AC inconsistencies)"""
        
    def trigger_recovery(self) -> RecoveryResult:
        """Automatically recover from detected corruption"""
```

### HP-003-01: MutationTracker
```python
class MutationTracker:
    """Tracks vision mutations from PHASE-06 protocol"""
    
    def record_mutation(self, mutation: VisionMutation):
        """Record vision mutation with timestamp"""
        
    def query_history(self, ac_id: str, time_range: TimeRange) -> List[VisionMutation]:
        """Query mutation history by AC or time"""
        
    def rollback_to_vision(self, timestamp: datetime):
        """Restore previous vision state"""
```

### HP-003-02: ConfidenceScorer
```python
class ConfidenceScorer:
    """Scores agent action confidence for risk assessment"""
    
    def score_action(self, action: AgentAction) -> ConfidenceScore:
        """Calculate confidence score (0.0-1.0)"""
        
    def _analyze_historical_patterns(self, action: AgentAction) -> float:
        """Score based on action similarity to historical patterns"""
        
    def _check_governance_conformance(self, action: AgentAction) -> float:
        """Score based on governance rule adherence"""
        
    def _assess_resource_availability(self, action: AgentAction) -> float:
        """Score based on available resources"""
```

---

## 📊 Test Coverage Requirements

Minimum per AC:
- **20+ test cases per AC** (6 ACs × 20 = 120+ tests minimum)
- **95%+ line coverage** for implementation
- **100% acceptance criteria coverage** (all test cases pass)
- **Integration tests** cross-AC boundary cases

---

## ✅ Governance Checklist

For each AC completion:

- [ ] All tests passing (pytest shows 100% pass rate)
- [ ] Type hints on all functions/methods
- [ ] Google-style docstrings on all classes/methods
- [ ] Specific exception handling (no bare except)
- [ ] Module names kebab-case, ≤25 characters
- [ ] Git commit with AC-HP-XXX-XX prefix
- [ ] SSOT validation passed on commit
- [ ] Phase documentation updated

---

## 🔄 Phase-to-Phase Dependencies

### Integration with Previous Phases

**PHASE-09 (Governance Tools):**
```python
from cortex.governance import GovernanceDB, AuditLog

db = GovernanceDB()
audit = AuditLog()  # Log hallucination detection events
ac_registry = db.get_ac_registry()  # Check AC existence
```

**PHASE-10 (Adaptive Execution):**
```python
from cortex.orchestrators.adaptive import ExecutionContext, OrchestratorRoutingEngine

context = ExecutionContext(...)
router = OrchestratorRoutingEngine()
# Use routing in sandbox execution decisions
```

**PHASE-07 (Extended IR-002):**
```python
# Extend IR-002-01 canonicalization with PHASE-11 enhancements
from cortex.infrastructure.canonicalization import BaseCanonicalizer

class IntentCanonicalizer(BaseCanonicalizer):
    """Extends IR-002-01 with AC-ID and phase extraction"""
```

### Integration with Future Phases

**PHASE-12 (Knowledge Ecosystem):**
- Confidence scoring used for knowledge validation
- Mutation tracking provides audit trail for knowledge updates
- Sandbox prevents knowledge corruption

---

## 📈 Progress Tracking

Update phase-11.yaml as you complete each AC:

```yaml
# After HP-001-01 completion:
AC-HP-001-01:
  status: "COMPLETED"
  tests_passing: 20
  git_checkpoint: "commit-hash"
  completed_at: "2026-01-XX..."

# Update phase progress:
progress_percentage: 16.7  # 1/6 ACs
completed_ac_ids: 1
```

---

## 🎯 Success Criteria

### Phase Complete When:
1. ✅ All 6 ACs with status=COMPLETED
2. ✅ 120+ tests all passing
3. ✅ Zero governance violations
4. ✅ SSOT hash chain valid
5. ✅ Phase locked with completion timestamp

### Code Quality:
- Type hint coverage: 100%
- Docstring coverage: 100%
- Test coverage: 95%+ lines
- Exception specificity: 100%
- Naming compliance: 100%

---

## 🆘 Debugging & Troubleshooting

### Test Failures
```bash
# Run single test file with verbose output
pytest tests/unit/test_intent_canonicalizer.py::TestIntentCanonicalizer::test_extract_ac_id_from_standard_format -vv

# Run with print statements
pytest tests/unit/test_intent_canonicalizer.py -vv -s
```

### Import Errors
```bash
# Verify module imports
python -c "from cortex.hallucination_prevention import IntentCanonicalizer"

# Check __init__.py exports
cat src/hallucination_prevention/__init__.py
```

### SSOT Validation Failures
```bash
# Check SSOT integrity
python -c "from cortex_brain.state.ssot_manager import SSOTManager; print(SSOTManager().verify_integrity())"

# View audit logs
sqlite3 cortex-brain/state/governance.db "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 10;"
```

---

## 📞 Quick Commands Reference

```bash
# Start phase implementation
cd /Users/asifhussain/PROJECTS/CORTEX

# Run all PHASE-11 tests
pytest tests/unit/test_hallucination_prevention*.py -v

# Run specific AC tests
pytest tests/unit/test_intent_canonicalizer.py -v

# Commit AC completion
git add -A && git commit -m "HP-XXX-XX: [Title] - [Number] tests passing"

# Update phase status
cat docs/phases/phase-11.yaml | grep progress_percentage

# Verify prerequisites
grep "PHASE-09.*locked: true" .github/roadmap/cortex-master.yaml
```

---

## 🎬 Begin Implementation

**You are ready to start PHASE-11 immediately.**

### First Action:
1. Read `/docs/PHASE-11-EXECUTIVE-SUMMARY.md` (5 min)
2. Review `/docs/phases/phase-11.yaml` specifications (10 min)
3. Create test directory structure (2 min)
4. Begin HP-001-01 TDD implementation (30 min)

**Command to begin:**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python -m pytest tests/unit/test_intent_canonicalizer.py::TestIntentCanonicalizer -v --tb=short 2>&1 | head -20
```

---

**Guide Generated:** 2026-01-15T17:19:25.734055Z  
**For:** PHASE-11-HALLUCINATION-PREVENTION  
**Status:** Ready for Implementation
