# CORTEX Knowledge Integration - Gap Analysis Report

**Report ID:** GAP-KN-002  
**Date:** 2026-01-18  
**Analyst:** CORTEX Builder  
**Status:** Analysis Complete - Action Required

---

## Executive Summary

Analysis of the knowledge integration wiring reveals **3 critical gaps** and **5 enhancement opportunities**. The technical knowledge repository (KnowledgeRepository) is well-integrated into MasterOrchestrator with 30 tests, but the parallel business knowledge system (BKIO/DomainBrain) lacks equivalent structured storage for future enhancements.

---

## Current State Assessment

### ✅ Technical Knowledge Repository (COMPLETE)

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| KnowledgeRepository class | ✅ LIVE | 30 | Full |
| .knowledge-index.json | ✅ LIVE | 4 | Full |
| MasterOrchestrator integration | ✅ LIVE | 12 | Full |
| coordinate_operation knowledge eval | ✅ LIVE | 2 | Full |
| Graceful degradation | ✅ LIVE | 2 | Full |

### ✅ Business Knowledge (Domain Brain) (COMPLETE)

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| BKIO Orchestrator | ✅ LIVE | 70+ | Full |
| DomainBrainAPI | ✅ LIVE | 50+ | Full |
| Conflict Resolution | ✅ LIVE | 25 | Full |
| Document Parsing | ✅ LIVE | 20 | Full |
| Audit Trail | ✅ LIVE | 20+ | Full |
| Version Manager | ✅ LIVE | 20+ | Full |
| Orphan Detector | ✅ LIVE | 20+ | Full |
| **Total Domain Brain** | ✅ | **353** | Full |

---

## 🔴 Critical Gaps Identified

### GAP-1: No BusinessKnowledgeRepository Parallel to KnowledgeRepository

**Severity:** HIGH  
**Impact:** Future enhancement brittleness

The technical knowledge system uses `KnowledgeRepository` with `.knowledge-index.json` for fast O(1) lookups. The business knowledge system (BKIO) uses `DomainBrainAPI` with in-memory storage. This asymmetry creates:

- No persistent index for business knowledge entries
- No equivalent `get_relevant_business_knowledge()` method
- No domain-mapping for business knowledge queries

**Recommendation:** Create `BusinessKnowledgeRepository` parallel to `KnowledgeRepository`

---

### GAP-2: BKIO Not Wired to MasterOrchestrator coordinate_operation

**Severity:** MEDIUM  
**Impact:** Business knowledge not evaluated during request composition

`coordinate_operation()` now evaluates technical knowledge via `_evaluate_knowledge_for_request()`, but does NOT evaluate business domain knowledge from BKIO/DomainBrain.

**Current Flow:**
```
coordinate_operation()
├── Governance validation ✅
├── Boundary enforcement ✅  
├── Technical knowledge evaluation ✅  <- KnowledgeRepository
├── Business knowledge evaluation ❌  <- MISSING
└── Domain orchestrator delegation
```

**Recommendation:** Add `_evaluate_business_knowledge_for_request()` method

---

### GAP-3: Missing Integration Test for BKIO → MasterOrchestrator Registration

**Severity:** MEDIUM  
**Impact:** Potential brittleness in orchestrator wiring

While BKIO has 70+ unit tests, there's no integration test verifying:
- BKIO registration in MasterOrchestrator's domain_orchestrators
- BKIO invocation through coordinate_operation
- BKIO knowledge contribution to composite requests

**Recommendation:** Add integration tests for BKIO registration and wiring

---

## 🟡 Enhancement Opportunities

### ENH-1: Unified Knowledge Query Interface

Create a unified interface that queries BOTH technical and business knowledge:

```python
def get_all_relevant_knowledge(operation, context):
    technical = self._knowledge_repository.get_relevant_knowledge(...)
    business = self._business_knowledge_repository.get_relevant_knowledge(...)
    return merge_and_rank(technical, business)
```

---

### ENH-2: Knowledge Version Tracking in Composite Requests

Track which knowledge version/entries were used in each request:

```python
aggregated = {
    "knowledge_context": {
        "technical_entries_used": ["KB-ARC-001", "KB-SEC-003"],
        "business_domains_consulted": ["payments", "compliance"],
        "knowledge_version": "1.0.35"
    }
}
```

---

