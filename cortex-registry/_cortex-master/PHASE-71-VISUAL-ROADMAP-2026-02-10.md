# PHASE 71: LENS Intelligence Integration Framework
## Visual Strategy & Implementation Roadmap

**Created:** 2026-02-10  
**Authority:** Workspace Analysis + CORTEX Architect  
**Status:** 🔴 PLANNED (Ready after Phase 70)  

---

## 📊 One-Page Strategy

```
PROBLEM (Workspace Analysis)
├─ Schema fragmentation (no standard contract)
├─ Missing evidence tracking (can't trust outputs)
├─ Full regeneration (30+ sec per call, doesn't scale)
├─ Monolithic output (no lazy-loading)
└─ Analyzer inconsistency (each exports own format)

SOLUTION (Phase 71)
├─ S1: LDv1 Schema + EvidenceProtocol
├─ S2: Retrofit all 4 analyzers for consistency
├─ S3: Incremental extraction (10x speedup)
├─ S4: Manifest-based publishing (lazy-loadable)
└─ S5: Documentation + integration

IMPACT
├─ Standardized LENS outputs (extensibility)
├─ Traceable intelligence (compliance-ready)
├─ 10x faster analysis (enterprise-scale)
├─ Multi-repo readiness (Phase 73)
└─ Unblocks Phase 72, 73, 74
```

---

## 🏗️ Five Stages at a Glance

| Stage | Focus | Duration | Tests | Effort | Status |
|-------|-------|----------|-------|--------|--------|
| **S1** | Schema + Protocol | 4-5 days | 45 | 16 hrs | 🔴 Planned |
| **S2** | Analyzer Standardization | 5-6 days | 45 | 20 hrs | 🔴 Planned |
| **S3** | Incremental + Cache | 5-7 days | 45 | 24 hrs | 🔴 Planned |
| **S4** | Manifest + Lazy-Load | 4-5 days | 45 | 18 hrs | 🔴 Planned |
| **S5** | Integration + Docs | 3-4 days | 15 | 16 hrs | 🔴 Planned |
| **TOTAL** | | **3-4 weeks** | **180** | **94 hrs** | |

---

## 🎯 Core Architecture (Post-Phase 71)

```
┌─────────────────────────────────────────────────┐
│           CORTEX LENS Intelligence Backbone     │
├─────────────────────────────────────────────────┤
│                                                 │
│  Layer 0: LDv1 Schema Foundation                │
│  ├─ Core entities (Repository, Artifact, etc.)  │
│  ├─ Evidence protocol (confidence + source)     │
│  └─ Validation (pydantic + JSON Schema)         │
│                                                 │
│  Layer 1: Intelligent Analysis                  │
│  ├─ GitHistoryAnalyzer (confidence: 1.0)        │
│  ├─ ASTAnalyzer (confidence: 1.0)               │
│  ├─ CommentExtractor (confidence: 0.9)          │
│  └─ SecurityThreatAnalyzer (confidence: 0.7-95) │
│      └─ All emit: results[] + evidence[] + conf │
│                                                 │
│  Layer 2: Incremental Extraction                │
│  ├─ Git-diff keyed (commit SHA)                 │
│  ├─ Cache with TTL + hash-check                 │
│  └─ Selective analyzer invocation               │
│      └─ 10x speedup on unchanged repos          │
│                                                 │
│  Layer 3: Manifest Publishing                   │
│  ├─ index.json (manifest + metadata)            │
│  ├─ 9 per-tab artifacts (lazy-loadable)         │
│  └─ evidence/ directory (audit trail)           │
│                                                 │
│  Layer 4: MCP Tool Exposure                     │
│  ├─ cortex_lens_analyze → manifest              │
│  ├─ cortex_lens_artifact_* → per-tab            │
│  └─ cortex_lens_repos → multi-repo registry     │
│                                                 │
│  Layer 5: Visualization Consumption             │
│  ├─ Dashboard reads manifest                    │
│  ├─ Lazy-load per tab on user click             │
│  └─ Fallback to embedded data if missing        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📈 Execution Timeline (3-4 Weeks)

```
Week 1 (Parallel with Phase 70)
├─ Mon-Tue: S1 Schema + Protocol (45 tests written)
│   └─ cortex/lens/schemas/ldv1_schema.json
│       cortex/lens/schemas/evidence_protocol.py
│       cortex/lens/schemas/artifact_registry.yaml
│
├─ Wed-Fri: S2 Analyzer Retrofitting Starts
│   └─ GitHistoryAnalyzer enhanced
│       ASTAnalyzer updated
│       [S2 continues into Week 2]

