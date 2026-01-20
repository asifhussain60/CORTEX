# Quick Start: Begin PHASE-03 Implementation

**Status**: Ready to code  
**Time to First Test**: 5 minutes  
**First AC**: TBD (see phase_tracker.PHASE-03)  

---

## 30-Second Overview

✅ **PHASE-02 is LOCKED** (prerequisite done)  
✅ **All prerequisites met**  
✅ **Use cortex-builder.prompt.md workflow**  
✅ **Single source of truth**: `phase_tracker:` in cortex-master.yaml  
✅ **Pre-commit validates every commit**  

---

## Start Here: Load PHASE-03 Details

```bash
# Step 1: View the phase
grep -A 150 "PHASE-03:" _workspaces/roadmap/cortex-master.yaml | grep -A 200 "acceptance_criteria:"

# This shows you:
# - AC-IDs (6 total)
# - Title & description for each AC
# - estimated_hours for each AC
# - test_count for each AC
# - Current status (NOT_STARTED)
```

---

## TDD Workflow for AC-1 (Example)

### Phase 1: Write Tests (RED)

```bash
# Step 1: Create test file
mkdir -p tests/unit
cat > tests/unit/test_phase_03_ac_001.py << 'EOF'
"""
Tests for PHASE-03 AC-1: Production Reliability Framework
AC-ID: AC-???-001-01
"""
import pytest

class TestProductionReliabilityFramework:
    """Test production reliability framework implementation."""
    
    def test_circuit_breaker_initialization(self):
        """Circuit breaker should initialize with default state."""
        # TODO: Implement test
        pytest.skip("Not yet implemented")
    
    def test_circuit_breaker_opens_on_threshold(self):
        """Circuit breaker should open when threshold exceeded."""
        # TODO: Implement test
        pytest.skip("Not yet implemented")
    
    # Add more tests based on acceptance criteria
EOF

# Step 2: Run tests (RED - should fail)
pytest tests/unit/test_phase_03_ac_001.py -v
```

### Phase 2: Write Code (GREEN)

```bash
# Step 1: Create implementation file
mkdir -p src/reliability
cat > src/reliability/circuit_breaker.py << 'EOF'
"""
Circuit breaker pattern for production reliability.

Implements:
- AC-???-001-01: Production Reliability Framework
"""

class CircuitBreaker:
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int = 5):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def reset(self) -> None:
        """Reset the circuit breaker."""
        self.failure_count = 0
        self.state = "CLOSED"
EOF

# Step 2: Implement tests to pass
# Step 3: Run tests (GREEN)
pytest tests/unit/test_phase_03_ac_001.py -v
```

### Phase 3: Update Phase Tracker

```bash
# Step 1: Edit cortex-master.yaml
# Find: phase_tracker.PHASE-03.acceptance_criteria[0] (first AC)
# Update status to: COMPLETED
# Add: completed_date: 2026-01-18
# Add: verified: true
# Add: tests_passing: 10

# Example (in YAML):
# - ac_id: AC-???-001-01
#   status: COMPLETED  <- CHANGED
#   completed_date: 2026-01-18  <- ADDED
#   verified: true  <- ADDED
#   tests_passing: 10  <- ADDED
```

### Phase 4: Validate & Commit

```bash
# Step 1: Run validator
python3 scripts/validate_phase_sync.py

# Step 2: Commit (pre-commit hook validates automatically)
git add tests/unit/test_phase_03_ac_001.py src/reliability/circuit_breaker.py _workspaces/roadmap/cortex-master.yaml
git commit -m "phase-03: AC-???-001-01 COMPLETED - Production Reliability Framework"

# Pre-commit hook automatically:
# - Validates phase sync
# - Checks AC-ID naming
# - Updates metadata if needed
# - Prevents broken states
```

---

## Governance Rules (Must Follow)

### CORE-001: Incremental Execution
```python
# ✅ GOOD: Function <500 lines
def process_event(event: Dict) -> Result:
    """Process event with validation."""
    # ... implementation ...
    return Result(success=True)

# ❌ BAD: Function >500 lines
def huge_function():
    # ... 600 lines of code ...
```

### CORE-008: TDD Pattern
```
RED   → Write failing test
GREEN → Write minimal code to pass
REFACTOR → Improve code quality
```

### CORE-011: Type Hints
```python
# ✅ GOOD: Type hints mandatory
def create_circuit_breaker(
    failure_threshold: int,
    timeout_seconds: float
) -> CircuitBreaker:
    """Create a new circuit breaker."""
    return CircuitBreaker(failure_threshold, timeout_seconds)

# ❌ BAD: Missing type hints
def create_circuit_breaker(failure_threshold, timeout_seconds):
    return CircuitBreaker(failure_threshold, timeout_seconds)
```

### CORE-012: Docstrings
```python
# ✅ GOOD: Google-style docstrings
def record_failure(self) -> None:
    """Record a failure and potentially open the circuit.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        None
    """
    self.failure_count += 1

# ❌ BAD: Missing docstring
def record_failure(self):
    self.failure_count += 1
```

### CORE-028: Portable Paths
```python
# ✅ GOOD: Use Path(__file__).parent
from pathlib import Path

config_file = Path(__file__).parent / "config.yaml"

# ❌ BAD: Hardcoded /Users/ path
config_file = "/Users/asifhussain/CORTEX/config.yaml"
```

---

## Validate Before Committing

