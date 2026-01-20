# CORTEX Prompts & Agents Refactoring - 2026-01-18

## Overview

All prompts and agents have been refactored to prevent the SSOT conflicts discovered in chat01.md. The key improvement is **unified, consistent file placement policy** enforced across ALL agents and prompts with NO exceptions.

---

## Issues Fixed (From chat01.md Analysis)

### Issue 1: Multiple SSOT References (CRITICAL)
- **Problem**: Some agents/prompts referenced `.github/roadmap/cortex-master.yaml` instead of `_workspaces/roadmap/cortex-master.yaml`
- **Impact**: False status reports, confusion about which file is authoritative
- **Fix**: ALL agents now use ONLY `_workspaces/roadmap/cortex-master.yaml` as SSOT

### Issue 2: Conflicting File Creation (CRITICAL)
- **Problem**: Inconsistent guidance across prompts about where to create .md files
- **Impact**: Files created in wrong locations (docs_md/, _workspaces/roadmap/, root)
- **Fix**: Unified policy - `.md` files ONLY in `docs/` folder, with zero exceptions

### Issue 3: docs_md/ Folder Creation (CRITICAL)
- **Problem**: Some prompts allowed or didn't prevent creation of docs_md/ folder
- **Impact**: Structure violation, confusion about documentation location
- **Fix**: ALL prompts explicitly forbid and check for docs_md/ creation

### Issue 4: Multiple cortex-*.yaml Files
- **Problem**: Archived and versioned files (v1, v2) could be read instead of current
- **Impact**: Reading outdated phase_tracker, incorrect status reports
- **Fix**: ALL prompts specify reading ONLY cortex-master.yaml (current version)

### Issue 5: Inconsistent Policy Documentation
- **Problem**: Similar guidance repeated with slight variations across 8+ files
- **Impact**: Confusion about what's allowed, different behaviors in different agents
- **Fix**: Unified policy table that's identical across ALL agents and prompts

---

## Refactoring Changes

### Agents (8 total)
All agents now have:
- ✅ Unified 🚫 FILE PLACEMENT POLICY section at top
- ✅ Red flag detection checklist
- ✅ Explicit forbidden patterns table
- ✅ SSOT source reference: `_workspaces/roadmap/cortex-master.yaml`
- ✅ Correct file locations table with authority levels

**Refactored Agents:**
1. `cortex-builder.md` - ✅ Refactored + expanded governance section
2. `cortex-gap-detection.md` - ✅ Refactored + prevention checklist
3. `cortex-planner.md` - ✅ Recreated (was corrupted)
4. `cortex-review-assumptions.md` - ✅ Recreated cleanly
5. `cortex-review-brittleness.md` - ✅ Recreated cleanly
6. `cortex-review-debt.md` - ✅ Recreated cleanly
7. `cortex-review-governance.md` - ✅ Recreated cleanly
8. `cortex-review-hallucination.md` - ✅ Recreated cleanly

### Prompts (4 total)
All prompts now have:
- ✅ Unified FILE PLACEMENT POLICY (identical to agents)
- ✅ PRE-IMPLEMENTATION VALIDATION CHECKLIST
- ✅ Red flag detection
- ✅ SSOT clarification section
- ✅ Forbidden patterns explicitly listed

**Refactored Prompts:**
1. `cortex-builder.prompt.md` - ✅ Updated with unified policy + validation checklist
2. `cortex-git-commit.prompt.md` - ✅ Updated with unified policy
3. `cortex-review.prompt.md` - Unchanged (already good)
4. `CORTEX.prompt.md` - Unchanged (already good)

---

## Key Prevention Mechanisms Added

### 1. Validation Checklist (Before Any File Output)
```
[ ] Markdown files? → MUST be docs/FILENAME.md (never elsewhere)
[ ] Creating docs_md/? → STOP - FORBIDDEN
[ ] Multiple cortex-*.yaml? → STOP - Keep ONLY cortex-master.yaml
[ ] Phase YAML? → MUST be _workspaces/roadmap/phases/phase-NN.yaml
[ ] Python scripts? → Move to src/, cortex_brain/, or scripts/ (not root)
[ ] Reading YAML? → Use ONLY _workspaces/roadmap/cortex-master.yaml
```

### 2. Forbidden Patterns Table
Explicit table in EVERY agent/prompt showing:
- What is forbidden (e.g., `docs_md/` folder)
- Why it's forbidden (e.g., structure violation)
- Immediate action required (e.g., DELETE IMMEDIATELY)

### 3. Red Flag Detection (🚩)
Explicit red flag list that triggers STOP & FIX IMMEDIATELY:
- `.md` files outside `docs/`
- `docs_md/` folder creation
- Multiple cortex-*.yaml files
- Stray `.py` files in root

### 4. File Location Authority Table
Shows not just location but AUTHORITY level:
- **CANONICAL**: Master plan (cortex-master.yaml)
- **Authoritative**: Phase specs (phase-XX.yaml)
- **Human-readable**: Docs in `docs/`
- **Tracking**: YAML reports

### 5. Unified Policy (NO Variations)
Same policy table appears in:
- ✅ All 8 agents (identical)
- ✅ All 4 prompts (identical)
- ✅ No local variations allowed

---

## Architecture Changes

