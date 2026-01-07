# Root Folder Violation Analysis - cortex5-epic

**Analysis Date:** 2026-01-07T07:45:00Z  
**Epic:** cortex5-epic-v3  
**Analyzer:** CORTEX Planner v1.0.0

---

## 🚨 Governance Violation Detected

**Rule Violated:** `PLAN_FILE_ORGANIZATION` (SKULL)  
**Severity:** HIGH  
**Impact:** Cluttered root folder, conflicts with clean folder policy

---

## 📋 Current Root Files

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `00-cortex5-epic-v3.md` | 9.7 KB | Master plan (v3) | ❌ VIOLATES |
| `00-cortex5-epic.md` | 43.1 KB | Master plan (v2/legacy) | ❌ VIOLATES |
| `README.md` | 15.9 KB | Quick start guide | ❌ VIOLATES |
| `CONTINUATION-PROMPT.md` | 916 B | Session continuation | ✅ ALLOWED |
| `plan-viewer.html` | 35.0 KB | Visual progress viewer | ✅ ALLOWED |
| `intermittent-thoughts.txt` | 1.1 KB | Scratchpad notes | ✅ ALLOWED |
| `cortex-logo.png` | 22.1 KB | CORTEX logo | ⚠️ ALLOWED (temporary) |

**Total Root Files:** 7  
**Violations:** 3 files (00-cortex5-epic-v3.md, 00-cortex5-epic.md, README.md)

---

## 🔍 Root Cause Analysis

### Why 00-* Files Were Created

**Pattern Origin:** Planning System v5.0 manifest (lines 118-157)

```yaml
required_files:
  - path: "00-{plan-name}.md"
    type: "plan"
    description: "Master plan document with meaningful name"
```

**Intent:** Master plan documents were designed to be quickly accessible on root.

**Problem:** This violates SKULL rule `PLAN_FILE_ORGANIZATION`:
- ✅ **ONLY allowed:** `plan-viewer.html` + `CONTINUATION-PROMPT.md` + `intermittent-thoughts.txt`
- ❌ **NOT allowed:** Master plans, READMEs, or any other markdown files

---

## 📐 Governance Policy (SKULL Rules)

### PLAN_FILE_ORGANIZATION Rule

**Source:** `cortex-brain/brain-protection-rules.yaml`

```yaml
PLAN_FILE_ORGANIZATION:
  description: "Only plan-viewer.html, CONTINUATION-PROMPT.md, and intermittent-thoughts.txt allowed on root"
  enforcement: "automated"
  violations:
    - "00-*.md files on root"
    - "README.md on root"
    - "Summary reports on root"
    - "Documentation files on root"
  
  correct_structure:
    root:
      - "plan-viewer.html"
      - "CONTINUATION-PROMPT.md"
      - "intermittent-thoughts.txt"
    
    subfolders:
      - "analysis/" # Gap analysis, architectural reviews
      - "artifacts/" # Generated code, configs
      - "context/" # Discovery reports, background
      - "reports/" # Progress reports, summaries
      - "tracking/" # Progress tracker, state
      - "phases/" # Phase-specific artifacts (EPIC mode)
```

---

## 🎯 Remediation Plan

### Action 1: Move 00-* Files to reports/

**Rationale:** Master plan documents are reference documentation, belong in `reports/`

```bash
mv 00-cortex5-epic-v3.md reports/master-plan-v3.md
mv 00-cortex5-epic.md reports/master-plan-v2-legacy.md
```

**Benefits:**
- ✅ Compliance with SKULL rules
- ✅ Clear separation: root = active files, reports/ = reference docs
- ✅ Easier to find archived plans (all in reports/)

---

### Action 2: Move README.md to reports/

**Rationale:** Quick start guides are onboarding documentation, not active files

```bash
mv README.md reports/quick-start-guide.md
```

**Benefits:**
- ✅ Compliance with SKULL rules
- ✅ Documentation centralized in reports/

---

### Action 3: Create Centralized Images Folder

**Rationale:** Logo is common across all plans, should not duplicate

**Option A: Centralized (Recommended)**
```bash
mkdir -p cortex-brain/documents/planning/assets/images/
cp cortex-logo.png cortex-brain/documents/planning/assets/images/
# Update plan-viewer.html to use relative path
```

