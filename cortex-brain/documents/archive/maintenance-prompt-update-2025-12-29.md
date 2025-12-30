# Maintenance Prompt Update Report

**Date:** December 29, 2025  
**Updated File:** `.github/prompts/cortex-maintenance.prompt.md`  
**Author:** GitHub Copilot

---

## 🎯 Objective

Enhance the CORTEX maintenance prompt to ensure critical new functionality is properly validated during system health checks:
1. **Interactive Planning Session** workflow
2. **Vision API Auto-Engagement** on image attachments
3. **Test Suite Health** validation

---

## 📝 Changes Made

### 1. Phase 1 Enhancement: Added Interactive Planning + Vision Validation

**Added Sections:**

#### 1a-2. Verify Interactive Planning Session ✨
- **Purpose:** Ensure the new interactive planning workflow is properly wired
- **Validates:**
  - Interactive session module exists
  - Session states defined (8 states: INITIALIZING → FINALIZED)
  - Workflow classes present (PlanningSession, DiscoveryEngine, ApprovalWorkflow, CleanupPhase)
  - State transitions validated
  - 29 tests passing (18 session + 11 workflow)

**Key Workflow States:**
```
INITIALIZING → DISCOVERY → CONTEXT_GATHERING → USER_REVIEW
USER_REVIEW → (APPROVED or REFINING)
APPROVED → DRAFTING → CLEANUP → FINALIZED
```

**Test Command:**
```bash
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v
```

#### 1a-3. Verify Vision API Auto-Engagement 👁️
- **Purpose:** Ensure Vision API automatically engages when images are attached
- **Validates:**
  - Vision orchestrator exists
  - Image detector exists
  - Vision context middleware exists
  - Auto-detection/analysis config enabled
  - Token budget enforcement (500 token limit)
  - Duplicate image caching (24hr TTL)

**Expected Features:**
- ✅ Automatic image detection in chat attachments
- ✅ Auto-engage Vision API without user prompting
- ✅ Context injection into planning/debugging workflows
- ✅ PNG, JPG, JPEG format support

**Smoke Test:**
```python
from src.tier1.vision_orchestrator import VisionOrchestrator
orchestrator = VisionOrchestrator(config)
result = orchestrator.process_request(
    user_request="analyze this",
    attachments=[{'type': 'image', 'path': '/test.png'}]
)
```

---

### 2. New Phase 4.5: Test Suite Health 🧪

**Purpose:** Validate test suite health during maintenance cycles

**When to Run Tests:**
- ✅ Interactive planning system modified
- ✅ Core orchestrators updated
- ✅ Brain protection rules changed
- ✅ Fixture patterns need validation
- ❌ Minor documentation updates (skip)
- ❌ Knowledge library additions (skip unless validation needed)

**Test Commands:**
```bash
# Full suite (397 tests, target ≥99% pass rate)
python3 -m pytest tests/orchestrators/planning/ --tb=no -q

# Core functionality only (29 tests, target 100%)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py \
                 tests/orchestrators/planning/test_toolkit_integration.py -v

# Quick categories via test runner
./test_planning.sh interactive   # 18 tests
./test_planning.sh toolkit        # 11 tests  
./test_planning.sh quick          # 29 tests
./test_planning.sh all            # 397 tests
```

**Health Metrics:**

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Core Tests Pass Rate | 100% | CRITICAL - Fix immediately |
| Full Suite Pass Rate | ≥99% | Review failures, assess if obsolete |
| Error Count | 0 | CRITICAL - All errors must be fixed |
| Test Execution Time | <30s | Acceptable, monitor for regression |

**Common Test Failures Documented:**
1. `ModuleNotFoundError: No module named 'core'` → Fix: Add toolkit to sys.path
2. `RuntimeError: Planning root not found` → Fix: Create planning/active directory
3. Tests passing but functionality broken → Fix: Check if testing obsolete API

---

### 3. Updated Success Criteria

Added three new validation requirements:

| New Check | Pass Condition |
|-----------|----------------|
| **Interactive Planning** | Session workflow tests 29/29 passing |
| **Vision Auto-Engagement** | Image detection and analysis wired |
| **Test Suite Health** | Core tests 100%, full suite ≥99% |

---

### 4. Enhanced Validation Checklist

**Added 3 new subsections:**

