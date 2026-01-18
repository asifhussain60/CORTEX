# PHASE-21 Implementation Guide
## Intelligent Knowledge Protocol: Unified Access, Smart Routing & Bulk Ingestion

**Date**: 2026-01-18  
**Status**: IN_PROGRESS  
**Total ACs**: 15 (expanded from 8)  
**Estimated Hours**: 76 hours (39 base + 37 extension)  
**Estimated Tests**: 220 tests  

---

## Executive Summary

PHASE-21 has been expanded to include **7 additional AC-IDs** providing extended knowledge services beyond the core functionality:

- **AC-IKP-004-02**: Ingestion Integration (2 hours) - formerly RefinementEngine
- **AC-IKP-004-03**: Repository Integration (2 hours) - **NEW**
- **AC-IKP-005-02**: Knowledge Query Optimization (6 hours) - **NEW**
- **AC-IKP-005-03**: Knowledge Update Propagation (4 hours) - **NEW**
- **AC-IKP-005-04**: Knowledge Versioning & History (5 hours) - **NEW**
- **AC-IKP-005-05**: Knowledge Search & Discovery (6 hours) - **NEW**
- **AC-IKP-005-06**: Knowledge Recommendations (5 hours) - **NEW**
- **AC-IKP-005-07**: Knowledge Analytics & Reporting (4 hours) - **NEW**

**Total New Hours**: 37 hours  
**Total New Tests**: 112 tests  

---

## Architecture Overview

### Layer 1: Protocol & Foundation (AC-IKP-001-01, 001-02)
- **KnowledgeProvider Protocol** - typing.Protocol for structural subtyping
- **Compliance Verification** - Type-safe validation of existing repositories

### Layer 2: Intelligent Routing (AC-IKP-002-01, 002-02)
- **IntelligentKnowledgeRouter** - Query-aware delegation with confidence scoring
- **MasterOrchestrator Integration** - Replace dual-backend queries

### Layer 3: Change Detection (AC-IKP-003-01, 003-02)
- **ChangeDetectionService** - Schema drift, semantic shift, anomaly detection
- **Alert Pipeline** - Threshold configuration and notification channels

### Layer 4: Ingestion & Refinement (AC-IKP-004-01, 004-02, 004-03)
- **BulkIngestionPipeline** - Scalable data transformation with registry pattern
- **Ingestion Integration** - End-to-end workflow with RefinementEngine
- **Repository Integration** - Bulk loading into existing knowledge repositories

### Layer 5: Unified Access (AC-IKP-005-01 through 005-07)
- **UnifiedKnowledgeService** - Single entry point facade
- **Query Optimization** - Caching, indexing, performance monitoring
- **Update Propagation** - Change propagation across backends
- **Versioning & History** - Track versions with rollback support
- **Search & Discovery** - Full-text and semantic search
- **Recommendations** - Context-aware knowledge recommendations
- **Analytics & Reporting** - Usage metrics and optimization insights

---

## Implementation Schedule

### Week 1: Protocol & Router Foundation (13 hours)
| AC-ID | Title | Hours | Tests | Dependencies |
|-------|-------|-------|-------|--------------|
| AC-IKP-001-01 | KnowledgeProvider Protocol | 2 | 10 | None |
| AC-IKP-001-02 | Protocol Compliance | 1 | 8 | AC-IKP-001-01 |
| AC-IKP-002-01 | IntelligentKnowledgeRouter | 4 | 20 | AC-IKP-001-01/02 |
| AC-IKP-002-02 | MasterOrchestrator Integration | 2 | 12 | AC-IKP-002-01 |

**Deliverables**:
- `src/core/knowledge/protocols.py` - KnowledgeProvider Protocol
- `src/core/knowledge/router.py` - IntelligentKnowledgeRouter
- Updated `MasterOrchestrator` with router integration
- 50 tests passing

---

### Week 2: Change Detection & Ingestion Pipeline (26 hours)
| AC-ID | Title | Hours | Tests | Dependencies |
|-------|-------|-------|-------|--------------|
| AC-IKP-003-01 | ChangeDetectionService | 6 | 25 | AC-IKP-001-01/02 |
| AC-IKP-003-02 | Alert Pipeline | 2 | 10 | AC-IKP-003-01 |
| AC-IKP-004-01 | BulkIngestionPipeline | 8 | 30 | None |
| AC-IKP-004-02 | Ingestion Integration | 2 | 15 | AC-IKP-004-01 |
| AC-IKP-004-03 | Repository Integration | 2 | 12 | AC-IKP-004-02 |

