# 🤖 CORTEX Machine Onboarding Guide

**Version:** 1.0.0 | **Date:** December 13, 2025  
**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 📋 Purpose

This guide enables machines (AI assistants, automated systems) to intelligently assimilate CORTEX updates after pulling the latest code. Follow these steps to realign and wire in all new enhancements immediately.

---

## ⚡ Quick Start (5 Minutes)

```bash
# 1. Pull latest changes
git pull origin CORTEX-3.0

# 2. Read this onboarding document
cat MACHINE-ONBOARDING.md

# 3. Run automated realignment
system maintenance

# 4. Verify integration
pytest tests/ --cov=src
```

---

## 🎯 What Changed: December 13, 2025 Updates

### 1️⃣ Master Planner Visual Tracker Enhancement

**Location:** `src/orchestrators/session_model.py` (PlanningSession class)

**New Capabilities:**
- **Timing Metrics:** Phase start/end timestamps with timezone awareness
- **Token Tracking:** Per-phase and total token consumption
- **Duration Formatting:** Human-readable durations (2h 15m, 3m 45s, 45s)
- **Sub-Plan Integration:** Track when sub-plans update master tracker

**New Fields:**
```python
phase_start_times: Dict[str, datetime]  # Phase start timestamps
phase_end_times: Dict[str, datetime]    # Phase completion timestamps
tokens_used: Dict[str, int]             # Per-phase token consumption
total_tokens_used: int                  # Total tokens across all phases
timezone: str                           # Auto-detected system timezone
sub_plan_updates: List[Dict[str, Any]]  # Sub-plan tracker updates
```

**New Methods:**
```python
record_phase_start(phase_name: str)
record_phase_end(phase_name: str, tokens_used: int)
record_sub_plan_update(sub_plan_name: str, phase_completed: str, notes: str)
_format_duration(seconds: float) -> str
_get_phase_duration(phase_name: str) -> str
```

**Enhanced Method:**
```python
render_progress_table() -> str  # Now includes timing, tokens, sub-plan updates
```

---

### 2️⃣ Planning Orchestrator Integration

**Location:** `src/orchestrators/planning_orchestrator.py`

**Enhanced Method:**
```python
update_phase_status(
    phase_name: str,
    status: str = 'in_progress',
    progress: int = 0,
    tokens_used: int = 0  # NEW PARAMETER
) -> None
```

**Automatic Behaviors:**
- **Auto-Start Recording:** When status='in_progress', automatically records phase start time
- **Auto-Completion Recording:** When status='completed', records end time + tokens
- **Progress Logging:** Logs timing and token metrics to console
- **Visual Rendering:** Displays updated progress table after phase completion

**Example Usage:**
```python
# Phase start (auto-records start time)
orchestrator.update_phase_status("Phase 1: RED", status="in_progress", progress=0)

# Phase completion (auto-records end time + tokens)
orchestrator.update_phase_status("Phase 1: RED", status="completed", progress=100, tokens_used=3200)
```

---

### 3️⃣ Sub-Plan Template Checkpoint Gates

**Location:** `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md`

**New Sections:**
- **Master Tracker Update Template:** Added at top of Migration Strategy section
- **Phase Checkpoints:** Added after EVERY phase (5 total)
- **Mandatory Gates:** Work CANNOT proceed to next phase until tracker is updated

**Checkpoint Pattern:**
```markdown
**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase X completion:
- Record status: ✅ Phase X [NAME] - COMPLETE
- Add metrics: duration, files created/modified, tests passing, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase X+1 until master tracker is updated**

---
```

**Impact:** Ensures master plan always has real-time visibility into sub-plan progress.

---

### 4️⃣ Manifest Documentation

**Location:** `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml`

**Enhanced Requirement:** REQ-005 (Visual Progress Rendering)

**Added:**
- Implementation notes detailing all enhancements
- Actual effort hours (6h)
- Implementation files list
- Enhancement date (2025-12-13)

**Status:** `implemented` → Fully operational in production

---

## 🔧 Integration Instructions

### Step 1: Verify Code Changes

```bash
# Check all modified files
git diff HEAD~1 src/orchestrators/session_model.py
git diff HEAD~1 src/orchestrators/planning_orchestrator.py
git diff HEAD~1 cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md
git diff HEAD~1 cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml
```

### Step 2: Run System Maintenance

```bash
# Option A: Via Copilot Chat (Recommended)
# In GitHub Copilot Chat, type:
system maintenance

# Option B: Via CLI (if available)
python -m src.main system maintenance
```

**What It Does:**
1. **Pre-Healthcheck:** Validate current system state
2. **Align:** Auto-fix inconsistencies
3. **Cleanup:** Remove orphaned files
4. **Optimize:** Performance improvements
5. **Refresh Prompts:** Regenerate documentation
6. **Post-Healthcheck:** Verify system integrity

### Step 3: Verify Test Coverage

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific tests for new functionality
pytest tests/orchestrators/test_session_model.py -v
pytest tests/orchestrators/test_planning_orchestrator.py -v
```

**Expected Results:**
- All tests passing (100%)
- No coverage regressions
- New methods covered by tests

### Step 4: Validate Planning System Integration

**Test Plan Execution:**
```bash
# Start interactive planning session
# In Copilot Chat:
plan feature: User Authentication

# Observe enhanced progress tracking:
# - Phase start/end timestamps
# - Token consumption metrics
# - Duration tracking
# - Sub-plan update recording
```

**Expected Output:**
```markdown
### 📊 Master Planner Visual Tracker

**Plan:** User Authentication
**Started:** 2025-12-13 14:30:00 UTC-05:00
**Duration:** 2h 15m
**Tokens Used:** 8,500 tokens
**Overall Progress:** 60.0% (3/5 phases)

