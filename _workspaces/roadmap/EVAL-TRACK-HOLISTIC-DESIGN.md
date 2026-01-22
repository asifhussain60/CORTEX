# TRACK:EVAL - HOLISTIC DESIGN

**Date:** 2026-01-22  
**Status:** Design Phase (Ready for Implementation)  
**Priority:** P2-OPTIONAL (Non-blocking enhancement)  
**Architecture:** Non-breaking optional layer with production fallback

---

## 1. STRATEGIC POSITIONING

### System Context
- **Production Status:** ✅ Mac (4/4), Win (7/7), Ah (11/11) tracks complete → 833 tests passing
- **Eval Track Role:** Optional semantic intelligence layer enabling Knowledge Graph–based reasoning
- **Integration Pattern:** Optional wrapper around existing SQLite governance; zero impact if disabled
- **Deployment Model:** Feature-flagged; graceful fallback to YAML when KG unavailable

### Business Value
| Dimension | Benefit | Impact |
|-----------|---------|--------|
| **Semantics** | Graph-based entity relationships vs flat YAML | Enable impact analysis, relationship traversal |
| **Routing** | Intelligent orchestration via pattern/capability matching | Reduce manual routing config by 20-30% |
| **Observability** | Relationship-aware compliance & traceability | Audit governance rule application across entities |
| **Scalability** | Graph queries on 1000+ entities vs linear scan | 10-100x faster for complex relationship queries |
| **Future-Proof** | Foundation for ML-driven rule inference | Enable adaptive governance (non-breaking later) |

---

## 2. ARCHITECTURAL DESIGN

### 2.1 Layer Stack (Adapter Pattern)

```
┌─────────────────────────────────────────────────────┐
│ INTENT ROUTER / MASTER ORCHESTRATOR (Consumer Layer) │
│ (Uses abstract query interface - no coupling)        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│ QUERY ADAPTER INTERFACE (Abstract Layer)             │
│ - execute_query(cypher|sql)                         │
│ - get_related_entities(entity_id, depth)            │
│ - validate_graph_consistency()                       │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼───────────┐   ┌────────▼────────┐
│ KG Backend        │   │ SQLite Fallback  │
│ (Neo4j/Neptune)   │   │ (Existing)       │
│ Optimized routing │   │ Always available │
└───────────────────┘   └──────────────────┘
```

### 2.2 Non-Breaking Integration

1. **Query abstraction** decouples KG implementation from routing logic
2. **Fallback circuit breaker** redirects to SQLite on timeout (>500ms)
3. **Feature flag** `KNOWLEDGE_GRAPH_ENABLED` in config
4. **Gradual adoption** - teams opt-in, never forced
5. **Zero breaking changes** - existing YAML-based workflows unaffected

### 2.3 Core Entities (Neo4j/Neptune Schema)

```
NODE TYPES:
  Domain: {name, owner, tier, risk_level}
  Rule: {id, name, tier, type, enabled, conflict_domain}
  Entity: {type, name, owner, relationships}
  Pattern: {name, description, applies_to_domains, expert}
  BestPractice: {name, category, governance_rule_applies}

RELATIONSHIPS:
  Domain -[GOVERNED_BY]-> Rule
  Rule -[CONFLICTS_WITH]-> Rule
  Domain -[DEPENDS_ON]-> Domain
  Entity -[IMPLEMENTS]-> Pattern
  Pattern -[FOLLOWS]-> BestPractice
  Rule -[APPLIES_TO]-> Entity
```

### 2.4 Execution Flow

```
User Request → IntentRouter
    ↓
Route query to Query Adapter (interface)
    ↓
    ├─→ [KG Enabled?] → YES → Neo4j query + caching
    │                         ├─ Success → Return results (fast path)
    │                         ├─ Timeout (>500ms) → Fallback to SQLite
    │                         └─ Error → Log & fallback
    │
    └─→ [KG Disabled or unavailable] → SQLite query (existing path)
        └─ Return results (deterministic)
```

