# Phase 14: Version Consolidation & Housekeeping (PRE-GA CRITICAL)

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 22, 2025  
**Status:** 📋 PLANNED  
**Duration:** 2 weeks (10 days)  
**Complexity:** HIGH - Holistic system-wide validation  
**Timeline:** Week 37-38 (PRE-GA, before public release)

---

## 📋 Executive Summary

**Purpose:** Ensure CORTEX 4.0 has ONLY version 4.0 artifacts - eliminate all v2/v3 naming, consolidate architecture diagrams, validate dashboard completeness, and ensure holistic system consistency before GA release.

**Why Critical:**
- ❌ Mixed versioning (v2, v3, v4.0) creates confusion
- ❌ Incomplete architecture documentation gaps (91% missing before Phase 6.5)
- ❌ Dashboard may not load all tabs/diagrams post-migration
- ❌ Inconsistent file naming prevents clean handoff
- ✅ Professional GA release requires unified branding

**Scope:**
1. **Version Consolidation:** All v2/v3 files renamed to v4.0 (code, docs, manifests)
2. **Architecture Completeness:** 100% diagram coverage (all orchestrators, workflows, integrations)
3. **Dashboard Validation:** All tabs load, all diagrams render, all links functional
4. **Naming Consistency:** File/class/function names follow CORTEX 4.0 conventions
5. **Documentation Audit:** Remove obsolete references, update all version mentions
6. **Manifest Cleanup:** Consolidate legacy manifests, ensure inheritance works

---

## 🎯 Success Criteria

**Phase 14 Complete When:**
- ✅ ZERO files with v2/v3 in name (excluding archives)
- ✅ 100% architecture diagram coverage (16 orchestrators documented)
- ✅ Dashboard loads all tabs without errors
- ✅ All cross-references point to v4.0 locations
- ✅ Git history clean (v2/v3 moved to archives with redirect docs)
- ✅ Test suite passing at 90%+ coverage
- ✅ Documentation hyperlinks validated (0 broken links)

---

## 📊 Current State Analysis

### Version Artifacts Found (December 22, 2025)

**Code Files:**
- `src/operations/modules/orchestration/*_v3.py` (maintenance_orchestrator_v3, etc.)
- `src/operations/modules/orchestration/*_v2.py` (smart_plan_loader_v2, complexity_analyzer_v2)
- Import references: `orchestration_3_0` namespace
- Test files: References to v2/v3 implementations

**Manifests:**
- `cortex-lens-v3-manifest.yaml` (should be v4.0 or archived)
- Planning System v3.0 references in manifests
- Legacy v2.5 compatibility requirements

**Documentation:**
- Mixed version references (Planning System 2.0 vs 3.0 vs 4.0)
- Architecture diagrams: 91% gap before Phase 6.5, now 36% complete
- Dashboard: Unknown completeness status

**Scripts:**
- `scripts/validation/verify_planning_system.py` imports `orchestration_3_0`
- `scripts/utilities/*_v2.py` files

---

## 🏗️ Phase 14 Task Breakdown

### 📦 Task 14.1: Version Consolidation Audit (Day 1-2)

**Duration:** 2 days  
**Owner:** CORTEX System  
**Risk:** LOW

**Objective:** Comprehensive inventory of all v2/v3 artifacts

**Deliverables:**
1. **Version Inventory Report:**
   - Python files: `**/*_v[23].py` (exclude archives)
   - YAML manifests: `**/*-v[23]-*.yaml`
   - Markdown docs: All v2/v3 version references
   - Import statements: `orchestration_3_0` namespace usage
   - Class names: `*V2`, `*V3` suffixes
   - Dashboard references: Hardcoded version paths

2. **Consolidation Strategy:**
   - **Archive Path:** `archive/version-migration/v2-v3-legacy/`
   - **Redirect Docs:** `MIGRATION-GUIDE-V3-TO-V4.md` for each moved file
   - **Import Rewiring:** Update all import paths to v4.0 locations
   - **Backward Compatibility:** Create v3 wrapper imports (deprecated warnings)