```bash
# Check phase sync
python3 scripts/validate_phase_sync.py

# Expected output:
# ✓ Metadata counts...
# ✓ Phase structure...
# ✓ AC-ID uniqueness...
# ✓ Dependencies (no cycles)...
# ✓ VALIDATION PASSED
```

---

## Full Checklist: First AC

- [ ] Read PHASE-03 acceptance criteria from phase_tracker
- [ ] Understand the AC requirement (what needs to be built)
- [ ] Create test file with RED tests
- [ ] Run tests (confirm they fail)
- [ ] Create implementation file
- [ ] Implement code to pass tests
- [ ] Run tests (confirm they pass)
- [ ] Add type hints to all functions
- [ ] Add Google-style docstrings
- [ ] Update phase_tracker: set AC status to COMPLETED
- [ ] Run validator: `python3 scripts/validate_phase_sync.py`
- [ ] Commit: `git commit -m "phase-03: AC-???-001-01 COMPLETED"`
- [ ] Move to AC-2, repeat

---

## Useful Commands

```bash
# View all ACs in PHASE-03
grep -A 200 "PHASE-03:" _workspaces/roadmap/cortex-master.yaml

# Count tests passing
pytest tests/unit/test_phase_03_ac_*.py -v --tb=short

# Run single AC test
pytest tests/unit/test_phase_03_ac_001.py::TestProductionReliabilityFramework::test_circuit_breaker_initialization -v

# Check phase status
python3 -c "
import yaml
with open('_workspaces/roadmap/cortex-master.yaml') as f:
    data = yaml.safe_load(f)
    p = data['phase_tracker']['PHASE-03']
    print(f\"PHASE-03: {p['completed_ac_ids']}/{p['ac_ids']} complete\")
"

# Validate before commit
python3 scripts/validate_phase_sync.py

# Commit with validation
git add -A && git commit -m "phase-03: AC-???-001-01 COMPLETED"
```

---

## File Structure

```
CORTEX/
├── _workspaces/roadmap/
│   └── cortex-master.yaml          ← CANONICAL PHASE DATA
│       └── phase_tracker:          ← Load AC details from here
│           └── PHASE-03:
│               └── acceptance_criteria:
├── src/
│   └── reliability/                ← New feature code here
│       └── circuit_breaker.py
├── tests/
│   └── unit/
│       └── test_phase_03_ac_*.py   ← Tests for each AC
└── scripts/
    └── validate_phase_sync.py      ← Run before commit
```

---

## 5-Minute Startup Script

```bash
#!/bin/bash
# Save as: start-phase-03.sh
# Run as: bash start-phase-03.sh

set -e

echo "🚀 Starting PHASE-03 Implementation"
echo ""

# Step 1: Create branches and folders
git checkout -b phase-03-implementation
mkdir -p src/reliability
mkdir -p tests/unit
echo "✓ Branch created, folders ready"

# Step 2: Create test template
cat > tests/unit/test_phase_03_ac_001.py << 'EOF'
"""Tests for PHASE-03 AC-1."""
import pytest

class TestPhase03AC001:
    def test_placeholder(self):
        pytest.skip("Ready for implementation")
EOF

# Step 3: Create implementation template
cat > src/reliability/circuit_breaker.py << 'EOF'
"""PHASE-03 AC-001: Production Reliability Framework."""

class CircuitBreaker:
    """Placeholder implementation."""
    pass
EOF

# Step 4: Show what to do next
echo ""
echo "✓ Templates created"
echo ""
echo "Next steps:"
echo "1. Open tests/unit/test_phase_03_ac_001.py and write RED tests"
echo "2. Run: pytest tests/unit/test_phase_03_ac_001.py -v"
echo "3. Open src/reliability/circuit_breaker.py and implement code"
echo "4. Run tests until GREEN"
echo "5. Update cortex-master.yaml: set AC status to COMPLETED"
echo "6. Run: python3 scripts/validate_phase_sync.py"
echo "7. Commit: git commit -m 'phase-03: AC-001-01 COMPLETED'"
echo ""
echo "Ready to code! 🎯"
```

---

## Troubleshooting

### Tests Won't Pass
```bash
# Check what you missed
pytest tests/unit/test_phase_03_ac_001.py -v --tb=long

# Verify imports
python3 -c "from src.reliability.circuit_breaker import CircuitBreaker; print('✓ Import works')"
```

### Validation Fails
```bash
# Run detailed validation
python3 scripts/validate_phase_sync.py --verbose

# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('_workspaces/roadmap/cortex-master.yaml'))"
```

### Commit Blocked
```bash
# Pre-commit hook issue?
# Run manually:
python3 scripts/validate_phase_sync.py

# If passes, commit with --no-verify (not recommended)
git commit --no-verify -m "message"
```

---

## Summary

1. ✅ All prerequisites satisfied
2. ✅ No blockers
3. ✅ SSOT principle applied
4. ✅ Pre-commit validation ready
5. ✅ Governance rules enforced

**Ready to implement PHASE-03!**

Start with TDD: Write test → Run (RED) → Implement → Run (GREEN) → Commit

---

**Questions?** See:
- PHASE-UNLOCK-READINESS-VERIFICATION.md (prerequisites)
- IMPLEMENTATION-GUIDE-NEXT-PHASES.md (detailed workflow)
- DETAILED-AC-INVENTORY.md (AC details)
- cortex-builder.prompt.md (official reference)