### Before Refactoring
```
Agent 1: "Create MD files in docs/"
Agent 2: "Create MD files in docs/ or _workspaces/roadmap/"
Agent 3: "Create MD files in docs/, _workspaces/roadmap/, or root"
Prompt 1: "MD files forbidden outside docs/"
Prompt 2: "MD files in docs/ unless reports"
Prompt 3: "Unclear guidance"

Result: Conflicting behavior, files in wrong locations
```

### After Refactoring
```
Agent 1-8: "MD files ONLY in docs/ - no exceptions"
Prompt 1-4: "MD files ONLY in docs/ - no exceptions"

Same file placement policy table used by ALL:
- Consistent enforcement
- Zero ambiguity
- One source of guidance
- Unified prevention mechanism

Result: Single, clear, enforced standard
```

---

## File Summary

### Agents - Before & After
| Agent | Status | Changes |
|-------|--------|---------|
| cortex-builder.md | ✅ Updated | Added unified policy, enhanced governance section, prevention checklist |
| cortex-gap-detection.md | ✅ Updated | Added unified policy, prevention checklist |
| cortex-planner.md | ✅ Recreated | Cleaned up corruption, added unified policy |
| cortex-review-assumptions.md | ✅ Recreated | Full cleanup, added unified policy |
| cortex-review-brittleness.md | ✅ Recreated | Full cleanup, added unified policy |
| cortex-review-debt.md | ✅ Recreated | Full cleanup, added unified policy |
| cortex-review-governance.md | ✅ Recreated | Full cleanup, added unified policy |
| cortex-review-hallucination.md | ✅ Recreated | Full cleanup, added unified policy |

### Prompts - Before & After
| Prompt | Status | Changes |
|--------|--------|---------|
| cortex-builder.prompt.md | ✅ Updated | Added unified policy, validation checklist, SSOT clarification |
| cortex-git-commit.prompt.md | ✅ Updated | Added unified policy section, consistency |
| cortex-review.prompt.md | ℹ️ Verified | Already good, no changes needed |
| CORTEX.prompt.md | ℹ️ Verified | Already good, no changes needed |

---

## SSOT Verification

### Single Source of Truth (SSOT) Established
- **Master Plan**: `_workspaces/roadmap/cortex-master.yaml` ← ONLY current source
- **Reference**: `_workspaces/roadmap/_archives/cortex-master-v1.yaml` ← READ-ONLY
- **Phases**: `_workspaces/roadmap/phases/phase-NN.yaml` ← Authoritative per phase

### How This Prevents chat01.md Issue
1. **Clear SSOT Reference**: All prompts/agents now reference cortex-master.yaml (not v1/v2/archived)
2. **Authority Levels**: Each file location shows authority level (CANONICAL, Authoritative, etc.)
3. **Unified Reading Instructions**: "Use ONLY _workspaces/roadmap/cortex-master.yaml" appears in every agent
4. **Validation Before Reading**: Checklist verifies correct YAML file is being used

---

## Testing the Refactoring

### Manual Verification
Run these commands to verify refactoring:

```bash
# 1. Check all agents have unified policy
grep -l "FILE PLACEMENT POLICY" .github/agents/*.md | wc -l
# Expected: 8

# 2. Verify no references to .github/roadmap/
grep -r ".github/roadmap" .github/agents/ .github/prompts/ 2>/dev/null | wc -l
# Expected: 0

# 3. Verify all reference cortex-master.yaml (current)
grep -c "cortex-master.yaml" .github/agents/*.md .github/prompts/*.md
# Expected: Multiple references in each file

# 4. Verify no docs_md/ references (except as "forbidden")
grep -r "docs_md" .github/agents/ .github/prompts/ | grep -v "FORBIDDEN" | wc -l
# Expected: 0 (only in "FORBIDDEN" context)

# 5. Verify YAML only enforcement for reports
grep -c "YAML only" .github/agents/*.md .github/prompts/*.md
# Expected: Multiple hits showing YAML-only for reports
```

---

## Lessons Learned for Future Prevention

### What Caused the Issue
1. **Lack of unified policy** - Different agents had different guidance
2. **Gradual drift** - Over time, files ended up in wrong places
3. **No prevention mechanism** - No checklist to catch errors before committing
4. **Ambiguous authority** - Multiple YAML files could be read

### How Refactoring Prevents Recurrence
1. **Unified Policy** - One policy table, used by ALL
2. **Explicit Forbidden Patterns** - Can't miss what's forbidden
3. **Red Flag Detection** - 🚩 triggers immediate action
4. **Authority Levels** - Clear which file is CANONICAL
5. **Validation Checklist** - Must verify before output
6. **Consistent Enforcement** - No variations across agents

---

## Going Forward

### For Agent/Prompt Developers
1. **Copy the unified policy table** - Don't create new variations
2. **Include validation checklist** - Verify before all outputs
3. **Reference cortex-master.yaml** - ONLY current SSOT
4. **Use red flag detection** - Act immediately on violations
5. **Keep consistency** - This standard applies to ALL future agents

### For Future Enhancement
If new agents are needed:
1. Start with template that has unified policy
2. Use identical file placement policy table
3. Include validation checklist
4. Test that references are correct
5. Never create local variations of the policy

---

## Summary

**Before**: Inconsistent guidance across 8 agents + 4 prompts = conflicting behavior, wrong files, wrong SSOT
**After**: Unified policy enforced across ALL agents + prompts = consistent behavior, correct files, single SSOT

**Prevention**: Validation checklists, red flag detection, and explicit forbidden patterns prevent recurrence.
