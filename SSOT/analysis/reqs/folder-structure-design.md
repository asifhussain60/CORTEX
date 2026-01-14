# Folder Structure Design & Migration Plan

**Date:** 2026-01-14  
**Version:** 1.0.0 - MIGRATION SPECIFICATION  
**Status:** Ready for Execution  
**Purpose:** Define clean nested folder structure for CORTEX 7.0 with kebab-case naming

---

## Executive Summary

CORTEX 7.0 reorganizes source code and configuration into a clean nested hierarchy:

- ✅ **cortex-brain/**: All governance, templates, and configuration (organized by tier)
- ✅ **src/**: All source code organized by component (orchestrators, infrastructure, mcp)
- ✅ **tests/**: Tests organized by layer (unit, integration, fixtures)
- ✅ **scripts/**: Utility scripts organized by purpose (admin, generate, tools)
- ✅ **SSOT/roadmap/**: All documentation consolidated (18 files → roadmap/)
- ✅ **Kebab-case naming**: All filenames max 25 characters
- ✅ **No root-level .md**: All documentation in SSOT/roadmap/

---

## Part 1: Current State Analysis

### 1.1 What Exists Now

```
CORTEX/ (root)
├── __backup/                           (safe, not touched)
├── SSOT/
│   ├── 18 root-level .md files         ⚠️  Need consolidation
│   └── roadmap/                        ✅ New consolidation folder
├── cortex-brain/
│   ├── (mixed organization)            ⚠️  Needs reorganization
│   ├── response-templates-v4.yaml      ⚠️  Should be in tier2
│   └── ...
├── src/
│   ├── orchestrators/                  ⚠️  Flat structure
│   │   ├── ado/
│   │   ├── audit_logger.py
│   │   ├── core/
│   │   ├── custom/
│   │   ├── tdd/
│   │   ├── planning/
│   │   └── ... (mixed organization)
│   └── ...
├── tests/
│   └── (flat structure)                ⚠️  Needs reorganization
└── scripts/
    └── (flat structure)                ⚠️  Needs reorganization
```

### 1.2 What's Wrong

| Issue | Impact | Fix |
|-------|--------|-----|
| 18 root-level .md files in SSOT/ | Cluttered, hard to maintain | Consolidate into roadmap/ |
| response-templates-v4.yaml in cortex-brain/ root | Mixed concerns | Move to tier2/response-templates/ |
| Flat orchestrators/ folder | Hard to find/navigate | Organize into core/, domain/, custom/ |
| Scattered response handling code | Unclear ownership | Consolidate in orchestrators/response/ |
| No registry organization | Hard to discover orchestrators | Create orchestrators/registry/ |
| Flat tests/ folder | Hard to navigate | Organize into unit/, integration/, fixtures/ |
| Flat scripts/ folder | Hard to find utilities | Organize into admin/, generate/, tools/ |
| Mixed file naming (snake_case, PascalCase) | Inconsistent | Enforce kebab-case, max 25 chars |

---

## Part 2: Target State Design

### 2.1 Complete Nested Structure

```
CORTEX/ (root, clean)
│
├── cortex-brain/
│   ├── tier0/                                    (immutable CORTEX core)
│   │   └── governance/
│   │       └── core-rules.yaml
│   │
│   ├── tier1/                                    (active state)
│   │   ├── tracking/
│   │   │   └── progress-tracker.json
│   │   ├── acceptance-criteria/
│   │   │   └── AC-INDEX.yaml
│   │   └── governance/
│   │       └── business-rules/
│   │
│   ├── tier2/                                    (practices & templates)
│   │   ├── response-templates/                   ⭐ MOVED HERE
│   │   │   ├── _schema/
│   │   │   │   └── standard-schema.yaml          (CORTEX 4.0 schema)
│   │   │   ├── core/
│   │   │   │   ├── master-orch.yaml              (MasterOrchestrator template)
│   │   │   │   ├── tdd-master.yaml               (TDD Master template)
│   │   │   │   ├── planning-orch.yaml
│   │   │   │   ├── governance-orch.yaml
│   │   │   │   └── evidence-orch.yaml
│   │   │   ├── domain/                           (domain-specific orchestrators)
│   │   │   │   ├── ado-orch.yaml
│   │   │   │   ├── vacuum-orch.yaml
│   │   │   │   └── investigation-orch.yaml
│   │   │   └── custom/                           (user-defined orchestrators)
│   │   │       └── .gitkeep
│   │   │
│   │   ├── engineering-standards/
│   │   │   ├── code-quality.yaml
│   │   │   ├── testing.yaml
│   │   │   └── security.yaml
│   │   │
│   │   └── configuration/
│   │       ├── core-config.yaml
│   │       └── environment.yaml
│   │
│   ├── tier3/                                    (knowledge patterns)
│   │   └── knowledge-patterns/
│   │       └── implementation-patterns.yaml
│   │
│   ├── cx6-plan/                                 (planning)
│   │   └── viewer/
│   │       └── plan-viewer-data.json
│   │
│   ├── documents/                                (generated docs)
│   │   ├── architecture/
│   │   ├── governance/
│   │   └── roadmap/
│   │
│   └── audit-logs/                               (operational logs)
│
├── src/                                          (application code)
│   ├── orchestrators/
│   │   ├── core/                                 ⭐ ORGANIZED
│   │   │   ├── base-orchestrator.py
│   │   │   ├── master-orchestrator.py
│   │   │   ├── tdd-master-orchestrator.py
│   │   │   ├── planning-orchestrator.py
│   │   │   ├── governance-orchestrator.py
│   │   │   └── evidence-orchestrator.py
│   │   │
│   │   ├── domain/
│   │   │   ├── ado-orchestrator.py
│   │   │   ├── vacuum-orchestrator.py
│   │   │   ├── investigation-orchestrator.py
│   │   │   └── sanitization-orchestrator.py
│   │   │
│   │   ├── custom/                               (user/plugin orchestrators)
│   │   │   └── .gitkeep
│   │   │
│   │   ├── middleware/                           ⭐ ORGANIZED
│   │   │   ├── governance-check.py
│   │   │   ├── execution-guard.py
│   │   │   └── audit-logger.py
│   │   │
│   │   ├── registry/                             ⭐ NEW
│   │   │   ├── orchestrator-registry.py
│   │   │   ├── template-registry.py
│   │   │   └── dependency-resolver.py
│   │   │
│   │   └── response/                             ⭐ NEW
│   │       ├── response-renderer.py
│   │       ├── template-resolver.py
│   │       └── response-formatter.py
│   │
│   ├── infrastructure/
│   │   ├── audit-logger/
│   │   │   ├── logger.py
│   │   │   ├── schema.py
│   │   │   └── queries.py
│   │   │
│   │   ├── governance/
│   │   │   ├── registry.py
│   │   │   ├── evaluator.py
│   │   │   └── middleware.py
│   │   │
│   │   ├── state/
│   │   │   ├── manager.py
│   │   │   ├── persistence.py
│   │   │   └── lifecycle.py
│   │   │
│   │   └── execution/
│   │       ├── request.py
│   │       ├── result.py
│   │       └── context.py
│   │
│   ├── mcp/
│   │   ├── tools/
│   │   │   ├── governance-tools.py
│   │   │   ├── audit-tools.py
│   │   │   ├── state-tools.py
│   │   │   ├── evidence-tools.py
│   │   │   └── orchestrator-tools.py
│   │   │
│   │   └── server.py
│   │
│   └── utils/
│       ├── pathlib-utils.py               (CORE-005: cross-platform paths)
│       ├── yaml-loader.py
│       └── validation.py
│
├── tests/                                        ⭐ ORGANIZED BY LAYER
│   ├── unit/
│   │   ├── test-orchestrators.py
│   │   ├── test-templates.py
│   │   ├── test-governance.py
│   │   └── test-infrastructure.py
│   │
│   ├── integration/
│   │   ├── test-orch-integration.py
│   │   ├── test-template-resolution.py
│   │   └── test-governance-enforcement.py
│   │
│   ├── fixtures/
│   │   ├── orchestrator-fixtures.py
│   │   ├── template-fixtures.yaml
│   │   └── context-fixtures.py
│   │
│   └── conftest.py
│
├── scripts/                                      ⭐ ORGANIZED BY PURPOSE
│   ├── admin/
│   │   ├── migrate-folder-structure.py
│   │   └── validate-ssot.py
│   │
│   ├── generate/
│   │   ├── gen-template-index.py
│   │   └── gen-orch-registry.py
│   │
│   └── tools/
│       └── get-ac-title.sh
│
├── SSOT/                                         (consolidated docs)
│   ├── roadmap/                                  ⭐ ALL CONSOLIDATION HERE
│   │   ├── 00-consolidation-summary.md          (existing)
│   │   ├── consolidated-requirements.md          (existing)
│   │   ├── framework-arch-spec.md                (existing)
│   │   ├── implementation-roadmap.md             (existing)
│   │   ├── prod-readiness-analysis.md            (existing)
│   │   ├── custom-response-templates.md          ⭐ NEW (created)
│   │   ├── folder-structure-design.md            ⭐ NEW (this file)
│   │   └── README.md                             (existing)
│   │
│   ├── quick-reference.md                        (REFERENCE - kept for now)
│   ├── README.md                                 (REFERENCE - kept for now)
│   └── DOCUMENT-INDEX.md                         (REFERENCE - kept for now)
│
├── __backup/                                     (unchanged)
├── .github/                                      (GitHub templates)
├── docs/                                         (user docs - unchanged)
├── README.md                                     (root readme)
├── LICENSE
├── requirements.txt
└── setup.py
```

### 2.2 File Naming Rules

**All new/renamed files follow:**

✅ **Kebab-case:** file-name.py (not FileName.py, not file_name.py)
✅ **Max 25 characters:** (including extension)
✅ **Descriptive:** orchestrator-registry.py (not reg.py or registry.py)
✅ **Test files:** test-component.py (not test_component.py or ComponentTest.py)

**Examples:**

| Component | Filename | Length |
|-----------|----------|--------|
| Master Orchestrator | `master-orchestrator.py` | 20 |
| TDD Master Orchestrator | `tdd-master-orchestrator.py` | 25 |
| Response Renderer | `response-renderer.py` | 19 |
| Template Resolver | `template-resolver.py` | 20 |
| Orchestrator Registry | `orchestrator-registry.py` | 22 |
| Governance Evaluator | `governance-evaluator.py` | 22 |
| Test Orchestrators | `test-orchestrators.py` | 20 |

---

## Part 3: Migration Steps

### 3.1 Phase 1: Directory Creation (No File Moves Yet)

```powershell
# Create directories (in order of dependency)

# cortex-brain/tier2
mkdir cortex-brain\tier2\response-templates\_schema
mkdir cortex-brain\tier2\response-templates\core
mkdir cortex-brain\tier2\response-templates\domain
mkdir cortex-brain\tier2\response-templates\custom
mkdir cortex-brain\tier2\engineering-standards
mkdir cortex-brain\tier2\configuration

# src/orchestrators
mkdir src\orchestrators\core
mkdir src\orchestrators\domain
mkdir src\orchestrators\custom
mkdir src\orchestrators\middleware
mkdir src\orchestrators\registry
mkdir src\orchestrators\response

# src/infrastructure
mkdir src\infrastructure\audit-logger
mkdir src\infrastructure\governance
mkdir src\infrastructure\state
mkdir src\infrastructure\execution

# src/mcp/tools
mkdir src\mcp\tools

# src/utils
mkdir src\utils

# tests
mkdir tests\unit
mkdir tests\integration
mkdir tests\fixtures

# scripts
mkdir scripts\admin
mkdir scripts\generate
mkdir scripts\tools
```

### 3.2 Phase 2: File Migration (One Category at a Time)

**Step 1: Response Templates**
```powershell
# Copy CORTEX 4.0 schema to _schema/
copy cortex-brain\response-templates-v4.yaml `
     cortex-brain\tier2\response-templates\_schema\standard-schema.yaml

# Create template files for each core orchestrator
# (Create new files with template content - detailed in Part 4)
```

**Step 2: Orchestrator Files**
```powershell
# Move core orchestrators
move src\orchestrators\master.py src\orchestrators\core\master-orchestrator.py
move src\orchestrators\tdd-master.py src\orchestrators\core\tdd-master-orchestrator.py
# ... etc for all core orchestrators

# Move domain orchestrators
move src\orchestrators\ado.py src\orchestrators\domain\ado-orchestrator.py
# ... etc

# Move middleware
move src\orchestrators\middleware\*.py src\orchestrators\middleware\
```

**Step 3: Infrastructure Files**
```powershell
# Move audit infrastructure
move src\infrastructure\audit-*.py src\infrastructure\audit-logger\

# Move governance infrastructure
move src\infrastructure\governance-*.py src\infrastructure\governance\

# Move state infrastructure
move src\infrastructure\state-*.py src\infrastructure\state\

# Move execution types
move src\infrastructure\execution-*.py src\infrastructure\execution\
move src\infrastructure\request.py src\infrastructure\execution\request.py
move src\infrastructure\result.py src\infrastructure\execution\result.py
```

**Step 4: Tests**
```powershell
# Move test files to appropriate layers
move tests\test-*.py tests\unit\
move tests\integration-test-*.py tests\integration\
move tests\fixtures\* tests\fixtures\
```

**Step 5: Scripts**
```powershell
# Move scripts to organized folders
move scripts\admin-*.py scripts\admin\
move scripts\gen-*.py scripts\generate\
move scripts\*.sh scripts\tools\
```

### 3.3 Phase 3: Update Imports (All Python Files)

**Pattern to replace:**

```python
# OLD
from src.orchestrators.master import MasterOrchestrator

# NEW
from src.orchestrators.core.master_orchestrator import MasterOrchestrator

# OLD
from src.orchestrators.middleware.governance_check import GovernanceChecker

# NEW  
from src.orchestrators.middleware.governance_check import GovernanceChecker

# OLD
from src.infrastructure.audit_logger import AuditLogger

# NEW
from src.infrastructure.audit_logger.logger import AuditLogger
```

**Tools to help:**
```bash
# Find all import statements
grep -r "from src.orchestrators" src/ tests/

# Find all from imports
grep -r "from src.infrastructure" src/ tests/

# Use IDE find-and-replace with regex
```

### 3.4 Phase 4: Delete Root SSOT Files

**After verifying all consolidation is complete:**

```powershell
# DELETE these 18 files from SSOT/ root (they're all consolidated in roadmap/)
Remove-Item SSOT\00-START-HERE.md
Remove-Item SSOT\anti-breakage-executive-summary.md
Remove-Item SSOT\before-and-after.md
Remove-Item SSOT\cortex7-arch-decisions.md
Remove-Item SSOT\CORTEX7-DOR-ASSESSMENT.md
Remove-Item SSOT\cortex7-governance-spec.md
Remove-Item SSOT\cortex7-ssot-reqs.yaml
Remove-Item SSOT\executive-summary.md
Remove-Item SSOT\findings-and-design-decision.md
Remove-Item SSOT\governance-registry-implementation.md
Remove-Item SSOT\governance-rule-evaluation.md
Remove-Item SSOT\governance-wiring-solution.md
Remove-Item SSOT\SOLUTION-COMPLETE.md
Remove-Item SSOT\what-prevents-breakage.md
Remove-Item SSOT\safety-executive-summary.md

# KEEP these 3 files (reference material)
# - SSOT\quick-reference.md
# - SSOT\README.md
# - SSOT\DOCUMENT-INDEX.md
```

---

## Part 4: File Creation Examples

### 4.1 Standard Response Template Schema

**File:** `cortex-brain/tier2/response-templates/_schema/standard-schema.yaml`

This will contain the CORTEX 4.0 schema (extracted from response-templates-v4.yaml)

### 4.2 Core Orchestrator Templates

**File:** `cortex-brain/tier2/response-templates/core/master-orch.yaml`

```yaml
schema_version: '4.6.0'
orchestrator: "MasterOrchestrator"
description: "Master Orchestrator response template"

mandatory_header:
  enabled: true
  template: |
    ## 🧠 CORTEX {operation_type}
    **Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅
    
    ---
    **Copyright © 2025-2026 Asif Hussain. All rights reserved.**
    
    ---

executive_summary:
  enabled: true
  sections:
    - name: "Outcomes"
      marker: "✅"
      required: true
    - name: "In Progress"
      marker: "⚙️"
      required: false
    - name: "Risks"
      marker: "⚠️"
      required: false
    - name: "Impact"
      marker: "🎯"
      required: false
    - name: "Next Steps"
      marker: "📋"
      required: true
```

### 4.3 TDD Master Custom Template

**File:** `cortex-brain/tier2/response-templates/core/tdd-master.yaml`

```yaml
schema_version: '4.6.0'
orchestrator: "TddMasterOrchestrator"
description: "TDD Master with test coverage metrics"

mandatory_header:
  enabled: true
  # Uses standard header

executive_summary:
  enabled: true
  sections:
    - name: "Outcomes"
      marker: "✅"
      required: true
    - name: "In Progress"
      marker: "⚙️"
      required: false

custom_sections:
  enabled: true
  sections:
    - name: "Test Results"
      marker: "📊"
      required: true
      format: |
        📊 TEST RESULTS
        
        • Unit Tests: {unit_passed}/{unit_total} passed
        • Integration Tests: {int_passed}/{int_total} passed
        • Coverage: {coverage}%
```

---

## Part 5: Validation Checklist

### Before Migration

- [ ] All files backed up (git status clean)
- [ ] Create feature branch: `git checkout -b feat/folder-restructure`
- [ ] Read this document fully
- [ ] Understand all kebab-case naming rules
- [ ] Identify all current file locations (use grep)

### During Migration

- [ ] Create all directories first (Phase 1)
- [ ] Verify no directory conflicts
- [ ] Move files one category at a time (Phase 2)
- [ ] Verify no files lost (checksum validation)
- [ ] Update imports systematically (Phase 3)
- [ ] Run tests after each import update batch
- [ ] Commit after each major phase

### After Migration

- [ ] All tests passing
- [ ] Code coverage ≥95%
- [ ] No import errors
- [ ] Cross-platform testing (Windows + macOS)
- [ ] Git diff clean (no unintended changes)
- [ ] Delete 18 SSOT root files (Phase 4)
- [ ] Final commit: `chore(folder): restructure for clean nested organization`

---

## Part 6: Success Criteria

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **Directory structure** | 100% complete | `tree cortex-brain/`, `tree src/`, `tree tests/` |
| **File naming** | All kebab-case, max 25 chars | `find . -name "*.py" \| grep -E "_[a-z]+" \| wc -l` (should be 0) |
| **No file loss** | 0 files missing | Checksum comparison before/after |
| **Imports updated** | 100% passing | `python -m pytest --co -q \| grep ERROR` (should be 0) |
| **Tests passing** | 100% (all layers) | `pytest tests/` output shows all green |
| **Cross-platform** | Windows + macOS + Linux | Tests pass on all 3 platforms |
| **Code coverage** | ≥95% | `pytest --cov=src/ \| tail -5` shows ≥95% |
| **SSOT consolidated** | 18 root files deleted | `ls SSOT/*.md \| grep -v roadmap` (should be 3 files) |

---

## Part 7: Risks & Mitigations

| Risk | Mitigation | Impact |
|-------|-----------|--------|
| **Import path breaks** | Test imports after each move; comprehensive grep | HIGH |
| **File lost in move** | Validate checksums before/after each category | HIGH |
| **Circular imports introduced** | Run import validator after changes | MEDIUM |
| **Path issues on Windows** | Use pathlib, test on Windows immediately | MEDIUM |
| **Tests break** | Run tests after every phase; don't batch moves | MEDIUM |
| **Wrong file renamed** | Review each rename before executing; use git | LOW |
| **Documentation outdated** | Update all docs simultaneously with code | LOW |

---

**Status:** READY FOR EXECUTION ✅

This migration follows a safe, incremental approach with validation at each step. No production code runs during migration; it's pure reorganization with import updates.
