# PHASE-21 Implementation Kickoff Checklist
## Ready to Begin: AC-IKP-004-02, AC-IKP-004-03, AC-IKP-005+

**Phase**: PHASE-21 - Intelligent Knowledge Protocol  
**Date Started**: 2026-01-18  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Total ACs**: 15 (8 core + 7 extensions)  
**Total Hours**: 76  
**Total Tests**: 220  

---

## Pre-Implementation Verification ✅

- [x] cortex-master.yaml consolidated (single source of truth)
- [x] AC-IKP-004-02 defined: Ingestion Integration (2 hours)
- [x] AC-IKP-004-03 defined: Repository Integration (2 hours) - NEW
- [x] AC-IKP-005-02 through 005-07 defined (32 hours) - NEW
- [x] Phase metadata updated (ac_ids: 8→15, hours: 39→76)
- [x] Timeline updated with all 15 ACs
- [x] Files to create list expanded (16→33 files)
- [x] Test expectations updated (150→220 tests)
- [x] Phase tracker (phase_21_intelligent_knowledge) updated
- [x] Validation script passed: `python3 scripts/validation/validate_phase_sync.py`
- [x] Git committed: "phase-21: added AC-IKP-004-02, AC-IKP-004-03, and 7 extension ACs"
- [x] Implementation guide created
- [x] Expansion summary created

---

## Week-by-Week Breakdown

### Week 1: Protocol & Router Foundation (13 hours)
**Dependency**: None  
**Tests**: 50  
**Status**: Ready to start

#### AC-IKP-001-01: KnowledgeProvider Protocol Definition (2 hours)
- [ ] Create `src/core/knowledge/protocols.py`
- [ ] Define typing.Protocol for structural subtyping
- [ ] Add methods: is_loaded, entry_count, domains, query, get_by_domain, get_relevant_knowledge
- [ ] Create 10 unit tests
- [ ] Create 2 integration tests
- [ ] Verify all 12 tests passing

#### AC-IKP-001-02: Protocol Compliance Verification (1 hour)
- [ ] Verify KnowledgeRepository satisfies protocol
- [ ] Verify BusinessKnowledgeRepository satisfies protocol
- [ ] Add compliance tests for structural subtyping
- [ ] Create 8 unit tests
- [ ] Create 3 integration tests
- [ ] Verify all 11 tests passing

#### AC-IKP-002-01: IntelligentKnowledgeRouter Implementation (4 hours)
- [ ] Create `src/core/knowledge/router.py`
- [ ] Implement query analysis and intent detection
- [ ] Implement backend routing with confidence scoring
- [ ] Implement result aggregation
- [ ] Create 20 unit tests
- [ ] Create 5 integration tests
- [ ] Verify all 25 tests passing

#### AC-IKP-002-02: MasterOrchestrator Knowledge Integration (2 hours)
- [ ] Integrate IntelligentKnowledgeRouter into MasterOrchestrator
- [ ] Replace dual-backend parallel queries
- [ ] Implement fallback to parallel mode if confidence < threshold
- [ ] Create 12 unit tests
- [ ] Create 4 integration tests
- [ ] Verify all 16 tests passing

**Week 1 Total**: 50 tests passing ✓

---

### Week 2: Change Detection & Ingestion Pipeline (26 hours)
**Dependency**: Week 1 completion  
**Tests**: 85 (cumulative: 135)  
**Status**: Ready after Week 1

#### AC-IKP-003-01: ChangeDetectionService Implementation (6 hours)
- [ ] Create `src/core/knowledge/change_detection.py`
- [ ] Implement schema drift detection
- [ ] Implement semantic shift detection
- [ ] Implement coverage gap detection
- [ ] Implement staleness detection
- [ ] Implement volume anomaly detection
- [ ] Create 25 unit tests
- [ ] Create 6 integration tests
- [ ] Verify all 31 tests passing

#### AC-IKP-003-02: Alert Pipeline and Notification System (2 hours)
- [ ] Configure alert thresholds
- [ ] Implement notification channels
- [ ] Integrate with audit trail
- [ ] Support manual override and acknowledgment
- [ ] Create 10 unit tests
- [ ] Create 3 integration tests
- [ ] Verify all 13 tests passing

#### AC-IKP-004-01: BulkIngestionPipeline Architecture (8 hours)
- [ ] Create `src/core/knowledge/ingestion/pipeline.py`
- [ ] Design extensible pipeline: IntakeAdapter → FilterStrategy → RefinementRule → OutputFormatter → Validator → StorageBackend
- [ ] Implement registry pattern for plugin discovery
- [ ] Support batch and streaming modes
- [ ] Create 30 unit tests
- [ ] Create 8 integration tests
- [ ] Verify all 38 tests passing