---

## 3. PHASE ARCHITECTURE (6 Sequential Phases)

### Phase 1: PHASE-KG-001-FOUNDATION (3-4 days, 40 tests)
**Goal:** Neo4j/Neptune infrastructure + schema design

**Deliverables:**
- `cortex/core/knowledge_graph/kg_adapter.py` - Abstract Query Adapter interface
- `cortex/core/knowledge_graph/neo4j_backend.py` - Neo4j implementation
- `cortex/core/knowledge_graph/kg_schema.py` - Schema definitions (node types, relationships)
- `cortex/core/knowledge_graph/kg_config.py` - Connection pooling, retry logic, timeouts
- `tests/test_kg_001_foundation.py` - 40 unit tests (adapter interface, schema validation, connection)

**Architecture Principles:**
- Repository pattern isolates database logic
- Connection pooling prevents resource exhaustion
- Schema version tracking for migrations
- Circuit breaker for graceful degradation

**Tests Cover:**
- Adapter interface contract (8 tests)
- Neo4j connection lifecycle (6 tests)
- Schema node/relationship creation (12 tests)
- Index management (8 tests)
- Error handling & recovery (6 tests)

**Acceptance Criteria:**
- ✅ Query Adapter interface fully typed (CORE-011)
- ✅ Neo4j backend implements interface
- ✅ Schema deployed to test DB
- ✅ All 40 tests passing with 100% coverage
- ✅ Connection timeout < 2s; query timeout < 500ms

---

### Phase 2: PHASE-KG-002-ENTITY-SYNC (2-3 days, 60 tests)
**Goal:** Sync BusinessKnowledgeRepository entities → KG graph

**Deliverables:**
- `cortex/core/knowledge_graph/entity_sync.py` - Non-destructive sync pipeline
- `cortex/core/knowledge_graph/relationship_engine.py` - Relationship creation logic
- `cortex/core/knowledge_graph/conflict_resolver_kg.py` - Deduplication strategy
- `cortex/core/knowledge_graph/sqlite_fallback.py` - SQLite sync mechanism
- `tests/test_kg_002_entity_sync.py` - 60 integration tests

**Sync Strategy (Non-Destructive):**
1. Read all entities from `BusinessKnowledgeRepository` (existing)
2. Check KG for existing nodes (query by natural key: `domain.name + rule.id`)
3. If not present: INSERT node + relationships
4. If present & unchanged: Skip
5. If present & changed: UPDATE node properties (relationships immutable)
6. Generate audit trail (created/updated timestamps)
7. Fallback to SQLite if KG unavailable

**Deduplication Logic:**
- Natural key: `{domain_name}:{rule_id}:{entity_type}`
- Conflict detection: Rules with same domain but different tier
- Resolution: Keep existing if created >7 days ago; update if recent

**Tests Cover:**
- Entity extraction from BusinessKnowledgeRepository (8 tests)
- Node creation & properties (10 tests)
- Relationship creation (governance, conflict, dependency) (15 tests)
- Deduplication & conflict resolution (12 tests)
- SQLite fallback on KG failure (10 tests)
- Idempotency (sync twice → no duplicates) (5 tests)

**Acceptance Criteria:**
- ✅ All 1000+ existing entities synced to KG
- ✅ Zero duplicates (deduplication validated)
- ✅ All relationships created correctly
- ✅ SQLite fallback works on KG timeout
- ✅ 60 tests passing (100% coverage)
- ✅ Audit trail logged for every sync operation

---

### Phase 3: PHASE-KG-003-QUERY-LAYER (2-3 days, 50 tests)
**Goal:** Query engine + semantic search + rule inference

**Deliverables:**
- `cortex/core/knowledge_graph/query_engine.py` - Cypher query builder
- `cortex/core/knowledge_graph/semantic_search.py` - Relationship traversal (1-3 hops)
- `cortex/core/knowledge_graph/rule_inference.py` - Inference engine (apply rules based on graph state)
- `cortex/core/knowledge_graph/sqlite_query_adapter.py` - SQLite implementation of Query Adapter
- `tests/test_kg_003_query_layer.py` - 50 tests

