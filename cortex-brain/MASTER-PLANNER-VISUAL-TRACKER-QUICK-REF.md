# Master Planner Visual Tracker - Quick Reference

**Version:** Planning System 2.0.1  
**Date:** December 13, 2025  
**Status:** ✅ ACTIVE

---

## 🎯 What is the Master Planner Visual Tracker?

A comprehensive metrics dashboard that tracks planning progress with:
- ⏱️ Timestamps (start/end) with timezone
- 🎟️ Token usage per phase and total
- ⏰ Phase durations in human-readable format
- 📊 Visual progress bars
- ✅ Sub-plan completion tracking

---

## 📊 Example Output

```markdown
### 📊 Master Planner Visual Tracker

**Plan:** User Authentication System
**Started:** 2025-12-13 09:15:22 UTC-05:00
**Completed:** 2025-12-13 15:02:47 UTC-05:00
**Duration:** 5h 47m
**Tokens Used:** 18,450 tokens
**Overall Progress:** 100.0% (5/5 phases)

| Phase | Name | Status | Progress | Duration | Tokens | Tasks |
|-------|------|--------|----------|----------|--------|-------|
| 🚀 Phase 1 | Foundation | Completed | [██████████] 100% | 2h 15m | 5,300 | 8/8 |
| 🔨 Phase 2 | Development | Completed | [██████████] 100% | 3h 10m | 8,150 | 8/8 |
| ✅ Phase 3 | Validation | Completed | [██████████] 100% | 22m | 2,500 | 8/8 |
| 🚀 Phase 4 | Deployment | Completed | [██████████] 100% | 18m | 1,800 | 6/6 |
| 📊 Phase 5 | Review | Completed | [██████████] 100% | 12m | 700 | 4/4 |

**Sub-Plan Tracker Updates:** ✅ 5 updates recorded
```

---

## 🔧 How It Works (Automatic)

The tracker automatically:
1. **Records start time** when phase status changes to `in_progress`
2. **Records end time + tokens** when phase status changes to `completed`
3. **Calculates duration** in human-readable format (2h 15m, 3m 45s, 42s)
4. **Accumulates tokens** across all phases for total tracking
5. **Renders progress** after each phase completion

**You don't need to manually update anything!** Just use the normal planning workflow.

---

## 📝 Sub-Plan Completion Gates (Manual Requirement)

When working with sub-plans, you **MUST** update the master planner visual tracker at the end of each phase **before** proceeding to the next phase.

### Template for Manual Updates

```markdown
### 📊 Master Planner Visual Tracker - [Your Sub-Plan Name]

**Started:** 2025-12-13 09:00:00 UTC-05:00
**Last Updated:** 2025-12-13 15:30:00 UTC-05:00
**Tokens Used:** 12,500 tokens

| Phase | Status | Duration | Files Modified | Tests | Tokens |
|-------|--------|----------|----------------|-------|--------|
| Phase 1: RED | ✅ COMPLETE | 2h 15m | 8 files | 45 tests | 3,200 |
| Phase 2: GREEN | ✅ COMPLETE | 3h 45m | 12 files | 45 pass | 5,300 |
| Phase 3: REFACTOR | 🔄 IN PROGRESS | 1h 20m ⏳ | 6 files | 45 pass | 4,000 |
| Phase 4: CUTOVER | ⏸️ PENDING | - | - | - | - |
| Phase 5: CLEANUP | ⏸️ PENDING | - | - | - | - |

**Overall Progress:** 40% complete (2/5 phases)
```

### Checkpoint Requirements

At the end of **EVERY** phase:

1. ✅ Update tracker status to `✅ COMPLETE`
2. ✅ Add duration (e.g., "2h 15m")
3. ✅ Record files modified count
4. ✅ Record test count/pass rate
5. ✅ Record tokens used in that phase
6. ✅ Update overall progress percentage
7. ✅ **Save the master plan document**
8. ⛔ **DO NOT proceed** to next phase until tracker is updated

---

## 🎯 Checkpoint Locations (Sub-Plan Template)

The sub-plan template (`00-sub-plan-template.md`) includes explicit checkpoints:

```markdown
**🎯 CHECKPOINT:** Update Master Planner Visual Tracker with Phase 1 completion:
- Record status: ✅ Phase 1 RED - COMPLETE
- Add metrics: duration, tests created, tokens used
- Update overall progress percentage
- **Do NOT proceed to Phase 2 until master tracker is updated**
```

