---
id: intelligence-lens-analysis-pipeline
title: LENS intelligence pipeline + Diamond Facade architecture
purpose: Show how CORTEX understands codebases through evidence-based multi-layer analysis, and how the IntelligenceFacade (Diamond architecture) provides a single entry point for all intelligence operations.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/lens/
  - cortex/intelligence/facade.py
  - cortex/intelligence/provider.py
  - cortex/knowledge/registry_proxy.py
last_verified: 2026-03-09
phase_status: "Phase 107 COMPLETE · Phase 109 COMPLETE · Phase 141 COMPLETE (wiring permanence golden tests)"
diagram_type: Intelligence
render: ascii
render_html: true
d3_method: "d3.tree() — 4-layer pipeline + diamond facade"
---

# LENS Intelligence Pipeline — 4-Layer Code Analysis

```
 ═══════════════════════════════════════════════════════════════════════════════
  LENS: Language → Examination → Navigation → Synthesis
  "Understand the code before touching it"
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  LAYER 1: LANGUAGE (Git History)                                        │
  │                                                                         │
  │  Commits · Authors · Timestamps · Change frequency                      │
  │                                                                         │
  │  Reveals: hotspots, ownership, velocity, churn patterns                 │
  │  Example: "auth/ modified 42 times by 3 authors — high-activity zone"   │
  └──────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  LAYER 2: EXAMINATION (AST Structure)                                   │
  │                                                                         │
  │  Parse tree · Syntax · Dependencies · Complexity metrics                │
  │                                                                         │
  │  Reveals: architecture, circular deps, function complexity, dead code   │
  │  Example: "payment_service.py depends on 7 modules, cyclomatic: 14"    │
  └──────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  LAYER 3: NAVIGATION (Annotations & Comments)                           │
  │                                                                         │
  │  Docstrings · TODO/FIXME · Design decisions · Human intent              │
  │                                                                         │
  │  Reveals: original design intent, known tech debt, planned changes      │
  │  Example: "# TODO: Replace with Redis cache — SQLite won't scale"      │
  └──────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  LAYER 4: SYNTHESIS (Patterns & Anti-Patterns)                          │
  │                                                                         │
  │  Architecture patterns · Enterprise patterns · Best practices           │
  │                                                                         │
  │  Reveals: pattern adherence, anti-patterns, improvement opportunities   │
  │  Example: "Repository pattern detected, but missing Unit of Work"      │
  └──────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CONFIDENCE SCORING                                                     │
  │                                                                         │
  │  Evidence from layers:  1 layer = LOW (<50%)                            │
  │                         2 layers = MEDIUM (50-79%)                      │
  │                         3+ layers = HIGH (80%+)                         │
  │                                                                         │
  │  HIGH confidence → direct recommendation                                │
  │  MEDIUM confidence → recommendation + alternatives                      │
  │  LOW confidence → ask user for clarification                            │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Intelligence Tiers (Response Time)

```
  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
  │    QUICK    │     │   TARGETED   │     │    FULL     │
  │   < 200ms  │     │    < 2s      │     │   < 10s     │
  │             │     │              │     │             │
  │ Cached rules│     │ LENS + YAMLs │     │ LENS + KG + │
  │ only        │     │              │     │ Profiles    │
  │             │     │              │     │             │
  │ Stage 1:   │     │ IMPLEMENT /  │     │ INVESTIGATE │
  │ Interaction │     │ FIX / REFACTOR│     │ (deep)     │
  └─────────────┘     └──────────────┘     └─────────────┘
```

**Business impact:** CORTEX never guesses. Every recommendation is backed by evidence from your actual codebase — git history, code structure, developer comments, and pattern analysis.

---

# Intelligence Diamond — Single Entry Point Architecture

*Phase 107 COMPLETE · Phase 109 COMPLETE*

```
 ═══════════════════════════════════════════════════════════════════════════════
  IntelligenceFacade: Single canonical entry — no more 3-way provider choice
  "One call replaces three imports"
 ═══════════════════════════════════════════════════════════════════════════════

                         ┌───────────────────────────────────┐
                         │          CALLERS (Phase 109)       │
                         │                                   │
                         │  TDDOrchestrator                  │
                         │  EnforcementOrchestrator          │
                         │  IntentRouterImpl                 │
                         │  RefactoringOrchestrator          │
                         │  HealthOrchestrator               │
                         │  VacuumOrchestrator               │
                         │  MasterOrchestratorInit           │
                         │  SecurityVulnerabilityOrchestrator│
                         └─────────────────┬─────────────────┘
                                           │
                              from cortex.intelligence.facade
                              import IntelligenceFacade
                                           │
                                           ▼
                         ┌───────────────────────────────────┐
                         │       IntelligenceFacade          │
                         │   cortex/intelligence/facade.py   │
                         │                                   │
                         │   Mediator — 3 public methods:    │
                         │   · analyze()                     │
                         │   · synthesize()                  │
                         │   · query()                       │
                         └──────────┬─────────┬─────────┬───┘
                                    │         │         │
              ┌─────────────────────┘         │         └────────────────────┐
              │                               │                              │
              ▼                               ▼                              ▼
  ┌───────────────────┐          ┌─────────────────────┐          ┌───────────────────┐
  │   analyze()       │          │   synthesize()       │          │   query()         │
  │                   │          │                      │          │                   │
  │  LENS pipeline    │          │  KnowledgeSynthesis  │          │  KnowledgeRegistry│
  │  (4-layer scan:   │          │  Engine              │          │  Proxy            │
  │   git → AST →     │          │                      │          │                   │
  │   annotations →   │          │  Merges patterns,    │          │  Direct lookup:   │
  │   patterns)       │          │  rules, context      │          │  rules, patterns, │
  │                   │          │  for a given query   │          │  governance       │
  │  Returns:         │          │                      │          │                   │
  │  confidence score │          │  Returns:            │          │  Returns:         │
  │  + evidence dict  │          │  SynthesizedResult   │          │  QueryResult      │
  └───────────────────┘          └─────────────────────┘          └───────────────────┘
         │                                  │                               │
         └──────────────────────────────────┼───────────────────────────────┘
                                            │
                                            ▼
                         ┌───────────────────────────────────┐
                         │     INTELLIGENCE DIAMOND          │
                         │   Target shape (Phase 109-C):     │
                         │                                   │
                         │   cortex/intelligence/            │
                         │     ├── analysis/    (LENS + AST) │
                         │     ├── knowledge/   (synthesis)  │
                         │     ├── learning/    (RCA + mem.) │
                         │     └── models/      (shared)     │
                         │                                   │
                         │  Status: DEFERRED (future sprint) │
                         │  (26 subdirs → 4 canonical dirs)  │
                         └───────────────────────────────────┘
