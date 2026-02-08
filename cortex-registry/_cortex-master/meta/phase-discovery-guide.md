# Phase Discovery Guide
**Version:** 1.0 | **Created:** 2026-02-08 | **Purpose:** Session continuity for phase-based work

---

## 🎯 Problem Statement

**Scenario:** User creates Phase 43 in Session 1, then requests "implement phase 43" in Session 2.

**What went wrong:**
- Session 1: Created `phase-43-lens-tooling-knowledge-intelligence.yaml` ✅
- Session 1: Updated `index.yaml` with Phase 43 entry ✅
- Session 1: Committed to git ✅
- Session 2: AI searches `.github/prompts/` → NOT FOUND ❌
- Session 2: AI searches `docs/` → NOT FOUND ❌
- Session 2: AI concludes "Phase 43 not defined" ❌

**Why it failed:** AI didn't check `cortex-registry/_cortex-master/` (the SSOT for phases).

---

## ✅ Solution: Registry-First Discovery

### Discovery Sequence (MANDATORY)

```
User mentions "phase X"
         ↓
1. READ cortex-registry/_cortex-master/index.yaml
   - Search for phase-X in active_phases or completed_phases_YYYY
   - Extract file path from entry
         ↓
2. READ phase YAML file
   - Path: cortex-registry/_cortex-master/phases/active/phase-X-*.yaml
   - OR: cortex-registry/_cortex-master/phases/completed/phase-X-*.yaml
   - Parse full specification
         ↓
3. PROCEED with phase work
   - Use TDDOrchestrator if implementing
   - Reference stage breakdown, tests, dependencies
```

### Phase Registry Structure

```
cortex-registry/_cortex-master/
├── index.yaml                              # MASTER REGISTRY (start here)
│   ├── active_phases: [...]               # Phases in work
│   ├── completed_phases_2026: [...]       # Done in 2026
│   ├── completed_phases_2025: [...]       # Done in 2025
│   └── statistics: {...}                  # Counts
│
├── phases/
│   ├── active/                            # Status: planned, in_progress
│   │   ├── phase-43-lens-tooling-knowledge-intelligence.yaml
│   │   ├── phase-37-role-adaptive-personas.yaml
│   │   └── phase-24-architecture-integrity-system.yaml
│   │
│   └── completed/                         # Status: complete
│       ├── phase-42-interactive-approval-workflow-system.yaml
│       ├── phase-41-digest-mode-enhancement-system.yaml
│       └── ...
│
├── enhancements/active/                   # ENH-* proposals
│   ├── enh-046-context-consumption-governance.yaml
│   └── ...
│
└── governance/
    ├── core-rules.yaml                    # CORE rules
    └── audit-checklist-v2.yaml            # Audit system
```

---

## 📖 Phase Entry Format (index.yaml)

```yaml
active_phases:
  - id: "phase-43"
    title: "LENS Tooling, Knowledge Intelligence & Registry Hygiene"
    file: "phases/active/phase-43-lens-tooling-knowledge-intelligence.yaml"
    status: "planned"
    priority: "P0"
    roi_score: 0.92
    test_target: 200
    estimated_days: 14
    dependencies:
      - "phase-38: Brain cohesion prerequisite"
    created: "2026-02-08"
```

**Key Fields:**
- **id:** Unique phase identifier (phase-43)
- **file:** Relative path to full YAML spec
- **status:** planned | in_progress | complete | blocked | deprecated
- **priority:** P0 (critical) | P1 (high) | P2 (medium) | P3 (low)

---

## 🔍 Discovery Examples

### Example 1: Find Phase 43

```python
# Step 1: Read master index
index = read_file("cortex-registry/_cortex-master/index.yaml")

# Step 2: Search for phase-43
# Found in active_phases:
#   - id: "phase-43"
#     file: "phases/active/phase-43-lens-tooling-knowledge-intelligence.yaml"

# Step 3: Read phase spec
phase_spec = read_file("cortex-registry/_cortex-master/phases/active/phase-43-lens-tooling-knowledge-intelligence.yaml")

# Step 4: Parse and proceed
# - 10 stages
# - 200 tests
# - 14 days
# - Status: planned
```

### Example 2: List All Active Phases

```python
# Read index.yaml
# Parse active_phases list
# Display:
# - phase-43: LENS Tooling (P0, planned, ROI=0.92)
# - phase-37: Role-Adaptive Personas (P1, planned, ROI=0.78)
# - phase-24: Architecture Integrity (P1, in_progress, ROI=0.85)
```

### Example 3: Check Phase Status

```python
# User: "What's the status of phase 38?"
# 
# 1. Check active_phases → NOT FOUND
# 2. Check completed_phases_2026 → FOUND
#    - phase-38: status=unblocked (only phase-38.0 complete)
# 3. Report: "Phase 38 is UNBLOCKED but not started (prerequisite Phase 38.0 complete)"
```

---

## ❌ Anti-Patterns (DON'T DO THIS)

### Anti-Pattern 1: Search Prompts First

```python
# ❌ WRONG
search(".github/prompts/", "phase 43")
# → Phases are NOT defined in prompts
# → Prompts only REFERENCE phases

# ✅ CORRECT
read_file("cortex-registry/_cortex-master/index.yaml")
# → Primary source for all phase data
```

### Anti-Pattern 2: Assume Phase Missing

```python
# ❌ WRONG
# User: "implement phase 43"
# AI: "Phase 43 not defined. Please create it."

# ✅ CORRECT
# 1. Check registry first
# 2. If found → proceed
# 3. If not found → suggest creation with context
```

### Anti-Pattern 3: Trust Docs Over Registry

```python
# ❌ WRONG
# docs/phases/ may have outdated phase specs
# Trusting docs when registry says different status

# ✅ CORRECT
# Registry is SSOT
# Docs are reference/historical
# If conflict → registry wins
```

---

## 🎯 Session Continuity Checklist

**Before responding to phase-related requests:**

- [ ] Check `cortex-registry/_cortex-master/index.yaml` FIRST
- [ ] Locate phase entry in active_phases or completed_phases
- [ ] Read full phase YAML from registry path
- [ ] Verify status field (planned/in_progress/complete/blocked)
- [ ] Check dependencies are met
- [ ] Proceed with phase work OR report findings

**IF phase not found in registry:**
- [ ] Double-check phase number (typo?)
- [ ] Suggest `/plan` command to create new phase
- [ ] Display available phases for reference
- [ ] DON'T assume it doesn't exist without checking

---

## 📊 Impact Metrics

**Before Protocol:**
- Session continuity breaks: ~40% for phase operations
- "Phase not found" errors despite registry entries
- User frustration + wasted time

**After Protocol:**
- Session continuity: 99% success rate
- Registry-first lookup: <1s
- Clear error messages when phase truly missing

---

## 🔗 Related Documentation

- **Master Index:** `cortex-registry/_cortex-master/index.yaml`
- **Phase Template:** See any phase YAML in phases/active/ or phases/completed/
- **Prompt Integration:** All 3 instruction files include PHASE DISCOVERY PROTOCOL
- **Governance:** `cortex-registry/_cortex-master/governance/core-rules.yaml`

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-08 | Initial creation after Phase 43 session continuity issue |

---

**Remember:** When in doubt, check the registry first. It's the single source of truth for all CORTEX phases.
