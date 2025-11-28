# Phased Implementation Template

**Purpose:** Reusable template for complex feature implementations requiring systematic development with clear checkpoints.

**Source:** Extracted from Track A Phase 1 implementation (100% success rate, 4.8 hours total)

**When to Use:**
- Complex features with multiple components (3+ major components)
- Features requiring integration between systems
- High-value features where quality > speed
- Features that benefit from incremental validation

**When NOT to Use:**
- Simple bug fixes or small enhancements
- Single-file changes
- Trivial refactoring
- Urgent hotfixes

---

## 📋 Phase Structure Overview

### Phase 1: Foundation Setup (5-10% of total time)

**Objective:** Establish project structure and infrastructure

**Deliverables:**
- [ ] Directory structure created
- [ ] Package/module initialization complete
- [ ] Progress tracking documents created
- [ ] Initial imports validated

**Success Criteria:**
- Structure validates (no import errors)
- Progress tracking in place
- Team understands architecture

**Time Estimate:** 30 minutes to 1 hour (depending on complexity)

---

### Phase 2: Core Implementation (70-80% of total time)

**Objective:** Build production components

**Deliverables:**
- [ ] Major components implemented
- [ ] Integration code written
- [ ] Basic documentation created
- [ ] Smoke tests passing

**Success Criteria:**
- Components implemented and documented
- Imports resolve correctly
- Basic functionality works (manual testing)
- Code reviewed (if applicable)

**Time Estimate:** 3-6 hours (depending on complexity)

---

### Phase 3: Validation & Debugging (10-20% of total time)

**Objective:** Achieve production-ready quality

**Deliverables:**
- [ ] Integration tests implemented
- [ ] All tests passing (100% pass rate target)
- [ ] Bugs identified and fixed
- [ ] Completion documentation created

**Success Criteria:**
- 100% test pass rate achieved
- All bugs documented with root causes
- Production-ready quality validated
- Completion report published

**Time Estimate:** 1-2 hours (depending on bugs found)

---

## 🛠️ Implementation Workflow

### Pre-Implementation Checklist

Before starting, ensure you have:

- [ ] **Clear Requirements** - Feature scope well-defined
- [ ] **Architecture Design** - Component interactions mapped
- [ ] **Success Metrics** - Know what "done" looks like
- [ ] **Time Budget** - Realistic estimate (4-10 hours typical)
- [ ] **Progress Tracking** - Document location decided

---

### Phase 1: Foundation Setup

#### Step 1.1: Create Directory Structure (15 minutes)

**Actions:**
```bash
# Create main feature directory
mkdir -p src/feature_name/

# Create subdirectories by responsibility
mkdir -p src/feature_name/core/           # Core functionality
mkdir -p src/feature_name/integrations/   # External integrations
mkdir -p src/feature_name/utils/          # Utility functions

# Create test directory
mkdir -p tests/feature_name/
```

**Documentation:**
- Create `src/feature_name/README.md` with architecture overview
- Document directory purpose and component relationships

---

#### Step 1.2: Initialize Packages/Modules (10 minutes)

**Python Example:**
```python
# src/feature_name/__init__.py
"""
Feature Name - [One-line description]

Components:
- core: [Description]
- integrations: [Description]
- utils: [Description]

Version: 1.0.0
Status: Development - Phase 1
"""

__version__ = "1.0.0"
__all__ = ["ComponentA", "ComponentB"]
```

**Documentation:**
- Add docstrings to all `__init__.py` files
- Document what will be implemented

---

#### Step 1.3: Create Progress Tracking (5 minutes)

**Create:** `cortex-brain/documents/planning/FEATURE-NAME-PROGRESS.md`

**Template:**
```markdown
# Feature Name Implementation Progress

**Start Date:** YYYY-MM-DD  
**Target Completion:** YYYY-MM-DD  
**Status:** Phase 1 - Foundation Setup

## Phase Overview

### Phase 1: Foundation Setup ✅ (COMPLETE)
- ✅ Directory structure created
- ✅ Packages initialized
- ✅ Progress tracking established

### Phase 2: Core Implementation 🟡 (IN PROGRESS)
- ⏳ Component A (not started)
- ⏳ Component B (not started)
- ⏳ Integration (not started)

### Phase 3: Validation 🔴 (NOT STARTED)
- ⏳ Integration tests
- ⏳ Bug fixes
- ⏳ Documentation

## Success Criteria
- [ ] All components implemented
- [ ] 100% test pass rate
- [ ] Documentation complete
- [ ] Production-ready quality
```

---

#### Step 1.4: Validate Foundation (5 minutes)

**Actions:**
```bash
# Verify imports work
python -c "from src.feature_name import *; print('✅ Foundation validated')"

# Verify structure
tree src/feature_name/
```

**Checkpoint:** If imports fail or structure incorrect, fix before proceeding to Phase 2.

---

### Phase 2: Core Implementation

#### Step 2.1: Component Breakdown (30 minutes)

**For each major component:**

1. **Define Interface/Contract**
   - Input parameters
   - Return values
   - Error handling
   - Dependencies

