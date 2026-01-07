# C150 Remediation Plan

**Plan ID:** c150-remediation  
**Created:** January 4, 2026  
**Status:** Ready for Execution  
**Estimated Duration:** 96 hours (12 business days)

---

## 🎯 Purpose

Fix critical gaps identified in C150 (HTML Glassmorphism Alignment) plan review:

- **6 orchestrators broken** (cannot instantiate)
- **Runtime governance missing** (SKULL compliance gap)
- **CORTEX-5.0 docs incomplete** (stubs only)
- **Deployment validation missing** (Phase 11)
- **Dead code not removed** (1,009 CSS classes identified)
- **Dual-source brittleness** (YAML + DB simultaneously)
- **82 unit tests blocked** (67 vacuum + 15 cleanup)

---

## 📁 Quick Start

### View Full Plan

```bash
cat 00-c150-remediation-plan.yaml
```

### Execute Plan (Python Orchestration)

```bash
# Phase -2: Setup Verification
python scripts/orchestration/setup_verification.py

# Phase 0: Context Discovery
python scripts/orchestration/context_discovery.py

# Phase 1: Acceptance Criteria Validation
python scripts/orchestration/acceptance_criteria_validator.py

# ... (continue for all phases)
```

### Track Progress

```bash
cat tracking/progress-tracker.json
```

---

## 📊 Key Metrics

| Metric | Target |
|--------|--------|
| Orchestrators Fixed | 6/6 (100%) |
| Unit Tests Unblocked | 82 (67 vacuum + 15 cleanup) |
| Documentation Written | 2,800+ lines |
| Deployment Validated | Staging + Production |
| Dead Code Removed | 1,009 CSS classes |
| Dual-Source Resolved | 100% (database-only) |

---

## 🗂️ Folder Structure

```
c150-remediation-plan/
├── 00-c150-remediation-plan.yaml  # Master plan (YAML-based)
├── README.md                       # This file
├── analysis/                       # Gap analysis, validation reports
├── artifacts/                      # Patches, fixes, generated code
├── context/                        # Context discovery, background
├── reports/                        # Progress, completion reports
└── tracking/                       # progress-tracker.json, state
```

---

## 🔀 Phase Overview

| Phase | Name | Hours | Python Script |
|-------|------|-------|---------------|
| **-2** | Setup Verification | 0.5 | `setup_verification.py` |
| **0** | Context Discovery | 1.0 | `context_discovery.py` |
| **1** | Acceptance Criteria Cross-Check | 1.5 | `acceptance_criteria_validator.py` |
| **2** | Fix planning_v5 Orchestrator | 2.0 | `fix_orchestrator.py` |
| **3** | Fix StateManager Interface | 4.0 | `fix_state_manager.py` |
| **4** | Fix Python 3.9/3.10 Compatibility | 3.0 | `python_compatibility_fixer.py` |
| **5** | Implement Runtime Governance | 10.0 | `create_governance_middleware.py` |
| **6** | Resolve Dual-Source Brittleness | 3.0 | `dual_source_cutover.py` |
| **7** | Write Refinement Docs | 6.0 | `generate_orchestrator_docs.py` |
| **8** | Write Debug Docs | 6.0 | `generate_orchestrator_docs.py` |
| **9** | Document Features + Diagrams | 10.0 | `generate_feature_docs.py` |
| **10** | Execute Dead Code Removal | 4.0 | `execute_css_cleanup.py` |
| **11** | Deployment Validation | 48.0 | `deployment_validator.py` |
| **12** | Update C150 Certificate | 1.0 | `update_completion_certificate.py` |
| **13** | Automate Acceptance Validation | 8.0 | `create_acceptance_validator.py` |
| **14** | Automate Brittleness Checking | 6.0 | `create_brittleness_checker.py` |
| **999** | Teardown + REFACTOR + Commit | 2.0 | `teardown_refactor.py` |

**Total:** 96 hours (12 business days)

---

## ✅ Acceptance Criteria

### AC-1: Orchestrator Instantiation
- **Requirement:** All 6 orchestrators instantiate without errors
- **Validation:** Run instantiation tests
- **Pass Criteria:** 0 errors, all constructors succeed

