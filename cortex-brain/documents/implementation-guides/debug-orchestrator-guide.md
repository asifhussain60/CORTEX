# Debug Orchestrator Implementation Guide

**Version:** 2.0.0  
**Author:** Asif Hussain  
**Created:** January 4, 2026  
**Status:** Complete

---

## 📋 Overview

The Debug Orchestrator provides intelligent debugging workflow with autonomous execution, error analysis, root cause detection, fix generation, and automated verification.

### Key Features

✅ **Bug Report Parsing** - Natural language and structured format support  
✅ **Error Analysis** - Stack trace parsing and categorization  
✅ **Root Cause Detection** - Pattern matching with confidence scoring  
✅ **Fix Generation** - Multiple solution paths with impact assessment  
✅ **Template Injection** - CORTEX_DEBUG_ markers for logging  
✅ **One-Shot Cleanup** - Automated marker removal with verification  
✅ **Git Checkpoints** - Rollback capability at key phases  
✅ **Pattern Learning** - Knowledge graph integration  
✅ **Quality Gates** - DoR/DoD enforcement  
✅ **Autonomous Workflow** - Full workflow automation

---

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from src.orchestrators.debug import DebugOrchestrator

# Initialize
orchestrator = DebugOrchestrator(workspace_root=Path("/path/to/project"))

# Start debug session
result = orchestrator.parse_bug_report(
    description="ImportError when running tests",
    error_message="ImportError: No module named 'missing_module'",
    test_failures=["tests/test_module.py::test_function"]
)

print(f"Session ID: {result['session_id']}")
```

### Autonomous Workflow

```python
# Execute complete workflow autonomously
result = orchestrator.execute_debug_workflow_autonomously(
    bug_description="Tests failing with ImportError",
    error_message="ImportError: No module named 'missing_module'",
    target_files=["src/main.py"],
    auto_apply_fix=False  # Manual approval for fixes
)

print(f"Status: {result['status']}")
print(f"Phases: {result['phases_completed']}")
print(f"Root Causes: {len(result['root_causes'])}")
```

---

## 🔍 Workflow Phases

### Phase 1: Bug Report Intake

**Implementation:** DBG-001

Parses bug reports from multiple sources:
- Natural language descriptions
- Error messages
- Stack traces
- Test failure lists

```python
result = orchestrator.parse_bug_report(
    description="Function crashes with AttributeError",
    error_message="AttributeError: 'NoneType' object has no attribute 'method'",
    stack_trace="...",
    test_failures=["test_service.py::test_function"]
)
```

**Output:**
- Session ID
- Error type and category
- Affected components
- Affected files
- Severity assessment

### Phase 2: Review Integration

**Implementation:** DBG-002

Triggers contextual architectural review scoped to bug context:

```python
review_findings = orchestrator.run_contextual_review()
```

**Findings Classification:**
- BLOCKER - Must fix before proceeding
- CRITICAL - High priority issues
- INFO - Informational findings

### Phase 3: Debug Marker Injection

**Implementation:** DBG-003

Injects CORTEX_DEBUG_ markers for logging:

```python
injection_result = orchestrator.inject_debug_markers(
    target_files=["src/service.py", "src/helper.py"],
    injection_strategy="moderate"  # minimal, moderate, comprehensive
)
```

**Strategies:**
- **Minimal** - Entry points only (main, __init__, run)
- **Moderate** - Public methods (not starting with _)
- **Comprehensive** - All functions

**Marker Format (Python):**
```python
# CORTEX_DEBUG_START - Session: {session_id} - Location: {location}
import logging
_cortex_logger = logging.getLogger("cortex.debug.{session_id}")
_cortex_logger.debug("CORTEX_DEBUG: {location} - Entry")
_cortex_logger.debug(f"CORTEX_DEBUG: {location} - State: {locals()}")
# CORTEX_DEBUG_END
```

### Phase 4: Root Cause Analysis

**Implementation:** DBG-006

Generates ranked hypotheses using:
- Error pattern matching
- Review findings correlation
- Code flow analysis (from debug logs)
- Test correlation patterns

```python
root_causes = orchestrator.analyze_root_cause(debug_logs=[...])

for cause in root_causes:
    print(f"Rank {cause['rank']}: {cause['hypothesis']}")
    print(f"Confidence: {cause['confidence']:.1%}")
    print(f"Evidence: {cause['evidence']}")
```

**Confidence Scoring:**
- 0.85-1.0: Very High
- 0.70-0.84: High
- 0.50-0.69: Medium
- <0.50: Low

### Phase 5: Fix Generation

**Implementation:** DBG-005

Generates actionable fix proposals:

```python
fix_proposals = orchestrator.generate_fix_proposals(max_proposals=3)

for fix in fix_proposals:
    print(f"{fix['title']} (confidence: {fix['confidence']:.1%})")
    print(f"Approach: {fix['approach']}")
    print(f"Impact: {fix['impact']['scope']} scope, {fix['impact']['risk']} risk")
    print("\nSteps:")
    for step in fix['fix_steps']:
        print(f"  {step}")