#### AC-IKP-004-02: Ingestion Integration (2 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/ingestion/refinement_adapter.py`
- [ ] Integrate RefinementEngine with BulkIngestionPipeline
- [ ] Connect intake adapters to refinement rules to storage
- [ ] Implement end-to-end workflow
- [ ] Support error handling and recovery
- [ ] Create 15 unit tests
- [ ] Create 5 integration tests
- [ ] Verify all 20 tests passing

#### AC-IKP-004-03: Repository Integration (2 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/ingestion/repository_adapter.py`
- [ ] Integrate with KnowledgeRepository
- [ ] Integrate with BusinessKnowledgeRepository
- [ ] Enable bulk loading of policies, specs, knowledge
- [ ] Track ingestion metrics and audits
- [ ] Create 12 unit tests
- [ ] Create 4 integration tests
- [ ] Verify all 16 tests passing

**Week 2 Total**: 85 new tests passing (cumulative: 135) ✓

---

### Week 3: Unified Knowledge Services (37 hours)
**Dependency**: Week 2 completion  
**Tests**: 112 (cumulative: 220)  
**Status**: Ready after Week 2

#### AC-IKP-005-01: UnifiedKnowledgeService Façade (4 hours)
- [ ] Create `src/core/knowledge/unified_service.py`
- [ ] Implement single entry point wrapping IntelligentKnowledgeRouter
- [ ] Support unified query interface with source attribution
- [ ] Enable cross-backend aggregation and deduplication
- [ ] Create 15 unit tests
- [ ] Create 4 integration tests
- [ ] Verify all 19 tests passing

#### AC-IKP-005-02: Knowledge Query Optimization (6 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/query_optimizer.py`
- [ ] Implement query result caching with TTL invalidation
- [ ] Create knowledge indices for common patterns
- [ ] Add query performance monitoring
- [ ] Provide optimization recommendations
- [ ] Support complex queries with joins
- [ ] Create 18 unit tests
- [ ] Create 5 integration tests
- [ ] Verify all 23 tests passing

#### AC-IKP-005-03: Knowledge Update Propagation (4 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/update_propagation.py`
- [ ] Implement change propagation across backends
- [ ] Support incremental updates
- [ ] Support batch updates
- [ ] Maintain consistency across backends
- [ ] Handle conflict resolution
- [ ] Create 14 unit tests
- [ ] Create 4 integration tests
- [ ] Verify all 18 tests passing

#### AC-IKP-005-04: Knowledge Versioning & History (5 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/versioning.py`
- [ ] Track versions with metadata (author, timestamp, reason)
- [ ] Implement rollback functionality
- [ ] Maintain audit trail for all changes
- [ ] Support version branching
- [ ] Support semantic versioning
- [ ] Create 16 unit tests
- [ ] Create 5 integration tests
- [ ] Verify all 21 tests passing

#### AC-IKP-005-05: Knowledge Search & Discovery (6 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/search_engine.py`
- [ ] Implement full-text search
- [ ] Implement semantic search with embeddings
- [ ] Provide faceted search and filtering
- [ ] Implement result ranking and relevance scoring
- [ ] Support query expansion and normalization
- [ ] Create 20 unit tests
- [ ] Create 6 integration tests
- [ ] Verify all 26 tests passing

#### AC-IKP-005-06: Knowledge Recommendations (5 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/recommendations.py`
- [ ] Recommend knowledge based on operation context
- [ ] Learn from user behavior
- [ ] Integrate with MasterOrchestrator
- [ ] Support personalized recommendations
- [ ] Implement confidence scoring
- [ ] Create 17 unit tests
- [ ] Create 5 integration tests
- [ ] Verify all 22 tests passing

#### AC-IKP-005-07: Knowledge Analytics & Reporting (4 hours) ⭐ NEW
- [ ] Create `src/core/knowledge/analytics.py`
- [ ] Track knowledge usage metrics
- [ ] Generate effectiveness reports
- [ ] Provide optimization insights
- [ ] Implement dashboard metrics collection
- [ ] Support custom analytics queries
- [ ] Create 12 unit tests
- [ ] Create 4 integration tests
- [ ] Verify all 16 tests passing

**Week 3 Total**: 112 new tests passing (cumulative: 220) ✓

---

## Daily Implementation Pattern

### For Each AC (TDD Cycle):

1. **RED Phase** (25% time)
   - [ ] Write all test cases first
   - [ ] Run tests - all should fail
   - [ ] Commit: "ac-XXX-XX: test suite created (RED)"

