# OBSOLETE FILES INVENTORY
**Status:** TIER 0 CLEANUP DOCUMENTATION  
**Last Updated:** 2026-01-24  
**Authority:** CORTEX Master Orchestrator  
**Purpose:** Identify files that could cause confusion for the master orchestrator and prevent stale data propagation

---

## Executive Summary

This inventory documents **168 obsolete files & directories** across CORTEX that:
- Duplicate functionality in newer architecture
- Serve as migration scripts (no longer needed post-migration)
- Archive legacy implementations
- Could cause routing confusion or stale data consumption

**Risk Level:** 🔴 **HIGH** — Master orchestrator may reference obsolete knowledge bases or routing tables  
**Remediation Time:** ~4 hours  
**Priority:** BLOCKING for Production Readiness Phase 3

---

## 1. CRITICAL DUPLICATE KNOWLEDGE BASE (HIGHEST PRIORITY)

### Issue: THREE COPIES OF KNOWLEDGE BASE
The knowledge repository is replicated in **3 separate locations**, creating confusion for master orchestrator context routing:

#### Location 1: `cortex/knowledge/best-practices/` (PRIMARY)
- **Status:** ✅ Active/Current
- **Structure:** Flat categorization (ui-ux-design, architecture, backend-python, etc.)
- **File Count:** 46 YAML files
- **Usage:** Referenced in knowledge repository initialization
- **Recommendation:** KEEP — This is the canonical location

**Contents (46 files):**
```
ai-ml-domains/
  - domain-rag-integration.yaml
  - embeddings-strategy.yaml
  - retrieval-pipeline.yaml
  - vector-database-guide.yaml
architecture/
  - api-versioning.yaml
  - ddd-aggregates-entities.yaml
  - ddd-bounded-contexts.yaml
  - ddd-domain-events.yaml
  - engineering-anti-patterns.yaml
  - engineering-design-patterns.yaml
  - engineering-solid-principles.yaml
  - graphql-best-practices.yaml
  - microservices-resilience-patterns.yaml
  - rest-api-design.yaml
backend-python/
  - clean-code.yaml
  - code-review.yaml
  - refactoring.yaml
database-management/
  - oracle-best-practices.yaml
devops-infrastructure/
  - aws-best-practices.yaml
  - cicd-pipelines.yaml
  - infrastructure-as-code.yaml
  - monitoring-observability.yaml
frontend-js-ts/
  - react-best-practices.yaml
performance-optimization/
  - caching-strategies.yaml
  - optimization-techniques.yaml
  - profiling-analysis.yaml
qa-automation-testing/
  - ai-assisted-testing.yaml
  - company-domain-knowledge.yaml
  - mstest-framework-patterns.yaml
  - page-object-patterns.yaml
  - qa-coding-standards.yaml
security/
  - api-security-checklist.yaml
  - owasp-top-10.yaml
  - secure-coding-practices.yaml
testing-validation/
  - selenium-to-playwright-migration.yaml
  - tdd-best-practices.yaml
  - test-doubles.yaml
  - testing-pyramid.yaml
ui-ux-design/
  - glassmorphism-design-standards.yaml
  - ui-ux-best-practices.yaml
INDEX.yaml
```

#### Location 2: `cortex/brain/knowledge/` (SECOND COPY)
- **Status:** ⚠️ Redundant — Mirrors Location 1
- **Structure:** Same categorization but different directory nesting
- **File Count:** 36 YAML files
- **Usage:** Likely stale — not actively referenced
- **Recommendation:** DELETE — Consolidate to Location 1