**Query Capabilities:**
1. **Direct lookups:** `GET entity BY domain:rule_id`
2. **Relationship traversal:** `GET related_entities(entity, depth=1|2|3)`
3. **Pattern queries:** `GET entities MATCHING pattern_name WITH constraint`
4. **Inference:** `APPLY rule_set TO entity_set` (rule inference engine)
5. **Consistency checks:** `VALIDATE no_circular_conflicts()`

**Semantic Search Examples:**
- "Get all domains governed by tier0 rules"
- "Find entities that depend on domain X"
- "Get pattern instances applying to rule Y"
- "Get expert recommendations for entity Z"

**Fallback Logic (SQLite):**
- Translates Cypher queries to equivalent SQL
- Supports 1-3 hop traversal via recursive CTEs
- Same interface, different implementation
- 10-100x slower than KG but always available

**Tests Cover:**
- Query builder interface (6 tests)
- Neo4j Cypher queries (12 tests)
- Relationship traversal (1-3 hops) (10 tests)
- Rule inference engine (8 tests)
- SQLite equivalents (10 tests)
- Timeout & error handling (4 tests)

**Acceptance Criteria:**
- ✅ Query Adapter fully implemented (Neo4j + SQLite)
- ✅ All query types tested & working
- ✅ Traversal queries handle 3-hop depth correctly
- ✅ Inference produces correct rule sets
- ✅ SQLite queries produce identical results to KG
- ✅ 50 tests passing (100% coverage)

---

### Phase 4: PHASE-KG-004-ROUTING-OPTIMIZATION (2-3 days, 40 tests)
**Goal:** Integrate KG insights into IntentRouter

**Deliverables:**
- `cortex/intent_router/kg_routing_strategy.py` - KG-based routing decisions
- `cortex/intent_router/semantic_capability_matcher.py` - Pattern/capability matching
- `cortex/core/knowledge_graph/routing_cache.py` - Query result caching (Redis or in-memory)
- `tests/test_kg_004_routing_optimization.py` - 40 integration tests

**Optimization Strategy:**
1. **Semantic capability matching:** Match challenges to handlers via pattern knowledge
2. **Relationship-aware selection:** Prioritize handlers managing related domains
3. **Pattern-based routing:** Route via best-practice patterns (non-breaking, optional layer)
4. **Caching:** Cache query results for 5 min (configurable)
5. **Fallback:** Use existing YAML routing if KG query fails

**Example Workflow:**
```
Challenge: "Clean VPC resources"
  ↓
KG Query: "GET handlers EXPERT_IN(AWS) WITH pattern(CleanerInterface)"
  ↓
Results: [VPCCleaner, VolumeDetacher, SecurityGroupCleaner]
  ↓
Prioritize by conflict_domain (lower priority = route first)
  ↓
Return routing decision
```

**Integration with MasterOrchestrator:**
- Add optional `kg_routing_enabled` feature flag
- Non-breaking: Existing YAML routing still works
- Fallback on timeout or error
- Log routing decision + source (KG vs YAML)

**Tests Cover:**
- Feature flag toggling (4 tests)
- Semantic capability matching (10 tests)
- Pattern-based priority calculation (8 tests)
- Cache hit/miss scenarios (6 tests)
- Fallback to YAML routing (6 tests)
- E2E routing decision workflow (6 tests)

**Acceptance Criteria:**
- ✅ KG routing operational and tested
- ✅ Fallback to YAML on any KG error
- ✅ Caching reduces query latency by 50%
- ✅ MasterOrchestrator integration non-breaking
- ✅ 40 tests passing (100% coverage)
- ✅ Performance benchmark: <50ms per routing decision (p95)

---

### Phase 5: PHASE-KG-005-VALIDATION (2-3 days, 20 tests)
**Goal:** Production hardening + full observability

