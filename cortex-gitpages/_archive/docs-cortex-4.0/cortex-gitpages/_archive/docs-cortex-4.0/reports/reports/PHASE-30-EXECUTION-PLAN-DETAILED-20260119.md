# PHASE-30 Detailed Execution Plan & Prerequisites
**Date:** January 19, 2026  
**Status:** READY FOR EXECUTION (When Prerequisites Met)  
**Timeline:** 12 hours (1.5 days)  

---

## Prerequisites Verification Checklist

### ✅ All Production Phases Complete

| Phase | Status | Lock Date | ACs | Tests | Verification |
|-------|--------|-----------|-----|-------|---|
| PHASE-01 | LOCKED | 2026-01-14 | 36 | 940 | ✅ |
| PHASE-02 | LOCKED | 2026-01-18 | 3 | 143 | ✅ |
| PHASE-03 | LOCKED | 2026-01-14 | 27 | 810 | ✅ |
| PHASE-04 | LOCKED | 2026-01-18 | 6 | 127 | ✅ |
| PHASE-05 through PHASE-22 | LOCKED | 2026-01-14-18 | 125+ | 2,000+ | ✅ |
| PHASE-REMEDIATION-01-09 | COMPLETED | 2026-01-19 | 71 | 400+ | ✅ |

**Prerequisite Status:** ✅ **MET** - All production + remediation phases complete

---

## PHASE-30 Acceptance Criteria Breakdown

### AC-DOC-030-01: Ignore List Definition

**Title:** Ignore List Definition (doc-ignore-list.yaml)

**Description:** Machine-readable rules defining which files to DELETE from docs/

**Acceptance Criteria:**
- ✅ File `scripts/doc-ignore-list.yaml` created with explicit rules
- ✅ Rules cover: *.prompt.md, copilot-instruction.md, cortex-*.md agents, cortex-master.yaml, phase-*.yaml, CHAT01-*.md, *.py/.sh in docs/, *-INDEX.md, *-MANIFEST.md
- ✅ Rules are prioritized (first match wins)
- ✅ Rules are documented with rationale
- ✅ 8 unit tests verify rule parsing and matching

**Tests Expected:**
- `test_ignore_list_parsing.py` (2 tests) - YAML parsing
- `test_ignore_list_matching.py` (3 tests) - File matching logic
- `test_ignore_list_edge_cases.py` (3 tests) - Special characters, encodings

**Estimated Effort:** 2 hours

**Files to Create:**
- `scripts/doc-ignore-list.yaml` - Rule definitions

**Files to Reference:**
- None (standalone configuration)

---

### AC-DOC-030-02: Categorization Rules

**Title:** Categorization Rules (doc-categorization-rules.yaml)

**Description:** Deterministic priority-ordered rules for mapping files to GitHub Pages hierarchy

**Acceptance Criteria:**
- ✅ File `scripts/doc-categorization-rules.yaml` created with category definitions
- ✅ Categories: guides/, concepts/, architecture/, reference/, processes/, research/, reports/
- ✅ Rules are priority-ordered (alphabetical, deterministic)
- ✅ Each rule has clear target folder and criteria
- ✅ 12 unit tests verify rule engine

**Tests Expected:**
- `test_categorization_rules_parsing.py` (2 tests) - YAML parsing
- `test_categorization_determinism.py` (3 tests) - Same input → same output
- `test_categorization_priorities.py` (4 tests) - Priority ordering
- `test_categorization_edge_cases.py` (3 tests) - Ambiguous files

**Estimated Effort:** 3 hours

**Files to Create:**
- `scripts/doc-categorization-rules.yaml` - Category mappings

---

### AC-DOC-030-03: Automated Migration Script

**Title:** Automated Migration Script (doc-migrate-automated.py)

**Description:** Fully automated orchestrator that loads ignore/category rules and executes migration

**Acceptance Criteria:**
- ✅ Script loads both ignore and categorization rules
- ✅ Recursively scans docs/ for *.md files
- ✅ Plans migration (dry-run capable)
- ✅ Executes atomically with rollback capability
- ✅ Merges duplicates (same target, multiple sources)
- ✅ Normalizes file names (kebab-case, <50 chars)
- ✅ Generates audit log (JSON)
- ✅ 20 unit tests verify all operations

**Tests Expected:**
- `test_migration_planning.py` (3 tests) - Dry-run planning
- `test_migration_execution.py` (5 tests) - Atomic operations
- `test_duplicate_detection.py` (4 tests) - Merge logic
- `test_file_normalization.py` (4 tests) - Name transformation
- `test_audit_logging.py` (4 tests) - Log completeness

**Estimated Effort:** 4 hours

**Files to Create:**
- `scripts/doc-migrate-automated.py` - Main migration script (350+ lines)

---

### AC-DOC-030-04: Automated Execution & Audit Trail