```

**Fix Categories:**
- Import Addition (90% automatable)
- Type Conversion (80% automatable)
- Path Correction (85% automatable)
- Logic Correction (70% automatable)

### Phase 6: Fix Verification

**Implementation:** DBG-005

Apply and verify fixes with test execution:

```python
verification = orchestrator.apply_and_verify_fix(
    fix_proposal=best_fix,
    run_tests=True
)

if verification['test_results']['status'] == 'passed':
    print("✅ Fix verified!")
else:
    print("❌ Tests still failing - trying next fix")
```

### Phase 7: Marker Cleanup

**Implementation:** DBG-004

One-shot removal of all debug markers:

```python
cleanup_result = orchestrator.cleanup_debug_markers(verify=True)

print(f"Markers removed: {cleanup_result['markers_removed']}")
print(f"Files cleaned: {cleanup_result['file_count']}")
print(f"Verification: {'✅ PASSED' if cleanup_result['verification_passed'] else '❌ FAILED'}")
```

**Verification:**
- Scans workspace for remaining markers
- Reports count and locations
- Fails if any markers remain

### Phase 8: Pattern Learning

**Implementation:** DBG-010

Captures patterns for future use:

```python
pattern_result = orchestrator.learn_debug_patterns()

print(f"Patterns learned: {pattern_result['patterns_learned']}")
# Patterns stored in Tier 2 Knowledge Graph
```

---

## ✅ Quality Gates

### Definition of Ready (DoR)

**Implementation:** DBG-015

Validates bug is ready for debugging:

```python
bug_data = {
    "reproducible": True,
    "affected_files": ["src/main.py"],
    "test_failures": ["test_module::test_case"]
}

is_ready, unmet_criteria = orchestrator.validate_dor(bug_data)

if not is_ready:
    for criterion in unmet_criteria:
        print(f"❌ {criterion}")
```

**DoR Criteria:**
- [ ] Bug is reproducible
- [ ] Affected files identified
- [ ] Tests failing consistently

### Definition of Done (DoD)

**Implementation:** DBG-015

Validates session completion:

```python
is_complete, unmet_criteria = orchestrator.validate_dod()

if is_complete:
    print("✅ Debug session complete!")
else:
    for criterion in unmet_criteria:
        print(f"❌ {criterion}")
```

**DoD Criteria:**
- [ ] All tests passing
- [ ] Zero debug markers remaining
- [ ] Patterns learned to Tier 2
- [ ] Git checkpoint created

---

## 🔄 Git Checkpoint Integration

**Implementation:** DBG-014

Automatic checkpoints at key phases:

```python
# Checkpoints created automatically:
# 1. Pre-injection
# 2. Post-fix-application
# 3. Post-cleanup

# Access checkpoint history
checkpoints = orchestrator.current_session.git_checkpoints
print(f"Checkpoints: {', '.join(checkpoints)}")
```

**Checkpoint Naming:**
```
debug-pre-injection-20260104-143022
debug-post-fix-application-20260104-143145
debug-post-cleanup-20260104-143230
```

---

## 📊 Error Pattern Library

### Import Errors

**Pattern:** `missing_import`  
**Confidence:** 90%  
**Fix:** Add import statement

```python
# Before
def use_module():
    return ModuleName.function()

# After
from package import ModuleName

def use_module():
    return ModuleName.function()
```

### Type Mismatches

**Pattern:** `type_mismatch`  
**Confidence:** 80%  
**Fix:** Add type conversion

```python
# Before
def process(value: int):
    return value + 10

process("5")  # TypeError

# After
def process(value: int):
    return value + 10

process(int("5"))  # OK
```

### Null References

**Pattern:** `null_reference`  
**Confidence:** 75%  
**Fix:** Add None check

```python
# Before
result = obj.method()  # obj is None

# After
if obj is not None:
    result = obj.method()
else:
    result = default_value
```

### Logic Errors

**Pattern:** `incorrect_logic`  
**Confidence:** 70%  
**Fix:** Correct conditional

```python
# Before
if value == 0:
    return "positive"  # Wrong!

# After
if value > 0:
    return "positive"
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all debug orchestrator tests
pytest tests/orchestrators/debug/ -v

# Run specific test class
pytest tests/orchestrators/debug/test_debug_orchestrator.py::TestErrorAnalyzer -v

# Run with coverage
pytest tests/orchestrators/debug/ --cov=src/orchestrators/debug --cov-report=html
```

### Test Coverage

**Current Coverage:** 100% (all critical requirements)

**Test Categories:**
- Error Analysis (DBG-001)
- Root Cause Detection (DBG-006)
- Fix Generation (DBG-005)
- Marker Injection (DBG-003)
- Marker Cleanup (DBG-004)
- Autonomous Workflow (DBG-016)
- Quality Gates (DBG-015)
- Git Checkpoints (DBG-014)
- Phase Events (DBG-012)

---

## 🎯 Examples

### Example 1: Simple Import Error

```python
orchestrator = DebugOrchestrator(Path.cwd())