**Deliverables**:
- `src/core/knowledge/change_detection.py` - Change detection engine
- `src/core/knowledge/ingestion/` - Complete pipeline package
- `src/core/knowledge/ingestion/pipeline.py` - BulkIngestionPipeline
- Integration with existing repositories
- 85 tests passing

---

### Week 3: Unified Services & Extensions (37 hours)
| AC-ID | Title | Hours | Tests | Dependencies |
|-------|-------|-------|-------|--------------|
| AC-IKP-005-01 | UnifiedKnowledgeService | 4 | 15 | AC-IKP-002-01 |
| AC-IKP-005-02 | Query Optimization | 6 | 18 | AC-IKP-005-01 |
| AC-IKP-005-03 | Update Propagation | 4 | 14 | AC-IKP-005-01 |
| AC-IKP-005-04 | Versioning & History | 5 | 16 | AC-IKP-005-01 |
| AC-IKP-005-05 | Search & Discovery | 6 | 20 | AC-IKP-005-01 |
| AC-IKP-005-06 | Recommendations | 5 | 17 | AC-IKP-005-01 |
| AC-IKP-005-07 | Analytics & Reporting | 4 | 12 | AC-IKP-005-01 |

**Deliverables**:
- `src/core/knowledge/unified_service.py` - Facade pattern
- `src/core/knowledge/query_optimizer.py` - Caching & indexing
- `src/core/knowledge/update_propagation.py` - Change propagation
- `src/core/knowledge/versioning.py` - Version management
- `src/core/knowledge/search_engine.py` - Full-text & semantic search
- `src/core/knowledge/recommendations.py` - Recommendations engine
- `src/core/knowledge/analytics.py` - Metrics & reporting
- Full integration tests
- 220 total tests passing

---

## AC-ID Details & Success Criteria

### AC-IKP-004-02: Ingestion Integration (2 hours)

**Objective**: Connect RefinementEngine with BulkIngestionPipeline for end-to-end workflow.

**Description**:
- Integrate RefinementEngine with BulkIngestionPipeline
- Connect intake adapters to refinement rules to storage backends
- Implement end-to-end ingestion workflow with error handling
- Support both batch and streaming modes

**Success Criteria**:
- [ ] Ingestion integrated with refinement engine
- [ ] End-to-end workflow works correctly
- [ ] Error handling and recovery mechanisms implemented
- [ ] Both batch and streaming modes supported
- [ ] 15 unit tests passing
- [ ] 5 integration tests passing

**Files to Create**:
- `src/core/knowledge/ingestion/refinement_adapter.py` - Adapter connecting pipeline to refinement
- `tests/unit/core/knowledge/test_ingestion_pipeline.py` - Pipeline tests

**Files to Modify**:
- `src/core/knowledge/ingestion/pipeline.py` - Add refinement stage

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-004-03: Repository Integration (2 hours)

**Objective**: Integrate BulkIngestionPipeline with existing KnowledgeRepository and BusinessKnowledgeRepository.

**Description**:
- Integrate BulkIngestionPipeline with existing KnowledgeRepository
- Integrate BulkIngestionPipeline with BusinessKnowledgeRepository
- Enable bulk loading of company policies, technical specs, domain knowledge
- Track ingestion metrics and audits
- Support incremental and full-refresh ingestion modes

**Success Criteria**:
- [ ] Pipeline integrated with KnowledgeRepository
- [ ] Pipeline integrated with BusinessKnowledgeRepository
- [ ] Bulk loading operational for all knowledge types
- [ ] Ingestion metrics tracked and logged
- [ ] Audit trail captured for all ingestions
- [ ] 12 unit tests passing
- [ ] 4 integration tests passing

**Files to Create**:
- `src/core/knowledge/ingestion/repository_adapter.py` - Repository adapters
- `tests/unit/core/knowledge/test_ingestion_repository_integration.py` - Integration tests