**Automation:**
```python
# scripts/validation/version_consolidation_audit.py
import re
from pathlib import Path

def find_version_artifacts(root: Path):
    """Find all v2/v3 artifacts in codebase."""
    results = {
        'python_files': [],
        'yaml_files': [],
        'doc_references': [],
        'import_statements': [],
        'class_names': []
    }
    
    # Scan Python files
    for py_file in root.rglob('*.py'):
        if 'archive' in str(py_file):
            continue
        
        # File name check
        if re.search(r'_v[23]\.py$', py_file.name):
            results['python_files'].append(py_file)
        
        # Import check
        content = py_file.read_text()
        if 'orchestration_3_0' in content:
            results['import_statements'].append(py_file)
        
        # Class name check
        if re.search(r'class \w+V[23]', content):
            results['class_names'].append(py_file)
    
    # Scan YAML manifests
    for yaml_file in root.rglob('*.yaml'):
        if 'archive' in str(yaml_file):
            continue
        if re.search(r'-v[23]-', yaml_file.name):
            results['yaml_files'].append(yaml_file)
    
    # Scan Markdown docs
    for md_file in root.rglob('*.md'):
        if 'archive' in str(md_file):
            continue
        content = md_file.read_text()
        if re.search(r'\bv[23]\.\d+\b', content):
            results['doc_references'].append(md_file)
    
    return results
```

**Validation:**
- Report generated: `cortex-brain/documents/reports/VERSION-CONSOLIDATION-AUDIT-2025-12-22.md`
- Total artifacts counted
- Migration plan approved

---

### 🔧 Task 14.2: Code Migration (Day 3-5)

**Duration:** 3 days  
**Owner:** CORTEX System  
**Risk:** MEDIUM (breaking changes possible)

**Objective:** Migrate all v2/v3 code to v4.0 naming

**Sub-Tasks:**

#### 14.2.1: Python Files (Day 3)
- Rename files: `*_v2.py` → `*.py` (v4.0 implied)
- Update class names: `ClassV2` → `Class`
- Rewrite imports: `orchestration_3_0` → `orchestrators`
- Add deprecation wrappers for v3 imports

**Example:**
```python
# OLD: src/operations/modules/orchestration/smart_plan_loader_v2.py
# NEW: src/operations/modules/orchestration/smart_plan_loader.py

# BACKWARD COMPAT WRAPPER:
# src/operations/modules/orchestration/smart_plan_loader_v2.py
"""
DEPRECATED: Use smart_plan_loader.py instead.
This wrapper maintained for backward compatibility until CORTEX 5.0.
"""
import warnings
from .smart_plan_loader import SmartPlanLoader

warnings.warn(
    "smart_plan_loader_v2 is deprecated, use smart_plan_loader",
    DeprecationWarning,
    stacklevel=2
)

SmartPlanLoaderV2 = SmartPlanLoader  # Alias for compatibility
```

#### 14.2.2: Test Files (Day 4)
- Update test imports
- Rename test files: `test_*_v2.py` → `test_*.py`
- Validate all tests pass

#### 14.2.3: Scripts & Utilities (Day 5)
- Update validation scripts
- Rename utility scripts
- Update CLI wrappers

**Validation:**
- All tests passing (pytest)
- No import errors
- Deprecation warnings logged but non-blocking

---

### 📝 Task 14.3: Manifest Consolidation (Day 6)

**Duration:** 1 day  
**Owner:** CORTEX System  
**Risk:** LOW

**Objective:** Unify manifest versioning to v4.0

**Actions:**
1. **Archive Legacy Manifests:**
   - `cortex-lens-v3-manifest.yaml` → `archive/manifests/cortex-lens-v3-legacy.yaml`
   - Create redirect: `cortex-lens-manifest.yaml` (v4.0)