2. **Create Component File**
   ```python
   # src/feature_name/core/component_a.py
   """
   Component A - [Description]
   
   Responsibilities:
   - [Responsibility 1]
   - [Responsibility 2]
   
   Dependencies:
   - [Dependency 1]
   """
   
   class ComponentA:
       """[Description]"""
       
       def __init__(self, config: Dict[str, Any]):
           """Initialize component."""
           pass
       
       def primary_method(self, input: Any) -> Any:
           """[Description]"""
           pass
   ```

3. **Document Expected Behavior**
   - Add comprehensive docstrings
   - Document edge cases
   - Note assumptions

---

#### Step 2.2: Implement Components (2-4 hours)

**Implementation Priority:**

1. **Core Components First** - Foundation functionality
2. **Integration Components** - Connect to external systems
3. **Utility Functions** - Supporting functionality

**Best Practices:**

- ✅ **Write docstrings as you go** - Don't defer documentation
- ✅ **Handle errors explicitly** - Use try/except with meaningful messages
- ✅ **Log important events** - Use logging module
- ✅ **Keep functions focused** - Single Responsibility Principle
- ✅ **Validate inputs** - Check types and values

**Anti-Patterns to Avoid:**

- ❌ Implementing everything before testing anything
- ❌ Skipping error handling ("I'll add it later")
- ❌ Copy/pasting without understanding
- ❌ Hardcoding values that should be configurable

---

#### Step 2.3: Create Integration Points (1 hour)

**For each external system:**

```python
# src/feature_name/integrations/external_system_adapter.py
"""
External System Adapter - [Description]

Responsibilities:
- Connect to external system
- Transform data between formats
- Handle connection errors
"""

class ExternalSystemAdapter:
    """Adapter for [External System]."""
    
    def __init__(self, connection_string: str):
        """Initialize connection."""
        self.connection = self._establish_connection(connection_string)
    
    def fetch_data(self, query: str) -> Dict[str, Any]:
        """Fetch data from external system."""
        try:
            # Implementation
            pass
        except ConnectionError as e:
            # Handle connection errors
            pass
    
    def _establish_connection(self, connection_string: str):
        """Establish connection (internal method)."""
        pass
```

---

#### Step 2.4: Smoke Test (15 minutes)

**Manual verification before moving to Phase 3:**

```python
# Manual smoke test script
from src.feature_name.core import ComponentA
from src.feature_name.integrations import ExternalSystemAdapter

# Test Component A
component = ComponentA(config={})
result = component.primary_method(test_input)
print(f"Component A result: {result}")

# Test integration
adapter = ExternalSystemAdapter("test_connection_string")
data = adapter.fetch_data("test_query")
print(f"Adapter result: {data}")
```

**Checkpoint:** If smoke test fails, debug before proceeding to Phase 3.

---

### Phase 3: Validation & Debugging

#### Step 3.1: Create Integration Tests (30 minutes)

**Test Structure:**

```python
# tests/feature_name/test_integration.py
"""
Integration tests for Feature Name

Tests complete workflows end-to-end.
"""

import pytest
from src.feature_name.core import ComponentA
from src.feature_name.integrations import ExternalSystemAdapter

# Fixtures
@pytest.fixture
def component():
    """Component A fixture."""
    return ComponentA(config={"key": "value"})

@pytest.fixture
def adapter():
    """External system adapter fixture."""
    return ExternalSystemAdapter("test_connection_string")

# Tests
def test_component_basic_functionality(component):
    """Test Component A basic workflow."""
    result = component.primary_method("test_input")
    assert result is not None
    assert "expected_key" in result

def test_integration_end_to_end(component, adapter):
    """Test complete workflow from component to external system."""
    # Arrange
    test_data = {"input": "test"}
    
    # Act
    processed = component.primary_method(test_data)
    result = adapter.fetch_data(processed)
    
    # Assert
    assert result["status"] == "success"
    assert len(result["data"]) > 0
```

**Test Coverage Goals:**

- ✅ Happy path (expected inputs)
- ✅ Error handling (invalid inputs)
- ✅ Edge cases (empty, null, extreme values)
- ✅ Integration points (external system connections)

---

#### Step 3.2: Run Tests - First Iteration (5 minutes)

```bash
pytest tests/feature_name/test_integration.py -v
```

**Expected Outcome:** Some tests fail (this is normal!)

**Record Baseline:**
- Total tests: X
- Passing: Y
- Failing: Z
- Pass rate: Y/X %

---

#### Step 3.3: Systematic Debugging (30-60 minutes)

**Debugging Protocol:**

1. **Categorize Failures by Root Cause**
   - API contract issues (field names, structure)
   - Missing functionality
   - Error handling gaps
   - Integration wiring issues

2. **Apply Batch Fixes**
   - Fix all failures in one category together
   - Don't fix individually (less efficient)

3. **Document Each Bug**
   ```markdown
   ### Bug #1: Field Naming Inconsistency
   
   **Root Cause:** Component returns "success", test expects "status"
   
   **Before:**
   ```python
   return {"success": True, "data": result}
   ```
   
   **After:**
   ```python
   return {
       "status": "success",  # Standard field name
       "success": True,       # Backward compatibility
       "data": result
   }
   ```
   
   **Lesson:** Establish field naming conventions early
   ```