**Files to Modify**:
- `src/core/knowledge/ingestion/pipeline.py` - Add repository storage backends

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-02: Knowledge Query Optimization (6 hours)

**Objective**: Implement query result caching, indexing, and performance optimization.

**Description**:
- Implement query result caching with TTL-based invalidation
- Create knowledge indices for common query patterns
- Add query performance monitoring and metrics
- Provide optimization recommendations based on usage patterns
- Support complex queries with joins across backends

**Success Criteria**:
- [ ] Query result caching implemented and effective
- [ ] Indices created for common query patterns
- [ ] Performance monitoring integrated
- [ ] Optimization recommendations generated
- [ ] Complex query joins supported
- [ ] 18 unit tests passing
- [ ] 5 integration tests passing

**Files to Create**:
- `src/core/knowledge/query_optimizer.py` - Query optimization engine
- `src/core/knowledge/query_cache.py` - Caching layer
- `src/core/knowledge/query_indexer.py` - Index management
- `tests/unit/core/knowledge/test_query_optimizer.py` - Optimizer tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-03: Knowledge Update Propagation (4 hours)

**Objective**: Implement change propagation across knowledge backends.

**Description**:
- Implement change propagation mechanism across backends
- Support incremental updates with minimal data transfer
- Support batch updates for bulk operations
- Maintain consistency across distributed backends
- Handle conflict resolution and versioning

**Success Criteria**:
- [ ] Changes propagate reliably across backends
- [ ] Incremental updates implemented
- [ ] Batch updates supported
- [ ] Consistency maintained across backends
- [ ] Conflicts detected and resolved
- [ ] 14 unit tests passing
- [ ] 4 integration tests passing

**Files to Create**:
- `src/core/knowledge/update_propagation.py` - Propagation engine
- `src/core/knowledge/conflict_resolution.py` - Conflict handling
- `tests/unit/core/knowledge/test_update_propagation.py` - Propagation tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-04: Knowledge Versioning & History (5 hours)

**Objective**: Track knowledge versions with metadata and support rollback.

**Description**:
- Track knowledge versions with comprehensive metadata
- Support rollback to previous versions
- Maintain complete audit trail for all changes
- Implement version branching for experimental knowledge
- Support semantic versioning

**Success Criteria**:
- [ ] Versioning system implemented
- [ ] Version metadata captured (author, timestamp, reason)
- [ ] Rollback functionality works reliably
- [ ] Audit trail complete and comprehensive
- [ ] Version branching supported
- [ ] 16 unit tests passing
- [ ] 5 integration tests passing

**Files to Create**:
- `src/core/knowledge/versioning.py` - Versioning engine
- `src/core/knowledge/version_store.py` - Version storage
- `tests/unit/core/knowledge/test_versioning.py` - Versioning tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-05: Knowledge Search & Discovery (6 hours)

**Objective**: Implement full-text and semantic search capabilities.

**Description**:
- Implement full-text search across all knowledge backends
- Support semantic search using embedding similarity
- Provide faceted search and filtering capabilities
- Implement search result ranking and relevance scoring
- Support search query expansion and normalization

**Success Criteria**:
- [ ] Full-text search implemented and fast
- [ ] Semantic search functional with embeddings
- [ ] Faceted search and filtering working
- [ ] Results ranked by relevance
- [ ] Search query expansion working
- [ ] 20 unit tests passing
- [ ] 6 integration tests passing

**Files to Create**:
- `src/core/knowledge/search_engine.py` - Search engine
- `src/core/knowledge/semantic_search.py` - Semantic search layer
- `src/core/knowledge/search_indexer.py` - Search indexing
- `tests/unit/core/knowledge/test_search_engine.py` - Search tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-06: Knowledge Recommendations (5 hours)

**Objective**: Recommend relevant knowledge based on operation context.

**Description**:
- Recommend relevant knowledge based on operation context
- Learn from user behavior to improve recommendations
- Integrate with MasterOrchestrator for contextual suggestions
- Support personalized recommendations per user
- Implement recommendation confidence scoring

**Success Criteria**:
- [ ] Recommendations generated accurately
- [ ] Behavioral learning implemented
- [ ] MasterOrchestrator integration complete
- [ ] Personalization working
- [ ] Confidence scoring accurate
- [ ] 17 unit tests passing
- [ ] 5 integration tests passing