**Deliverables:**
- `cortex/core/knowledge_graph/consistency_validator.py` - Graph validation rules
- `cortex/core/knowledge_graph/kg_observability.py` - Metrics & dashboards
- `cortex/core/knowledge_graph/kg_health_check.py` - Liveness probes
- `tests/test_kg_005_validation.py` - 20 tests
- `docs/KNOWLEDGE-GRAPH-OPERATIONS.md` - Operational runbook

**Validation Checks:**
1. **No circular conflicts:** Rule A conflicts with B conflicts with C conflicts with A → ERROR
2. **Referential integrity:** All `GOVERNED_BY` edges reference existing rules
3. **Domain coverage:** All entities have exactly one primary domain
4. **Relationship cardinality:** Check relationship counts match expectations
5. **Performance benchmarks:** Compare KG queries vs SQLite baseline (< 10x slower)

**Observability:**
- Metrics: Query latency (p50/p95/p99), cache hit rate, fallback rate
- Dashboards: Graph health, query performance, sync status
- Alerts: Connection failures, query timeouts, validation failures
- Logging: Query execution traces with correlation IDs

**Health Checks:**
- Connection probe (ping Neo4j)
- Query responsiveness (benchmark query)
- Sync status (last successful sync time)
- Data integrity (consistency validator)

**Tests Cover:**
- Circular conflict detection (3 tests)
- Referential integrity checks (3 tests)
- Domain coverage validation (2 tests)
- Performance benchmarking (5 tests)
- Metrics collection & emission (4 tests)
- Health check endpoints (3 tests)

**Acceptance Criteria:**
- ✅ All validation checks passing
- ✅ Zero graph inconsistencies
- ✅ Performance vs SQLite baseline documented
- ✅ Metrics exported to observability platform
- ✅ Health endpoints responding correctly
- ✅ 20 tests passing (100% coverage)
- ✅ All 7000+ existing tests still passing (regression suite)

---

### Phase 6: PHASE-EVAL-SUMMARY (1 day, 15 tests)
**Goal:** Production readiness assessment + decision criteria

**Deliverables:**
- `_workspaces/roadmap/reports/KNOWLEDGE-GRAPH-PRODUCTION-ASSESSMENT.md` - Performance report
- `_workspaces/roadmap/reports/KNOWLEDGE-GRAPH-ADOPTION-DECISION.md` - Decision criteria
- `docs/KNOWLEDGE-GRAPH-DEPLOYMENT-PLAYBOOK.md` - Deployment guide
- `tests/test_eval_summary.py` - 15 validation tests

**Assessment Criteria:**
| Criterion | Target | Status |
|-----------|--------|--------|
| Query latency (p95) | <100ms | _Measured in Phase 5_ |
| Cache hit rate | >70% | _Measured in Phase 5_ |
| Fallback rate | <1% | _Measured in Phase 5_ |
| Graph consistency | 100% | _Validated in Phase 5_ |
| Regression suite | 100% passing | _Validated in Phase 5_ |
| Adoption friction | <5% ops overhead | _To be assessed_ |

**Adoption Decision Framework:**
1. **If all criteria met:** Recommend production deployment (feature-flagged opt-in)
2. **If latency <100ms p95:** Enable by default; teams can opt-out
3. **If fallback >5%:** Keep opt-in; investigate reliability issues
4. **If performance acceptable but not stellar:** Deploy as opt-in; enable after 1 month metrics review

**Deployment Playbook Sections:**
- Prerequisites (Neo4j 4.4+ or Neptune)
- One-click deployment script (Docker Compose or CloudFormation)
- Configuration (connection pooling, cache settings, feature flags)
- Rollback procedure (disable feature flag, keep KG data for recovery)
- Monitoring setup (Prometheus scrape config, Grafana dashboards)
- Training materials for operations team

**Tests Cover:**
- Performance regression detection (5 tests)
- Adoption metrics collection (4 tests)
- Deployment playbook validation (3 tests)
- Rollback procedure verification (3 tests)