Week 2
├─ Mon-Wed: S2 Completion (45 tests passing)
│   ├─ CommentExtractor enhanced
│   ├─ SecurityThreatAnalyzer updated
│   └─ Integration tests written
│
├─ Thu-Fri: S3 Incremental Extraction Starts
│   └─ IncrementalExtractor scaffolding
│       Cache strategy designed

Week 3
├─ Mon-Wed: S3 Incremental + Cache (45 tests written)
│   ├─ Git-diff keyed extraction working
│   ├─ Cache hit/miss flow implemented
│   └─ Performance baseline measured
│
├─ Thu-Fri: S4 Manifest Publishing Starts
│   └─ Artifact publisher scaffolding

Week 4
├─ Mon-Wed: S4 Completion (45 tests passing)
│   ├─ Manifest structure tested
│   ├─ Lazy-loader working
│   └─ SPA integration verified
│
├─ Thu-Fri: S5 Integration + Documentation
│   ├─ End-to-end tests (15 total)
│   ├─ LDv1 spec published
│   └─ Phase 72 unblocked
```

---

## 💡 Key Design Decisions (Why)

### Decision 1: LDv1 vs Ad-hoc JSON

| Choice | Reason |
|--------|--------|
| **LDv1 Schema** | Extensible, standards-based, enables multi-repo future |
| ~~Ad-hoc~~ | Current approach; doesn't scale; hard to extend |

### Decision 2: Evidence on Every Node

| Choice | Reason |
|--------|--------|
| **Mandatory evidence[]** | Compliance + trust + audit trail (5% overhead worth it) |
| ~~Optional~~ | Saves perf but creates audit gap |

### Decision 3: Incremental vs Full Extraction

| Choice | Reason |
|--------|--------|
| **Git-diff keyed cache** | 10x speedup; deterministic (commit SHA); shareable |
| ~~Full extract~~ | Current; slow on re-runs; no caching |

### Decision 4: Manifest + Lazy-Load vs Monolithic

| Choice | Reason |
|--------|--------|
| **Manifest-driven** | Scales to multi-repo; lazy-loads per-tab; supports streaming |
| ~~Single JSON~~ | Current; works now; breaks at enterprise scale |

### Decision 5: Hybrid MCP + Optional REST

| Choice | Reason |
|--------|--------|
| **Phase 71: MCP-first** | Aligns with CORTEX architecture; extensible |
| ~~Separate REST API~~ | Creates divergence; Phase 74+ can add as optional facade |

---

## 🎯 Success Metrics (Proof of Value)

### S1 Schema Definition ✅
```
Metric: LDv1 schema + EvidenceProtocol defined
Pass Criteria:
  ✅ JSON Schema file created (cortex/lens/schemas/)
  ✅ Pydantic models for all entities
  ✅ 45 tests passing (schema validation + evidence)
  ✅ Artifact registry YAML complete
```

### S2 Analyzer Standardization ✅
```
Metric: All 4 analyzers emit evidence[] + confidence
Pass Criteria:
  ✅ GitHistoryAnalyzer: confidence = 1.0 (git deterministic)
  ✅ ASTAnalyzer: confidence = 1.0 (AST deterministic)
  ✅ CommentExtractor: confidence = 0.9 (regex-based)
  ✅ SecurityThreatAnalyzer: confidence = 0.7-0.95 (pattern-based)
  ✅ 45 tests passing (per-analyzer + integration)
  ✅ Zero breaking changes (backward compat)
```

### S3 Incremental Extraction ✅
```
Metric: 10x speedup on repeated analysis + 70%+ cache hit rate
Pass Criteria:
  ✅ Small repos (no change): 30s → 0.5s (60x)
  ✅ Medium repos (10% change): 30s → 5s (6x)
  ✅ Large repos (1% change): 120s → 10s (12x)
  ✅ Cache hit rate > 70% on repeated runs
  ✅ 45 tests passing (cache + incremental + perf)
```

### S4 Manifest Publishing ✅
```
Metric: 9 artifacts per repo, lazy-loadable via manifest
Pass Criteria:
  ✅ index.json manifest generated + validated
  ✅ 9 per-tab artifacts (overview, arch, domain, data, etc.)
  ✅ Lazy-loader working (fetch on-demand)
  ✅ SPA integration verified
  ✅ 45 tests passing (manifest + lazy-load)
```

### S5 Integration ✅
```
Metric: LDv1 production-ready + Phase 72 unblocked
Pass Criteria:
  ✅ End-to-end tests passing (15 total)
  ✅ LDv1 spec published + documented
  ✅ Zero breaking changes
  ✅ Performance verified on CORTEX + sample monorepo
  ✅ Phase 72+ dependencies satisfied
