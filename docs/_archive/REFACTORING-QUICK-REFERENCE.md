# Agents & Prompts Refactoring - Quick Reference

**Date**: 2026-01-18  
**Status**: ✅ COMPLETE - All agents and prompts refactored  
**Requirement**: Learn from chat01.md SSOT issues and prevent recurrence

---

## What Was Fixed

### Original Issue (from chat01.md)
- Chat reported "100% COMPLETE" incorrectly
- Root cause: Multiple conflicting YAML files and wrong references
- .md files created in wrong locations (docs_md/, _workspaces/roadmap/, etc.)
- Inconsistent guidance across agents led to inconsistent behavior

### Solution Applied
- Unified file placement policy across ALL agents and prompts
- Explicit forbidden patterns with zero exceptions
- Validation checklists before every file output
- Clear SSOT (Single Source of Truth) designation
- Red flag detection for immediate action

---

## Changes by File

### Agents (8 files - All Updated/Recreated)

| Agent | Type | Changes |
|-------|------|---------|
| `cortex-builder.md` | Update | Unified policy + prevention checklist + enhanced governance |
| `cortex-gap-detection.md` | Update | Unified policy + YAML-only enforcement |
| `cortex-planner.md` | Recreate | Cleanup + unified policy + governance sections |
| `cortex-review-assumptions.md` | Recreate | Clean version with unified policy |
| `cortex-review-brittleness.md` | Recreate | Clean version with unified policy |
| `cortex-review-debt.md` | Recreate | Clean version with unified policy |
| `cortex-review-governance.md` | Recreate | Clean version with unified policy |
| `cortex-review-hallucination.md` | Recreate | Clean version with unified policy |

### Prompts (4 files - 2 Updated, 2 Verified)

| Prompt | Type | Changes |
|--------|------|---------|
| `cortex-builder.prompt.md` | Update | Unified policy + validation checklist |
| `cortex-git-commit.prompt.md` | Update | Unified policy consistency |
| `cortex-review.prompt.md` | Verify | ✅ Already good, no changes |
| `CORTEX.prompt.md` | Verify | ✅ Already good, no changes |

---

## Unified Policy (IN ALL AGENTS & PROMPTS)

### Forbidden File Patterns (ZERO EXCEPTIONS)
```
❌ .md files anywhere except docs/ → DELETE IMMEDIATELY
❌ docs_md/ folder → DELETE IMMEDIATELY
❌ Multiple cortex-*.yaml files → DELETE extra files
❌ .py scripts in root → DELETE at end of session
❌ .md files in _workspaces/roadmap/ → DELETE IMMEDIATELY
❌ References to .github/roadmap/ → FIX to _workspaces/roadmap/
```

### Correct File Locations (AUTHORITY LEVELS)
```
🔴 CANONICAL: _workspaces/roadmap/cortex-master.yaml
🟠 Authoritative: _workspaces/roadmap/phases/phase-NN.yaml
🟡 Implementation: src/, cortex-brain/tierX/, scripts/
🟢 Human-readable: docs/ (MD only)
🔵 Tracking: _workspaces/roadmap/reports/ (YAML only)
```

---

## Prevention Mechanisms

### 1. Validation Checklist
Every agent/prompt includes:
```
[ ] Markdown files? → MUST be docs/ (never elsewhere)
[ ] Creating docs_md/? → STOP - FORBIDDEN
[ ] Multiple cortex-*.yaml? → STOP - SSOT violation
[ ] Phase YAML? → MUST be _workspaces/roadmap/phases/
[ ] Python scripts? → Move to src/ or cortex-brain/ (not root)
[ ] Reading YAML? → Use ONLY cortex-master.yaml (not v1/v2)
```

### 2. Red Flag Detection 🚩
Explicit triggers for IMMEDIATE action:
```
🚩 .md files outside docs/
🚩 docs_md/ folder
🚩 Multiple cortex-*.yaml
🚩 Stray .py files in root
🚩 Wrong roadmap references
```

