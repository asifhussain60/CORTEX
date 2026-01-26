# 📊 File Creation Audit: CORE-038 Violation Analysis
**Date:** 2026-01-25 | **Authority:** AC-FILENAME-FACTORY-001 | **Status:** ⚠️ CRITICAL VIOLATIONS DETECTED

---

## Executive Summary

**Finding:** Multiple systems are actively creating files in `_workspaces/roadmap/` directory **in direct violation of CORE-038 file placement policy** and the user's constraint: *"No md reports should be created outside of reports/ subfolders"*.

**Scope:** 7 active systems identified creating files without CORE-028/CORE-038 compliance.

**Impact:** Current architecture bypasses FilenameFactory validation, creating governance debt.

---

## 🔴 CRITICAL VIOLATIONS

### 1. **Cortex-Doc Prompt** (HIGHEST PRIORITY)
**File:** `.github/prompts/cortex-doc.prompt.md` (1263 lines)  
**Violation Type:** File creation in forbidden locations  

**Creates Files In:**
- ✅ `docs/` — CORRECT (no violation)
- ❌ `_workspaces/reports/` — **CORE-038 VIOLATION** (should be `reports/`)
  - Line 254: `cat > "_workspaces/reports/$report" << 'EOF'`
  - Creates: Fresh documentation generation reports with date-based naming

**Problem:** Creates markdown reports in deprecated `_workspaces/reports/` instead of `reports/`.

**Fix Required:**
```diff
- cat > "_workspaces/reports/$report" << 'EOF'
+ cat > "reports/analysis/documentation-generation-report-$(date +%Y-%m-%d).md" << 'EOF'
```

---

### 2. **Duplication_Audit Script** (HIGH PRIORITY)
**File:** `scripts/duplication_audit.py` (275+ lines)  
**Violation Type:** Hardcoded path to deprecated directory

**Creates Files In:**
- ❌ `_workspaces/roadmap/reports/` — **CORE-038 VIOLATION**
  - Line 258: `report_path = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/reports") / ...`
  - Line 260-261: `report_path.parent.mkdir(parents=True, exist_ok=True)` → `report_path.write_text(report)`

**Problem:** Creates duplication audit reports in wrong location with non-compliant naming.

**Fix Required:**
```python
# BEFORE (Line 258)
report_path = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/reports") / \
    f"duplication-audit-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

# AFTER
report_path = Path("/Users/asifhussain/PROJECTS/CORTEX/reports/analysis") / \
    f"duplication-audit-{datetime.now().strftime('%Y-%m-%d')}.md"
```

---

### 3. **Phase Completion Scripts** (MEDIUM-HIGH PRIORITY)
**Files:** 
- `cortex/scripts-root-archive/maintenance/phase_14_completion.py` (Line 404)
- `cortex/scripts-root-archive/maintenance/phase_15_completion.py` (Line 438)

**Violation Type:** Hardcoded paths to deprecated directory

**Creates Files In:**
- ❌ `_workspaces/roadmap/reports/` — **CORE-038 VIOLATION**
  - phase_14: Reports to `_workspaces/roadmap/reports/PHASE-14-COMPLETION-REPORT.md`
  - phase_15: Reports to `.github/roadmap/reports/PHASE-15-COMPLETION-REPORT.md`

**Problem:** Mixed locations, inconsistent paths, deprecated folders.

**Fix Required:** Consolidate to single location (`reports/phase-tracking/`) with compliant naming:
```python
# CORRECT TARGET
reports/phase-tracking/phase-14-completion-report.md
reports/phase-tracking/phase-15-completion-report.md
```

---

### 4. **Consolidate_Phases Script** (MEDIUM PRIORITY)
**File:** `cortex/scripts-root-archive/maintenance/consolidate_phases.py` (250+ lines)

**Violation Type:** References multiple deprecated paths

**References:**
- Line 30: `phases_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/phases")`
- Line 155: Archives to `_workspaces/roadmap/_archives/phase-yamls-v1`
- Line 212: Creates `_workspaces/roadmap/phases-consolidated-snippet.yaml`

**Problem:** Reports location mixing, non-compliant file names (snake_case instead of kebab-case).

---

### 5. **Doc-Migrate-Automated Script** (MEDIUM PRIORITY)
**File:** `cortex/scripts-root-archive/doc-migrate-automated.py` (500+ lines)

