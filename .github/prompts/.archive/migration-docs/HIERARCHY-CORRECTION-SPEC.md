# CORTEX Hierarchical Terminology Correction

**Created:** 2026-02-14  
**Authority:** CORE-042 Alignment with Industry Standards (Scrum/SAFe)  
**Status:** DESIGN SPECIFICATION

---

## 🎯 Problem

**Current State (INCORRECT):**
```
INITIATIVE → PHASE → STAGE → TASK (CORE-042)
         └─ Wave (misused as sub-unit within phases)
```

**Issues:**
1. ❌ "Wave" used as small unit within phases (contradicts industry standards)
2. ❌ Missing EPIC/FEATURE concepts (strategic planning gap)
3. ❌ INITIATIVE poorly defined (confused with Epic)
4. ❌ Inconsistent prefixes across codebase

---

## ✅ Solution: Industry-Aligned Hierarchy

**Corrected Hierarchy (Scrum/SAFe Aligned):**

```
EPIC (E-)           Strategic initiative, 3-12 months
  └─ FEATURE (F-)   Deliverable capability, 2-8 weeks
      └─ PHASE (P-) Milestone/increment, 1-4 weeks  
          └─ STAGE (S-) Work unit, 2-5 days
              └─ TASK (T-) Atomic work, 2-8 hours
```

### Definitions

| Level | Prefix | Duration | Scope | Example |
|-------|--------|----------|-------|---------|
| **EPIC** | `E-` | 3-12 months | Strategic goal, portfolio level | E-001: Production-Ready SaaS Platform |
| **FEATURE** | `F-` | 2-8 weeks | Deliverable capability | F-010: MCP Gateway with TDD Enforcement |
| **PHASE** | `P-` | 1-4 weeks | Milestone, increment | P-048: Holistic Validation Gate |
| **STAGE** | `S-` | 2-5 days | Work unit | S1: Pre-Implementation Validation |
| **TASK** | `T-` | 2-8 hours | Atomic work | T-001: Write validation tests |

### Key Changes

1. **EPIC replaces INITIATIVE**
   - More aligned with Scrum/SAFe terminology
   - Clearer strategic scope
   - Portfolio-level planning

2. **FEATURE added as new level**
   - Bridges gap between EPIC and PHASE
   - Represents deliverable capability
   - Aligns with user stories/features in Scrum

3. **"Wave" deprecated as execution concept**
   - Historical "PHASE-X" files → archived
   - Concept absorbed into EPIC or FEATURE
   - Session-scoped execution → use PHASE directly

---

## 📋 Migration Strategy

### Phase 1: Archive Legacy "Wave" Files (NON-DESTRUCTIVE)

**Location:** `cortex-registry/history/_archive/obsolete-plans/`

**Files to Archive:**
```
PHASE-*.yaml                          → obsolete-plans/PHASE-*.yaml.deprecated
PHASE-*-SUMMARY.md                    → obsolete-plans/PHASE-*-SUMMARY.md.deprecated
SESSION-SCOPED-WAVES.md              → obsolete-plans/SESSION-SCOPED-WAVES.md.deprecated
AUTONOMOUS-PHASE-EXECUTION-GUIDE.md   → obsolete-plans/AUTONOMOUS-PHASE-EXECUTION-GUIDE.md.deprecated
HIGH-ROI-PHASE-PRIORITIZATION.md      → obsolete-plans/HIGH-ROI-PHASE-PRIORITIZATION.md.deprecated
```

**Preservation Strategy:**
- ✅ Keep all content (no deletion)
- ✅ Add deprecation notices
- ✅ Map old phase IDs to new Epic/Feature IDs
- ✅ Update references in README

### Phase 2: Update Core Documentation

#### 2.1 Update CORE-042 Rule

**File:** `.github/copilot-instructions.md`

**OLD:**
```markdown
| **CORE-042** | **Hierarchical Terminology** — PHASE→STAGE→TASK (I-/P-/S-/T- prefixes). |
```

**NEW:**
```markdown
| **CORE-042** | **Hierarchical Terminology** — EPIC→FEATURE→PHASE→STAGE→TASK (E-/F-/P-/S-/T- prefixes). |
```