**Contents (36 files):**
```
cloud/
  - aws-best-practices.yaml
database/
  - oracle-best-practices.yaml
ddd/
  - aggregates-entities.yaml
  - bounded-contexts.yaml
  - domain-events.yaml
devops/
  - cicd-pipelines.yaml
  - infrastructure-as-code.yaml
  - monitoring-observability.yaml
domains/
  - domain-rag-integration.yaml
  - embeddings-strategy.yaml
  - retrieval-pipeline.yaml
  - vector-database-guide.yaml
engineering/
  - anti-patterns.yaml
  - api-design/api-versioning.yaml
  - api-design/graphql-best-practices.yaml
  - api-design/rest-api-design.yaml
  - clean-code.yaml
  - code-review.yaml
  - design-patterns.yaml
  - refactoring.yaml
  - solid-principles.yaml
frontend/
  - react-best-practices.yaml
microservices/
  - resilience-patterns.yaml
performance/
  - caching-strategies.yaml
  - optimization-techniques.yaml
  - profiling-analysis.yaml
security/
  - api-security-checklist.yaml
  - owasp-top-10.yaml
  - secure-coding-practices.yaml
testing/
  - selenium-to-playwright-migration.yaml
  - tdd-best-practices.yaml
  - test-doubles.yaml
  - testing-pyramid.yaml
ui-ux/
  - glassmorphism-design-standards.yaml
  - ui-ux-best-practices.yaml
```

#### Location 3: `cortex/brain/tier3/knowledge/` (THIRD COPY — UPPERCASE)
- **Status:** ❌ OBSOLETE — Duplicate with uppercase categories
- **Structure:** Nested UPPERCASE category folders + KNOWLEDGE-TAXONOMY.yaml
- **File Count:** 42 YAML files + metadata
- **Usage:** Appears to be abandoned tier-based approach
- **Recommendation:** DELETE — This tier3 structure is not used in current architecture

**Contents (42+ files):**
```
ARCHITECTURE/ (14 files)
  - aggregates-entities.yaml
  - anti-patterns.yaml
  - api-versioning.yaml
  - bounded-contexts.yaml
  - clean-code.yaml
  - code-review.yaml
  - design-patterns.yaml
  - domain-events.yaml
  - graphql-best-practices.yaml
  - react-best-practices.yaml
  - refactoring.yaml
  - resilience-patterns.yaml
  - rest-api-design.yaml
  - solid-principles.yaml
DATA-MANAGEMENT/
  - oracle-best-practices.yaml
DEPLOYMENT/
  - aws-best-practices.yaml
  - cicd-pipelines.yaml
  - infrastructure-as-code.yaml
  - monitoring-observability.yaml
DOCUMENTATION/
  - glassmorphism-design-standards.yaml
  - ui-ux-best-practices.yaml
KNOWLEDGE-CURATION/ (4 files)
  - domain-rag-integration.yaml
  - embeddings-strategy.yaml
  - retrieval-pipeline.yaml
  - vector-database-guide.yaml
PERFORMANCE/ (3 files)
SECURITY/ (3 files)
TESTING-VALIDATION/ (4 files)
KNOWLEDGE-TAXONOMY.yaml (metadata)
```

### Impact Analysis
- **Master Orchestrator Confusion:** When routing intent to knowledge repo, may load stale data from Location 2 or 3
- **Context Bloat:** Triples memory footprint when all three are loaded during initialization
- **Update Nightmare:** Changes to Location 1 are not reflected in Locations 2 & 3
- **Test Ambiguity:** Tests may randomly reference different versions

### Remediation Action Items
| Item | Action | Effort | Done? |
|------|--------|--------|-------|
| AC-REM-KB-001 | Verify Location 1 is the active knowledge source in `cortex_brain/tier0/governance_registry.py` | 0.5h | ❌ |
| AC-REM-KB-002 | Remove all imports/references to Location 2 (`cortex/brain/knowledge/`) | 1h | ❌ |
| AC-REM-KB-003 | Delete Location 2 (`cortex/brain/knowledge/`) directory entirely | 0.5h | ❌ |
| AC-REM-KB-004 | Delete Location 3 (`cortex/brain/tier3/knowledge/`) directory entirely | 0.5h | ❌ |
| AC-REM-KB-005 | Update knowledge registry config to point only to Location 1 | 1h | ❌ |
| AC-REM-KB-006 | Run tests to verify no stale references remain | 0.5h | ❌ |

---

## 2. OBSOLETE FOLDER STRUCTURE MIGRATION FILES

