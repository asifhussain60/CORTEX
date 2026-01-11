# CORTEX 6.0 Plan Updates - 3-Layer Response Template Architecture

**Date:** January 10, 2026  
**Update Type:** Phase 2 Enhancement  
**Impact:** 8 new AC-IDs added (AC-TEMPLATE-001 to 008)  
**Total AC-IDs:** 111 (was 102)

---

## 📊 Summary of Changes

### **Files Updated:**

| File | Changes | Status |
|------|---------|--------|
| `holistic-snowball-plan.yaml` | Added response_template_architecture component to Phase 2 | ✅ Updated |
| `4-week-implementation-plan.yaml` | Updated total_ac_ids: 102 → 111 | ✅ Updated |
| `AC-INDEX.yaml` | Registered AC-TEMPLATE-001 to 008 | ✅ Updated |
| `progress-tracker.json` | Added enhancement to active epic | ✅ Updated |
| `cortex-plan-viewer.html` | Added component card with visual highlighting | ✅ Updated |
| `response-template-architecture.mmd` | New Mermaid diagram created | ✅ Created |
| `TEMPLATE-ARCHITECTURE-PLAN.yaml` | Comprehensive implementation plan | ✅ Created |
| `TEMPLATE-ARCHITECTURE-APPROVED.md` | Executive approval summary | ✅ Created |

---

## 🎯 What Was Added

### **New Component: 3-Layer Response Template Architecture**

**Location:** Phase 2 (Orchestration Core)  
**Priority:** HIGH  
**Duration:** 4 weeks (3 implementation phases)  
**Owner:** Infrastructure Team

**Problem Solved:**
- Current `response-templates-v4.yaml` is 2046 lines (violates CORE-002 anti-bloat)
- Duplication across 40+ orchestrators
- Maintenance burden
- No consistency enforcement

**Solution:**
Three-layer architecture with strict precedence rules:

1. **Layer 1 - Core Blocks** (`tier0/response-blocks.yaml`)
   - 15-20 atomic markdown fragments
   - Max 50 lines total
   - Examples: header, progress, next_steps, error, warning, completion
   - CORE-002 governance enforced

2. **Layer 2 - Category Templates** (`tier2/response-templates/{category}.yaml`)
   - 5 category files × 50 lines = 250 lines
   - Categories: core, integration, maintenance, conversion, security
   - Block composition rules + category-specific overrides

3. **Layer 3 - Orchestrator Overrides** (in manifests)
   - Max 15 lines per orchestrator
   - Only deviations from category template
   - Falls back to category → core

**Precedence:** Orchestrator > Category > Core

---

## 📋 New Acceptance Criteria

| AC-ID | Title | Phase | Description |
|-------|-------|-------|-------------|
| **AC-TEMPLATE-001** | Extract Core Blocks | 1 | Extract 15-20 atomic blocks from v4.yaml → tier0/response-blocks.yaml |
| **AC-TEMPLATE-002** | Block Schema Validation | 1 | Create JSON schema for block structure validation |
| **AC-TEMPLATE-003** | ResponseRenderer Block Loader | 1 | Update ResponseRenderer to load and cache blocks (<5ms) |
| **AC-TEMPLATE-004** | Create Category Templates | 2 | Create 5 category templates in tier2/ (50 lines each) |
| **AC-TEMPLATE-005** | Category Inheritance Resolver | 2 | Implement precedence resolution (orchestrator > category > core) |
| **AC-TEMPLATE-006** | Backwards Compatibility Layer | 2 | Support v4.yaml during migration period (2-week window) |
| **AC-TEMPLATE-007** | Migrate Core Orchestrators | 3 | Migrate 10 core orchestrators + validate all 40+ |
| **AC-TEMPLATE-008** | Delete v4.yaml After Validation | 3 | Remove v4.yaml after all orchestrators validated |

---

## 🎯 Targets & Guarantees

| Metric | Current | Target | Delta |
|--------|---------|--------|-------|
| **Total Lines** | 2046 | <300 | **-86%** |
| **Render Time** | ~80ms | <50ms | **-38%** |
| **Duplication** | ~45% | 0% | **-45%** |
| **Consistency** | ~70% | 100% | **+30%** |
| **Maintenance Events/Month** | ~8 | <2 | **-75%** |

---

## 🏗️ Implementation Phases

### **Phase 1: Foundation (Week 1)**
**AC-IDs:** AC-TEMPLATE-001, AC-TEMPLATE-002, AC-TEMPLATE-003

**Deliverables:**
- `cortex-brain/tier0/response-blocks.yaml` (50 lines)
- Block schema validator
- ResponseRenderer block loader with caching

**Tests:**
- `tests/response_templates/test_core_blocks.py`
- `tests/response_templates/test_block_schema.py`
- `tests/response_templates/test_renderer_loader.py`

### **Phase 2: Categories (Week 2)**
**AC-IDs:** AC-TEMPLATE-004, AC-TEMPLATE-005, AC-TEMPLATE-006

**Deliverables:**
- 5 category templates (core, integration, maintenance, conversion, security)
- Inheritance resolver (precedence engine)
- Backwards compatibility layer (v4.yaml fallback)

**Tests:**
- `tests/response_templates/test_category_templates.py`
- `tests/response_templates/test_inheritance_resolver.py`
- `tests/response_templates/test_backwards_compat.py`