#### 2.2 Update cortex-architect.prompt.md

**File:** `.github/prompts/cortex-architect.prompt.md`

**Search/Replace:**
- `PHASE-X` → `E-XXX` or `F-XXX` (context-dependent)
- `phase_id` → `epic_id` or `feature_id`
- "Phase 7" → "Epic 001" (example)
- "Phase Execution" → "epic execution" or "feature delivery"

#### 2.3 Update Agent Specifications

**Files:** `.github/agents/core/*.md`

**Updates:**
- `phase-creation-standards.md` § Phase Structure → Remove wave references
- `cortex-phase-resolver.md` § Wave planning → Epic/Feature planning

### Phase 3: Update Registry Structure

#### 3.1 Create New Registry Structure

**New Directories:**
```
cortex-registry/
├── epics/              # Strategic initiatives (NEW)
│   ├── active/
│   └── completed/
├── features/           # Deliverable capabilities (NEW)
│   ├── active/
│   └── completed/
├── phases/             # Existing - no change
│   ├── active/
│   └── completed/
└── history/
    └── _archive/
        └── obsolete-plans/  # Deprecated phase files
```

#### 3.2 Migration Mapping

**Example Mappings:**

| Old Wave ID | New Hierarchy | Rationale |
|-------------|---------------|-----------|
| PHASE-1 | E-001: Production Foundation | Strategic scope (months) |
| PHASE-Q | F-010: Multi-Cycle TDD | Feature-level (weeks) |
| PHASE-R | F-011: Debug Tooling | Feature-level (weeks) |
| PHASE-7-CLEANUP | P-052: Interface Compliance | Phase-level (days) |

### Phase 4: Update Code References

#### 4.1 Enum Updates

**File:** `tests/unit/orchestrators/strategies/test_planning_strategy.py`

**OLD:**
```python
class PlanningLevel(Enum):
    INITIATIVE = "initiative"
    PHASE = "phase"
    WAVE = "wave"
    stages = "stages"
    STAGE = "stage"
    TASK = "task"
```

**NEW:**
```python
class PlanningLevel(Enum):
    EPIC = "epic"          # Strategic (3-12 months)
    FEATURE = "feature"    # Deliverable (2-8 weeks)
    PHASE = "phase"        # Milestone (1-4 weeks)
    STAGE = "stage"        # Work unit (2-5 days)
    TASK = "task"          # Atomic (2-8 hours)
    # Deprecated levels (remove in Phase 2)
    INITIATIVE = "initiative"  # → EPIC
    WAVE = "wave"              # → EPIC or FEATURE
    stages = "stages"            # → FEATURE
    METHOD = "method"          # Too granular, remove
    CLASS = "class"            # Too granular, remove
```

#### 4.2 Model Updates

**File:** `cortex/orchestrators/planning/strategies/wave.py`

**Action:** Rename to `epic.py` or deprecate

**File:** `cortex/models/phase_detail_schema.py`

**No changes needed** - operates at Phase level

#### 4.3 CLI Updates

**File:** `cortex/cli/phase_creator.py`

**Remove Wave Template:**
```python
WAVE = {
    "phase_id": "",        # DEPRECATED
    "name": "",
    ...
}
```

**Add Epic/Feature Templates:**
```python
EPIC = {
    "epic_id": "",        # E-XXX format
    "title": "",
    "strategic_goal": "",
    "duration_months": 0,
    "features": []
}

FEATURE = {
    "feature_id": "",     # F-XXX format
    "title": "",
    "deliverable": "",
    "duration_weeks": 0,
    "phases": []
}
```

### Phase 5: Update Documentation

#### 5.1 Planning Orchestrator Guide

**File:** `docs/planning-orchestrator-guide.md`

**Update Glossary:**
```markdown
| Term | Definition |
|------|------------|
| **Epic** | Strategic initiative (3-12 months) |
| **Feature** | Deliverable capability (2-8 weeks) |
| **Phase** | Milestone with clear deliverables (1-4 weeks) |
| **Stage** | Work unit within a phase (2-5 days) |
| **Task** | Atomic work item (2-8 hours) |
| ~~**Wave**~~ | **DEPRECATED** - Use Epic or Feature |
| ~~**Initiative**~~ | **DEPRECATED** - Use Epic |
```

