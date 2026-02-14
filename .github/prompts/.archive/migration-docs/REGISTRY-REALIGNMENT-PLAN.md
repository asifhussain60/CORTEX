# Registry Realignment Plan: PHASE→STAGE→TASK

**Created:** 2026-02-14  
**Authority:** CORE-042 Simplification + User Request  
**Scope:** Complete registry, prompts, and agent realignment

---

## 🎯 Objective

Realign entire CORTEX system from historical wave/epic/feature complexity to simple PHASE→STAGE→TASK hierarchy while preserving all history and metadata.

---

## 📋 Realignment Strategy

### Phase 1: Registry Structure (NON-DESTRUCTIVE)

**Current Structure:**
```
cortex-registry/_cortex-master/
├── work/
│   ├── waves/              ← DEPRECATED
│   │   ├── active/
│   │   └── archived/
│   ├── phases/             ← KEEP
│   │   ├── active/
│   │   └── completed/
│   └── enhancements/       ← KEEP
```

**New Structure:**
```
cortex-registry/_cortex-master/
├── work/
│   ├── phases/             ← PRIMARY (all phases here)
│   │   ├── active/
│   │   └── completed/
│   └── enhancements/       ← SECONDARY (ENH-XXX groupings)
├── history/
│   └── _archive/
│       └── obsolete-plans/  ← MOVE all historical content here
```

**Actions:**
1. Move `work/waves/*` → `history/_archive/obsolete-plans/`
2. Add deprecation notice to README
3. Create historical→phase mapping file
4. Update all references in README.md

### Phase 2: README.md Realignment

**Current:** "phase status Summary" with 16 completed phases  
**New:** "Phase Status Summary" with phases grouped by completion date

**Mapping Strategy:**
- Phase 1 → Phase-01 (Foundation Security)
- Phase 7 → Phase-07 (Orchestrator Consolidation)
- Phase 8 → Phase-08 (Planning Capability)
- LEGACY-WAVE-A → Phase-10 (Critical Blockers)
- LEGACY-WAVE-B → Phase-11 (Operability & Monitoring)
- ... etc

**Preserve All Metadata:**
- Tests count
- Commits count
- Date
- Git hash
- All history preserved in archive

### Phase 3: Agent Files Cleanup

**Files with Legacy References:**
- `.github/agents/core/phase-creation-standards.md` (partial - finish)
- `.github/agents/core/cortex-phase-resolver.md` (legacy-wave-3 references)
- `.github/agents/core/cortex-master-plan-auditor.md` (if exists)

**Actions:**
- Replace "historical wave" → "phase group"
- Remove Wave template examples
- Update all code snippets
- Fix dependency examples (WAVE-H → PHASE-XX)

### Phase 4: Prompt Files Cleanup

**Files:**
- All files in `.github/prompts/`
- Focus on guides/ subdirectory

**Search & Replace:**
- "historical wave" → "phase" (contextual)
- "Wave" → "Phase" (titles)
- "WAVE-X" → "Phase X" (references)

### Phase 5: Orchestrator Integration

**Ensure ALL orchestrators understand:**
```python
HIERARCHY = {
    "PHASE": "1-4 weeks, work milestone (P-XXX)",
    "STAGE": "2-5 days, work unit (S-1, S-2, etc.)",
    "TASK": "2-8 hours, atomic work (T-001, T-002, etc.)"
}
```

**Files to Update:**
- `cortex/orchestrators/planning/` (all files)
- `cortex/orchestrators/interaction/` (if references exist)
- Any orchestrator with phase/wave logic

---

## 🗂️ File Operations (Detailed)

### Registry Operations

```bash
# 1. Archive phase files (preserve history)
mkdir -p cortex-registry/_cortex-master/history/_archive/obsolete-plans/
mv cortex-registry/_cortex-master/work/waves/* \
   cortex-registry/_cortex-master/history/_archive/obsolete-plans/

# 2. Create deprecation notice
cat > cortex-registry/_cortex-master/history/_archive/obsolete-plans/README.md <<EOF
# Deprecated phase files

**Deprecated:** 2026-02-14  
**Reason:** CORE-042 simplified hierarchy (PHASE→STAGE→TASK)

These files used "Wave" terminology which has been deprecated.
All content preserved for historical reference.

See: WAVE-TO-PHASE-MAPPING.yaml for new phase IDs
EOF

# 3. Create mapping file
cat > cortex-registry/_cortex-master/history/_archive/obsolete-plans/WAVE-TO-PHASE-MAPPING.yaml <<EOF
# Wave → Phase Mapping
# Generated: 2026-02-14
# Authority: CORE-042 Simplification

mappings:
  - old_id: "Phase 1"
    new_id: "PHASE-01"
    name: "Foundation Security"
    tests: 336
    commits: "15+"
    date: "2026-02-13"
    git_hash: "07c84a4c1"
    
  - old_id: "Phase 7"
    new_id: "PHASE-07"
    name: "Orchestrator Consolidation"
    tests: 233
    commits: "8"
    date: "2026-02-11"
    git_hash: "Multiple"
    
  # ... etc for all 16 waves
EOF
```