### **Phase 3: Migration (Week 3-4)**
**AC-IDs:** AC-TEMPLATE-007, AC-TEMPLATE-008

**Deliverables:**
- 10 core orchestrators migrated (Planning, TDD, ADO, Investigation, Vacuum, Cleanup, Sanitization, Debug, Refinement, MasterOrchestrator)
- All 40+ orchestrators validated
- Performance benchmarks met
- **response-templates-v4.yaml DELETED** ✂️

**Tests:**
- `tests/integration/test_orchestrator_migration.py`
- `tests/integration/test_full_migration.py`

---

## 🔗 Integration with MasterOrchestrator

### **Flow:**
```
handle_request() → execute_orchestrator() → OrchestratorResult
    ↓
ResponseRenderer.render()
    ↓
1. Load core blocks (tier0/response-blocks.yaml)
2. Load category template (tier2/response-templates/{category}.yaml)
3. Load orchestrator overrides (manifests/{orch}/response_config)
4. Merge with precedence: orchestrator > category > core
5. Compose blocks per work breakdown structure
6. Return markdown
```

### **Location:**
- `src/orchestrators/response_renderer.py` (line 99)

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation | Timeline |
|------|--------|------------|----------|
| Breaking existing rendering | HIGH | Phased migration + backwards compat flag | 2-week window |
| Category assignment conflicts | MEDIUM | Multi-category inheritance support | Audit logs track resolution |
| Testing overhead (40+ orchestrators) | MEDIUM | Auto-generate test matrix from registry | AC-TEMPLATE-007 |

---

## 🛡️ Governance Alignment

**CORE Rules Enforced:**
- **CORE-002:** Anti-bloat (<300 lines total)
- **CORE-008:** TDD enforcement (all AC-IDs have tests)
- **CORE-019:** TDD-Master required for implementation

**Audit Trail:**
- Category: INFRASTRUCTURE
- Retention: 30 days (INFO level)
- All operations logged to EnterpriseAuditLogger

**Evidence Bundle Requirements:**
- Location: `cortex-brain/tier1/evidence-bundles/AC-TEMPLATE-*/`
- Contents: manifest.yaml, test_results.json, performance_metrics.json, audit_trace.jsonl
- Validation: Test coverage ≥80%, performance <50ms, CORE-002 enforced

---

## 📈 Impact on Plan Metrics

### **Before:**
- Total AC-IDs: 102
- Phase 2 components: 5
- Total template lines: 2046

### **After:**
- Total AC-IDs: **111** (+9)
- Phase 2 components: **6** (+1)
- Total template lines: **<300** (-86%)

### **Design Score:**
Maintained at **97/100** (no impact - this is a refactoring enhancement)

---

## 🗂️ File Locations

### **Plan Documents:**
- **Full Plan:** `cortex-brain/tier1/acceptance-criteria/TEMPLATE-ARCHITECTURE-PLAN.yaml`
- **Approval Doc:** `cortex-brain/tier1/tracking/TEMPLATE-ARCHITECTURE-APPROVED.md`
- **Mermaid Diagram:** `cortex-brain/documents/cx6-holistic-analysis/response-template-architecture.mmd`

### **Master Plans Updated:**
- `cortex-brain/documents/cx6-holistic-analysis/holistic-snowball-plan.yaml` (v1.1.0)
- `cortex-brain/documents/cx6-holistic-analysis/4-week-implementation-plan.yaml`

### **Tracking:**
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` (schema 1.7)
- `cortex-brain/tier1/tracking/progress-tracker.json`

### **Viewer:**
- `templates/plan-viewer/cortex-plan-viewer.html` (updated with visual highlighting)

---

## 📅 Timeline

| Milestone | Date | Status |
|-----------|------|--------|
| Plan Created | 2026-01-10 | ✅ Complete |
| AC-IDs Registered | 2026-01-10 | ✅ Complete |
| Plan Documents Updated | 2026-01-10 | ✅ Complete |
| Viewer Updated | 2026-01-10 | ✅ Complete |
| **Implementation Start** | **2026-01-13** | ⏳ Scheduled |
| Phase 1 Complete | 2026-01-20 | ⏳ Planned |
| Phase 2 Complete | 2026-01-27 | ⏳ Planned |
| Phase 3 Complete | 2026-02-10 | ⏳ Planned |
| **Cutover Date (v4 deletion)** | **2026-02-28** | ⏳ Planned |

---

## ✅ Approval Status

**Status:** ✅ APPROVED  
**Approved By:** Asif Hussain  
**Approval Date:** 2026-01-10  
**Implementation Confidence:** VERY HIGH (97/100 design score)

---

## 🔍 Visual Representation

See Mermaid diagram: `cortex-brain/documents/cx6-holistic-analysis/response-template-architecture.mmd`

**Diagram shows:**
- Problem (v4.yaml bloat)
- Solution (3-layer architecture)
- Layer details and precedence
- Implementation phases
- Targets and evidence bundles

---

## 📝 Notes

- This is a **refactoring enhancement** that improves maintainability without changing functionality
- **No breaking changes** during 2-week backwards compatibility window
- All 40+ orchestrators will be validated before v4.yaml deletion
- Evidence bundles required for all 8 AC-IDs (test coverage, performance, governance compliance)

---

**Last Updated:** 2026-01-10T17:30:00Z  
**Document Version:** 1.0  
**Status:** Ready for Implementation