**Option B: Per-Plan Images Subfolder**
```bash
mkdir -p images/
mv cortex-logo.png images/
# Update plan-viewer.html to use images/ subfolder
```

**Recommendation:** Use Option A (centralized) to avoid duplication across 10+ plans.

---

### Action 4: Update Vacuum Orchestrator

**Add Pattern:** `00-*.md` files on plan root

**File:** `cortex-brain/cleanup-rules.yaml`

```yaml
plan_root_violations:
  - pattern: "00-*.md"
    action: "move"
    destination: "reports/"
    reason: "Master plans belong in reports/, not root"
  
  - pattern: "README.md"
    action: "move"
    destination: "reports/"
    reason: "Quick start guides belong in reports/"
  
  - pattern: "*.png"
    action: "move"
    destination: "images/"
    reason: "Images belong in images/ subfolder"
    exceptions:
      - "plan-viewer.html" # Embedded data URIs allowed
```

---

## 🔄 Execution Steps

1. **Move master plans to reports/**
   ```bash
   mv 00-cortex5-epic-v3.md reports/master-plan-v3.md
   mv 00-cortex5-epic.md reports/master-plan-v2-legacy.md
   ```

2. **Move README to reports/**
   ```bash
   mv README.md reports/quick-start-guide.md
   ```

3. **Create centralized images folder**
   ```bash
   mkdir -p ../../assets/images/
   cp cortex-logo.png ../../assets/images/cortex-logo-200.png
   ```

4. **Update plan-viewer.html**
   ```html
   <!-- Before -->
   <img src="cortex-logo.png" alt="CORTEX Logo" />
   
   <!-- After -->
   <img src="../../assets/images/cortex-logo-200.png" alt="CORTEX Logo" />
   ```

5. **Remove duplicate logo**
   ```bash
   rm cortex-logo.png
   ```

6. **Update vacuum orchestrator rules**
   - Add `00-*.md` pattern to cleanup-rules.yaml
   - Add `README.md` pattern to cleanup-rules.yaml

7. **Run vacuum to validate**
   ```bash
   python3 -m src.main "vacuum cortex-brain/documents/planning/active/cortex5-epic --dry-run"
   ```

8. **Commit changes**
   ```bash
   git add .
   git commit -m "fix(cortex5-epic): Enforce PLAN_FILE_ORGANIZATION SKULL rule

   - Moved 00-*.md files to reports/ (master plans are reference docs)
   - Moved README.md to reports/quick-start-guide.md
   - Centralized cortex-logo.png in planning/assets/images/
   - Updated plan-viewer.html to use centralized logo path
   - Updated vacuum rules to prevent future violations
   
   Root folder now: 3 files (plan-viewer.html, CONTINUATION-PROMPT.md, intermittent-thoughts.txt)
   
   Co-authored-by: CORTEX Planner v1.0.0 <cortex@asifhussain.dev>"
   ```

---

## ✅ Expected Final State

**Root Folder (3 files only):**
- ✅ `plan-viewer.html` (35 KB)
- ✅ `CONTINUATION-PROMPT.md` (916 B)
- ✅ `intermittent-thoughts.txt` (1.1 KB)

**reports/ Folder (documentation):**
- ✅ `master-plan-v3.md` (9.7 KB, moved from root)
- ✅ `master-plan-v2-legacy.md` (43.1 KB, moved from root)
- ✅ `quick-start-guide.md` (15.9 KB, moved from root)

**../../assets/images/ (centralized):**
- ✅ `cortex-logo-200.png` (22.1 KB, centralized for all plans)

**Vacuum Rules Updated:**
- ✅ `00-*.md` → move to reports/
- ✅ `README.md` → move to reports/

---

## 📊 Compliance Status

| Rule | Before | After |
|------|--------|-------|
| **PLAN_FILE_ORGANIZATION** | ❌ FAIL (7 files) | ✅ PASS (3 files) |
| **NO_SUMMARY_FILES** | ✅ PASS | ✅ PASS |
| **VACUUM_MANDATORY** | ⏸️ N/A | ✅ EXECUTED |
| **VIEWER_UPDATE_MANDATORY** | ⏸️ N/A | ✅ UPDATED |

**Overall Compliance:** ❌ 25% → ✅ 100%

---

**Analysis Complete:** Ready for execution  
**Next Step:** Execute remediation plan via terminal commands
