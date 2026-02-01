# PHASE 8.2: UNIFIED ROUTING - QUICK REFERENCE
**Status:** 🚧 ACTIVE | **Priority:** P0-CRITICAL | **Timeline:** 4 weeks

---

## 🎯 Objective
Enable ALL user requests to map directly to orchestrator instances via keyword-based routing with Tier 0 enforcement.

---

## 📋 Current Problem
```
User: "Use CORTEX LENS to onboard repo: XYZ"
  ↓
IntentRouter detects: IMPLEMENT
  ↓
Returns: "GeneralImplementationHandler" (STRING)
  ↓
❌ DEAD END - No orchestrator invocation
```

---

## ✅ After Phase 8.2
```
User: "Use CORTEX LENS to onboard repo: XYZ"
  ↓
IntentRouter extracts keywords: ["cortex", "lens", "onboard"]
  ↓
Looks up orchestrator registry
  ↓
Returns: OnboardingOrchestrator (INSTANCE)
Fallback: LENSOrchestrator
Confidence: 0.99
  ↓
✅ MasterOrchestrator.execute(OnboardingOrchestrator)
```

---

## 🚀 Implementation Phases

### Phase 8.2 (Week 1-2): Keyword Routing
- ✅ Extend intent-routing.yaml with orchestrator references
- ✅ Create OrchestratorLookup adapter
- ✅ Enhance IntentRouter with keyword extraction
- ✅ Add RoutingEnforcementEngine (Tier 0 blocking)
- ✅ 25+ unit tests, 15+ integration tests

### Phase 8.3 (Week 3): Semantic Ranking
- ✅ Candidate ranking algorithm
- ✅ Interactive disambiguation UI
- ✅ 12+ edge case tests

### Phase 8.4 (Week 4): Optional NLP
- ✅ Lightweight embedding model (optional)
- ✅ Synonym expansion
- ✅ A/B testing framework

### Phase 8.5 (Week 4): LENS Microsoft Stack
- ✅ C# AST analyzer
- ✅ SQL/Oracle query analyzer
- ✅ Angular/TypeScript analyzer
- ✅ Edge case detector (multi-language)

### Phase 8.6 (Day 1-2): Production Verification
- ✅ Extend verify_prod_ready.py (6 new checks)
- ✅ Routing health dashboard
- ✅ CI/CD integration

---

## 📊 6 New Production Checks

| Check | Name | Blocking |
|-------|------|----------|
| 13 | Orchestrator Keyword Mapping | ✅ YES |
| 14 | Routing Confidence Thresholds | ✅ YES |
| 15 | Fallback Orchestrators | ⚠️ NO |
| 16 | Enforcement Rules Active | ✅ YES |
| 17 | LENS Analyzers Wired | ⚠️ NO |
| 18 | Routing Performance | ⚠️ NO |

---

## 🔧 Key Files Modified

```
cortex_brain/tier3/knowledge/intent-routing.yaml
  + orchestrator field
  + keywords field
  + fallback_orchestrators field

cortex/orchestrators/registry/orchestrator_lookup.py
  + NEW: OrchestratorLookup adapter

cortex/orchestrators/core/intent_router.py
  + _extract_keywords()
  + _lookup_orchestrators()
  + _rank_orchestrators()
  + _resolve_orchestrator_instance()

cortex/orchestrators/core/routing_enforcement.py
  + NEW: RoutingEnforcementEngine

cortex/brain/analysis/ast_analyzer_csharp.py
  + NEW: C# AST analysis

cortex/brain/analysis/sql_analyzer.py
  + NEW: SQL/Oracle analysis

cortex/brain/analysis/typescript_analyzer.py
  + NEW: Angular/TypeScript analysis

cortex/brain/analysis/edge_case_detector.py
  + NEW: Multi-language edge cases

_workspaces/docker-plan/verify_prod_ready.py
  + Checks 13-18
```

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Routing Accuracy | 95%+ |
| Routing Latency (p95) | <10ms |
| Disambiguation Rate | <5% |
| Enforcement Block Rate | <1% |
| User Satisfaction | 8.5/10 |

---

## 🔍 Example: Keyword Mapping

```yaml
# intent-routing.yaml
implement:
  onboarding:
    orchestrator: "OnboardingOrchestrator"
    keywords:
      - "onboard"
      - "setup"
      - "initialize"
      - "bootstrap"
      - "welcome"
    fallback_orchestrators:
      - "LENSOrchestrator"
      - "SetupOrchestrator"
    confidence_boost: 0.25
    blocking: true
  
  lens_analysis:
    orchestrator: "LENSOrchestrator"
    keywords:
      - "lens"
      - "analyze"
      - "inspect"
      - "examine"
      - "code intelligence"
    fallback_orchestrators:
      - "OnboardingOrchestrator"
    confidence_boost: 0.20
    blocking: true
```

---

## 🛡️ Enforcement Rules (Tier 0 Blocking)

1. **ROUTING-001:** Keywords must map to registered orchestrators
2. **ROUTING-002:** Confidence must exceed threshold (default: 0.6)
3. **ROUTING-003:** Fallback orchestrators required for ambiguous requests
4. **ROUTING-004:** All routing decisions must be auditable

---

## 📈 Microsoft Stack Support

### C# Analysis
- Classes, methods, properties
- LINQ queries
- Async/await patterns
- Dependency injection
- Entity Framework

### SQL/Oracle Analysis
- T-SQL stored procedures
- PL/SQL packages
- SQL injection detection
- Query complexity analysis
- Table dependencies

### Angular/TypeScript Analysis
- TypeScript classes
- Angular components/services/pipes
- RxJS observable patterns
- Routing configuration
- HTTP client usage

### Edge Cases Detected
- **C#:** Null reference exceptions, missing cancellation tokens
- **SQL:** Missing transactions, unbounded result sets
- **Oracle:** Missing exception handlers, SQL injection
- **Angular:** Memory leaks, missing error handlers

---

## 🚦 Rollout Strategy

1. **Alpha (Week 1-2):** Internal testing, 50+ manual tests
2. **Beta (Week 3):** 10% traffic, A/B testing
3. **GA (Week 4):** 100% traffic, production monitoring

---

## ⚙️ Commands

```bash
# Run production verification
python _workspaces/docker-plan/verify_prod_ready.py

# Run routing tests
pytest tests/integration/orchestrators/test_unified_routing.py -v

# Check routing metrics
curl http://localhost:8000/metrics | grep routing

# View routing health
curl http://localhost:8000/health/routing
```

---

## 📚 Documentation

- **Full Spec:** [PHASE-8.2-UNIFIED-ROUTING.yaml](_workspaces/docker-plan/PHASE-8.2-UNIFIED-ROUTING.yaml)
- **Master Plan:** [migration-phases-plan.yaml](_workspaces/docker-plan/migration-phases-plan.yaml)
- **Prod Checks:** [verify_prod_ready.py](_workspaces/docker-plan/verify_prod_ready.py)

---

## 🎯 Next Actions

1. ✅ Review PHASE-8.2-UNIFIED-ROUTING.yaml
2. 📋 Start ROUTE-001: Extend intent-routing.yaml
3. 📋 Create OrchestratorLookup adapter
4. 📋 Enhance IntentRouter
5. 📋 Add enforcement engine
6. 📋 Write tests (40+ tests)
7. 📋 Extend verify_prod_ready.py
8. 📋 Deploy to Alpha environment

---

**Owner:** CORTEX Team  
**Start Date:** 2026-01-30  
**Target Completion:** 2026-02-27 (4 weeks)