These appear after:
- ✅ Phase 1 (RED)
- ✅ Phase 2 (GREEN)
- ✅ Phase 3 (REFACTOR)
- ✅ Phase 4 (CUTOVER)
- ✅ Phase 5 (CLEANUP)

---

## 🚀 Using in Planning Workflow

### For Master Plans (Automatic)

When you run Planning System 2.0:

```python
# Just use normal planning workflow
orchestrator = PlanningOrchestrator(cortex_root="/path/to/cortex")

# Start planning
result = orchestrator.generate_incremental_plan(
    feature_name="User Authentication",
    feature_requirements=requirements
)

# Tracker is automatically populated!
```

The orchestrator automatically:
- Records phase start times
- Records phase end times with token counts
- Renders progress table after each phase
- Logs timing and token metrics

### For Sub-Plans (Manual Updates Required)

When following a sub-plan:

1. **Start Phase 1** - Work on RED phase tasks
2. **Complete Phase 1** - All tests written and RED
3. **🎯 CHECKPOINT** - Update master tracker:
   ```markdown
   | Phase 1: RED | ✅ COMPLETE | 2h 15m | 8 files | 45 tests | 3,200 |
   ```
4. **Save master plan**
5. **Proceed to Phase 2**

Repeat for each phase.

---

## 📈 Metrics Tracked

| Metric | Description | Example |
|--------|-------------|---------|
| **Start Time** | When planning/phase started | 2025-12-13 09:15:22 UTC-05:00 |
| **End Time** | When planning/phase completed | 2025-12-13 15:02:47 UTC-05:00 |
| **Timezone** | Auto-detected from system | UTC-05:00 (Eastern) |
| **Duration** | Human-readable time span | 2h 15m, 3m 45s, 42s |
| **Tokens Used** | Per-phase token consumption | 5,300 tokens |
| **Total Tokens** | Cumulative across all phases | 18,450 tokens |
| **Progress** | Visual progress bar | [██████░░░░] 60% |
| **Tasks** | Completed/total tasks | 8/8 |
| **Sub-Plan Updates** | Number of sub-plan tracker updates | ✅ 5 updates |

---

## 🛠️ Troubleshooting

### Tracker Not Showing Metrics

**Problem:** Tracker shows "-" for duration/tokens

**Cause:** Phase status not properly updated

**Solution:**
```python
# Ensure you call update_phase_status with tokens_used
self.update_phase_status(
    phase_name="Foundation",
    status="completed",
    progress=100,
    tokens_used=5300  # Don't forget this!
)
```

### Timezone Showing UTC Instead of Local

**Problem:** Timezone shows "UTC" instead of local timezone

**Cause:** System timezone detection failed

**Solution:** Manually set timezone in PlanningSession:
```python
session.timezone = "UTC-05:00"  # Eastern Time
```

### Sub-Plan Updates Not Recorded

**Problem:** "Sub-Plan Tracker Updates: ✅ 0 updates recorded"

**Cause:** Not calling `record_sub_plan_update()`

**Solution:**
```python
session.record_sub_plan_update(
    sub_plan_name="Intelligence Orchestrator",
    phase_completed="Phase 2: GREEN",
    notes="45 tests passing, 520 LOC"
)
```

---

## 📚 Related Documentation

- **Full Enhancement Report:** `cortex-brain/documents/reports/master-planner-visual-tracker-enhancement-2025-12-13.md`
- **Planning System 2.0 Guide:** `.github/prompts/modules/planning-orchestrator-guide.md`
- **Sub-Plan Template:** `cortex-brain/documents/planning/orchestrators/00-sub-plan-template.md`
- **Orchestrator Manifest:** `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml`

---

## ✅ Quick Checklist

**For Orchestrator Usage (Automatic):**
- ✅ Use Planning System 2.0 normally
- ✅ Tracker auto-populates with metrics
- ✅ No manual updates needed

**For Sub-Plan Execution (Manual):**
- ✅ Update tracker at end of each phase
- ✅ Record: status, duration, files, tests, tokens
- ✅ Update overall progress percentage
- ✅ Save master plan document
- ✅ Proceed to next phase only after update

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 13, 2025