**Files to Create**:
- `src/core/knowledge/recommendations.py` - Recommendations engine
- `src/core/knowledge/behavioral_learner.py` - Behavior learning
- `tests/unit/core/knowledge/test_recommendations.py` - Recommendation tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

### AC-IKP-005-07: Knowledge Analytics & Reporting (4 hours)

**Objective**: Track knowledge usage metrics and generate insights.

**Description**:
- Track knowledge usage metrics and patterns
- Generate reports on knowledge effectiveness
- Provide insights for knowledge base optimization
- Implement dashboard metrics collection
- Support custom analytics queries

**Success Criteria**:
- [ ] Metrics tracked and stored
- [ ] Effectiveness reports generated
- [ ] Optimization insights provided
- [ ] Dashboard metrics available
- [ ] Custom query support implemented
- [ ] 12 unit tests passing
- [ ] 4 integration tests passing

**Files to Create**:
- `src/core/knowledge/analytics.py` - Analytics engine
- `src/core/knowledge/metrics_collector.py` - Metrics collection
- `src/core/knowledge/reporting.py` - Report generation
- `tests/unit/core/knowledge/test_analytics.py` - Analytics tests

**Type Hints**: Mandatory (CORE-011)  
**Docstrings**: Google style (CORE-012)  
**Exception Handling**: Specific (CORE-013)  

---

## Governance Compliance

All ACs must comply with:

| Rule | Requirement | Status |
|------|-------------|--------|
| **CORE-008** | TDD (tests first, RED → GREEN) | ✅ Required |
| **CORE-011** | Type hints mandatory | ✅ Required |
| **CORE-012** | Google-style docstrings | ✅ Required |
| **CORE-013** | Specific exception handling | ✅ Required |
| **CORE-027** | Audit trail (AC_START → AC_EXECUTE → AC_COMPLETE) | ✅ Required |
| **CORE-028** | Kebab-case filenames, <25 chars | ✅ Required |

---

## Testing Strategy

### Unit Tests
- **Target**: 190 tests total
- **Framework**: pytest
- **Coverage**: >90% code coverage per module
- **Isolation**: Use mocks for external dependencies

### Integration Tests
- **Target**: 30 tests total
- **Scope**: Full workflows, multi-module interactions
- **Data**: Use fixtures from `tests/fixtures/knowledge/`
- **Validation**: Real repository operations

### Total Test Suite
- **Expected**: 220 tests
- **Pass Rate**: 100%
- **Command**: `pytest tests/unit/core/knowledge/ tests/integration/ -v`

---

## File Structure

```
src/core/knowledge/
├── __init__.py
├── protocols.py                 # AC-IKP-001-01
├── router.py                    # AC-IKP-002-01
├── change_detection.py          # AC-IKP-003-01
├── unified_service.py           # AC-IKP-005-01
├── query_optimizer.py           # AC-IKP-005-02
├── update_propagation.py        # AC-IKP-005-03
├── versioning.py                # AC-IKP-005-04
├── search_engine.py             # AC-IKP-005-05
├── recommendations.py           # AC-IKP-005-06
├── analytics.py                 # AC-IKP-005-07
└── ingestion/
    ├── __init__.py
    ├── intake.py                # Intake adapters
    ├── filters.py               # Filter strategies
    ├── refinement.py            # Refinement rules
    ├── transformers.py          # Data transformers
    ├── validators.py            # Validation logic
    ├── pipeline.py              # AC-IKP-004-01, 004-02, 004-03
    └── __init__.py

tests/unit/core/knowledge/
├── test_protocols.py
├── test_router.py
├── test_change_detection.py
├── test_ingestion_pipeline.py
├── test_unified_service.py
├── test_query_optimizer.py
├── test_update_propagation.py
├── test_versioning.py
├── test_search_engine.py
├── test_recommendations.py
└── test_analytics.py

tests/integration/
├── test_unified_knowledge_service.py
├── test_ingestion_repository_integration.py
└── test_knowledge_end_to_end.py
```

---

## Execution Checklist