#### 5.2 README Updates

**File:** `cortex-registry/README.md`

Add deprecation notice:
```markdown
## ⚠️ Terminology Update (2026-02-14)

**DEPRECATED TERMS:**
- "Wave" → Use **Epic** (strategic) or **Feature** (deliverable)
- "Initiative" → Use **Epic**

**NEW HIERARCHY:**
```
EPIC (E-) → FEATURE (F-) → PHASE (P-) → STAGE (S-) → TASK (T-)
```

**Legacy phase files archived:** `history/_archive/obsolete-plans/`
```

---

## 🎯 Implementation Checklist

### Non-Destructive Phase (Day 1)

- [ ] Create archive directory: `history/_archive/obsolete-plans/`
- [ ] Move all PHASE-*.yaml files (preserve content)
- [ ] Add deprecation notices to moved files
- [ ] Create PHASE-ID-MAPPING.yaml (old → new mapping)
- [ ] Update README with deprecation notice

### Core Documentation Phase (Day 1-2)

- [ ] Update CORE-042 in `.github/copilot-instructions.md`
- [ ] Update `.github/prompts/cortex-architect.prompt.md` (all Wave references)
- [ ] Update `.github/agents/core/phase-creation-standards.md`
- [ ] Update `.github/agents/core/cortex-phase-resolver.md`

### Registry Structure Phase (Day 2)

- [ ] Create `cortex-registry/epics/` directory
- [ ] Create `cortex-registry/features/` directory
- [ ] Create initial Epic files (E-001, E-002) from major Waves
- [ ] Create Feature files from minor Waves
- [ ] Update index.yaml with new structure

### Code Updates Phase (Day 2-3)

- [ ] Update `PlanningLevel` enum (deprecate old values)
- [ ] Rename/deprecate `wave.py` → `epic.py`
- [ ] Update CLI templates (remove Wave, add Epic/Feature)
- [ ] Update all imports and references
- [ ] Update test files

### Documentation Phase (Day 3)

- [ ] Update `docs/planning-orchestrator-guide.md`
- [ ] Update `docs/guides/user-planning-orchestrator.md`
- [ ] Create migration guide for users
- [ ] Update all examples in docs/

### Validation Phase (Day 3)

- [ ] Run full test suite (no failures)
- [ ] Verify no broken references
- [ ] Check all grep results for "wave" mentions
- [ ] Validate CLI still works
- [ ] Update MCP tool descriptions if needed

---

## 📊 Impact Analysis

### Files Affected (Estimated)

| Category | Count | Effort |
|----------|-------|--------|
| Prompt files | 2 | 2h |
| Agent specs | 3 | 1h |
| Registry files | 20+ | 3h |
| Python code | 10 | 4h |
| Documentation | 8 | 2h |
| Tests | 5 | 1h |
| **TOTAL** | **48+** | **13h** |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing prompts | 🟡 Medium | Archive old files, add deprecation notices |
| User confusion | 🟡 Medium | Clear migration guide, examples |
| Lost context | 🟢 Low | Non-destructive migration (preserve all files) |
| Test failures | 🟢 Low | Gradual deprecation with backward compatibility |

---

## 🔮 Post-Migration Benefits

1. **Industry Alignment:** Standard Scrum/SAFe terminology
2. **Clearer Hierarchy:** No ambiguity about scope levels
3. **Better Planning:** Epic → Feature → Phase natural flow
4. **Reduced Confusion:** "Wave" no longer misused as small unit
5. **Improved Tooling:** CLI can generate proper Epic/Feature templates

---

## 📚 References

- **Scrum Guide:** Epic > Feature > Story hierarchy
- **SAFe Framework:** Portfolio Epic > Feature > User Story
- **CORE-042:** Hierarchical Terminology requirement
- **ENH-084:** Phase Creation Standards

---

**Next Step:** Execute Phase 1 (Archive Legacy Files) with silent autonomous mode.