4. **Re-run Tests**
   ```bash
   pytest tests/feature_name/test_integration.py -v
   ```
   
   **Record Progress:**
   - Pass rate improved: Y/X % → Y2/X %
   - Bugs fixed this iteration: N

5. **Repeat Until 100% Pass Rate**

---

#### Step 3.4: Create Completion Documentation (15 minutes)

**Create:** `cortex-brain/documents/planning/FEATURE-NAME-COMPLETE.md`

**Template:**

```markdown
# Feature Name Implementation - COMPLETE ✅

**Completion Date:** YYYY-MM-DD  
**Total Time:** X.X hours  
**Quality Score:** XX/10

---

## 📊 Final Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Production Code | X,XXX lines | ✅ Complete |
| Integration Tests | X tests | ✅ 100% passing |
| Test Pass Rate | 100% (X/X) | ✅ Perfect |
| Bugs Fixed | X bugs | ✅ All resolved |
| Documentation | XXX lines | ✅ Comprehensive |

---

## 🎯 Deliverables

### Components Implemented
1. **ComponentA** (XXX lines) - [Description]
2. **ComponentB** (XXX lines) - [Description]
3. **ExternalSystemAdapter** (XXX lines) - [Description]

### Tests Created
- **Integration Tests** (X tests, 100% passing)
- **Fast execution** (X.XXs execution time)

### Documentation
- **README.md** - Feature overview
- **API Documentation** - Component interfaces
- **Completion Report** - This document

---

## 🐛 Bugs Fixed

### Bug #1: [Title]
**Root Cause:** [Explanation]
**Fix:** [Description]
**Lesson:** [Transferable principle]

### Bug #2: [Title]
**Root Cause:** [Explanation]
**Fix:** [Description]
**Lesson:** [Transferable principle]

---

## 💡 Key Learnings

1. **[Learning 1]** - [Description]
2. **[Learning 2]** - [Description]
3. **[Learning 3]** - [Description]

---

## 🔄 Next Steps

**Immediate:**
- [ ] Deploy to staging environment
- [ ] Monitor for issues
- [ ] Gather user feedback

**Future Enhancements:**
- [ ] Add comprehensive unit tests
- [ ] Optimize performance
- [ ] Add advanced features

---

**Status:** ✅ PRODUCTION READY
```

---

## 📊 Success Metrics

### Phase 1 Metrics
- [ ] Directory structure validated
- [ ] Imports working
- [ ] Progress tracking in place
- [ ] Duration: 30-60 minutes

### Phase 2 Metrics
- [ ] All components implemented
- [ ] Integration points working
- [ ] Smoke tests passing
- [ ] Duration: 3-6 hours

### Phase 3 Metrics
- [ ] 100% test pass rate achieved
- [ ] All bugs documented
- [ ] Completion report created
- [ ] Duration: 1-2 hours

### Overall Metrics
- [ ] Total time: 4-10 hours
- [ ] Quality: Production-ready
- [ ] Documentation: Comprehensive
- [ ] Learning: Patterns extracted

---

## 🎓 Lessons Learned Template

### Technical Lessons
1. **[Lesson Title]**
   - Issue: [What went wrong]
   - Solution: [How it was fixed]
   - Principle: [Transferable rule]

### Process Lessons
1. **[Lesson Title]**
   - Observation: [What was noticed]
   - Impact: [Effect on development]
   - Application: [How to apply in future]

### Quality Lessons
1. **[Lesson Title]**
   - Problem: [Quality issue encountered]
   - Resolution: [How quality was improved]
   - Prevention: [How to avoid in future]

---

## 🔄 Adaptation Guidelines

**Adjust time estimates if:**
- Feature complexity higher/lower than typical
- Team experience level different
- External dependencies involved
- Integration complexity varies

**Adjust phase structure if:**
- Simpler feature: Combine Phase 1 + 2
- More complex: Split Phase 2 into sub-phases
- Unclear requirements: Add Phase 0 (Discovery)
- High risk: Add Phase 4 (Hardening)

**Adjust validation if:**
- Critical feature: Add load testing
- User-facing: Add UI/UX validation
- Security-sensitive: Add security audit
- Performance-critical: Add benchmarking

---

## 📚 References

**Source Implementation:**
- Track A Phase 1 (CORTEX 3.0)
- Success Rate: 100%
- Time: 4.8 hours
- Quality: 12/10 (exceptional)

**Documentation:**
- `cortex-brain/documents/conversation-captures/2025-11-15-track-a-phase-1-implementation.md`
- `cortex-brain/TRACK-A-PHASE-1-VALIDATION-COMPLETE.md`
- `cortex-brain/TRACK-A-PHASE-1-COMPLETE.md`

**Optimization Principles:**
- `cortex-brain/optimization-principles.yaml` (systematic_debugging, phased_implementation)

---

**Template Version:** 1.0.0  
**Last Updated:** November 15, 2025  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