2. **Update Planning System References:**
   - Keep `planning-system-2.0-manifest.yaml` (it's a SPEC, not implementation)
   - Update all references to point to v4.0 implementations

3. **Validate Inheritance:**
   - ADO manifest inherits Planning System 2.0 ✅
   - Sanitization manifest inherits Planning System 2.0 ✅
   - No broken inheritance chains

**Validation:**
- Manifest validator passes
- Inheritance resolver finds all parent manifests
- No cyclic dependencies

---

### 🎨 Task 14.4: Architecture Diagram Completeness (Day 7-8)

**Duration:** 2 days  
**Owner:** CORTEX System  
**Risk:** LOW (building on Phase 6.5 work)

**Objective:** Achieve 100% architecture diagram coverage

**Current Status (Phase 6.5 Progress):**
- ✅ Week 1 CRITICAL: ExecutionOrchestrator, BaseOrchestrator, Interactions (3/3)
- ✅ Week 2 Day 1 HIGH: TDD v4.0 (1/4)
- ☐ Week 2 HIGH Remaining: Planning System, Documentation, DevOps (3/4)
- ☐ Week 3 MEDIUM: ADO, Sanitization, Maintenance, CI/CD (4/4)

**Phase 14 Additions (Beyond Phase 6.5):**
- System architecture overview (high-level)
- Integration flow diagram (orchestrator→brain→MCP→git)
- Execution mode routing (🤖/👤/🔒)
- Tier 1/2 brain architecture
- MCP Gateway architecture
- Response template rendering flow

**Deliverables:**
- 22 total diagrams (11 from Phase 6.5 + 11 system-level)
- All diagrams in Mermaid format
- HTML exports for dashboard
- Cross-references validated

**Validation:**
- Every orchestrator has architecture doc
- System-level diagrams complete
- Dashboard can load all diagrams

---

### 🖥️ Task 14.5: Dashboard Validation (Day 9)

**Duration:** 1 day  
**Owner:** CORTEX System  
**Risk:** MEDIUM (UI/UX validation)

**Objective:** Validate dashboard loads all tabs and diagrams correctly

**Test Checklist:**
1. **Tab Loading:**
   - ✅ Overview tab renders
   - ✅ Orchestrators tab lists all 16 orchestrators
   - ✅ Architecture tab shows system diagrams
   - ✅ Metrics tab displays current stats
   - ✅ Documentation tab links work

2. **Diagram Rendering:**
   - ✅ All Mermaid diagrams render without errors
   - ✅ Interactive elements (clickable nodes) functional
   - ✅ Zoom/pan controls work
   - ✅ Export buttons functional

3. **Link Validation:**
   - ✅ Internal links (cross-references) resolve
   - ✅ External links (GitHub, docs) accessible
   - ✅ API doc links point to correct modules

4. **Performance:**
   - ✅ Dashboard loads in <3 seconds
   - ✅ No console errors
   - ✅ Mobile responsive

**Automation:**
```python
# scripts/validation/dashboard_validator.py
from selenium import webdriver
import time

def validate_dashboard(dashboard_url: str):
    """Validate dashboard completeness."""
    driver = webdriver.Chrome()
    results = []
    
    # Load dashboard
    driver.get(dashboard_url)
    time.sleep(2)
    
    # Check all tabs
    tabs = driver.find_elements_by_css_selector('[role="tab"]')
    for tab in tabs:
        tab.click()
        time.sleep(1)
        
        # Check for errors
        errors = driver.find_elements_by_css_selector('.error')
        if errors:
            results.append(f"❌ {tab.text}: {len(errors)} errors")
        else:
            results.append(f"✅ {tab.text}: OK")
    
    # Check diagrams
    diagrams = driver.find_elements_by_css_selector('.mermaid')
    results.append(f"📊 Diagrams found: {len(diagrams)}")
    
    driver.quit()
    return results
```

**Validation:**
- Dashboard health report generated
- All tabs load successfully
- Zero console errors
- Performance benchmarks met

---

### 📚 Task 14.6: Documentation Audit (Day 10)

**Duration:** 1 day  
**Owner:** CORTEX System  
**Risk:** LOW

**Objective:** Final sweep for consistency and broken links

**Actions:**
1. **Version Reference Cleanup:**
   - Replace all "CORTEX 3.0" with "CORTEX 4.0" (where appropriate)
   - Update architecture diagrams to show v4.0
   - Fix mixed version mentions (2.0 spec vs 4.0 implementation)

2. **Broken Link Detection:**
   - Scan all Markdown files for `[text](path)` links
   - Validate internal links resolve
   - Validate external links accessible
   - Generate broken link report

3. **File Path Updates:**
   - Update all references to moved files
   - Create redirect docs for archived files
   - Validate import paths in code examples

**Automation:**
```python
# scripts/validation/link_validator.py
import re
from pathlib import Path
from urllib.parse import urlparse

def validate_markdown_links(root: Path):
    """Validate all Markdown links."""
    broken_links = []
    
    for md_file in root.rglob('*.md'):
        content = md_file.read_text()
        
        # Find all Markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for text, url in links:
            parsed = urlparse(url)
            
            # Internal link
            if not parsed.scheme:
                target = (md_file.parent / url).resolve()
                if not target.exists():
                    broken_links.append({
                        'file': md_file,
                        'text': text,
                        'url': url,
                        'type': 'internal'
                    })
            
            # External link (skip for speed, manual check)
            # elif parsed.scheme in ['http', 'https']:
            #     # Could validate with requests.head()
    
    return broken_links
```

**Deliverables:**
- Broken link report: `cortex-brain/documents/reports/LINK-VALIDATION-REPORT.md`
- Version consistency report
- All issues resolved

**Validation:**
- Zero broken internal links
- All version references consistent
- Documentation passes review

---

## 📊 Phase 14 Metrics

**Before Phase 14:**
- Version artifacts: ~50+ files with v2/v3 naming
- Architecture coverage: 36% (4/11 weeks of Phase 6.5)
- Dashboard status: Unknown
- Link health: Unknown
- Naming consistency: ~70%

**After Phase 14:**
- Version artifacts: 0 (100% v4.0, legacy archived)
- Architecture coverage: 100% (22/22 diagrams)
- Dashboard status: 100% functional
- Link health: 100% (0 broken internal links)
- Naming consistency: 100%

---

## 🔗 Dependencies

**Prerequisites:**
- ✅ Phase 6 complete (all orchestrators migrated)
- ✅ Phase 6.5 complete (architecture docs 100%)
- ✅ Phase 9 complete (documentation finalized)

**Blocks:**
- Phase 13 (STS) cannot start until Phase 14 complete
- GA Release blocked until Phase 14 complete

---

## 🎯 Validation Gates

**Gate 1: Version Audit Complete (Day 2)**
- Inventory report approved
- Migration strategy documented
- Risk assessment complete

**Gate 2: Code Migration Complete (Day 5)**
- All tests passing
- No import errors
- Deprecation wrappers functional

**Gate 3: Architecture Complete (Day 8)**
- 100% diagram coverage
- All diagrams validated
- Dashboard integration ready

**Gate 4: Dashboard Validated (Day 9)**
- All tabs load
- Zero errors
- Performance benchmarks met

**Gate 5: Documentation Audit Complete (Day 10)**
- Zero broken links
- Version consistency verified
- Final review passed

---

## 🚨 Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking changes from renames | MEDIUM | HIGH | Deprecation wrappers, thorough testing |
| Dashboard rendering issues | LOW | MEDIUM | Pre-validate diagrams, fallback UI |
| Import path confusion | MEDIUM | HIGH | Clear migration guide, automated refactoring |
| Incomplete diagram coverage | LOW | LOW | Phase 6.5 establishes pattern |
| Performance degradation | LOW | MEDIUM | Benchmark before/after, optimize as needed |

---

## 📝 Rollback Plan

**If Phase 14 fails:**
1. Revert git commits (all changes in feature branch)
2. Restore v2/v3 wrapper imports
3. Re-enable legacy manifests
4. Document blockers in issue tracker
5. Schedule remediation sprint

**Rollback Trigger:**
- >5% test failures
- Dashboard completely broken
- Critical import errors in production
- Timeline exceeds 3 weeks (50% overrun)

---

## 🎓 Success Metrics

**Phase 14 Success When:**
- ✅ Version consolidation: 100% (0 v2/v3 files outside archives)
- ✅ Architecture coverage: 100% (22/22 diagrams)
- ✅ Dashboard health: 100% (all tabs functional)
- ✅ Link validation: 100% (0 broken internal links)
- ✅ Naming consistency: 100%
- ✅ Test coverage: 90%+ maintained
- ✅ Documentation review: APPROVED
- ✅ Pre-GA checklist: 100%

**Deliverables:**
1. Version consolidation report
2. Architecture diagram catalog (22 diagrams)
3. Dashboard validation report
4. Link validation report
5. Migration guide (v3→v4.0)
6. Pre-GA readiness certificate

---

## 📚 Related Documentation

- **Phase 6.5:** [Architecture Documentation Gap](./phase-06.5-architecture-docs.md) (baseline for diagrams)
- **Phase 9:** Documentation Finalization (prerequisite)
- **Dashboard Design:** `docs/features/dashboard-system.html`
- **Version History:** `CHANGELOG.md`
- **Migration Guide:** `cortex-brain/documents/implementation-guides/VERSION-CONSOLIDATION-GUIDE.md` (to be created)

---

## ✅ Approval & Sign-Off

**Phase 14 Approved When:**
- [ ] Executive summary reviewed
- [ ] Task breakdown validated
- [ ] Resource allocation confirmed
- [ ] Risk mitigation approved
- [ ] Timeline feasible
- [ ] Success criteria clear

**Approvers:**
- Development Lead: ___________________ Date: ___________
- QA Lead: ___________________ Date: ___________
- Documentation Lead: ___________________ Date: ___________

---

**Created:** December 22, 2025  
**Status:** 📋 PLANNED - Awaiting Phase 9 completion  
**Estimated Start:** Week 37  
**Target Completion:** Week 38  
**Criticality:** 🔴 PRE-GA BLOCKER