### Issue: One-Time Migration Scripts Still Present
These scripts were used to migrate CORTEX folder structure but are no longer needed:

#### Python Scripts (cortex/scripts-root-archive/)
```
❌ migrate_folder_structure.py
   └─ ONE-TIME USE: Migrated old folder layout to new tier0/tier1 structure
   └─ Location: /cortex/scripts-root-archive/migrate_folder_structure.py
   └─ Backup exists: /cortex/scripts-root-archive/maintenance/migrate_folder_structure.py
   └─ Recommendation: DELETE BOTH

❌ migration-validator.py
   └─ ONE-TIME USE: Validated migration completeness
   └─ Location: /cortex/scripts-root-archive/migration-validator.py
   └─ Recommendation: DELETE

❌ doc-migrate-automated.py
   └─ ONE-TIME USE: Automated doc migration (specific to 2025-11 migration)
   └─ Location: /cortex/scripts-root-archive/doc-migrate-automated.py
   └─ Recommendation: DELETE

❌ create_stubs.py
   └─ ONE-TIME USE: Generated stub files during Phase A
   └─ Location: /cortex/scripts-root-archive/create_stubs.py
   └─ Recommendation: DELETE

❌ phase_c_stub_generator.py
   └─ ONE-TIME USE: Generated Phase C stubs (now complete)
   └─ Location: /cortex/scripts-root-archive/phase_c_stub_generator.py
   └─ Recommendation: DELETE
```

#### Configuration Files (cortex/scripts-root-archive/)
```
❌ doc-categorization-rules.yaml
   └─ Configuration for doc migration (no longer used)
   └─ Location: /cortex/scripts-root-archive/doc-categorization-rules.yaml
   └─ Recommendation: DELETE

❌ doc-ignore-list.yaml
   └─ List of docs to ignore during migration (stale)
   └─ Location: /cortex/scripts-root-archive/doc-ignore-list.yaml
   └─ Recommendation: DELETE
```

#### Deployment Subfolder
```
❌ /cortex/scripts-root-archive/deployment/
   └─ Contains old deployment scripts not integrated into main deployment/
   └─ Structure needs review before deletion
   └─ Recommendation: AUDIT FIRST, THEN DELETE if no active references
```

**Total Items:** 11 files + 1 directory to evaluate

---

## 3. OBSOLETE TEST FILES FOR REMOVED FEATURES

### Issue: Tests for Migration Infrastructure No Longer Needed

#### Folder Structure Tests (No Longer Applicable)
```
❌ tests/unit/test_folder_structure.py
   └─ Tested old folder structure migration logic
   └─ Location: /tests/unit/test_folder_structure.py
   └─ Status: Obsolete (migration complete)
   └─ Recommendation: DELETE

❌ tests/unit/test_folder_structure_design.py
   └─ Tested proposed folder structure designs (pre-migration)
   └─ Location: /tests/unit/test_folder_structure_design.py
   └─ Status: Obsolete (migration implemented)
   └─ Recommendation: DELETE

❌ tests/unit/infrastructure/test_folder_structure_design.py
   └─ Duplicate of above in infrastructure subfolder
   └─ Location: /tests/unit/infrastructure/test_folder_structure_design.py
   └─ Status: Obsolete
   └─ Recommendation: DELETE

❌ tests/unit/infrastructure/test_folder_migration_script.py
   └─ Tested the migration script (no longer used)
   └─ Location: /tests/unit/infrastructure/test_folder_migration_script.py
   └─ Status: Obsolete
   └─ Recommendation: DELETE

❌ tests/unit/test_migration_script.py
   └─ Root-level test for migration (stale)
   └─ Location: /tests/unit/test_migration_script.py
   └─ Status: Obsolete
   └─ Recommendation: DELETE
```

**Total Test Files:** 5 files

---

## 4. OBSOLETE INFRASTRUCTURE MODULES

### Issue: One-Off Utility Scripts Not Integrated Into Main System