| Phase | Name | Status | Progress | Duration | Tokens | Tasks |
|-------|------|--------|----------|----------|--------|-------|
| 🔴 Phase 1 | RED | Completed | ████████████ 100% | 45m | 3,200 | 12/12 |
| 🟢 Phase 2 | GREEN | Completed | ████████████ 100% | 1h 10m | 4,800 | 8/8 |
| 🔵 Phase 3 | REFACTOR | In Progress | ████░░░░░░░░ 30% | 20m ⏳ | 500 | 2/6 |
| ⚙️ Phase 4 | CUTOVER | Pending | ░░░░░░░░░░░░ 0% | - | - | 0/4 |
| 🧹 Phase 5 | CLEANUP | Pending | ░░░░░░░░░░░░ 0% | - | - | 0/3 |

**Sub-Plan Tracker Updates:** ✅ 2 updates recorded
```

---

## 🧪 Testing Checklist

- [ ] **System Maintenance:** Run full 6-phase maintenance
- [ ] **Unit Tests:** All tests passing (100%)
- [ ] **Coverage:** No regressions in code coverage
- [ ] **Planning Session:** Create new session, verify timing/token tracking
- [ ] **Phase Updates:** Call `update_phase_status()` with tokens parameter
- [ ] **Progress Rendering:** Verify enhanced progress table format
- [ ] **Sub-Plan Integration:** Test sub-plan tracker update recording
- [ ] **Timezone Detection:** Verify correct timezone display
- [ ] **Duration Formatting:** Check human-readable formats (Xh Ym, Xm Ys, Xs)

---

## 📚 Documentation References

**Enhanced Files:**
- `src/orchestrators/session_model.py` - PlanningSession model
- `src/orchestrators/planning_orchestrator.py` - Phase status updates
- `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md` - Checkpoint gates
- `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml` - REQ-005 enhancement

**Related Guides:**
- `.github/prompts/CORTEX.prompt.md` - Universal entry point
- `cortex-brain/brain-protection-rules.yaml` - SKULL enforcement
- `SETUP-GUIDE.md` - Complete setup instructions

**Quick References:**
- `cortex-brain/MASTER-PLANNER-VISUAL-TRACKER-QUICK-REF.md` - Enhanced tracker guide
- `cortex-brain/documents/reports/master-planner-visual-tracker-enhancement-2025-12-13.md` - Full enhancement report

---

## 🚨 Common Issues & Solutions

### Issue 1: "AttributeError: 'PlanningSession' object has no attribute 'phase_start_times'"

**Cause:** Using old session instance created before update

**Solution:**
```python
# Create new session after pulling updates
session = PlanningSession(plan_id="new-plan")
# Or reload existing sessions to pick up new fields
```

### Issue 2: "TypeError: update_phase_status() got an unexpected keyword argument 'tokens_used'"

**Cause:** Using old orchestrator instance

**Solution:**
```bash
# Restart Python environment
# Reimport planning_orchestrator
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
```

### Issue 3: Progress table missing timing/token columns

**Cause:** Old template cached

**Solution:**
```bash
# Regenerate prompts and templates
system maintenance
# Or specifically:
regenerate_prompts
```

---

## 🎓 Learning Resources

**New Capabilities Tutorial:**
1. **Timing Metrics:** See `cortex-brain/documents/reports/master-planner-visual-tracker-enhancement-2025-12-13.md`
2. **Token Tracking:** Check `src/orchestrators/session_model.py` docstrings
3. **Checkpoint Gates:** Review `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md`

**API Examples:**
```python
# Example 1: Phase timing and token tracking
session = PlanningSession(plan_id="auth-feature")
session.record_phase_start("Phase 1: RED")
# ... do work ...
session.record_phase_end("Phase 1: RED", tokens_used=3200)

# Example 2: Sub-plan tracker updates
session.record_sub_plan_update(
    sub_plan_name="Authentication Module",
    phase_completed="Phase 2: GREEN",
    notes="All tests passing, 100% coverage"
)

# Example 3: Render enhanced progress
progress_table = session.render_progress_table()
print(progress_table)
```

---

## ✅ Verification Commands

```bash
# 1. Code integrity
git status
git log -1 --stat

# 2. Python environment
python --version  # Requires 3.8+
pip list | grep -E "(pytest|pyyaml|jinja2)"

# 3. System health
pytest tests/ --cov=src --cov-report=term-missing -v

# 4. CORTEX operations
# In Copilot Chat:
help
system maintenance
plan test: Sample Feature

# 5. Documentation
ls -la cortex-brain/documents/reports/master-planner-visual-tracker-*
cat cortex-brain/MASTER-PLANNER-VISUAL-TRACKER-QUICK-REF.md
```

---

## 🎯 Success Criteria

Your machine integration is complete when:

✅ **All tests passing** (100% pass rate)  
✅ **System maintenance** runs without errors  
✅ **Planning sessions** show enhanced progress tables  
✅ **Phase updates** record timing and tokens automatically  
✅ **Sub-plan checkpoints** enforce tracker updates  
✅ **Documentation** reflects all new capabilities  

---

## 🆘 Support

**Issues?** Check these resources:

1. **GitHub Issues:** [github.com/asifhussain60/CORTEX/issues](https://github.com/asifhussain60/CORTEX/issues)
2. **Documentation:** `cortex-brain/documents/reports/`
3. **Quick Refs:** `cortex-brain/*-QUICK-REF.md`
4. **Logs:** `logs/cortex_*.log`

**Still stuck?** Run diagnostics:
```bash
python -m src.main healthcheck
```

---

**Last Updated:** December 13, 2025  
**Next Review:** After next major feature release
