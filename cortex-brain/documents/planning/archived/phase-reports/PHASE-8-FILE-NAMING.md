# File Naming Governance - Phase 8 Summary

**Feature:** CORTEX-SETUP-001 Phase 8  
**Created:** 2025-12-03  
**Problem:** Excessively long filenames (up to 84 chars) causing VS Code tab overflow

---

## 🎯 Problem Statement

**Current State:**
- Filenames up to 84 characters long
- VS Code tabs consume entire screen
- Difficult to scan and find files
- Redundant timestamps and verbose descriptions
- No governance or validation

**Examples of Problem Files:**
```
❌ ADO-ENTRY-POINT-ENHANCEMENT-PROPOSAL_20251201_20251201_20251202_20251202_20251202.md (84 chars)
❌ CONVERSATION-CAPTURE-2025-11-17-DOCUMENT-GENERATION-VALIDATION-GAP.md (69 chars)
❌ PLAN-2025-11-21-ENTERPRISE-DOC-ORCHESTRATOR-IMAGE-INTEGRATION.md (64 chars)
```

**Impact:**
- 🔴 **UX:** Only 1-2 tabs visible in VS Code
- 🔴 **Productivity:** Excessive scrolling to find files
- 🔴 **Maintenance:** Hard to reference files in documentation
- 🟡 **Professionalism:** Looks disorganized

---

## ✅ Solution

### Filename Length Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| **Maximum** | 45 characters | ~5 tabs visible in VS Code |
| **Minimum** | 10 characters | Prevents meaningless names |
| **Optimal** | 20-35 characters | Descriptive yet concise |

### Naming Convention Pattern

```
{TYPE}-{ID}-{SHORT_TITLE}.{ext}
```

**Components:**
- **TYPE:** PLAN, ADO, REPORT, CAPTURE, ANALYSIS (max 8 chars)
- **ID:** 3-6 character numeric/alphanumeric
- **SHORT_TITLE:** 2-4 hyphenated words (15-25 chars)

**Good Examples:**
```
✅ PLAN-001-shared-env-setup.md (28 chars)
✅ ADO-4567-auth-fix.md (18 chars)
✅ REPORT-2025Q4-setup-metrics.md (31 chars)
✅ CAPTURE-nov17-doc-gen.md (25 chars)
```

**Bad Examples:**
```
❌ PLAN-2025-11-17-COMPREHENSIVE-IMPLEMENTATION-STRATEGY.md (60 chars)
❌ doc.md (3 chars - too short)
❌ p.md (1 char - meaningless)
```

---

## 🔧 Implementation

### 8 Tasks (1-2 days)

1. **Tier 0 Governance Rule** - Add `FILENAME_LENGTH_GOVERNANCE` to brain protection rules
2. **Naming Convention Docs** - Create official guidelines with examples
3. **Filename Validator** - Utility to check filename validity
4. **Shortening Algorithm** - Intelligent abbreviation engine
5. **Planning Orchestrator Update** - Generate short filenames automatically
6. **Realignment Script** - Comprehensive migration tool for existing files (dry-run + execute modes)
7. **Pre-Commit Hook** - Git hook warns on long filenames
8. **Documentation Updates** - Add conventions to all guides

**Key Enhancement:** Task 6 expanded from simple "bulk rename" to full realignment script with atomic operations, cross-reference updating, backup/rollback, and detailed reporting.

---

## 📚 Abbreviation Dictionary

Domain-specific abbreviations to maintain meaning while shortening:

| Full Word | Abbreviation | Example |
|-----------|-------------|---------|
| authentication | auth | `auth-impl.md` |
| implementation | impl | `feature-impl.md` |
| configuration | config | `env-config.md` |
| documentation | docs | `api-docs.md` |
| orchestrator | orch | `setup-orch.md` |
| environment | env | `shared-env.md` |
| integration | integ | `ado-integ.md` |
| validation | valid | `schema-valid.md` |
| optimization | optim | `perf-optim.md` |
| comprehensive | (remove) | Filler word |
| complete | (remove) | Filler word |
| enhancement | enhance | `ux-enhance.md` |
| application | app | `web-app.md` |

---

## 🛡️ Tier 0 Governance Rule