### ENH-3: Hot-Reload for Knowledge Updates

Add ability to refresh knowledge without restart:

```python
def reload_knowledge(self):
    self._knowledge_repository.reload()
    self._business_knowledge_repository.reload()
```

---

### ENH-4: Knowledge Relevance Scoring

Implement TF-IDF or embedding-based relevance scoring instead of keyword matching.

---

### ENH-5: Knowledge Audit Trail

Log which knowledge entries influenced each decision:

```python
self.logger.log_operation_complete(
    ac_id="AC-KN-002-01",
    operation="KNOWLEDGE_APPLIED",
    details={
        "entries_applied": [...],
        "confidence_scores": {...}
    }
)
```

---

## Test Harness Status

### Current Test Coverage

| Test File | Tests | Status |
|-----------|-------|--------|
| test_master_orchestrator_knowledge.py | 30 | ✅ All Pass |
| test_ac_db_003_01.py (BKIO) | 70 | ✅ All Pass |
| test_master_orchestrator.py | 16 | ✅ All Pass |
| test_orchestrator_registry.py | ~50 | ✅ All Pass |
| test_hallucination_remediation.py | 22 | ✅ All Pass |
| tests/unit/domain_brain/*.py | 353 | ✅ All Pass |

### Missing Test Coverage (Gaps)

| Missing Test | Priority | Gap |
|--------------|----------|-----|
| BKIO → MasterOrchestrator registration | HIGH | GAP-3 |
| Business knowledge in coordinate_operation | HIGH | GAP-2 |
| Unified knowledge query | MEDIUM | ENH-1 |
| Knowledge reload | LOW | ENH-3 |

---

## Recommended Implementation Order

### Phase 1: Address Critical Gaps (Estimated: 4h)

1. **Create BusinessKnowledgeRepository** (GAP-1)
   - Mirror KnowledgeRepository structure
   - Add `.business-knowledge-index.json`
   - Add domain-based queries
   - 15 tests

2. **Wire to MasterOrchestrator** (GAP-2)
   - Add `_business_knowledge_repository` attribute
   - Add `_evaluate_business_knowledge_for_request()`
   - Include in coordinate_operation flow
   - 10 tests

3. **BKIO Integration Tests** (GAP-3)
   - Test BKIO registration
   - Test BKIO in coordinate_operation
   - 5 tests

### Phase 2: Enhancements (Estimated: 6h)

1. Unified query interface (ENH-1)
2. Version tracking (ENH-2)
3. Hot reload (ENH-3)
4. Relevance scoring (ENH-4) - Optional
5. Knowledge audit (ENH-5)

---

## Architecture Diagram

### Current State
```
┌─────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                       │
├─────────────────────────────────────────────────────────────┤
│  _governance_registry      ─── GovernanceRegistry           │
│  _boundary_rules           ─── BehavioralBoundaryRules      │
│  _knowledge_repository     ─── KnowledgeRepository    ✅    │
│  _business_knowledge_repo  ─── ???                    ❌    │
│  domain_orchestrators      ─── Dict[str, IOrchestrator]     │
│                                ├── BKIO  (NOT REGISTERED)   │
│                                └── Others                   │
└─────────────────────────────────────────────────────────────┘
```

### Target State
```
┌─────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                       │
├─────────────────────────────────────────────────────────────┤
│  _governance_registry      ─── GovernanceRegistry           │
│  _boundary_rules           ─── BehavioralBoundaryRules      │
│  _knowledge_repository     ─── KnowledgeRepository    ✅    │
│  _business_knowledge_repo  ─── BusinessKnowledgeRepo  ✅    │
│  domain_orchestrators      ─── Dict[str, IOrchestrator]     │
│                                ├── BKIO  (REGISTERED)  ✅   │
│                                └── Others                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Files to Create/Modify

### Create:
- `src/domain_brain/business_knowledge_repository.py`
- `cortex-brain/tier3/business-knowledge/.business-knowledge-index.json`
- `tests/integration/test_bkio_master_orchestrator.py`

### Modify:
- `src/orchestrators/core/master_orchestrator.py` (add business knowledge)
- `tests/integration/test_master_orchestrator_knowledge.py` (add unified tests)

---

**Report End**

**Next Action:** Implement GAP-1, GAP-2, GAP-3 to ensure zero brittleness in knowledge integration wiring.