#### Python Modules Not Actively Used
```
❌ cortex/infrastructure/folder_structure_designer.py
   └─ Used to design folder structure layout (now finalized)
   └─ Location: /cortex/infrastructure/folder_structure_designer.py
   └─ Status: Design phase COMPLETE
   └─ Recommendation: DELETE or ARCHIVE

❌ cortex/infrastructure/folder_migration_script.py
   └─ Duplicate migration logic (redundant with scripts-root-archive/)
   └─ Location: /cortex/infrastructure/folder_migration_script.py
   └─ Status: Obsolete
   └─ Recommendation: DELETE

❌ cortex/infrastructure/threshold_monitor.py
   └─ One-off monitoring script (unclear current usage)
   └─ Location: /cortex/infrastructure/threshold_monitor.py
   └─ Status: ⚠️ AUDIT REQUIRED — may be actively used
   └─ Recommendation: VERIFY REFERENCES before deleting

❌ cortex/core/governance/stakeholder_notification.py
   └─ One-off notification module (not integrated into main governance)
   └─ Location: /cortex/core/governance/stakeholder_notification.py
   └─ Status: Unclear if active
   └─ Recommendation: AUDIT REQUIRED
```

**Total Modules:** 4 items (2 AUDIT REQUIRED)

---

## 5. OBSOLETE TOOLS & SCAFFOLDERS

### Issue: Orchestrator Scaffolding Infrastructure No Longer Needed

```
❌ cortex/tools/scaffolder_templates.py
   └─ Generated scaffolder templates (one-time use)
   └─ Location: /cortex/tools/scaffolder_templates.py
   └─ Status: Stale
   └─ Recommendation: DELETE

❌ cortex/tools/orchestrator_scaffolder.py
   └─ Scaffolded new orchestrators during development (now complete)
   └─ Location: /cortex/tools/orchestrator_scaffolder.py
   └─ Status: Obsolete (orchestrators are implemented)
   └─ Recommendation: DELETE
```

**Total Items:** 2 files

---

## 6. OBSOLETE BRAIN/VACUUM CONFIGURATION

```
❌ cortex/brain/vacuum/config.yaml
   └─ Configuration for a "vacuum" operation (unclear purpose)
   └─ Location: /cortex/brain/vacuum/config.yaml
   └─ Status: ⚠️ AUDIT REQUIRED
   └─ Recommendation: Verify purpose before deletion
```

**Total Items:** 1 file (AUDIT REQUIRED)

---

## 7. ARCHIVE DIRECTORIES WITH UNKNOWN CONTENTS

### Potential Obsolete Directories (Requires Deep Audit)

```
⚠️ _workspaces/roadmap/_archives/
   └─ Archived roadmap files (may contain historical reference)
   └─ Status: Likely stale but may have historical value
   └─ Recommendation: MOVE TO DOCUMENT VAULT, not delete

⚠️ _workspaces/docs/archives/
   └─ Archived documentation (historical)
   └─ Status: Likely stale
   └─ Recommendation: AUDIT FOR IMPORTANT CONTEXT

⚠️ cortex/scripts-root-archive/deployment/
   └─ Old deployment scripts
   └─ Status: Unknown — may contain legacy deployment logic
   └─ Recommendation: AUDIT BEFORE DELETION
```

---

## 8. STALE LOG FILES

```
❌ cortex/test_audit_trail.log
   └─ Test output log (likely stale from previous test run)
   └─ Location: /cortex/test_audit_trail.log
   └─ Status: Non-critical
   └─ Recommendation: DELETE (logs should go to temp directory)
```

**Total Items:** 1 file

---

## 9. REDUNDANT TIER0 CONFIGURATION FILES

### Issue: Configuration Metadata That May Be Duplicated

```
⚠️ cortex/brain/tier0/intent-to-ac-id-mapping.yaml
   └─ Maps intents to AC-IDs (may duplicate cortex_brain/tier0/ version)
   └─ Location: /cortex/brain/tier0/intent-to-ac-id-mapping.yaml
   └─ Status: AUDIT REQUIRED — verify if this is canonical

⚠️ cortex/brain/tier0/governance-loading-sequence.yaml
   └─ Governance initialization sequence
   └─ Status: AUDIT REQUIRED — verify if actively used

⚠️ cortex/brain/tier0/lens-protocol-implementation.yaml
   └─ LENS protocol definition
   └─ Status: AUDIT REQUIRED — verify if used or duplicated elsewhere

⚠️ cortex/brain/tier0/response-headers.yaml
   └─ Response header templates
   └─ Status: AUDIT REQUIRED — verify if actively referenced
```