**Acceptance Criteria:**
- ✅ Production assessment complete with measured data
- ✅ Decision framework clear (go/no-go criteria documented)
- ✅ Deployment playbook tested
- ✅ Rollback procedure verified
- ✅ 15 tests passing (100% coverage)

---

## 4. DEPENDENCY & SEQUENCING

### Phase Ordering (Strictly Sequential)
```
PHASE-KG-001 (Foundation)
    ↓
PHASE-KG-002 (Entity Sync)
    ↓
PHASE-KG-003 (Query Layer)
    ↓
PHASE-KG-004 (Routing Optimization)
    ↓
PHASE-KG-005 (Validation)
    ↓
PHASE-EVAL-SUMMARY (Assessment)
```

### Hard Blockers
- **Blocker for Phase 1:** Mac track PHASE-E-TDD-IMPLEMENTATION complete (domain_brain ≥90% tests passing)
- **Blocker for Phase 2:** Phase 1 complete + BusinessKnowledgeRepository stable
- **Blocker for Phases 3-6:** Previous phase complete

### No Blockers Within Phase
- Each phase is self-contained; no external dependencies beyond previous phase

---

## 5. GOVERNANCE & SAFETY

### CORE Rules Applied
- **CORE-008 (TDD):** Tests written first; 100+ tests passing before code shipment
- **CORE-011 (Types):** All public APIs fully typed (no `Any`)
- **CORE-012 (Docstrings):** Google-style docstrings on all functions
- **CORE-013 (Error Handling):** No bare `except:` clauses; structured error recovery
- **CORE-017 (Strict Enforcement):** No exemptions; all rules enforced
- **CORE-026 (Git Checkpoints):** Checkpoint commit before each phase
- **CORE-027 (Audit Trail):** AC_START → AC_EXECUTE → AC_COMPLETE logged

### Production Safeguards
1. **Feature flag:** `KNOWLEDGE_GRAPH_ENABLED` must be explicitly set to enable
2. **Circuit breaker:** 3 failures → disable KG; revert to SQLite automatically
3. **Fallback latency:** If KG query >500ms, fallback to SQLite (no hanging)
4. **Graceful degradation:** System fully functional without KG (not required)
5. **Monitoring alert:** Alert on circuit breaker trip (ops will investigate)

### Zero Impact When Disabled
- Feature flag = false → All KG code skipped (no overhead)
- Existing YAML routing unaffected
- No KG schema required
- Deployment optional (backward compatible)

---

## 6. SUCCESS CRITERIA

### Phase Success (Each Phase)
- ✅ All acceptance criteria met
- ✅ All tests passing (≥98% success rate)
- ✅ All CORE governance rules enforced
- ✅ Audit trail logged (AC_START → EXECUTE → COMPLETE)
- ✅ Git commit with machine marker (`eval: phase-id: summary`)
- ✅ Production-ready code (no TODOs, no stubs)

### Track Success (All 6 Phases)
- ✅ 225+ tests passing across all phases
- ✅ Knowledge Graph in production with feature flag
- ✅ Adoption decision made with supporting data
- ✅ Deployment playbook tested & operational
- ✅ Zero regression in existing CORTEX functionality
- ✅ System works identically with KG disabled

### Business Success
- ✅ Semantic routing available for opt-in adoption
- ✅ Foundation for future ML-driven inference
- ✅ Scalable to 10,000+ entities
- ✅ <5% operational overhead (monitoring/alerting)
- ✅ Reversible deployment (can disable via flag)

---

## 7. RESOURCE & TIMELINE

| Phase | Effort | Tests | Parallel? | Start After |
|-------|--------|-------|-----------|------------|
| KG-001 | 3-4d | 40 | No | Mac PHASE-E complete |
| KG-002 | 2-3d | 60 | No | KG-001 complete |
| KG-003 | 2-3d | 50 | No | KG-002 complete |
| KG-004 | 2-3d | 40 | No | KG-003 complete |
| KG-005 | 2-3d | 20 | No | KG-004 complete |
| EVAL-SUMMARY | 1d | 15 | No | KG-005 complete |
| **Total** | **12-16d** | **225** | Sequential | Blocks: None |