result = orchestrator.execute_debug_workflow_autonomously(
    bug_description="Tests fail with ImportError",
    error_message="ImportError: No module named 'requests'",
    test_failures=["tests/test_api.py::test_get_data"],
    auto_apply_fix=False
)

# Output:
# Root Cause: Missing module import (confidence: 90%)
# Fix Proposal: Add missing import
# Steps:
#   1. Identify the missing module name from error message
#   2. Add import statement at top of affected file
#   3. Verify import path is correct
#   4. Run tests to verify fix
```

### Example 2: Type Mismatch

```python
result = orchestrator.execute_debug_workflow_autonomously(
    bug_description="Function fails with wrong type",
    error_message="TypeError: expected int, got str",
    stack_trace="File 'app.py', line 42, in process_data",
    target_files=["src/app.py"]
)

# Output:
# Root Cause: Incorrect data type passed to function (confidence: 80%)
# Fix Proposal: Fix Type Mismatch
# Impact: low scope, medium risk
```

### Example 3: Manual Debugging with Markers

```python
# Parse bug
orchestrator.parse_bug_report(
    description="Complex logic error",
    test_failures=["tests/test_complex.py"]
)

# Inject markers
orchestrator.inject_debug_markers(
    target_files=["src/complex_module.py"],
    injection_strategy="comprehensive"
)

# Run code and collect logs...
debug_logs = ["Variable x is None at line 42", "Entering loop iteration 5"]

# Analyze
root_causes = orchestrator.analyze_root_cause(debug_logs=debug_logs)

# Generate fixes
fixes = orchestrator.generate_fix_proposals()

# Apply best fix
orchestrator.apply_and_verify_fix(fixes[0])

# Cleanup
orchestrator.cleanup_debug_markers()
```

---

## 🔧 Configuration

### Injection Strategies

Customize marker injection behavior:

```python
# Minimal: Only main entry points
injector.inject_markers(target_files=[...], strategy="minimal")

# Moderate: Public methods (default)
injector.inject_markers(target_files=[...], strategy="moderate")

# Comprehensive: All functions
injector.inject_markers(target_files=[...], strategy="comprehensive")
```

### Root Cause Confidence Thresholds

Adjust confidence requirements:

```python
# Only show high-confidence hypotheses
high_confidence = [h for h in hypotheses if h['confidence'] > 0.7]
```

---

## 📚 Integration

### With TDD Workflow

```python
# TDD Workflow triggers debug on test failure
from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

tdd = TDDWorkflowOrchestrator()
tdd.on_bug_reported(bug_description="Test failed", failing_tests=[...])
# Automatically triggers DebugOrchestrator
```

### With Review Orchestrator

```python
# Debug automatically triggers contextual review
orchestrator.run_contextual_review()
# Returns scoped architectural findings
```

### With Knowledge Graph

```python
# Patterns automatically saved after successful debug
orchestrator.learn_debug_patterns()
# Stored in Tier 2 for future pattern matching
```

---

## 🐛 Troubleshooting

### Issue: Markers not found

**Solution:** Check file paths are correct and files exist

```python
# Verify files
for file in target_files:
    if not Path(file).exists():
        print(f"❌ File not found: {file}")
```

### Issue: Low confidence fixes

**Solution:** Provide more context (stack trace, debug logs)

```python
# Better
orchestrator.analyze_root_cause(
    debug_logs=collected_logs  # Improves confidence
)
```

### Issue: Cleanup verification fails

**Solution:** Check for nested markers or malformed tags

```python
# Count markers manually
remaining = cleanup.count_remaining_markers()
print(f"Remaining markers: {remaining}")
```

---

## 📖 Requirements Coverage

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| DBG-001 | Bug Report Intake | ✅ Complete |
| DBG-002 | Review Integration | ✅ Complete |
| DBG-003 | Template Injection | ✅ Complete |
| DBG-004 | Marker Cleanup | ✅ Complete |
| DBG-005 | Fix Verification Loop | ✅ Complete |
| DBG-006 | Root Cause Analysis | ✅ Complete |
| DBG-007 | Browser Console Bridge | ✅ Complete |
| DBG-008 | Log File Instrumentation | ✅ Complete |
| DBG-009 | Session Persistence | ✅ Complete |
| DBG-010 | Pattern Learning | ✅ Complete |
| DBG-011 | Event Tracing | ✅ Complete |
| DBG-012 | Phase Events | ✅ Complete |
| DBG-013 | Response Templates | ✅ Complete |
| DBG-014 | Git Checkpoints | ✅ Complete |
| DBG-015 | Quality Gates | ✅ Complete |
| DBG-016 | Autonomous Workflow | ✅ Complete |

---

## 🎓 Best Practices

1. **Always validate DoR** before starting debug session
2. **Use moderate strategy** for marker injection (balances coverage and noise)
3. **Review top 3 root causes** before applying fixes
4. **Create git checkpoint** before applying fixes manually
5. **Verify marker cleanup** after every session
6. **Learn patterns** from successful debug sessions

---

## 📞 Support

For issues or questions:
- Check test suite: `tests/orchestrators/debug/`
- Review manifest: `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`
- Consult response templates: `cortex-brain/response-templates/debug-templates.yaml`

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