**Instinct:** `FILENAME_LENGTH_GOVERNANCE`  
**Severity:** WARNING (not blocking)  
**Scope:** All documents, plans, reports, captures in `cortex-brain/documents/`

**Validation Logic:**
```python
def validate_filename(filename: str) -> tuple[bool, str, Optional[str]]:
    name_without_ext = filename.rsplit('.', 1)[0]
    length = len(name_without_ext)
    
    if length > 45:
        suggestion = abbreviate_filename(filename)
        return (False, f"Too long ({length} chars, max 45)", suggestion)
    
    if length < 10:
        return (False, f"Too short ({length} chars, min 10)", None)
    
    return (True, "Valid filename", None)
```

**Warning Output:**
```
⚠️  Filename too long: 'PLAN-2025-11-17-comprehensive-impl.md' (42 chars)

Guideline:
- Maximum: 45 chars
- Minimum: 10 chars
- Optimal: 20-35 chars

✅ Suggested: 'PLAN-001-comp-impl.md' (22 chars)

Rationale: Maintain readability in VS Code tabs
```

---

## 📊 Expected Impact

### Before (Current State)
```
VS Code Tab Bar:
[PLAN-2025-11-17-COMPREHENSIVE-IMPLEMENTATION...] [ADO-ENTRY-POINT-EN...]
```
Only 2 tabs visible, excessive scrolling

### After (With Governance)
```
VS Code Tab Bar:
[PLAN-001-impl] [ADO-4567-auth] [REPORT-Q4-metrics] [CAPTURE-docs] [ANALYSIS-perf]
```
5+ tabs visible, easy scanning

### Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Average filename length | 52 chars | 28 chars | 46% reduction |
| Tabs visible in VS Code | 1-2 | 5-6 | 3x increase |
| File scan time | ~10s | ~2s | 80% faster |
| Tab overflow instances | 95% | <5% | 95% reduction |

---

## 🚀 Migration Strategy

### Realignment Script Process

**Script:** `scripts/realign_filenames.py`  
**Modes:** Dry-run (default) and Execute (--execute flag)

**Phase 1: Scan & Analysis**
1. **Scan:** Find all `.md` files in `cortex-brain/documents/` >45 or <10 chars
2. **Analyze:** Generate optimized names using abbreviation dictionary
3. **Detect:** Identify potential filename collisions
4. **Map:** Find all cross-references in `.md`, `.yaml`, `.json` files

**Phase 2: Preview (Dry-Run Mode)**
1. **Display:** Show sample transformations with character savings
2. **Report:** Generate `FILENAME-REALIGNMENT-REPORT.md` with impact analysis
3. **Estimate:** Calculate average length reduction and tabs visible improvement
4. **Exit:** No changes made, exit code 0

**Phase 3: Execution (--execute flag)**
1. **Backup:** Create `cortex-brain/backups/filename-realignment-{timestamp}.tar.gz`
2. **Verify:** Ensure backup integrity before proceeding
3. **Git Check:** Warn if uncommitted changes exist
4. **Rename:** Atomically rename all files (rollback on any failure)
5. **Update:** Modify cross-references in all affected files
6. **Registry:** Update plan registry database (if exists)
7. **Validate:** Verify all links work post-rename
8. **Report:** Generate `FILENAME-REALIGNMENT-COMPLETION-REPORT.md`

### Safety Features

**Pre-Execution:**
- ✅ Backup creation and verification
- ✅ Git status check
- ✅ Collision detection
- ✅ Dry-run requirement (must preview first)

**During Execution:**
- ✅ Atomic operations (all-or-nothing)
- ✅ Transaction-like rollback on failure
- ✅ No partial state

**Post-Execution:**
- ✅ Link validation
- ✅ Completion report with rollback instructions
- ✅ Backup available for manual restore

### Example Migration

**This Plan File:**

**Before:**
```
shared-environment-default-activation.md (41 chars) ❌
```

**After:**
```
PLAN-001-shared-env-setup.md (27 chars) ✅ [-34%]
```

**Cross-Reference Updates:**
```diff
- See [feature plan](./shared-environment-default-activation.md)
+ See [feature plan](./PLAN-001-shared-env-setup.md)
```

**Real CORTEX Examples:**