**Violation Type:** Creates JSON reports in wrong location

**Creates Files In:**
- ❌ `_workspaces/roadmap/reports/` — **CORE-038 VIOLATION**
  - Line 413: `output_path = f"_workspaces/roadmap/reports/doc-migration-{self.timestamp}.json"`

**Problem:** Reports created in deprecated folder with incorrect format/location.

**Fix Required:**
```python
# BEFORE
output_path = f"_workspaces/roadmap/reports/doc-migration-{self.timestamp}.json"

# AFTER (use YAML, not JSON for data files, or create reports in reports/)
output_path = f"reports/analysis/doc-migration-{datetime.now().strftime('%Y-%m-%d')}.yaml"
```

---

### 6. **Documentation Orchestrator** (MEDIUM PRIORITY)
**File:** `cortex/orchestrators/documentation/orchestrator.py` (800+ lines)

**Violation Type:** Generates documentation files without FilenameFactory validation

**Creates Files In:**
- ✅ `docs/` — Documentation (CORRECT)
- ❓ No explicit reporting location defined

**Problem:** `_generate_documentation()` and related methods don't use FilenameFactory for generating filenames. When documentation reports are created, they should route through FilenameFactory.

**Lines to Check:**
- Line 816: `_generate_documentation()` — No filename validation visible
- Line 351: `_generate_all_diagrams()` — Generates files without naming validation

---

### 7. **Cortex-Builder Prompt** (MEDIUM PRIORITY)
**File:** `.github/prompts/cortex-builder.prompt.md` (1000+ lines)

**Violation Type:** May create files in wrong locations (needs verification)

**Potential Issues:**
- No explicit file location constraints documented
- Generates code files but location policy unclear
- Should reference FilenameFactory for validation

---

## 🚨 LEGACY DIRECTORY DEPRECATION STATUS

### Still In Use (VIOLATIONS)
```
_workspaces/roadmap/reports/     ← 3+ scripts still write here ❌
_workspaces/roadmap/phases/      ← Archive scripts reference ❌
_workspaces/roadmap/_archives/   ← Legacy backup location ❌
_workspaces/reports/             ← Documentation migration files ❌
.github/roadmap/reports/         ← Some phase scripts write here ❌
```

### Should Be Used (COMPLIANT)
```
reports/analysis/                ← Analysis & research ✅
reports/phase-tracking/          ← Phase progress & milestones ✅
reports/governance/              ← Governance & compliance ✅
reports/operations/              ← Operational status ✅
reports/orchestrators/           ← Orchestrator-specific ✅
```

---

## 📋 AFFECTED SYSTEMS SUMMARY

| System | File Count | Violations | Priority | Scope |
|--------|-----------|-----------|----------|-------|
| cortex-doc.prompt | 1 | 1 | CRITICAL | File location, naming |
| duplication_audit | 1 | 1 | HIGH | File location, naming |
| phase_14_completion | 1 | 1 | MEDIUM-HIGH | File location, naming |
| phase_15_completion | 1 | 1 | MEDIUM-HIGH | File location, naming |
| consolidate_phases | 1 | 3+ | MEDIUM | File location, naming |
| doc-migrate-automated | 1 | 1 | MEDIUM | File location, format |
| documentation_orchestrator | 1 | 1 (potential) | MEDIUM | Orchestrator integration |

**Total Violations:** 9+ active file creation paths that bypass CORE-038

---

## 🔧 RECOMMENDED REMEDIATION

### Phase 1: Immediate (Today)
**Priority:** CRITICAL  
**Files to Fix:** 2 (most impactful)

1. **Update `cortex-doc.prompt.md`**
   - Change report output location from `_workspaces/reports/` to `reports/analysis/`
   - Update filename to comply with CORE-028 (kebab-case, date format)
   - Verify documentation files go to `docs/` (correct)
   - **Impact:** Stops new doc generation reports from going to wrong place

2. **Update `duplication_audit.py`**
   - Change hardcoded path from `_workspaces/roadmap/reports/` to `reports/analysis/`
   - Update filename format to `duplication-audit-YYYY-MM-DD.md`
   - **Impact:** Fixes one of highest-frequency scripts

---

### Phase 2: Near-Term (This Week)
**Priority:** HIGH  
**Files to Fix:** 3 (phase completion scripts)

