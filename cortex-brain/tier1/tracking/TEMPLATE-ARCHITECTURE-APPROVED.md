# 3-Layer Response Template Architecture - APPROVED

**Plan ID:** template-architecture-refactor-2026-01  
**Status:** ✅ APPROVED  
**Priority:** P0-CRITICAL  
**Created:** 2026-01-10  
**Implementation Start:** 2026-01-13  
**Target Completion:** 2026-02-07  
**Cutover Date:** 2026-02-28

---

## ✅ DECISION: Option A Accepted

**Recommendation accepted:** 3-layer hybrid architecture over per-orchestrator templates (Option B) or status quo (Option C).

---

## 📋 Executive Summary

### Problem
- **Current:** response-templates-v4.yaml = 2046 lines
- **Violation:** CORE-002 anti-bloat principle
- **Risk:** Maintenance burden, duplication, inconsistency

### Solution
**3-layer composition with precedence:**
1. **Layer 1:** Core blocks (tier0/response-blocks.yaml, 50 lines)
2. **Layer 2:** Category templates (tier2/response-templates/{category}.yaml, 50 lines each)
3. **Layer 3:** Orchestrator overrides (manifests/{orch}/response_config, 15 lines)

**Precedence:** Orchestrator > Category > Core

### Guarantees
- **Total lines:** <300 (down from 2046) — **86% reduction**
- **Render time:** <50ms
- **Duplication:** 0%
- **Consistency:** 100%
- **Maintenance:** <2 events/month

---

## 📊 Acceptance Criteria

| AC-ID | Title | Priority | Phase | Status |
|-------|-------|----------|-------|--------|
| **AC-TEMPLATE-001** | Extract Core Blocks | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-002** | Block Schema Validation | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-003** | ResponseRenderer Block Loader | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-004** | Create Category Templates | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-005** | Category Inheritance Resolver | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-006** | Backwards Compatibility Layer | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-007** | Migrate Core Orchestrators | P1-HIGH | 2 | Not Started |
| **AC-TEMPLATE-008** | Delete v4.yaml After Validation | P1-HIGH | 2 | Not Started |

**Total:** 8 AC-IDs registered in AC-INDEX.yaml

---

## 🏗️ Implementation Phases

### Phase 1: Foundation (Week 1)
**AC-IDs:** AC-TEMPLATE-001, AC-TEMPLATE-002, AC-TEMPLATE-003

**Deliverables:**
- `cortex-brain/tier0/response-blocks.yaml` (50 lines)
- Block schema validator
- ResponseRenderer block loader with caching (<5ms load)

**Tests:**
- `tests/response_templates/test_core_blocks.py`
- `tests/response_templates/test_block_schema.py`
- `tests/response_templates/test_renderer_loader.py`

### Phase 2: Categories (Week 2)
**AC-IDs:** AC-TEMPLATE-004, AC-TEMPLATE-005, AC-TEMPLATE-006

**Deliverables:**
- 5 category templates (core, integration, maintenance, conversion, security)
- Inheritance resolver (precedence engine)
- Backwards compatibility layer (v4.yaml fallback)

**Tests:**
- `tests/response_templates/test_category_templates.py`
- `tests/response_templates/test_inheritance_resolver.py`
- `tests/response_templates/test_backwards_compat.py`

### Phase 3: Migration (Week 3-4)
**AC-IDs:** AC-TEMPLATE-007, AC-TEMPLATE-008

**Deliverables:**
- 10 core orchestrators migrated (Planning, TDD, ADO, Investigation, Vacuum, Cleanup, Sanitization, Debug, Refinement, MasterOrchestrator)
- All 40+ orchestrators validated
- Performance benchmarks met
- **response-templates-v4.yaml DELETED**

**Tests:**
- `tests/integration/test_orchestrator_migration.py`
- `tests/integration/test_full_migration.py`

---

## 🎯 Architecture Integration

### Master Orchestrator Flow
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