```

## Migration State (Phase 109)

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Orchestrator wiring (Sub-Phase A): ✅ COMPLETE                     │
  │  8 orchestrators rewired → IntelligenceFacade (all GAPs CLOSED)    │
  │                                                                     │
  │  Workflow primitive (Sub-Phase B): ✅ COMPLETE                      │
  │  intelligence-injection.yaml → IntelligenceFacade (not mixin)      │
  │                                                                     │
  │  Dead code cleanup (Sub-Phase D): ✅ COMPLETE                       │
  │  phase97_integration.py deleted (zero importers, confirmed)        │
  │                                                                     │
  │  Directory flatten (Sub-Phase C): ↗ DEFERRED (future sprint)       │
  │  26 subdirs → 4 diamond dirs (analysis/knowledge/learning/models/) │
  │  GAP-109-11 + GAP-109-12 status: OPEN — deferred, not blocking     │
  │                                                                     │
  │  Legacy direct imports (Sub-Phase D cont.): ↗ DEFERRED             │
  │  cortex/tools/ + cortex/mcp/tools/ bypass — tracked for next phase │
  └─────────────────────────────────────────────────────────────────────┘
```

**Business impact:** CORTEX intelligence is now accessible through a single, stable API. Orchestrators that previously had to choose between three different providers now call one facade — reducing coupling, improving testability, and establishing the foundation for the diamond directory structure (Sub-Phase C, deferred to a future sprint).

---

# Knowledge Acquisition Layer (KAL) — Auto-Growing Intelligence

*Phase 137 COMPLETE*

```
 ═══════════════════════════════════════════════════════════════════════════════
  KAL: Detects gaps → Synthesises YAML → Validates → Registers
  "CORTEX grows its own knowledge when coverage drops below 80%"
 ═══════════════════════════════════════════════════════════════════════════════

  LENS Output (domain signals)
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  DomainSignalExtractor                                               │
  │  cortex/intelligence/knowledge/domain_signal_extractor.py           │
  │                                                                      │
  │  Flattens LENS dict → regex pattern matching → domain signal list   │
  │  Loaded from: cortex-registry/config/domain-signal-map.yaml (cached)│
  └──────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  KnowledgeCoverageAssessor                                           │
  │  cortex/intelligence/knowledge/knowledge_coverage_assessor.py       │
  │                                                                      │
  │  Multi-level matching: exact → prefix → keyword containment         │
  │  score < 0.80 → acquisition_needed = True                           │
  └──────────────────────────────┬───────────────────────────────────────┘
                                 │ (if acquisition_needed)
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  KnowledgeAcquisitionOrchestrator                                    │
  │  cortex/intelligence/knowledge/knowledge_acquisition_orchestrator.py│
  │                                                                      │
  │  Per-domain pipeline:                                                │
  │    synthesize → validate (7 rules) → write → register               │
  │                                                                      │
  │  OPJ consultation before loop                                        │
  │  URS MILD_REWARD on success                                          │
  │  IntelligenceFacade cache invalidation post-acquisition             │
  └──────────────────────────────────────────────────────────────────────┘

  7-Rule Schema Validation:
  ✅ Valid YAML syntax     ✅ Required title field
  ✅ Required domain field ✅ best_practices is a list
  ✅ ≥ 3 practice items   ✅ No empty/None practices
  ✅ No duplicate titles (case-insensitive)
```

**Business impact:** CORTEX is designed to detect when its knowledge base is insufficient for the domain under analysis and synthesise validated knowledge YAML files automatically — so recommendations improve without manual library updates.

