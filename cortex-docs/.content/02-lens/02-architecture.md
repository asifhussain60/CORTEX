# LENS Architecture

---
title: LENS Internal Architecture
type: explanation
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/lens/
order: 2
---

## Architecture Overview

```
cortex/lens/
├── analyzers/              15 specialized analysis components
├── adapters/               Language-specific adapters (Python, TS, C#)
├── cache/                  Analysis result caching layer
├── cache.py                Cache utilities
├── cached_lens_orchestrator.py   Cache-aware pipeline orchestration
├── capability_discovery.py       Capability detection
├── core.py                       Core LENS types and utilities
├── crawler_generator.py          Repository crawling
├── dashboard_data_aggregator.py  Aggregates data for dashboards
├── discovery/                    File and module discovery
├── dotnet/                       .NET-specific analysis
├── dotnet_analyzer.py            .NET analyzer entry point
├── extractors/                   Data extraction utilities
├── facade.py                     Simplified consumer API
├── infrastructure_integration.py Infrastructure awareness
├── lens_orchestrator.py          Main LENS pipeline coordinator
├── lens_registry.py              Analyzer registration
├── lens_tiered_mcp_api.py        MCP API integration
├── ml_patterns/                  Machine learning pattern detection
├── models/                       Data models
├── orchestrator.py               Orchestrator base for LENS
├── schemas/                      Output validation schemas
└── templates/                    Output formatting
```

---

## Pipeline Flow

```
[Source Files Discovered]
        │
        ▼
[Language Detection] ── which adapter to use?
        │
        ▼
[Cache Check] ── has this file been analyzed recently?
        │
        ├── Cache HIT → return cached results
        └── Cache MISS ↓
        │
        ▼
[15 Parallel Analyzer Components Launch]
        │
        ├── AST Analyzer
        ├── Git History Analyzer
        ├── Comment Analyzer
        ├── Import Analyzer
        ├── Security Analyzer
        ├── Pattern Analyzer
        ├── Metrics Analyzer
        └── Domain Analyzer
        │
        ▼
[Results Synthesis]
        │
        ▼
[Cache Store] ── save for future lookups
        │
        ▼
[LENSContext] ── unified output to Brain
```

---

## Key Design Decisions

1. **Parallel execution:** All 15 analyzer components run concurrently — total latency is bounded by the slowest analyzer, not the sum
2. **Cache-first:** `cached_lens_orchestrator.py` checks cache before launching analyzers
3. **Adapter pattern:** Language-specific logic is isolated in `adapters/` — adding a new language means adding an adapter
4. **Facade API:** `facade.py` provides a simplified API so consumers don't need to know the pipeline internals

---

*Verified against `cortex/lens/` directory · 25 February 2026*
