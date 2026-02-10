# CORTEX Terminology Hierarchy Standard
**Version:** 1.0  
**Authority:** CORE-042 (New Rule)  
**Created:** 2026-02-07  
**Purpose:** Eliminate phase/stage/task confusion with clear 4-level hierarchy

---

## 🎯 Problem Statement

**Issue:** Terms "Phase", "Stage", and "Task" used inconsistently across CORTEX, creating ambiguity:
- "Phase 38" vs "Phase 38.0" unclear (parent vs child?)
- Status messages contradictory: "Phase 38.0 COMPLETE" + "Phase 38 READY"
- No clear hierarchy in planning responses

**Root Cause:** Flat terminology without parent/child distinction.

---

## ✅ Standard Hierarchy (4 Levels)

```
INITIATIVE (Strategic goal spanning weeks/months)
  └─ PHASE (Major deliverable, typically 1-2 weeks)
      └─ STAGE (Sequential milestone, typically 1-3 days)
          └─ TASK (Atomic unit, typically hours)
```

### Level Definitions

| Level | Scope | Duration | Example | Numbering |
|-------|-------|----------|---------|-----------|
| **INITIATIVE** | Strategic goal | Weeks-months | Brain Cohesion & Health System | I-38 |
| **PHASE** | Major deliverable | 1-2 weeks | Baseline Remediation | P-38.1 |
| **STAGE** | Sequential milestone | 1-3 days | Test Collection Fix | S-1 |
| **TASK** | Atomic unit | Hours | Fix test_intent_router.py | T-1 |

---

## 📋 Naming Conventions

### Format Patterns

```yaml
# INITIATIVE
ID: I-{number}
Example: I-38 (Brain Cohesion & Health System)
Status: ACTIVE, BLOCKED, ARCHIVED
Description: High-level goal with multiple phases

# PHASE
ID: P-{initiative}.{phase}
Example: P-38.1 (Baseline Remediation - first phase of I-38)
Status: planned, active, completed, blocked
Description: Major work block with stages

# STAGE
ID: S-{stage}
Example: S-1 (within current phase context)
Status: pending, in-progress, complete
Description: Sequential milestone within phase

# TASK
ID: T-{task}
Example: T-1 (within current stage context)
Status: todo, doing, done
Description: Atomic unit within stage
```

---

## 🔄 Migration from Old Terminology

### Mapping Table

| Old (Confusing) | New (Clear) | Rationale |
|-----------------|-------------|-----------|
| Phase 38 | I-38 (Initiative-38) | Top-level strategic goal |
| Phase 38.0 | P-38.1 (Phase-38.1) | First phase of I-38 |
| Stage 1-7 (of Phase 38) | P-38.2, P-38.3, etc. | Each was really a phase |
| Stage 0-6 (of Phase 38.0) | S-0 to S-6 | True sequential stages |
| Tasks (unspecified) | T-1, T-2, etc. | Atomic units |

### Example: Initiative-38 Restructured

**OLD (Ambiguous):**
```
Phase 38: Brain Cohesion & Health System
  - Phase 38.0: Remediation (COMPLETE)
  - Stage 1: Brain Health Monitor (READY)
  - Stage 2: Cohesion Analysis (BLOCKED)
```

**NEW (Clear):**
```
I-38: Brain Cohesion & Health System (ACTIVE)
  ├─ P-38.1: Baseline Remediation (COMPLETED ✅)
  │   ├─ S-0: Phase 34 Restore (COMPLETE)
  │   ├─ S-1: Test Collection Fix (COMPLETE)
  │   ├─ S-2: Orchestrator Inventory (COMPLETE)
  │   ├─ S-3: Baseline Metrics (COMPLETE)
  │   ├─ S-4: Test Suite Validation (COMPLETE)
  │   ├─ S-5: Readiness Validation (COMPLETE)
  │   └─ S-6: Unblock Initiative (COMPLETE)
  │
  ├─ P-38.2: Brain Health Monitor (READY 🟢)
  │   ├─ S-1: Health metrics collection (PENDING)
  │   ├─ S-2: Threshold configuration (PENDING)
  │   └─ S-3: Alert system (PENDING)
  │
  ├─ P-38.3: Cohesion Analysis (BLOCKED ⚪)
  └─ P-38.4: Auto-Healing System (BLOCKED ⚪)
```

---

## 🎨 Response Format Standards

### Status Messages (Clear Hierarchy)

**✅ CORRECT:**
```
I-38 Status: ACTIVE
  └─ P-38.1: COMPLETED (100% readiness)
  └─ P-38.2: READY (Implementation can begin)
```

**❌ INCORRECT:**
```
Phase 38.0 Status: COMPLETE
Phase 38 Status: ACTIVE (Ready to implement)
```

### Progress Reports

**Format:**
```markdown
## I-{num}: {Initiative Name}

**Status:** {ACTIVE|BLOCKED|ARCHIVED}  
**Progress:** {X}/{Y} phases complete

### Phases

| Phase | Status | Progress | Next Action |
|-------|--------|----------|-------------|
| P-{num}.1 | ✅ COMPLETE | 100% | - |
| P-{num}.2 | 🟢 READY | 0% | Begin S-1 |
| P-{num}.3 | ⚪ BLOCKED | 0% | Wait for P-{num}.2 |
```

