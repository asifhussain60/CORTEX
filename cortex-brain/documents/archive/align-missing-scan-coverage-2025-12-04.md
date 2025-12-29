# CORTEX Align - Missing Scan Coverage Analysis

**Date:** December 4, 2025  
**Author:** Asif Hussain  
**Context:** Comprehensive audit of align orchestrator scan coverage

---

## 🎯 Executive Summary

**Current Coverage:** Align scans 3 locations
**Missing Coverage:** 3 additional locations with 49+ executable files
**Impact:** ~39% of executable codebase invisible to align orchestrator

---

## 📊 Current Scan Coverage

### ✅ Currently Scanned (3 locations)

| Location | Purpose | File Count | Status |
|----------|---------|------------|--------|
| `src/operations/*.py` | User-facing commands | 13 files | ✅ Scanned |
| `src/orchestrators/*.py` | Complex workflows | 8 files | ✅ Scanned (fixed today) |
| `src/operations/modules/` | Utility modules | 57 files | ✅ Scanned |
| **TOTAL** | | **78 files** | **100% coverage** |

---

## ⚠️ Missing Scan Coverage (3 locations)

### 1. `src/workflows/` - Workflow Definitions (29 files)

**Purpose:** Multi-stage workflow orchestration (TDD, feature development, planning)

**Key Files Found:**
- `workflow_engine.py` - Core workflow execution engine
- `tdd_workflow_orchestrator.py` - TDD workflow controller
- `tdd_workflow_integrator.py` - Integration with TDD system
- `feature_workflow.py` - Feature development workflow
- `workflow_pipeline.py` - Pipeline orchestration
- `stages/dod_dor_clarifier.py` - DoR/DoD validation stage
- `stages/threat_modeler.py` - Threat modeling stage
- `stages/doc_generator.py` - Documentation generation stage
- `stages/code_cleanup.py` - Code cleanup stage

**Registration Status:** ❌ NONE registered

**User Impact:** HIGH
- Users can't trigger workflows via natural language
- No response templates for workflow operations
- Intent router doesn't recognize workflow commands

**Should Be Registered?** 🤔 **DEPENDS**
- **YES for orchestrators:** `tdd_workflow_orchestrator.py`, `workflow_engine.py`
- **NO for stages:** Individual stages are internal components, not user-facing
- **Recommendation:** Register top-level workflow orchestrators (3-5 files)

---

### 2. `src/cortex_agents/` - Specialized Agents (19 files)

**Purpose:** AI agents with specialized capabilities (test generation, health checks, screenshot analysis)

**Key Files Found:**
- `application_health_agent.py` - Health monitoring agent
- `screenshot_analyzer.py` - Vision API screenshot analysis
- `test_generator/agent.py` - Test generation orchestrator
- `test_generator/mutation_tester.py` - Mutation testing
- `test_generator/coverage_analyzer.py` - Coverage analysis
- `test_generator/pattern_learner.py` - Pattern learning
- `test_generator/failure_analyzer.py` - Test failure analysis

**Registration Status:** ❌ NONE registered

**User Impact:** MEDIUM
- Agents work but aren't discoverable via natural language
- No standardized response format
- Hard to invoke agents directly

**Should Be Registered?** 🤔 **DEPENDS**
- **YES for top-level agents:** `application_health_agent.py`, `screenshot_analyzer.py`
- **NO for sub-agents:** `test_generator/*` are components of TestGeneratorAgent
- **Recommendation:** Register user-facing agents only (2-3 files)

---

### 3. `src/entry_points/` - Entry Point Scripts (1 file)

**Purpose:** CLI/API entry points for CORTEX features

**Key Files Found:**
- `ux_enhancement_entry_point.py` - UX enhancement system entry point

**Registration Status:** ❌ NOT registered

**User Impact:** LOW
- Entry points are infrastructure, not user operations
- Typically invoked programmatically, not via chat

**Should Be Registered?** ❌ **NO**
- Entry points are internal plumbing
- Users don't directly invoke entry points
- Registration would clutter operations list

---

## 📋 Registration Decision Matrix

### Criteria for Registration

An operation should be registered if it meets **ANY** of these criteria:

1. ✅ **User-Invocable:** User can/should trigger it via natural language
2. ✅ **Standalone:** Can execute independently without parent orchestrator
3. ✅ **Response-Worthy:** Needs standardized response format
4. ✅ **Discoverable:** Should appear in help/documentation
5. ❌ **Internal Component:** Part of larger operation (don't register)
6. ❌ **Infrastructure:** Plumbing/framework code (don't register)

### Recommended Additions

| File | Register? | Reason | Priority |
|------|-----------|--------|----------|
| `workflows/tdd_workflow_orchestrator.py` | ✅ YES | User-facing TDD workflow | P0 |
| `workflows/workflow_engine.py` | ✅ YES | Core workflow execution | P1 |
| `workflows/feature_workflow.py` | ✅ YES | Feature development flow | P1 |
| `cortex_agents/application_health_agent.py` | ✅ YES | User-invocable health checks | P0 |
| `cortex_agents/screenshot_analyzer.py` | ✅ YES | Vision API analysis | P0 |
| `workflows/stages/*` | ❌ NO | Internal workflow components | N/A |
| `cortex_agents/test_generator/*` | ❌ NO | Sub-components of agent | N/A |
| `entry_points/*` | ❌ NO | Infrastructure code | N/A |

**Total Recommended:** 5 new operations (3 workflows + 2 agents)

---

## 🔧 Implementation Plan

### Phase 1: Add Workflows Directory Scan

**Target:** `src/workflows/*.py` (top-level only, exclude `stages/`)

**Code Changes:**
```python
# feature_registration_validator.py
def __init__(self, project_root: Optional[Path] = None):
    self.operations_dir = self.project_root / "src" / "operations"
    self.orchestrators_dir = self.project_root / "src" / "orchestrators"
    self.workflows_dir = self.project_root / "src" / "workflows"  # NEW
    self.modules_dir = self.operations_dir / "modules"
    
    self.excluded_files = {
        "__init__.py",
        "base_operation_module.py",
        "workflow_base.py",  # NEW
        "rollback_command_parser.py",
    }

def scan_operations_directory(self) -> List[str]:
    # ... existing code ...
    
    # Scan src/workflows/*.py (exclude stages/)
    if not self.workflows_dir.exists():
        logger.warning(f"Workflows directory not found: {self.workflows_dir}")
    else:
        for file in self.workflows_dir.glob("*.py"):  # Top-level only
            if file.name not in self.excluded_files:
                operations.append(file.stem)
```

**Expected Additions:** 8-10 workflow files discovered

---

### Phase 2: Add Agents Directory Scan

**Target:** `src/cortex_agents/*.py` (top-level only, exclude subdirectories)

**Code Changes:**
```python
# feature_registration_validator.py
def __init__(self, project_root: Optional[Path] = None):
    # ... existing code ...
    self.agents_dir = self.project_root / "src" / "cortex_agents"  # NEW
    
    self.excluded_files = {
        "__init__.py",
        "base_agent.py",  # NEW
        "agent_base.py",  # NEW
        # ... existing excludes ...
    }

def scan_operations_directory(self) -> List[str]:
    # ... existing code ...
    
    # Scan src/cortex_agents/*.py (exclude subdirectories)
    if not self.agents_dir.exists():
        logger.warning(f"Agents directory not found: {self.agents_dir}")
    else:
        for file in self.agents_dir.glob("*.py"):  # Top-level only
            if file.name not in self.excluded_files:
                operations.append(file.stem)
```

**Expected Additions:** 2-3 agent files discovered

---

### Phase 3: Smart Filtering

**Problem:** Not all Python files are operations

**Solution:** Add heuristic filters

```python
def is_registerable_operation(file_path: Path) -> bool:
    """
    Determine if a Python file should be registered as an operation.
    
    Heuristics:
    - Has execute() or run() or main() function
    - Has docstring with operation description
    - Not in excluded subdirectories (stages/, internal/, etc.)
    - Not a base class or utility
    """
    try:
        content = file_path.read_text()
        
        # Must have executable entry point
        has_entry_point = any(pattern in content for pattern in [
            'def execute(',
            'def run(',
            'def main(',
            'def orchestrate(',
        ])
        
        if not has_entry_point:
            return False
        
        # Must have docstring (operation description)
        has_docstring = '"""' in content or "'''" in content
        
        return has_docstring
        
    except Exception:
        return False
```

---

## 📊 Impact Analysis

### Before Additional Scans
- **Scannable Locations:** 3 (operations, orchestrators, modules)
- **Total Files Scanned:** 78
- **Registration Rate:** 100% of scanned files

### After Additional Scans (Recommended)
- **Scannable Locations:** 5 (+ workflows, + agents)
- **Total Files Scanned:** ~85-90 (78 + 5 recommended + 2-5 discovered)
- **Registration Rate:** ~95% (some workflow stages excluded)

### After Additional Scans (All Files)
- **Scannable Locations:** 5
- **Total Files Scanned:** ~126 (78 + 29 workflows + 19 agents)
- **Registration Rate:** ~62% (many internal components excluded)
- **⚠️ Risk:** Over-registration clutters operations list

---

## 🎯 Recommendations

### Recommended Approach: **Selective Registration**

1. ✅ **Add workflows/ scan** - Register top-level orchestrators only
2. ✅ **Add cortex_agents/ scan** - Register user-facing agents only
3. ✅ **Add smart filtering** - Exclude internal components automatically
4. ❌ **Don't register stages/** - Internal workflow components
5. ❌ **Don't register test_generator/** - Sub-components of TestGeneratorAgent
6. ❌ **Don't register entry_points/** - Infrastructure code

### Implementation Priority

**P0 (Critical):**
- Add `workflows/` scan with `stages/` exclusion
- Add `cortex_agents/` scan with subdirectory exclusion

**P1 (High):**
- Implement `is_registerable_operation()` filter
- Add workflow-specific metadata extraction

**P2 (Medium):**
- Add agent-specific response templates
- Create workflow documentation auto-generation

**P3 (Low):**
- Scan plugin directories (if extensible)
- Scan custom user operations (if supported)

---

## 🧪 Testing Strategy

### Test Case 1: Workflows Discovery
```python
# Expected: Find 8-10 workflow orchestrators
validator = FeatureRegistrationValidator()
ops = validator.scan_operations_directory()
workflow_ops = [op for op in ops if 'workflow' in op]
assert len(workflow_ops) >= 5  # At least 5 workflows
```

### Test Case 2: Smart Filtering
```python
# Expected: Exclude workflow stages
ops = validator.scan_operations_directory()
assert 'dod_dor_clarifier' not in ops  # Stage, not operation
assert 'tdd_workflow_orchestrator' in ops  # Orchestrator
```

### Test Case 3: Agent Discovery
```python
# Expected: Find 2-3 top-level agents
ops = validator.scan_operations_directory()
agent_ops = [op for op in ops if 'agent' in op or 'analyzer' in op]
assert 'application_health_agent' in agent_ops
assert 'screenshot_analyzer' in agent_ops
```

---

## 🔍 Current vs. Recommended Coverage

### Current Scan Pattern
```
src/
  ├── operations/*.py          ✅ SCANNED
  ├── orchestrators/*.py       ✅ SCANNED
  └── operations/modules/*/    ✅ SCANNED
```

### Recommended Scan Pattern
```
src/
  ├── operations/*.py          ✅ SCANNED
  ├── orchestrators/*.py       ✅ SCANNED
  ├── workflows/*.py           ✅ ADD (exclude stages/)
  ├── cortex_agents/*.py       ✅ ADD (exclude subdirs)
  └── operations/modules/*/    ✅ SCANNED
```

### Not Recommended (Over-Registration)
```
src/
  ├── workflows/stages/        ❌ DON'T SCAN (internal)
  ├── cortex_agents/*/         ❌ DON'T SCAN (sub-components)
  ├── entry_points/            ❌ DON'T SCAN (infrastructure)
  ├── utils/                   ❌ DON'T SCAN (utilities)
  └── core/                    ❌ DON'T SCAN (framework)
```

---

## 📝 Summary

**Answer to "What other folders should align look at?"**

1. ✅ **`src/workflows/*.py`** - Top-level workflow orchestrators (5-8 files)
2. ✅ **`src/cortex_agents/*.py`** - User-facing agents (2-3 files)
3. ❌ **`src/entry_points/`** - Infrastructure, don't register
4. ❌ **`src/workflows/stages/`** - Internal components, don't register
5. ❌ **`src/cortex_agents/*/`** - Sub-components, don't register

**Total New Operations:** ~5-11 files (selective registration)

**Implementation Effort:** LOW
- 2 new directory scans
- 1 smart filter function
- ~30 lines of code

**User Impact:** HIGH
- Workflows discoverable via natural language
- Agents standardized response format
- Complete system coverage

---

**Next Steps:**
1. Implement workflows/ and cortex_agents/ scans
2. Add smart filtering for stages/ and subdirectories
3. Test with full system alignment
4. Document newly discovered operations

---

**Report Generated:** December 4, 2025 11:15 AM  
**Status:** Analysis Complete - Awaiting Implementation Approval