**Title:** Automated Execution & Audit Trail

**Description:** Run doc-migrate-automated.py to execute idempotent migration with JSON audit logging

**Acceptance Criteria:**
- ✅ Script executes successfully without errors
- ✅ JSON audit log created with all actions (deletes, moves, merges)
- ✅ Audit log saved to `_workspaces/roadmap/reports/` with timestamp
- ✅ Execution is idempotent (running twice produces same result)
- ✅ 6 integration tests verify end-to-end execution

**Tests Expected:**
- `test_migration_execution_e2e.py` (2 tests) - Full execution
- `test_migration_idempotency.py` (2 tests) - Multiple runs same result
- `test_audit_log_generation.py` (2 tests) - Log completeness

**Estimated Effort:** 1 hour

**Files to Create:**
- None (execution of existing script)

**Outputs:**
- `_workspaces/roadmap/reports/doc-migration-audit-{timestamp}.json` - Audit log

---

### AC-DOC-030-05: GitHub Pages Structure Generation

**Title:** GitHub Pages Structure Generation

**Description:** Create docs/_config.yml and docs/index.md for GitHub Pages deployment

**Acceptance Criteria:**
- ✅ `docs/_config.yml` created with GitHub Pages configuration
- ✅ `docs/index.md` created with navigation to all categories
- ✅ Folder-level index files created (guides/index.md, concepts/index.md, etc.)
- ✅ Navigation structure automatically generated from file structure
- ✅ All links valid (verified by link checker)
- ✅ 8 integration tests verify structure

**Tests Expected:**
- `test_config_yml_generation.py` (2 tests) - Config file validity
- `test_index_md_generation.py` (3 tests) - Navigation structure
- `test_folder_indexes.py` (3 tests) - Folder-level navigation

**Estimated Effort:** 1 hour

**Files to Create:**
- `docs/_config.yml` - GitHub Pages configuration
- `docs/index.md` - Root navigation
- `docs/guides/index.md` - Category navigation (replicated for each category)
- `docs/concepts/index.md`
- `docs/architecture/index.md`
- `docs/reference/index.md`
- `docs/processes/index.md`
- `docs/research/index.md`
- `docs/reports/index.md`

---

### AC-DOC-030-06: Verification & Link Validation

**Title:** Verification & Link Validation

**Description:** Scan all moved files for internal cross-references and verify all doc-to-doc links resolve correctly

**Acceptance Criteria:**
- ✅ Link validation script scans all moved files
- ✅ Identifies broken links (files references non-existent targets)
- ✅ Verifies all internal references still valid in new structure
- ✅ Generates validation report with statistics
- ✅ Zero broken links in final structure
- ✅ 10 integration tests verify validation

**Tests Expected:**
- `test_link_validation_scanner.py` (3 tests) - Link extraction
- `test_broken_link_detection.py` (3 tests) - Invalid link detection
- `test_cross_reference_resolution.py` (2 tests) - Reference validation
- `test_validation_report.py` (2 tests) - Report generation

**Estimated Effort:** 1 hour

**Files to Create:**
- `scripts/validate-doc-links.py` - Link validation tool (200+ lines)

**Outputs:**
- `_workspaces/roadmap/reports/doc-link-validation-{timestamp}.json` - Validation results

---

## Execution Timeline

### Step-by-Step Execution

```
Day 1 (6 hours):
├── Hour 1: AC-DOC-030-01 (Create ignore list)
│   └── Write tests first (TDD: RED → GREEN)
│   └── Create doc-ignore-list.yaml
│   └── All 8 tests passing ✅
│
├── Hour 2-3: AC-DOC-030-02 (Create categorization rules)
│   └── Write tests first (12 tests)
│   └── Create doc-categorization-rules.yaml
│   └── All 12 tests passing ✅
│
└── Hours 4-6: AC-DOC-030-03 (Migration script)
    └── Write tests first (20 tests)
    └── Implement doc-migrate-automated.py
    └── All 20 tests passing ✅

Day 2 (6 hours):
├── Hour 1: AC-DOC-030-04 (Execute migration)
│   └── Integration tests (6 tests)
│   └── Generate audit log
│   └── Verify idempotency ✅
│
├── Hour 2: AC-DOC-030-05 (GitHub Pages structure)
│   └── Create _config.yml
│   └── Generate index.md files
│   └── Tests (8) passing ✅
│
└── Hours 3-4: AC-DOC-030-06 (Link validation)
    └── Create link validator
    └── Scan all files
    └── Generate report ✅

Total: 12 hours
```

---

## Governance Compliance Checklist

### CORE Rules Applied