**Before:**
```
ADO-ENTRY-POINT-ENHANCEMENT-PROPOSAL_20251201_20251201_20251202_20251202_20251202.md (84 chars) ❌
CONVERSATION-CAPTURE-2025-11-17-DOCUMENT-GENERATION-VALIDATION-GAP.md (69 chars) ❌
PLAN-2025-11-21-ENTERPRISE-DOC-ORCHESTRATOR-IMAGE-INTEGRATION.md (64 chars) ❌
```

**After:**
```
ADO-4567-entry-enhance.md (24 chars) ✅ [-71%]
CAPTURE-nov17-doc-gen-gap.md (28 chars) ✅ [-59%]
PLAN-002-doc-orch-image-integ.md (32 chars) ✅ [-50%]
```

### Usage Examples

**Dry-Run (Safe Preview):**
```bash
# Default mode - no changes made
python scripts/realign_filenames.py

# With verbose output
python scripts/realign_filenames.py --verbose

# Check specific directory
python scripts/realign_filenames.py --directory cortex-brain/documents/planning/
```

**Execution (Apply Changes):**
```bash
# Apply all renames (with safety checks)
python scripts/realign_filenames.py --execute

# Apply with confirmation prompt
python scripts/realign_filenames.py --execute --confirm

# Force execution (skip warnings)
python scripts/realign_filenames.py --execute --force
```

**Rollback (If Needed):**
```bash
# Restore from backup
cd /Users/asifhussain/PROJECTS/CORTEX
tar -xzf cortex-brain/backups/filename-realignment-{timestamp}.tar.gz -C cortex-brain/
```

---

## 🔍 Validation & Enforcement

### Automated Checks

1. **Brain Protector** - Warns during file creation
2. **Filename Validator** - Pre-save validation
3. **Pre-Commit Hook** - Git commit validation (warning only)
4. **Plan Registry** - Enforces pattern on plan creation

### Warning Flow

```
User creates: "PLAN-2025-12-03-very-long-comprehensive-implementation-strategy.md"
           ↓
Brain Protector detects: 68 characters (exceeds 45)
           ↓
Warning displayed:
  ⚠️  Filename too long (68 chars, max 45)
  ✅ Suggested: "PLAN-002-impl-strategy.md" (26 chars)
  
  Continue anyway? (Y/n)
           ↓
User chooses: Accept suggestion → File created with short name
```

---

## 📝 Documentation Updates

**Files to Update:**
1. `CORTEX.prompt.md` - Add filename convention section
2. `.github/copilot-instructions.md` - Update governance rules
3. `cortex-brain/documents/naming-conventions.md` - New comprehensive guide
4. `cortex-brain/documents/implementation-guides/filename-best-practices.md` - Developer guide

**Key Messages:**
- Filenames should be scannable in VS Code tabs
- Use abbreviations from domain dictionary
- Follow {TYPE}-{ID}-{SHORT_TITLE} pattern
- Optimal length: 20-35 characters

---

## ✅ Success Criteria

- [ ] Tier 0 rule added to `brain-protection-rules.yaml`
- [ ] Validator warns on files >45 or <10 chars
- [ ] Abbreviation dictionary with 20+ domain terms
- [ ] Planning orchestrator generates short names
- [ ] Bulk rename script migrates 50+ existing files
- [ ] Pre-commit hook active and functional
- [ ] All documentation updated
- [ ] 20+ tests covering validation/optimization

---

## 🎓 Best Practices

**Do:**
- ✅ Use meaningful abbreviations from dictionary
- ✅ Follow {TYPE}-{ID}-{SHORT_TITLE} pattern
- ✅ Keep filenames 20-35 characters
- ✅ Use hyphens for word separation
- ✅ Test filename in VS Code tab before committing

**Don't:**
- ❌ Include full dates (use short IDs instead)
- ❌ Use filler words (comprehensive, complete, full)
- ❌ Create ambiguous abbreviations (doc.md, p.md)
- ❌ Exceed 45 character maximum
- ❌ Go below 10 character minimum

---

**Next Action:** Implement Phase 8 tasks to establish file naming governance globally across CORTEX

*This is a holistic solution addressing file naming across all CORTEX operations and documents.*