### 3. Forbidden Patterns Table
Clear, explicit table in EVERY agent showing:
- What is forbidden
- Why it's forbidden
- What action to take

### 4. Authority Levels
Each location shows its authority:
- CANONICAL = only this one (cortex-master.yaml)
- Authoritative = for this domain
- Human-readable = for humans to read
- Tracking = for structured data

### 5. Unified Policy (NO VARIATIONS)
Same policy appears in:
- ✅ All 8 agents (identical)
- ✅ All 4 prompts (identical)
- ✅ No local variations

---

## SSOT Clarification

### Master Plan (CANONICAL)
```yaml
Location: _workspaces/roadmap/cortex-master.yaml
Purpose: Single source of truth for all phases
Content: phase_tracker section shows current status
Authority: CANONICAL - this is the only one in use
Read: YES - verify status, track progress
Modify: ONLY for phase_tracker updates
```

### Reference/Archive
```yaml
Location: _workspaces/roadmap/_archives/cortex-master-v1.yaml
Purpose: Baseline (258+ completed ACs)
Authority: READ-ONLY - historical reference
Read: YES - for precedents, patterns
Modify: NEVER - this is archived
```

### Phase Details
```yaml
Location: _workspaces/roadmap/phases/phase-NN.yaml
Purpose: Detailed AC list for each phase
Authority: Authoritative for this phase
Read: YES - for AC details
Modify: YES - to update AC status
```

---

## How to Use Going Forward

### When Creating an Agent
1. Copy the unified policy section from any agent
2. Use identical forbidden patterns table
3. Include validation checklist (don't create variations)
4. Reference cortex-master.yaml (ONLY source)
5. Include red flag detection
6. Do NOT create local policy variations

### When Creating a Prompt
1. Same as agents - copy unified policy
2. Include validation checklist
3. Reference _workspaces/roadmap/cortex-master.yaml
4. Use identical authority levels table
5. Enforce ZERO EXCEPTIONS on file placement

### When Something Goes Wrong
1. Check red flag list - does it match?
2. Verify file locations using authority table
3. Check SSOT - are you reading cortex-master.yaml?
4. Run validation checklist - did you miss something?
5. Commit only after checklist passes

---

## Verification Commands

```bash
# 1. Verify unified policy is in all agents
grep -l "FILE PLACEMENT POLICY" .github/agents/*.md | wc -l
# Expected: 8

# 2. Verify no .github/roadmap references
grep -r ".github/roadmap" .github/ 2>/dev/null | wc -l
# Expected: 0

# 3. Verify cortex-master.yaml is referenced
grep -c "cortex-master.yaml" .github/agents/*.md .github/prompts/*.md
# Expected: Multiple in each file

# 4. Verify docs_md only mentioned as forbidden
grep -r "docs_md" .github/ | grep -v "FORBIDDEN" | wc -l
# Expected: 0

# 5. Verify no .py files in root
ls -la *.py 2>/dev/null | grep -v "launch-dashboard\|verify_orchestrator"
# Expected: nothing

# 6. Verify unified policy consistency
diff <(grep -A 20 "FILE PLACEMENT POLICY" .github/agents/cortex-builder.md) \
     <(grep -A 20 "FILE PLACEMENT POLICY" .github/agents/cortex-planner.md)
# Expected: identical content
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| File placement guidance | Scattered across 8 agents | Unified policy in ALL |
| .md file locations | Ambiguous | ONLY docs/ - no exceptions |
| docs_md/ handling | Not consistently prevented | Explicitly FORBIDDEN + checked |
| SSOT reference | Multiple files possible | ONLY cortex-master.yaml |
| Validation | Not enforced | Checklist before all outputs |
| Red flags | Not defined | Explicit 🚩 detection |
| Consistency | Different per agent | Identical across all |

**Result**: Prevents recurrence of chat01.md issue with unified, enforceable policy.