**Total Items:** 4 files (ALL AUDIT REQUIRED)

---

## SUMMARY TABLE

| Category | Count | Priority | Action |
|----------|-------|----------|--------|
| **Knowledge Base Duplicates** | 78 files | 🔴 CRITICAL | DELETE Locations 2 & 3 |
| **Migration Scripts** | 11 items | 🔴 CRITICAL | DELETE |
| **Migration Tests** | 5 files | 🟡 HIGH | DELETE |
| **Unused Infrastructure** | 4 modules | 🟡 HIGH | AUDIT + DELETE |
| **Scaffolders** | 2 files | 🟡 HIGH | DELETE |
| **Archive Directories** | 3 dirs | 🟠 MEDIUM | AUDIT / VAULT |
| **Stale Config** | 4 files | 🟠 MEDIUM | AUDIT |
| **Log Files** | 1 file | 🟢 LOW | DELETE |
| **TOTAL** | **108 items** | **Mixed** | **See action plan** |

---

## REMEDIATION ACTION PLAN

### Phase 1: IMMEDIATE (HIGH RISK) — 2 hours
1. **Delete Knowledge Base Location 2** (`cortex/brain/knowledge/`)
   - Grep for imports/references first
   - Verify no active code references
   - Delete directory

2. **Delete Knowledge Base Location 3** (`cortex/brain/tier3/knowledge/`)
   - Grep for imports/references first
   - Verify no active code references
   - Delete directory

3. **Delete Migration Scripts** (`cortex/scripts-root-archive/`)
   - Delete: migrate_folder_structure.py (both copies)
   - Delete: migration-validator.py
   - Delete: doc-migrate-automated.py
   - Delete: create_stubs.py
   - Delete: phase_c_stub_generator.py
   - Delete: doc-categorization-rules.yaml
   - Delete: doc-ignore-list.yaml

4. **Delete Migration Tests**
   - Delete all 5 test files listed in Section 3

### Phase 2: AUDIT REQUIRED — 1.5 hours
1. Audit threshold_monitor.py for active references
2. Audit stakeholder_notification.py for active references
3. Audit cortex/brain/vacuum/config.yaml purpose
4. Audit cortex/brain/tier0/*.yaml files for canonical status

### Phase 3: ARCHIVE & CLEANUP — 0.5 hours
1. Move archive directories to separate DOCUMENT_VAULT location
2. Delete log files
3. Delete scaffolder files (if audit confirms no usage)
4. Run full test suite to verify no regressions

---

## IMPLEMENTATION NOTES

### Tools to Verify Before Deletion
```bash
# Search for references before deleting
grep -r "from cortex.brain.knowledge" cortex/ tests/
grep -r "from cortex.brain.tier3.knowledge" cortex/ tests/
grep -r "folder_structure" cortex/ tests/
grep -r "migration_script" cortex/ tests/
grep -r "threshold_monitor" cortex/ tests/
```

### Git Strategy
All deletions should be committed as:
```
AC-REM-KB-001: Remove duplicate knowledge base locations 2 & 3
AC-REM-MIGS-001: Remove obsolete migration scripts
AC-REM-TEST-001: Remove obsolete migration test files
```

### Verification Checklist
- [ ] No imports reference deleted locations
- [ ] All tests pass post-deletion
- [ ] Master orchestrator initialization completes without warnings
- [ ] Knowledge repository returns data from canonical location only
- [ ] Git history preserved (use `git rm`, not `rm`)

---

**Status:** Ready for Implementation  
**Owner:** CORTEX Maintenance Team  
**Next Review:** After Phase 3 Remediation Complete  
**Governance:** TIER 0 ENFORCEMENT — Master Orchestrator Reliability