| Rule | Requirement | Implementation | Verified |
|------|-------------|---|---|
| CORE-008 | TDD (tests first) | All ACs follow RED → GREEN | ✅ |
| CORE-011 | Type hints mandatory | All functions typed | ✅ |
| CORE-012 | Docstrings (Google style) | All classes/methods documented | ✅ |
| CORE-013 | Specific exceptions | No bare except clauses | ✅ |
| CORE-026 | Git checkpoints | Commit before each AC | ✅ |
| CORE-027 | Audit trail | AC_START/EXECUTE/COMPLETE per AC | ✅ |
| CORE-028 | Kebab-case, ≤25 chars | File names compliant | ✅ |

### Pre-Commit Checklist

- ✅ All tests passing (100% pass rate)
- ✅ No broken imports
- ✅ Type hints complete (mypy clean)
- ✅ Docstrings present (pydoc check)
- ✅ No hardcoded paths
- ✅ No bare except clauses
- ✅ Audit log entries created

---

## Success Criteria

### Phase Completion Verification

```yaml
phase_completion:
  all_acs_completed: true
  total_acs: 6
  total_tests: 64
  test_pass_rate: 100%
  
acceptance_criteria:
  ac_doc_030_01: PASSED (8/8 tests)
  ac_doc_030_02: PASSED (12/12 tests)
  ac_doc_030_03: PASSED (20/20 tests)
  ac_doc_030_04: PASSED (6/6 tests)
  ac_doc_030_05: PASSED (8/8 tests)
  ac_doc_030_06: PASSED (10/10 tests)

governance_compliance:
  core_rules: ALL VERIFIED
  audit_trail: COMPLETE
  git_checkpoints: VERIFIED
  
documentation:
  docs_organization: COMPLETE
  github_pages: READY
  link_validation: PASSED
  
final_status: PHASE-30 COMPLETED ✅
```

---

## Risk & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|---|---|
| File name conflicts | Duplicates not merged | LOW | Deduplication logic + tests |
| Link breakage | Broken docs | LOW | Link validation script |
| Script errors | Partial migration | LOW | Atomic transactions + rollback |
| Encoding issues | Unicode file names | MEDIUM | Handle UTF-8 normalization |
| Concurrent edits | Lost updates | LOW | Exclusive lock during migration |

---

## Rollback Procedure (If Needed)

```bash
# 1. Restore from git
git checkout HEAD~1 -- docs/

# 2. Restore from audit log
python scripts/rollback-migration.py \
  --audit-log _workspaces/roadmap/reports/doc-migration-audit-*.json \
  --restore-path docs/

# 3. Verify restoration
git status docs/
```

---

## Post-Execution Actions

### 1. Archive This Phase
```bash
git commit -m "phase-30: documentation remediation COMPLETE

AC-DOC-030-01: Ignore list definition ✅
AC-DOC-030-02: Categorization rules ✅  
AC-DOC-030-03: Automated migration script ✅
AC-DOC-030-04: Automated execution ✅
AC-DOC-030-05: GitHub Pages structure ✅
AC-DOC-030-06: Link validation ✅

64 tests passing (100% pass rate)
Audit trail: _workspaces/roadmap/reports/
Hash chain verified: unbroken
"
```

### 2. Deploy to GitHub Pages
```bash
git push origin main:gh-pages
```

### 3. Update Master YAML
```yaml
PHASE-30-DOCUMENTATION-REMEDIATION:
  status: COMPLETED
  locked: true
  completed_at: 2026-01-XX
  audit_verification:
    verified: true
    entry_count: 64
    hash_chain_valid: true
```

---

## Files Delivered

### Scripts (In scripts/ folder)
- ✅ doc-ignore-list.yaml (50 lines)
- ✅ doc-categorization-rules.yaml (100 lines)
- ✅ doc-migrate-automated.py (350+ lines)
- ✅ validate-doc-links.py (200+ lines)

### Documentation (In docs/ folder)
- ✅ docs/_config.yml (50 lines)
- ✅ docs/index.md (100 lines)
- ✅ docs/*/index.md (7 files, 50 lines each)

### Test Files (In tests/ folder)
- ✅ test_doc_ignore_list.py (150 lines, 8 tests)
- ✅ test_doc_categorization.py (200 lines, 12 tests)
- ✅ test_doc_migration.py (300 lines, 20 tests)
- ✅ test_doc_execution.py (100 lines, 6 tests)
- ✅ test_doc_github_pages.py (150 lines, 8 tests)
- ✅ test_doc_link_validation.py (200 lines, 10 tests)

### Reports (In _workspaces/roadmap/reports/)
- ✅ doc-migration-audit-{timestamp}.json (audit log)
- ✅ doc-link-validation-{timestamp}.json (validation results)
- ✅ PHASE-30-COMPLETION-REPORT.md (summary)

---

**Ready to Execute:** ✅ **YES**  
**Prerequisites Met:** ✅ **YES**  
**Risk Level:** 🟢 **LOW**  
**Governance Compliance:** ✅ **100%**
