# CORTEX Test Manifest

**Purpose:** Required test files for deployment package validation  
**Version:** 2.0 (Enhanced Pipeline Validation)  
**Status:** ✅ PRODUCTION

---

## 🎯 Test Package Requirements

**CRITICAL:** These test files MUST be included in ALL CORTEX deployments to ensure brain protection and system integrity after upgrades.

**NEW in v2.0:**
- Comprehensive deployment pipeline validation
- All agents discovery and wiring checks
- Response template completeness validation
- Documentation synchronization checks
- Post-upgrade smoke tests (<30 seconds)

---

### Deployment Validation

```plaintext
tests/test_deployment_pipeline.py         # Comprehensive feature wiring validation
```

**Purpose:** Validate all CORTEX features properly wired before deployment  
**Tests:**

- All agents discoverable and importable
- All workflows integrated (TDD, Planning, Feature)
- Response templates load correctly
- Database schema complete (tables, indexes, views)
- Entry points documented and functional
- Documentation synchronized
- Configuration files valid
- Dependencies available

**Usage:**

```bash
pytest tests/test_deployment_pipeline.py -v
```

---

### Post-Upgrade Smoke Tests

```plaintext
tests/test_post_upgrade_smoke.py          # Fast post-upgrade validation (<30s)
```

**Purpose:** Quick smoke tests immediately after upgrade  
**Tests:**

- Critical imports (FeedbackAgent, ViewDiscoveryAgent, TDDWorkflowIntegrator)
- Entry points accessible (CORTEX.prompt.md, help documentation)
- Database connectivity (Tier 2 connectable)
- Template loading (response-templates.yaml)
- Configuration valid (capabilities.yaml, brain-protection-rules.yaml)
- Version information present

**Usage:**

```bash
pytest tests/test_post_upgrade_smoke.py -v --tb=line -x
```

**Expected Runtime:** <30 seconds

---

## 🔄 Enhanced Validation Script

### Core Validation Script (Enhanced v2.0)

```plaintext
validate_issue3_phase4.py                  # Enhanced with pipeline validation
```

**NEW in v2.0:**

- [7/10] All Agents Wired Validation
  - Auto-discovers all agent modules in src/agents/
  - Validates each agent imports successfully
  - Reports failed imports with error details

- [8/10] Response Templates Validation
  - Loads response-templates.yaml
  - Checks all critical templates present (11 required)
  - Validates template structure (content, triggers)

- [9/10] Documentation Sync Validation
  - Verifies CORTEX.prompt.md exists
  - Checks all required modules present
  - Validates modules referenced in entry point
  - Ensures key commands documented

**Usage:**

```bash
python validate_issue3_phase4.py
```

**Validation Categories:** 10 total (was 6)

---

## 📊 Test Execution Flow

**Post-Upgrade Validation (Automated):**

```text
Upgrade Process:
1. Pull latest code ✅
2. Apply database migrations ✅
3. Run validate_issue3_phase4.py ⏳
   ├─ [1/10] Database Schema (4 tables, 14 indexes, 4 views)
   ├─ [2/10] FeedbackAgent (import, initialization, report creation)
   ├─ [3/10] ViewDiscoveryAgent (discovery, database persistence)
   ├─ [4/10] TDD Workflow Integrator (integration, selector retrieval)
   ├─ [5/10] Upgrade Compatibility (brain preservation)
   ├─ [6/10] End-to-End Workflow (feedback → discovery → test gen)
   ├─ [7/10] All Agents Wired (auto-discover all agents) ← NEW
   ├─ [8/10] Response Templates (11 critical templates) ← NEW
   ├─ [9/10] Documentation Sync (entry point + modules) ← NEW
   └─ [10/10] Comprehensive feature validation
4. If ALL tests pass ✅ → Upgrade complete
5. If ANY test fails ❌ → Recommend rollback
```

**Exit Codes:**

- `0` - All tests passed (upgrade successful)
- `1` - One or more tests failed (upgrade incomplete)
- `2` - Critical failure (brain protection compromised)

**Post-Upgrade Smoke Tests (Manual):**

```bash
# Quick validation (<30s)
pytest tests/test_post_upgrade_smoke.py -v

# Full deployment validation (comprehensive)
pytest tests/test_deployment_pipeline.py -v
```

---

## 📏 Deployment Size Impact

**Test Package Size:**

- `validate_issue3_phase4.py`: ~30 KB (enhanced)
- `test_brain_protector.py`: ~15 KB
- `test_issue3_fixes.py`: ~8 KB
- `test_deploy_issue3_fixes.py`: ~6 KB
- `test_deployment_pipeline.py`: ~16 KB ← NEW
- `test_post_upgrade_smoke.py`: ~5 KB ← NEW
- **Total:** ~80 KB

**Package Increase:** <100 KB  
**Value:** Priceless (prevents brain corruption, ensures all features wired, smooth upgrades)

---

### Core Validation Script
```
validate_issue3_phase4.py           # Main validation orchestrator (597 lines)
```

**Purpose:** Comprehensive post-upgrade validation  
**Validates:**
- Database schema (4 tables, 14 indexes, 4 views)
- Agent functionality (FeedbackAgent, ViewDiscoveryAgent)
- Workflow integration (TDD workflow end-to-end)
- Brain protection (SKULL rules)
- Entry point modules
- Configuration integrity