2. **GREEN Phase** (50% time)
   - [ ] Implement minimum code to pass tests
   - [ ] All tests should pass
   - [ ] Commit: "ac-XXX-XX: implementation complete (GREEN)"

3. **REFACTOR Phase** (25% time)
   - [ ] Improve code quality
   - [ ] Add type hints and docstrings
   - [ ] Optimize performance
   - [ ] Commit: "ac-XXX-xx: refactored for clarity (REFACTOR)"

4. **Validation**
   - [ ] Run: `python3 scripts/validation/validate_phase_sync.py`
   - [ ] Run: `pytest tests/unit/core/knowledge/ -v`
   - [ ] Run: `pytest tests/integration/ -v`
   - [ ] Update cortex-master.yaml: AC status → COMPLETED
   - [ ] Final commit: "ac-XXX-XX: COMPLETED with audit trail"

---

## Daily Checklist Template

```
## Day X: AC-IKP-XXX-YY Implementation

**AC Title**: [Title]
**Hours Allocated**: [X hours]
**Tests Expected**: [N unit + M integration]

### Morning (TDD RED)
- [ ] Created test file: tests/unit/core/knowledge/test_XXX.py
- [ ] Wrote N unit tests (all failing - RED)
- [ ] Wrote M integration tests (all failing - RED)
- [ ] Committed: "ac-XXX-xx: test suite created (RED)"

### Afternoon (TDD GREEN)
- [ ] Created implementation: src/core/knowledge/xxx.py
- [ ] Implemented all required functionality
- [ ] All N+M tests now passing (GREEN)
- [ ] Type hints added (CORE-011)
- [ ] Docstrings added (CORE-012)
- [ ] Committed: "ac-XXX-xx: implementation complete (GREEN)"

### Evening (TDD REFACTOR)
- [ ] Code review and refactoring
- [ ] Performance optimization
- [ ] Exception handling reviewed (CORE-013)
- [ ] All tests still passing
- [ ] Committed: "ac-XXX-xx: refactored for clarity (REFACTOR)"

### Validation
- [ ] python3 scripts/validation/validate_phase_sync.py ✓
- [ ] pytest tests/unit/core/knowledge/test_XXX.py -v (all passing)
- [ ] pytest tests/integration/test_XXX_integration.py -v (all passing)
- [ ] Updated cortex-master.yaml (AC status: COMPLETED)
- [ ] Final commit with audit trail

### Metrics
- [ ] Tests passing: N/N unit + M/M integration = (N+M)/(N+M) ✓
- [ ] Code coverage: >90% ✓
- [ ] Time spent: [X.X hours] vs [X hours] allocated
```

---

## Governance Compliance Checklist

For each AC, verify:

- [ ] **CORE-008**: Tests written first (RED before GREEN)
- [ ] **CORE-011**: Type hints on all functions/methods
- [ ] **CORE-012**: Google-style docstrings (class, methods, params, returns)
- [ ] **CORE-013**: Specific exception handling (no bare except)
- [ ] **CORE-027**: Audit trail entries created (AC_START, AC_EXECUTE, AC_COMPLETE)
- [ ] **CORE-028**: Filenames kebab-case, <25 characters
- [ ] **CORE-024**: All changes logged in audit trail

---

## Integration Test Scenarios

For each AC, create integration tests covering:

1. **Happy Path**
   - Normal operation with valid inputs
   - Expected outputs produced
   - All side effects captured

2. **Error Handling**
   - Invalid inputs rejected gracefully
   - Specific exceptions raised
   - Error messages clear and helpful

3. **Edge Cases**
   - Empty inputs
   - Very large inputs
   - Concurrent operations
   - Resource constraints

4. **Integration**
   - With other modules in Phase 21
   - With MasterOrchestrator
   - With knowledge repositories
   - With audit trail system

---

## Testing Commands

```bash
# Run all Phase 21 unit tests
pytest tests/unit/core/knowledge/ -v

# Run all Phase 21 integration tests
pytest tests/integration/ -v -k "knowledge"

# Run specific AC tests
pytest tests/unit/core/knowledge/test_protocols.py -v
pytest tests/unit/core/knowledge/test_router.py -v

# Run with coverage
pytest tests/unit/core/knowledge/ --cov=src/core/knowledge --cov-report=html

# Run validation
python3 scripts/validation/validate_phase_sync.py --verbose

# Run pre-commit validation
python3 scripts/validation/validate_phase_sync.py --fix
```

---

## Expected Weekly Progress

### Week 1 Milestones
- **Day 1-2**: AC-IKP-001-01 & 001-02 complete (Protocol foundation)
- **Day 3-4**: AC-IKP-002-01 & 002-02 complete (Router integration)
- **End of Week**: 50 tests passing, ready for Week 2