### Agent File Updates

**File: `.github/agents/core/phase-creation-standards.md`**

Remaining items (lines 180-370):
- Line 187: `dependencies: ["ENH-063", "WAVE-H"]` → `["ENH-063", "PHASE-XX"]`
- Line 188: `blocks: ["WAVE-J"]` → `["PHASE-YY"]`
- Line 195: "single-Phase Execution" → "single-phase execution"
- Line 266-276: Remove entire Wave template section
- Line 301: "Phase Execution plan" → "phase execution plan"
- Line 314: "wave-i.yaml" → "phase-i.yaml"
- Line 341: "Multi-Wave Enhancement" → "Multi-Stage Enhancement"
- Line 354: "Wave breakdown" → "Stage breakdown"
- Line 358-365: Remove "Session-Scoped Wave" example

**File: `.github/agents/core/cortex-phase-resolver.md`**

Updates needed:
- Line 339: "phase plan + execution order" → "Phase plan + execution order"
- Line 360: "phase organization" → "phase organization"
- Line 362: "Phase Structure (phases 45-47 in wave-3)" → "Phase group (phases 45-47)"
- Line 365: `phase_id: "wave-3"` → Remove (not needed)
- Line 375: "wave-3 in progress" → "phase-group-3 in progress"
- Line 402: `current_wave_id: "wave-3"` → Remove
- Line 445: `cortex_execute_wave_autonomous` → `cortex_execute_phase_group`
- Line 453: "wave state" → "phase state"

---

## 📊 Impact Analysis

### Files to Modify

| Category | Count | Effort |
|----------|-------|--------|
| Registry README | 1 | 1h |
| Registry structure | 1 move | 0.5h |
| Agent specs | 2 | 1h |
| Prompt files | 5-8 | 1.5h |
| Orchestrator code | 0 | 0h (no code changes needed) |
| **TOTAL** | **9-12** | **4h** |

### Data Preservation Checklist

- [ ] All Phase YAML files moved (not deleted)
- [ ] Wave→Phase mapping created
- [ ] Git hashes preserved
- [ ] Test counts preserved
- [ ] Commit counts preserved
- [ ] Dates preserved
- [ ] All status metadata preserved
- [ ] History fully accessible in archive

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Lost history | 🟢 LOW | Non-destructive move (everything archived) |
| Broken references | 🟡 MEDIUM | Update all references systematically |
| User confusion | 🟢 LOW | Clear deprecation notices + mapping |
| Orchestrator breaks | 🟢 LOW | No code changes (terminology only) |

---

## ✅ Validation Criteria

### Post-Realignment Checks

```bash
# 1. Verify no wave references in active docs
grep -r "wave\|Wave\|WAVE" .github/agents/core/*.md | grep -v "deprecated"
grep -r "wave\|Wave\|WAVE" .github/prompts/*.md | grep -v "deprecated"

# 2. Verify archive exists
ls -la cortex-registry/_cortex-master/history/_archive/obsolete-plans/

# 3. Verify mapping file
cat cortex-registry/_cortex-master/history/_archive/obsolete-plans/WAVE-TO-PHASE-MAPPING.yaml

# 4. Verify README updated
grep "Phase Status Summary" cortex-registry/_cortex-master/README.md

# 5. Verify tests still pass
pytest tests/ -v --tb=short
```

---

## 🚀 Execution Order

1. **Create archive directory** (30 sec)
2. **Move phase files** (1 min)
3. **Create mapping file** (10 min)
4. **Update README.md** (30 min)
5. **Fix agent specs** (30 min)
6. **Fix prompt files** (30 min)
7. **Validate** (15 min)
8. **Commit with AC marker** (5 min)

**Total:** ~2 hours

---

## 📝 Commit Message Template

```
AC-HIER-004: Complete Registry Realignment to PHASE→STAGE→TASK

Authority: CORE-042 + User Request (full realignment)
Scope: Registry, agents, prompts - all wave references

Changes:
1. Archived work/waves/ → history/_archive/obsolete-plans/
2. Created WAVE-TO-PHASE-MAPPING.yaml (16 mappings)
3. Updated README.md "phase status" → "Phase Status"
4. Fixed agent specs (2 files, 15+ references)
5. Fixed prompt files (5-8 files)

Preservation:
- ✅ All history preserved (non-destructive move)
- ✅ All metadata preserved (tests, commits, dates, hashes)
- ✅ Clear deprecation notices
- ✅ Wave→Phase mapping for continuity

Impact: Documentation only, no code changes
Tests: All passing (no functional changes)
Validation: grep confirms no active wave references

Next: All orchestrators now work with unified PHASE→STAGE→TASK
```

---

**Ready for execution:** All steps planned, non-destructive, preserves history.