- [ ] **Pre-Implementation**
  - [ ] Read cortex-builder.prompt.md for unified phase workflow
  - [ ] Verify cortex-master.yaml consolidation is complete
  - [ ] Run `python3 scripts/validation/validate_phase_sync.py` - should pass
  - [ ] Review existing KnowledgeRepository and BusinessKnowledgeRepository code
  - [ ] Understand MasterOrchestrator architecture
  - [ ] Review orchestrator_traits.py Protocol pattern

- [ ] **Week 1: Protocol & Router**
  - [ ] AC-IKP-001-01: KnowledgeProvider Protocol (10 tests passing)
  - [ ] AC-IKP-001-02: Protocol Compliance (8 tests passing)
  - [ ] AC-IKP-002-01: IntelligentKnowledgeRouter (20 tests passing)
  - [ ] AC-IKP-002-02: MasterOrchestrator Integration (12 tests passing)
  - [ ] Total: 50 tests passing

- [ ] **Week 2: Detection & Ingestion**
  - [ ] AC-IKP-003-01: ChangeDetectionService (25 tests passing)
  - [ ] AC-IKP-003-02: Alert Pipeline (10 tests passing)
  - [ ] AC-IKP-004-01: BulkIngestionPipeline (30 tests passing)
  - [ ] AC-IKP-004-02: Ingestion Integration (15 tests passing)
  - [ ] AC-IKP-004-03: Repository Integration (12 tests passing)
  - [ ] Total: 85 tests passing (cumulative: 135)

- [ ] **Week 3: Unified Services**
  - [ ] AC-IKP-005-01: UnifiedKnowledgeService (15 tests passing)
  - [ ] AC-IKP-005-02: Query Optimization (18 tests passing)
  - [ ] AC-IKP-005-03: Update Propagation (14 tests passing)
  - [ ] AC-IKP-005-04: Versioning & History (16 tests passing)
  - [ ] AC-IKP-005-05: Search & Discovery (20 tests passing)
  - [ ] AC-IKP-005-06: Recommendations (17 tests passing)
  - [ ] AC-IKP-005-07: Analytics & Reporting (12 tests passing)
  - [ ] Total: 112 tests passing (cumulative: 220)

- [ ] **Post-Implementation**
  - [ ] Run full test suite: `pytest tests/ -v` - 220/220 passing
  - [ ] Run validator: `python3 scripts/validation/validate_phase_sync.py --verbose`
  - [ ] Update cortex-master.yaml: set status: COMPLETED for each AC
  - [ ] Update cortex-master.yaml: set locked: true for PHASE-21 when complete
  - [ ] Commit to git with audit trail
  - [ ] Create phase completion report

---

## Reference Implementations

### Example: KnowledgeProvider Protocol (AC-IKP-001-01)

```python
"""KnowledgeProvider Protocol Definition"""
from typing import Protocol, List, Optional, Any, Dict

class KnowledgeProvider(Protocol):
    """Structural protocol for knowledge backend implementations."""
    
    @property
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded."""
        ...
    
    @property
    def entry_count(self) -> int:
        """Get number of knowledge entries."""
        ...
    
    @property
    def domains(self) -> List[str]:
        """Get list of knowledge domains."""
        ...
    
    def query(self, query_text: str) -> List[Dict[str, Any]]:
        """Query knowledge with natural language."""
        ...
    
    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all knowledge for a specific domain."""
        ...
    
    def get_relevant_knowledge(
        self, 
        intent_type: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get knowledge relevant to current operation."""
        ...
```

---

## Next Steps

1. Begin Week 1 implementation with AC-IKP-001-01 (KnowledgeProvider Protocol)
2. Follow TDD pattern: RED → GREEN → REFACTOR
3. Update AC status in cortex-master.yaml after each completion
4. Run validator after each day to ensure consistency
5. Create audit trail entries for each AC execution
6. Document lessons learned and patterns in tier2 knowledge base

---

## Support & Questions

Refer to:
- `cortex-builder.prompt.md` - Phase execution workflow
- `docs/cortex-review-enhanced.prompt.md` - Architecture patterns
- `cortex-brain/tier0/governance/core-rules.yaml` - Governance rules
- `cortex-brain/tier1/acceptance-criteria/` - AC templates
- Existing test files for reference implementations

---

**Document Generated**: 2026-01-18  
**Author**: cortex-builder  
**Phase**: PHASE-21  
**Status**: READY FOR IMPLEMENTATION