### Week 2 Milestones
- **Day 1-2**: AC-IKP-003-01 & 003-02 complete (Change detection)
- **Day 3-5**: AC-IKP-004-01, 004-02, 004-03 complete (Ingestion pipeline)
- **End of Week**: 85 new tests passing (135 cumulative), ready for Week 3

### Week 3 Milestones
- **Day 1**: AC-IKP-005-01 complete (Unified facade)
- **Day 2-3**: AC-IKP-005-02, 005-03, 005-04 complete (Query, propagation, versioning)
- **Day 4-5**: AC-IKP-005-05, 005-06, 005-07 complete (Search, recommendations, analytics)
- **End of Week**: 112 new tests passing (220 cumulative), PHASE-21 COMPLETE

---

## Success Criteria - PHASE-21 Complete

- [x] All 15 AC-IDs defined and consolidated
- [ ] All 220 tests implemented and passing
- [ ] All 15 ACs implemented with COMPLETED status
- [ ] All source files created (33 files total)
- [ ] All test files created (13 test modules)
- [ ] Type hints on all functions (CORE-011)
- [ ] Google-style docstrings on all classes/methods (CORE-012)
- [ ] Specific exception handling throughout (CORE-013)
- [ ] Audit trail entries for all 15 ACs (CORE-027)
- [ ] All filenames kebab-case, <25 chars (CORE-028)
- [ ] cortex-master.yaml updated: PHASE-21 locked: true
- [ ] Phase tracker entry updated: all ACs COMPLETED
- [ ] Git history clean with 45+ commits (3 per AC)
- [ ] Phase completion report generated
- [ ] Ready to proceed to PHASE-22 (MCP Protocol Compliance)

---

## Resources & References

📚 **Documentation**:
- `cortex-builder.prompt.md` - Phase execution guidelines
- `PHASE-21-IMPLEMENTATION-GUIDE.md` - Detailed specifications
- `PHASE-21-EXPANSION-SUMMARY.md` - Changes and metrics
- `cortex-brain/tier0/governance/core-rules.yaml` - Governance rules

💻 **Existing Code**:
- `src/orchestrators/core/master_orchestrator.py` - Reference for integration
- `src/orchestrators/orchestrator_traits.py` - Protocol pattern example
- `cortex-brain/state/knowledge_repository.py` - Repository interface
- `src/core/business_knowledge/business_knowledge_repository.py` - Business knowledge

🧪 **Test Templates**:
- `tests/unit/core/` - Unit test structure
- `tests/integration/` - Integration test examples
- `tests/fixtures/` - Test data and fixtures

🔧 **Validation Tools**:
- `scripts/validation/validate_phase_sync.py` - Phase consistency
- `pytest` - Test execution and coverage

---

## Getting Started Now 🚀

To begin AC-IKP-004-02 implementation immediately:

```bash
# 1. Verify phase state
python3 scripts/validation/validate_phase_sync.py

# 2. Create test file for AC-IKP-004-02
touch tests/unit/core/knowledge/test_ingestion_pipeline.py

# 3. Write test suite (RED phase)
# - Implement test cases
# - Run: pytest tests/unit/core/knowledge/test_ingestion_pipeline.py -v
# - Expected: All tests fail (RED)

# 4. Create implementation
touch src/core/knowledge/ingestion/refinement_adapter.py

# 5. Implement code (GREEN phase)
# - Minimum code to pass all tests
# - Run: pytest tests/unit/core/knowledge/test_ingestion_pipeline.py -v
# - Expected: All tests pass (GREEN)

# 6. Refactor and optimize (REFACTOR phase)
# - Add type hints and docstrings
# - Improve code clarity
# - All tests still passing

# 7. Validate and commit
python3 scripts/validation/validate_phase_sync.py
git add -A
git commit -m "ac-ikp-004-02: Ingestion Integration complete"
```

---

## Timeline Summary

| Week | Hours | ACs | Status | Tests |
|------|-------|-----|--------|-------|
| Week 1 | 13 | 4 | Ready Now | 50 |
| Week 2 | 26 | 5 | After Week 1 | 85 (135↑) |
| Week 3 | 37 | 7 | After Week 2 | 112 (220↑) |
| **Total** | **76** | **15** | **Ready** | **220** |

---

**🎯 PHASE-21 Ready for Full Implementation!**

**Next**: Begin AC-IKP-004-02 (Ingestion Integration) immediately.

---

Generated: 2026-01-18  
Author: cortex-builder  
Status: ✅ READY FOR IMPLEMENTATION