### Stage Tracking

**Format:**
```markdown
## P-{num}.{phase}: {Phase Name}

**Status:** {planned|active|completed|blocked}  
**Progress:** {X}/{Y} stages complete

### Stages

- [x] S-0: {Stage name} - COMPLETE
- [x] S-1: {Stage name} - COMPLETE
- [ ] S-2: {Stage name} - PENDING
```

---

## 🛡️ Governance Integration

### New CORE Rule

**CORE-042: Hierarchical Terminology**

All planning responses MUST use standardized hierarchy:
- INITIATIVE (I-{num}): Strategic goal
- PHASE (P-{num}.{phase}): Major deliverable
- STAGE (S-{num}): Sequential milestone
- TASK (T-{num}): Atomic unit

**Enforcement:** PlanOrchestrator validates all plan responses against hierarchy.

**Violation Example:**
```
❌ "Phase 38.0 complete, Phase 38 ready"
✅ "P-38.1 complete, P-38.2 ready to begin"
```

---

## 📊 Registry File Updates

### File Naming

```
# OLD (Ambiguous)
phase-38-brain-cohesion-health-system.yaml
phase-38.0-remediation-baseline-restoration.yaml

# NEW (Clear)
initiative-38-brain-cohesion-health-system.yaml
phase-38.1-baseline-remediation.yaml
phase-38.2-brain-health-monitor.yaml
```

### YAML Structure

```yaml
# initiative-{num}-{name}.yaml
id: "I-38"
type: "initiative"
name: "Brain Cohesion & Health System"
status: "active"
phases:
  - id: "P-38.1"
    name: "Baseline Remediation"
    status: "completed"
    file: "phases/completed/phase-38.1-baseline-remediation.yaml"
  
  - id: "P-38.2"
    name: "Brain Health Monitor"
    status: "ready"
    file: "phases/active/phase-38.2-brain-health-monitor.yaml"
```

---

## 🔧 Implementation Checklist

### Phase 1: Documentation (Immediate)
- [x] Create TERMINOLOGY-HIERARCHY.md (this file)
- [ ] Update CORE rules with CORE-042
- [ ] Update response-format-standards.md
- [ ] Update cortex-architect.prompt.md

### Phase 2: Registry Migration (Next Session)
- [ ] Rename registry files (phase-* → initiative-*, phase-X.Y-*)
- [ ] Update index.yaml with I-/P- prefixes
- [ ] Update YAML structures with type field
- [ ] Create migration script for existing files

### Phase 3: Code Updates (Following Session)
- [ ] Update PlanOrchestrator to use hierarchy
- [ ] Update PhaseManager validation
- [ ] Update DashboardGenerator templates
- [ ] Add CORE-042 to EnforcementOrchestrator

### Phase 4: Testing (Final Session)
- [ ] Test PlanOrchestrator with new terminology
- [ ] Verify dashboard generation
- [ ] Validate response formats
- [ ] Update all existing plan files

---

## 📚 Examples

### Planning Session

**User Request:**
```
"Begin Phase 38 implementation"
```

**✅ CORRECT Response:**
```markdown
## 🧠 CORTEX Implementation Plan

**Initiative:** I-38 (Brain Cohesion & Health System)  
**Phase:** P-38.2 (Brain Health Monitor)  
**Status:** READY (P-38.1 completed with 100% readiness)

### Phase Breakdown

P-38.2: Brain Health Monitor (15 tests, 2 days)
  ├─ S-1: Health metrics collection (4 tests, 6 hours)
  ├─ S-2: Threshold configuration (5 tests, 8 hours)
  └─ S-3: Alert system (6 tests, 10 hours)

**Next Action:** Begin S-1 (Health metrics collection)
```

**❌ INCORRECT Response:**
```markdown
Phase 38 Stage 1 ready to begin.
Phase 38.0 complete.
```

---

## 🎯 Benefits

1. **Eliminates Ambiguity**  
   - Clear parent/child relationships
   - Unambiguous status messages

2. **Improves Navigation**  
   - Easy to understand hierarchy depth
   - Clear "where am I" in large initiatives

3. **Better Progress Tracking**  
   - Percentage calculations more meaningful
   - Clear blocking relationships

4. **Consistent Communication**  
   - Team members use same language
   - No confusion between phase/stage

5. **Automated Validation**  
   - CORE-042 enforcement
   - PlanOrchestrator checks hierarchy

---

## 🚀 Quick Reference

| Level | Format | Example | Duration |
|-------|--------|---------|----------|
| **Initiative** | I-{num} | I-38 | Weeks-months |
| **Phase** | P-{num}.{phase} | P-38.2 | 1-2 weeks |
| **Stage** | S-{num} | S-1 | 1-3 days |
| **Task** | T-{num} | T-1 | Hours |

**Status Icons:**
- ✅ COMPLETED (green checkmark)
- 🟢 READY (green circle - can start)
- 🔵 ACTIVE (blue circle - in progress)
- ⚪ PLANNED (white circle - not started)
- 🔴 BLOCKED (red circle - cannot proceed)
- ⚫ ARCHIVED (black circle - deprecated)

---

*Version 1.0 - Terminology standard to eliminate phase/stage/task confusion*