### AC-2: Unit Test Recovery
- **Requirement:** 82 unit tests pass (67 vacuum + 15 cleanup)
- **Validation:** `pytest tests/test_vacuum_v2.py tests/test_cleanup_v2.py`
- **Pass Criteria:** 82/82 tests pass on Python 3.9 and 3.10

### AC-3: Runtime Governance
- **Requirement:** Middleware exists and functions
- **Validation:** Test 3 middleware files
- **Pass Criteria:** All exist, unit tests pass, integration test passes

### AC-4: Dual-Source Resolution
- **Requirement:** Code reads from database only
- **Validation:** Check for YAML reads, validate database queries
- **Pass Criteria:** 0 YAML reads, all unit tests pass

### AC-5: CORTEX-5.0 Documentation
- **Requirement:** Complete documentation (2 orchestrators, 5 features, 4 diagrams)
- **Validation:** Check file existence and content length
- **Pass Criteria:** All files exist with required content

### AC-6: Dead Code Removal
- **Requirement:** 1,009 CSS classes removed
- **Validation:** CSS file size reduction, HTML rendering unchanged
- **Pass Criteria:** Classes removed, Lighthouse scores maintained

### AC-7: Deployment Validation
- **Requirement:** Staging + production validated
- **Validation:** Check deployment reports, 24hr monitoring data
- **Pass Criteria:** Zero critical errors, uptime >99.9%

### AC-8: Certificate Correction
- **Requirement:** C150 certificate updated to 85%
- **Validation:** Check certificate file
- **Pass Criteria:** Status updated, KNOWN ISSUES added

### AC-9: Acceptance Automation
- **Requirement:** Validator script created
- **Validation:** Run script
- **Pass Criteria:** Script works, CI/CD integrated

### AC-10: Brittleness Automation
- **Requirement:** Checker script created
- **Validation:** Run script
- **Pass Criteria:** Script works, flags broken orchestrators

---

## 🛡️ SKULL Compliance

- **TDD_ENFORCEMENT:** Phase 5 middleware validates tests before implementation
- **HOLISTIC_DISCOVERY:** Phase 0 searches workspace before creating files
- **GIT_ISOLATION:** Phase 999 commits with `/cortex-git-commit` pattern
- **PLANNING_ISOLATION:** This plan implements fixes, doesn't create another plan
- **HAND_OFF_PROTOCOL:** Python scripts execute autonomously

---

## 📈 Success Metrics

### Code Quality
- ✅ 6 orchestrators instantiate (100%)
- ✅ 82 unit tests pass (100%)
- ✅ 0 interface mismatches
- ✅ 0 Python 3.9/3.10 issues

### Governance
- ✅ 3 middleware files implemented
- ✅ SKULL rules enforced at runtime
- ✅ 0 dual-source brittleness issues

### Documentation
- ✅ 2 orchestrator docs (400+ lines each)
- ✅ 5 feature docs created
- ✅ 4 diagrams created
- ✅ 100% CORTEX-5.0 coverage

### Production Readiness
- ✅ Staging validated (24hr monitoring)
- ✅ Production validated (24hr monitoring)
- ✅ Uptime >99.9%
- ✅ 0 critical errors

### Automation
- ✅ Acceptance criteria validator automated
- ✅ Brittleness checker automated
- ✅ CI/CD integration complete
- ✅ False completions prevented

---

## 📚 References

- **C150 Plan:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/`
- **C150 Review:** `cortex-brain/documents/investigations/c150-plan-review/`
- **Acceptance Criteria:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/artifacts/final-acceptance-criteria-link.md`
- **Brittleness Reports:**
  - `cortex-brain/documents/reports/C50-brittleness-test-summary-2026-01-04.md`
  - `cortex-brain/documents/reports/comprehensive-brittleness-audit-2026-01-02.md`

---

## 🚀 Next Steps

1. **Review this plan** with team
2. **Execute Phase -2** (Setup Verification)
3. **Execute Phase 0** (Context Discovery)
4. **Continue sequentially** through all phases
5. **Validate acceptance criteria** at completion
6. **Generate completion certificate** (honest 100% this time!)

---

**Plan Created:** January 4, 2026  
**Plan Author:** CORTEX Planning System v5  
**Python Execution:** YAML-based orchestration with autonomous Python scripts