#### Interactive Planning Subsection (8 checks)
- [ ] Interactive session module exists
- [ ] SessionState enum with 8 states
- [ ] PlanningSession, DiscoveryEngine, ApprovalWorkflow, CleanupPhase classes exist
- [ ] State transitions validated
- [ ] Interactive planning tests: 29/29 passing
- [ ] End-to-end workflow test passing
- [ ] Conversation history tracking operational
- [ ] Iterative refinement loop functional

#### Vision API Auto-Engagement Subsection (10 checks)
- [ ] Vision orchestrator exists
- [ ] Image detector exists
- [ ] Vision context middleware exists
- [ ] Config has `auto_detect_images: true`
- [ ] Config has `auto_analyze_on_detect: true`
- [ ] Config has `auto_inject_context: true`
- [ ] Image detection works for PNG, JPG, JPEG
- [ ] Vision API auto-engages without prompting
- [ ] Duplicate image caching operational
- [ ] Token budget enforcement active

#### Test Suite Health Subsection (7 checks)
- [ ] Core tests: 29/29 passing (100%)
- [ ] Full suite: ≥396 passing (≥99%)
- [ ] Error count: 0
- [ ] Test execution time: <30s
- [ ] Test report generated
- [ ] Known issues documented
- [ ] Obsolete tests deleted

---

### 5. Updated Phase Count

Changed from **8-Phase** to **9-Phase** Maintenance Pipeline:

```
Phase 1:   Toolkit + Interactive + Vision Validation
Phase 2:   Quick Health Check
Phase 3:   Full Diagnostic
Phase 4:   Wiring Integrity
Phase 4.5: Test Suite Health 🆕
Phase 5:   Knowledge Library Validation
Phase 6:   Review Reports
Phase 7:   Intent Router Validation
Phase 8:   Regenerate Lean Prompts
Phase 9:   Report Management
```

---

## 🎯 Benefits

### 1. **Comprehensive Validation**
- Interactive planning workflow is now part of maintenance checks
- Vision API auto-engagement validated systematically
- Test suite health monitored and enforced

### 2. **Proactive Issue Detection**
- Catches missing interactive session components early
- Detects Vision API configuration issues before user reports
- Identifies test suite degradation immediately

### 3. **Clear Success Criteria**
- 100% pass rate for core tests (mandatory)
- ≥99% pass rate for full suite (target)
- 0 errors (critical requirement)

### 4. **Actionable Guidance**
- Common test failures documented with fixes
- When to run tests vs when to skip
- Specific commands for different test categories

---

## 📊 Impact Analysis

### Before Update
- ❌ No validation for interactive planning workflow
- ❌ No validation for Vision API auto-engagement
- ❌ No test suite health checks
- ❌ Test failures could go unnoticed

### After Update
- ✅ Interactive planning validated (29 tests checked)
- ✅ Vision API auto-engagement validated (10 checks)
- ✅ Test suite health enforced (99%+ pass rate)
- ✅ Test failures caught during maintenance
- ✅ Proactive issue detection

---

## 🔍 File Changes Summary

**File:** `.github/prompts/cortex-maintenance.prompt.md`

**Lines Added:** ~150 lines
- Phase 1a-2: Interactive Planning (~40 lines)
- Phase 1a-3: Vision API (~35 lines)
- Phase 4.5: Test Suite Health (~50 lines)
- Updated checklists (~25 lines)

**Total Sections Updated:** 4
1. Phase 1 (expanded)
2. Phase 4.5 (new)
3. Success Criteria (expanded)
4. Validation Checklist (expanded)

---

## ✅ Validation

To verify these changes are working, run:

```bash
# 1. Verify interactive planning
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v
# Expected: 18/18 passing

# 2. Verify Vision API components exist
test -f src/tier1/vision_orchestrator.py && echo "✅ Vision orchestrator exists"
test -f src/tier1/image_detector.py && echo "✅ Image detector exists"

# 3. Run full test suite
python3 -m pytest tests/orchestrators/planning/ --tb=no -q
# Expected: 396+ passing, <5 failing (≥99% pass rate)
```

---

## 🎉 Conclusion

The maintenance prompt now comprehensively validates:
1. **Interactive Planning Session** - 8-state workflow with 29 tests
2. **Vision API Auto-Engagement** - Automatic image analysis without prompting
3. **Test Suite Health** - 99%+ pass rate enforcement

These additions ensure CORTEX 4.0's newest features remain healthy and functional during every maintenance cycle! 🚀