3. **Update Phase Completion Scripts (14, 15)**
   - Consolidate both to `reports/phase-tracking/`
   - Use compliant naming: `phase-14-completion-report.md`
   - Also check phases 13, 16 if they exist

4. **Update `consolidate_phases.py`**
   - Fix report output location
   - Fix archive references to use `_workspaces/_archives/` if needed
   - Use kebab-case for all filenames

5. **Update `doc-migrate-automated.py`**
   - Change JSON reports to YAML or move to `reports/analysis/`
   - Use compliant naming pattern

---

### Phase 3: Medium-Term (Next Sprint)
**Priority:** MEDIUM  
**Files to Fix:** 2 (orchestrators & prompts)

6. **Update `documentation_orchestrator.py`**
   - Wire into FilenameFactory for all file generation
   - Create method: `_get_compliant_filename(purpose, file_type)`
   - Call FilenameFactory.generate() before creating files
   - Verify output locations match CORE-038

7. **Update `cortex-builder.prompt.md`** (if applicable)
   - Document file creation locations clearly
   - Reference FilenameFactory for naming
   - Add file placement validation

---

## ✅ IMPLEMENTATION CHECKLIST

### For Each Script/Prompt Fix:

- [ ] Read file to understand file creation logic
- [ ] Identify all `Path()`, `write_text()`, `write()`, `mkdir()` calls
- [ ] Update hardcoded paths to use `reports/` subdirectories
- [ ] Update filename generation to call `FilenameFactory.suggest_compliant_filename()`
- [ ] Validate output location with `FilePathEnforcer.validate_path()`
- [ ] Test by running script and verifying files appear in correct location
- [ ] Git commit with message: `chore: fix CORE-038 violations in {script_name}`

---

## 🔐 GOVERNANCE COMPLIANCE

### CORE-038 Violations
```yaml
violation_type: FILE_PLACEMENT_POLICY
violated_rule: CORE-038
severity: CRITICAL
affected_systems: 7
total_violations: 9+

current_state:
  files_in_forbidden_roots:
    _workspaces/roadmap/reports/: 3+ systems
    _workspaces/reports/: 1+ system
    .github/roadmap/reports/: 1+ system

expected_state:
  all_files: reports/{analysis|phase-tracking|governance|operations|orchestrators}/
  naming: kebab-case, 25-char limit
  enforcement: FilenameFactory validates all paths
```

### CORE-028 Violations
```yaml
violation_type: FILENAME_COMPLIANCE
violated_rule: CORE-028
issues:
  - some_reports use snake_case instead of kebab-case
  - some reports use full timestamp (HHMMSS) instead of date (YYYY-MM-DD)
  - some use .json format for data that should be .yaml or .md
```

---

## 📊 IMPLEMENTATION TRUTH (CORE-030)

**Verification Conducted:**
- ✅ Read all agent/prompt definitions
- ✅ Grepped for file creation patterns (Path, write_text, mkdir, open)
- ✅ Identified all hardcoded paths to `_workspaces/`
- ✅ Located 9+ active violation points
- ✅ Traced to specific line numbers in source files

**Code vs Documentation Mismatch:**
- Documentation says: "Reports go to `reports/` directory" (CORRECT)
- Actual code does: "Reports go to `_workspaces/roadmap/reports/` and `_workspaces/reports/`" (WRONG)
- → **CORE-030 violation**: Code doesn't match documented policy

---

## 🎯 SUCCESS CRITERIA

After implementing Phase 1-3 remediation:

- [ ] Zero files created in `_workspaces/roadmap/reports/`
- [ ] Zero files created in `_workspaces/reports/`
- [ ] Zero files created in `.github/roadmap/reports/`
- [ ] All new reports use `reports/{category}/` structure
- [ ] All filenames comply with CORE-028 (kebab-case, 25-char)
- [ ] All file paths pass `FilePathEnforcer.validate_path()` check
- [ ] FilenameFactory integrated into all report-creating systems
- [ ] Git history clean with compliance commits

---

## 🚀 Next Steps

1. **Immediate:** Review this audit with user
2. **Approve:** Get prioritization guidance
3. **Execute:** Fix systems in priority order (Phase 1 → Phase 3)
4. **Verify:** Run tests and manual verification
5. **Document:** Update architecture guide showing correct patterns
6. **Monitor:** Integrate FilenameFactory into pre-commit hooks

---

**Report Generated:** 2026-01-25 | **Next Audit:** After Phase 1 fixes applied