**Wall-clock time:** 12-16 days (sequential; no parallelism)  
**Resource requirement:** 1 full-time engineer (or 0.5 FTE over 24-32 days)  
**Startup blocker:** Mac PHASE-E completion (domain_brain ≥90% tests)

---

## 8. FAILURE MODES & MITIGATION

| Failure Mode | Probability | Mitigation | Impact |
|--------------|-------------|-----------|--------|
| Neo4j connection fails | Medium | SQLite fallback + circuit breaker | Graceful degradation |
| Query timeout (>500ms) | Medium | Fallback to SQLite after timeout | Slight latency increase |
| Graph sync incomplete | Low | Idempotent sync; audit trail for debugging | Data freshness delay |
| Circular conflict not detected | Very Low | Validation in Phase 5 catches this | Safety net enforced |
| Performance regression (KG slower than YAML) | Medium | Phase 5 benchmarking + Phase 6 decision gate | Go/no-go decision |

**Worst-case scenario:** Phase 5 benchmarking shows KG 10x slower than SQLite
- **Mitigation:** Keep feature flag as opt-in; provide opt-out path; archive results for future optimization (Phase G)
- **Impact:** KG available but not recommended for production; still valuable for analysis/offline usage

---

## 9. INTEGRATION CHECKLIST

Before marking eval_track complete:

- [ ] Query Adapter interface exposed in `cortex/core/knowledge_graph/__init__.py`
- [ ] MasterOrchestrator imports `kg_routing_strategy` (lazy import, feature flag guarded)
- [ ] IntentRouter accepts optional `kg_enabled` parameter
- [ ] Feature flag `KNOWLEDGE_GRAPH_ENABLED` in `cortex/config/settings.py`
- [ ] Observability metrics registered with platform
- [ ] Health checks integrated into `/health` endpoint
- [ ] Deployment documentation in `docs/12-infrastructure/`
- [ ] Operational runbook in `_workspaces/roadmap/reports/`
- [ ] All 225+ tests passing in CI/CD
- [ ] Zero regression in existing 7000+ test suite

---

## 10. FUTURE ENHANCEMENTS (Phase G+)

Not in scope for eval_track but planned downstream:

1. **PHASE-G-ML-INFERENCE:** ML-driven rule optimization based on KG traversal patterns
2. **PHASE-H-KNOWLEDGE-PROTOCOL:** Formal knowledge protocol (publishing/consuming knowledge via MCP)
3. **PHASE-I-GRAPH-VIS:** Interactive graph visualization dashboard
4. **PHASE-J-BENCHMARK:** Performance optimization & Neo4j tuning
5. **PHASE-K-MULTI-TENANT:** Multi-tenant KG support

---

## 11. GO/NO-GO DECISION FRAMEWORK

**Decision Point:** End of Phase 6 (PHASE-EVAL-SUMMARY)

### GO Criteria (Recommend Production)
- ✅ Query latency p95 < 100ms
- ✅ Cache hit rate > 70%
- ✅ Fallback rate < 1%
- ✅ All 225 tests passing + no regression in 7000+ suite
- ✅ Adoption friction assessment < 5%

### CONDITIONAL GO (Opt-in Deployment)
- ✅ Query latency p95 < 250ms
- ✅ Cache hit rate > 50%
- ✅ Fallback rate < 5%
- ✅ All safety criteria met (no data corruption, graceful fallback)

### NO-GO (Archive for Phase G Optimization)
- ❌ Query latency p95 > 500ms
- ❌ Fallback rate > 10%
- ❌ Data consistency issues detected
- ❌ Operational complexity exceeds tolerance

---

**Design Approval:** Ready for track:eval autonomous execution