### Category Taxonomy
| Category | Orchestrators | Lines |
|----------|---------------|-------|
| **core.yaml** | Planning, TDD, Investigation | 40 |
| **integration.yaml** | ADO, Git, External APIs | 40 |
| **maintenance.yaml** | Vacuum, Cleanup, Sanitization | 40 |
| **conversion.yaml** | Data transformation | 40 |
| **security.yaml** | Security formatting | 40 |

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation | Timeline |
|------|--------|------------|----------|
| Breaking existing rendering | HIGH | Phased migration + backwards compat | 2 weeks |
| Category assignment conflicts | MEDIUM | Multi-category inheritance | Audit logs |
| Testing overhead | MEDIUM | Auto-generate test matrix | AC-TEMPLATE-007 |

---

## 📏 Success Metrics

| Metric | Target | Current | Delta |
|--------|--------|---------|-------|
| Total template lines | <300 | 2046 | **-86%** |
| Response render time | <50ms | ~80ms | **-38%** |
| Consistency score | 100% | ~70% | **+30%** |
| Maintenance events/month | <2 | ~8 | **-75%** |
| Orchestrator duplication | 0% | ~45% | **-45%** |

---

## 🛡️ Governance Alignment

**CORE Rules:**
- **CORE-002:** Anti-bloat enforced (<300 lines total)
- **CORE-008:** TDD enforcement (all AC-IDs have tests)
- **CORE-019:** TDD-Master required for implementation

**Audit Trail:**
- Category: INFRASTRUCTURE
- Retention: 30 days (INFO level)
- All operations logged to EnterpriseAuditLogger

**Evidence Bundles:**
- Location: `cortex-brain/tier1/evidence-bundles/AC-TEMPLATE-*/`
- Contents: manifest.yaml, test_results.json, performance_metrics.json, audit_trace.jsonl

---

## 📦 Deliverables

1. ✅ **Plan document:** `cortex-brain/tier1/acceptance-criteria/TEMPLATE-ARCHITECTURE-PLAN.yaml`
2. ✅ **AC-IDs registered:** AC-INDEX.yaml updated (8 new AC-IDs)
3. ✅ **Progress tracker updated:** enhancements list includes new architecture
4. 🔜 **Implementation:** Phase 1 starts 2026-01-13

**Files to create:**
- `cortex-brain/tier0/response-blocks.yaml` (50 lines)
- `cortex-brain/tier2/response-templates/core.yaml` (40 lines)
- `cortex-brain/tier2/response-templates/integration.yaml` (40 lines)
- `cortex-brain/tier2/response-templates/maintenance.yaml` (40 lines)
- `cortex-brain/tier2/response-templates/conversion.yaml` (40 lines)
- `cortex-brain/tier2/response-templates/security.yaml` (40 lines)

**Files to update:**
- `src/orchestrators/response_renderer.py` (3-layer loader)
- 40+ orchestrator manifests (add response_config)

**Files to delete:**
- `cortex-brain/response-templates-v4.yaml` (after Phase 3 validation) ✂️

---

## 🚀 Next Steps

1. **Immediate:** Review and approve TEMPLATE-ARCHITECTURE-PLAN.yaml
2. **Phase 1 Start:** 2026-01-13 (implement AC-TEMPLATE-001)
3. **Phase 2 Start:** 2026-01-20 (implement AC-TEMPLATE-004)
4. **Phase 3 Start:** 2026-01-27 (implement AC-TEMPLATE-007)
5. **Cutover:** 2026-02-28 (delete v4.yaml after all validation)

---

## 📚 References

- **Full Plan:** `cortex-brain/tier1/acceptance-criteria/TEMPLATE-ARCHITECTURE-PLAN.yaml`
- **AC Registry:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` (lines 3488+)
- **Progress Tracker:** `cortex-brain/tier1/tracking/progress-tracker.json`
- **Current v4.yaml:** `cortex-brain/response-templates-v4.yaml` (2046 lines, to be replaced)

---

**Approved By:** Asif Hussain  
**Approval Date:** 2026-01-10  
**Status:** ✅ READY FOR IMPLEMENTATION
