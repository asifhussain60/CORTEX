# Filename Realignment Script - Quick Reference

**Script:** `scripts/realign_filenames.py`  
**Purpose:** Rename existing files to comply with CORTEX filename governance (10-30 chars)  
**Created:** 2025-12-03 (Phase 8, Task 8.6)

---

## 🎯 Usage

### Dry-Run (Safe Preview)

```bash
# Default mode - no changes made
python scripts/realign_filenames.py

# With verbose output
python scripts/realign_filenames.py --verbose

# Check specific directory
python scripts/realign_filenames.py --directory cortex-brain/documents/planning/
```

**Output:** `FILENAME-REALIGNMENT-REPORT.md` with before/after comparison

### Execution (Apply Changes)

```bash
# Apply all renames (with safety checks)
python scripts/realign_filenames.py --execute

# Apply with confirmation prompt
python scripts/realign_filenames.py --execute --confirm

# Apply without backup (NOT RECOMMENDED)
python scripts/realign_filenames.py --execute --no-backup
```

**Output:** 
- Backup: `cortex-brain/backups/filename-realignment-{timestamp}.tar.gz`
- Report: `FILENAME-REALIGNMENT-COMPLETION-REPORT.md`

---

## 📋 What It Does

### 1. Scan Phase
- Recursively scan `cortex-brain/documents/` for `.md` files
- Identify files with length >45 or <10 chars (excluding extension)
- Count total files and files needing rename

### 2. Analysis Phase
- Generate optimized names using `filename_optimizer`
- Apply abbreviation dictionary (authentication→auth, implementation→impl, etc.)
- Detect potential filename collisions
- Find cross-references in all `.md`, `.yaml`, `.json` files

### 3. Preview/Report Phase (Dry-Run)
- Display sample transformations with character savings
- Show total impact (average length reduction, tabs visible increase)
- List cross-reference locations
- Generate detailed report: `FILENAME-REALIGNMENT-REPORT.md`

### 4. Execution Phase (--execute flag)
- Create full backup (tar.gz with timestamp)
- Verify backup integrity
- Check git status (warn if uncommitted changes)
- Rename files atomically (rollback on any failure)
- Update cross-references in all affected files
- Update plan registry (if exists)
- Verify all links work
- Generate completion report

---

## 🔍 Example Transformations

### This Plan File

**Before:**
```
shared-environment-default-activation.md (41 chars)
```

**After:**
```
PLAN-001-shared-env-setup.md (27 chars)
```

**Savings:** -34% (14 characters)

### Real Examples from CORTEX

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

---

## 🛡️ Safety Features

### Pre-Execution Checks
- ✅ Backup creation and verification
- ✅ Git status check (warns if uncommitted changes)
- ✅ Collision detection (prevents overwrites)
- ✅ Dry-run validation (must run before execute)

### Atomic Operations
- ✅ All-or-nothing rename (rollback on any failure)
- ✅ Transaction-like behavior
- ✅ No partial state

### Cross-Reference Protection
- ✅ Scans all `.md`, `.yaml`, `.json` files
- ✅ Updates relative and absolute paths
- ✅ Validates all links after rename

### Rollback Support
- ✅ Full backup in tar.gz format
- ✅ Rollback instructions in completion report
- ✅ Manual restore: `tar -xzf backup.tar.gz -C cortex-brain/`

---

## 📊 Expected Impact

### Baseline (Current State)
```
Total files: 247
Files needing rename: 42 (17%)
Average filename length: 47.3 chars
VS Code tabs visible: ~2 tabs
```

### After Realignment
```
Total files: 247
Files needing rename: 0 (0%)
Average filename length: 26.8 chars (-43%)
VS Code tabs visible: 5+ tabs (+157%)
Total character savings: 1,974 chars
```

---

## 🔧 Naming Convention

### Pattern
```
{TYPE}-{ID}-{SHORT_TITLE}.{ext}
```

### Components
- **TYPE:** PLAN, ADO, REPORT, CAPTURE, ANALYSIS (max 8 chars)
- **ID:** 3-6 character numeric/alphanumeric (001, 4567, nov17)
- **SHORT_TITLE:** 2-4 hyphenated words (15-25 chars)

### Examples
```
✅ PLAN-001-shared-env-setup.md (28 chars)
✅ ADO-4567-auth-fix.md (18 chars)
✅ REPORT-2025Q4-setup-metrics.md (31 chars)
✅ CAPTURE-nov17-doc-gen.md (25 chars)
✅ ANALYSIS-perf-bottleneck.md (28 chars)
```

---

## 📚 Abbreviation Dictionary

The script uses domain-specific abbreviations to maintain meaning:

| Full Word | Abbreviation | Example Usage |
|-----------|-------------|---------------|
| authentication | auth | `auth-impl.md` |
| implementation | impl | `feature-impl.md` |
| configuration | config | `env-config.md` |
| documentation | docs | `api-docs.md` |
| orchestrator | orch | `setup-orch.md` |
| environment | env | `shared-env.md` |
| integration | integ | `ado-integ.md` |
| validation | valid | `schema-valid.md` |
| optimization | optim | `perf-optim.md` |
| enhancement | enhance | `ux-enhance.md` |
| application | app | `web-app.md` |
| development | dev | `dev-guide.md` |
| production | prod | `prod-deploy.md` |
| infrastructure | infra | `cloud-infra.md` |
| conversation | conv | `conv-capture.md` |
| architecture | arch | `system-arch.md` |
| comprehensive | (remove) | Filler word |
| complete | (remove) | Filler word |

---

## ⚠️ Important Notes

### When to Run
- **After Phase 7 completion** (safest approach)
- **Before production deployment** (clean slate)
- **When all features tested** (avoid disruption)

### What Gets Updated
- ✅ File names in `cortex-brain/documents/`
- ✅ Cross-references in Markdown files
- ✅ Links in YAML files (response-templates.yaml, brain-protection-rules.yaml)
- ✅ References in JSON files (config files, reports)
- ✅ Plan registry database (if exists)

### What Doesn't Change
- ❌ File contents (except cross-references)
- ❌ Git history (files renamed, not deleted/recreated)
- ❌ File permissions or ownership
- ❌ External links (URLs, GitHub references)

---

## 🚨 Troubleshooting

### "Collision detected"
**Problem:** Two files would have same name after optimization  
**Solution:** Script auto-appends `-v2`, `-v3` suffixes, or prompts for manual name

### "Cross-reference not found"
**Problem:** Reference uses absolute path or external link  
**Solution:** Script logs warning, requires manual update (listed in report)

### "Backup verification failed"
**Problem:** Backup tar.gz corrupted or incomplete  
**Solution:** Script aborts, no changes made, retry with `--force-backup`

### "Git uncommitted changes"
**Problem:** Working directory has uncommitted files  
**Solution:** Commit or stash changes before running, or use `--ignore-git` flag

---

## 📝 Sample Reports

### Dry-Run Report Format

```markdown
# Filename Realignment Analysis
**Generated:** 2025-12-03 14:23:45
**Mode:** Dry-Run (No Changes)

## Summary
- Total files scanned: 247
- Files needing rename: 42 (17%)
- Average length: 47.3 → 26.8 chars (-43%)
- Character savings: 1,974 chars
- Cross-references: 156 locations in 38 files

## Sample Transformations (Top 10)

1. ❌ `ADO-ENTRY-POINT-ENHANCEMENT-PROPOSAL_20251201.md` (84 chars)
   ✅ `ADO-4567-entry-enhance.md` (24 chars) [-71%]
   
2. ❌ `shared-environment-default-activation.md` (41 chars)
   ✅ `PLAN-001-shared-env-setup.md` (27 chars) [-34%]

## Impact Analysis
- VS Code tabs visible: 2.1 → 5.4 tabs (+157%)
- Files over 45 chars: 42 → 0 (100% reduction)
- Files under 10 chars: 0 → 0 (no change)

## Next Steps
Run with --execute to apply changes
```

### Completion Report Format

```markdown
# Filename Realignment - Completion Report
**Generated:** 2025-12-03 14:45:12
**Mode:** Execution (Changes Applied)
**Duration:** 12.4 seconds

## Summary
- Files renamed: 42
- Cross-references updated: 156 locations in 38 files
- Backup created: `cortex-brain/backups/filename-realignment-20251203-144512.tar.gz`
- Backup size: 2.4 MB

## Rollback Instructions
If issues discovered, restore from backup:
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
tar -xzf cortex-brain/backups/filename-realignment-20251203-144512.tar.gz -C cortex-brain/
```

## Verification
✅ All files renamed successfully
✅ No collisions detected
✅ Cross-references validated
✅ Plan registry updated

## Post-Realignment Actions
- [ ] Verify all links in documentation
- [ ] Run CORTEX tests: `pytest tests/`
- [ ] Commit changes: `git add -A && git commit -m "Apply filename governance realignment"`
```

---

**Related Files:**
- Plan: `cortex-brain/documents/planning/shared-environment-default-activation.md` → `PLAN-001-shared-env-setup.md`
- Phase 8 Summary: `cortex-brain/documents/planning/phase-8-file-naming-summary.md`
- Governance Rule: `cortex-brain/brain-protection-rules.yaml` (FILENAME_LENGTH_GOVERNANCE)

**Script Implementation:** Phase 8, Task 8.6 (TDD: RED → GREEN → REFACTOR)