**Usage:**
```bash
# Full validation
python validate_issue3_phase4.py

# Category-specific validation
python validate_issue3_phase4.py --category=brain_protection
python validate_issue3_phase4.py --category=database
python validate_issue3_phase4.py --category=agents
```

---

### Brain Protection Tests
```
tests/tier0/test_brain_protector.py  # SKULL rule validation (22 tests)
```

**Purpose:** Verify Tier 0 brain protection active  
**Tests:**
- Rule loading from brain-protection-rules.yaml
- File system protections
- Memory isolation
- Unauthorized access prevention
- All 22 tests must pass (100% pass rate required)

**Usage:**
```bash
pytest tests/tier0/test_brain_protector.py -v
```

---

### Agent Integration Tests
```
tests/integration/test_issue3_fixes.py  # Agent functionality tests
```

**Purpose:** Validate Issue #3 fixes functional  
**Tests:**
- FeedbackAgent imports and initializes
- ViewDiscoveryAgent discovers elements
- Database persistence works
- TDD workflow integration
- End-to-end workflows

**Usage:**
```bash
pytest tests/integration/test_issue3_fixes.py -v
```

---

### Deployment Validation
```
tests/test_deploy_issue3_fixes.py    # Deployment readiness tests
```

**Purpose:** Pre-deployment validation  
**Tests:**
- All required files present
- Migration scripts functional
- Documentation synchronized
- Entry point modules exist
- Configuration files valid

**Usage:**
```bash
pytest tests/test_deploy_issue3_fixes.py -v
```

---

## 🔒 Why Tests Are Deployed

**1. Brain Protection Verification**
- Ensures SKULL rules active after upgrade
- Prevents brain corruption from misconfigured upgrades
- Validates file system protections intact

**2. Zero-Trust Validation**
- User machine validates upgrade success
- No dependency on external validation
- Immediate feedback on upgrade status

**3. Regression Prevention**
- Catches compatibility issues immediately
- Tests all critical paths post-upgrade
- Prevents broken deployments

**4. Rollback Decision Support**
- Automated test failures trigger rollback recommendation
- Clear pass/fail criteria
- Preserves working state if upgrade fails

**5. Confidence Assurance**
- Users know CORTEX is 100% functional
- No ambiguity about upgrade success
- Professional-grade deployment validation

---

## 📊 Test Execution Flow

**Automated Post-Upgrade Validation:**

```
Upgrade Process:
1. Pull latest code ✅
2. Apply database migrations ✅
3. Run validate_issue3_phase4.py ⏳
   ├─ Brain protection tests (22/22 must pass)
   ├─ Database schema validation (100% coverage)
   ├─ Agent functionality tests (all agents)
   ├─ Workflow integration tests (end-to-end)
   └─ Entry point validation (all modules)
4. If ALL tests pass ✅ → Upgrade complete
5. If ANY test fails ❌ → Recommend rollback
```

**Exit Codes:**
- `0` - All tests passed (upgrade successful)
- `1` - One or more tests failed (upgrade incomplete)
- `2` - Critical failure (brain protection compromised)

---

## 📏 Deployment Size Impact

**Test Package Size:**
- `validate_issue3_phase4.py`: ~25 KB
- `test_brain_protector.py`: ~15 KB
- `test_issue3_fixes.py`: ~8 KB
- `test_deploy_issue3_fixes.py`: ~6 KB
- **Total:** ~54 KB

**Package Increase:** <100 KB  
**Value:** Priceless (prevents brain corruption, ensures system integrity)

---

## ✅ Deployment Checklist

**Before deploying CORTEX:**

- [ ] `validate_issue3_phase4.py` included in package
- [ ] `tests/tier0/test_brain_protector.py` included
- [ ] `tests/integration/test_issue3_fixes.py` included
- [ ] `tests/test_deploy_issue3_fixes.py` included
- [ ] All tests pass locally (100% pass rate)
- [ ] pytest available in requirements.txt
- [ ] Test execution documented in upgrade-guide.md
- [ ] Automated test execution in Phase 3 of upgrade
- [ ] Rollback procedure includes test validation

---

## 🚨 Critical Test Failures

**If tests fail after upgrade:**

### Brain Protection Tests Fail
```
❌ Brain protection compromised
   → Rollback immediately
   → Verify brain-protection-rules.yaml intact
   → Check file system permissions
```

### Database Schema Tests Fail
```
❌ Database schema incomplete
   → Run migration scripts manually
   → Verify cortex-brain/tier2/ database exists
   → Check for migration errors in logs
```

### Agent Tests Fail
```
❌ Agents not functional
   → Verify src/agents/ files present
   → Check Python imports
   → Review agent initialization code
```

### Workflow Integration Tests Fail
```
❌ TDD workflow broken
   → Verify src/workflows/ files present
   → Check integration points
   → Review workflow orchestration
```

---

## 📖 Test Maintenance

**When adding new features:**

1. **Write Tests First** - TDD approach for new agents/workflows
2. **Update Test Manifest** - Add new test files to this document
3. **Include in Deployment** - Add to package requirements
4. **Update Validation Script** - Add new validation categories
5. **Document Test Purpose** - Explain what each test validates

**Test Quality Standards:**

- ✅ 100% pass rate required for deployment
- ✅ Tests must be deterministic (no flaky tests)
- ✅ Fast execution (<5 minutes total)
- ✅ Clear error messages on failure
- ✅ No external dependencies (offline-capable)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0 - Test Package Manifest  
**Last Updated:** 2025-11-23