```

---

## 🔗 Dependency Chain (Why Sequencing Matters)

```
Phase 70 (Alignment Remediation)
  └─ P0-blocking: Eliminates 620 stub tests + wiring gaps
     └─ MUST complete first (foundation)

Phase 71 (LENS Intelligence Integration)
  ├─ Depends on: Phase 70 complete
  ├─ Unblocks: Phase 72, 73, 74
  └─ Enables: Enterprise-scale LENS backbone

Phase 72 (UnifiedDigestIngestionFacade)
  ├─ Depends on: Phase 71 complete
  ├─ Unblocks: Phase 73 (composition layer ready)
  └─ Enables: Knowledge management at scale

Phase 73 (Multi-Repo LENS Consolidation)
  ├─ Depends on: Phase 71 + 72 complete
  ├─ Unblocks: Phase 74 (multi-repo analysis ready)
  └─ Enables: Cross-repo capability mapping

Phase 74 (Role-Based LENS Dashboard)
  ├─ Depends on: Phase 71 + 72 + 73 complete
  ├─ Unblocks: Phase 75+ (advanced visualization)
  └─ Enables: Business + engineering intelligence views
```

---

## 📋 Quick Reference: What Gets Built

### S1 Schema Deliverables
```
cortex/lens/schemas/
├── ldv1_schema.json           # JSON Schema for all artifacts
├── evidence_protocol.py        # EvidenceItem, confidence scoring
├── artifact_registry.yaml      # Manifest + per-artifact specs
└── __init__.py

tests/
└── test_lens_schema.py         # 45 tests (validation, evidence, registry)
```

### S2 Analyzer Enhancements
```
cortex/lens/analyzers/
├── git_history_analyzer.py     # + evidence[] + confidence: 1.0
├── (cortex/brain/analysis/)
│   ├── ast_analyzer.py         # + evidence[] + confidence: 1.0
│   ├── comment_extractor.py    # + evidence[] + confidence: 0.9
│   └── security_threat_analyzer.py  # + evidence[] + confidence: 0.7-95

tests/
└── test_lens_analyzers.py      # 45 tests (per-analyzer + integration)
```

### S3 Incremental Extraction
```
cortex/lens/
├── incremental_extraction.py    # IncrementalExtractor class
├── cache/
│   └── lens_cache.py           # Enhanced (git commit SHA keys)
└── __init__.py

tests/
└── test_incremental_extraction.py  # 45 tests (cache, perf, fallback)
```

### S4 Manifest Publishing
```
cortex/lens/publisher/
├── lens_manifest_publisher.py   # Outputs index.json + 9 artifacts
└── __init__.py

cortex/lens/loader/
├── lens_manifest_loader.py      # Lazy-loads per artifact
└── __init__.py

tests/
└── test_lens_manifest.py        # 45 tests (publish, lazy-load, validate)
```

### S5 Documentation
```
cortex/lens/
├── ldv1_integration_guide.md    # Spec + adapter protocol + examples
└── __init__.py

cortex-registry/_cortex-master/specifications/
└── ldv1-standard.yaml           # Canonical LDv1 specification

tests/
└── test_lens_integration_e2e.py # 15 end-to-end tests
```

---

## 🚀 Critical Success Factors

1. **Schema-First:** Define LDv1 before retrofitting analyzers (S1 must complete before S2)
2. **Evidence Everywhere:** No shortcuts; every output gets evidence[] + confidence
3. **Backward Compat:** Old LENS consumers must still work (no breaking changes)
4. **Measurement:** Baseline perf before S3; verify 10x improvement after
5. **Integration-Ready:** Phase 71 must leave Phase 72 completely unblocked

---

## ⚠️ Risk Mitigation (Fast Fail + Escalate)

| Risk | If Happens | Action |
|------|-----------|--------|
| Schema too strict | S1 day 3 | Add backward compat mode; alert lead |
| Analyzer overhead >10% | S2 mid-week | Profile + optimize; document trade-off |
| Cache invalidation fails | S3 day 2 | Fall back to full extract + hash-check |
| SPA integration complex | S4 day 2 | Extend S4-S5 timeline by 2 days |
| New gap discovered | Any stage | Use 2-3 day buffer in schedule |

---

## ✅ Next Actions (This Week)

- [ ] Review Phase 71 YAML + Executive Summary
- [ ] Approve budget: 94 hours + 30 hour contingency
- [ ] Assign tech lead (LENS domain expert)
- [ ] Create feature branch: `phase-71-lens-ldv1`
- [ ] Schedule kickoff meeting with team

---

**Phase 71 is the foundation. Everything after depends on it.**
