---
id: architecture-package-and-directory-map
title: Package and directory map
purpose: Provide a single diagram showing where every major CORTEX system lives, what it does, and how the pieces connect.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/
  - cortex-registry/
  - tests/
last_verified: 2026-03-03
diagram_type: Architecture
render: ascii
render_html: true
d3_method: "d3.tree() — directory tree with expandable nodes"
---

# Package & Directory Map

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │  REPO ROOT                                                                  │
 │                                                                             │
 │  cortex/                          ← Single canonical Python package         │
 │  ├── orchestrators/               ← 320 files across 15 domains           │
 │  │   ├── core/                       MasterOrch, IntentRouter, TDD, Enforce │
 │  │   ├── domain/                     Onboarding, Planning, Design           │
 │  │   ├── support/                    Debug, Sweep, Refactoring              │
 │  │   ├── health/                     Health, Vacuum                         │
 │  │   ├── workflow/                   WorkflowComposer, TemplateComposer     │
 │  │   ├── intelligence/               LENS-backed intelligence orchestrators │
 │  │   ├── git/                        GitOrchestrator, sync pipeline         │
 │  │   ├── persona/                    Role-based persona orchestrators       │
 │  │   ├── validation/                 Contract + wiring validation           │
 │  │   └── ... (15 domains total)                                             │
 │  ├── mcp/                         ← MCP stdio server + 30 registered tools  │
 │  │   └── tools/                      54 tool files                          │
 │  ├── lens/                        ← LENS analysis engine (8 analyzers)      │
 │  ├── intelligence/                ← Reasoning, learning, RCA engine         │
 │  │   ├── facade.py               ← IntelligenceFacade — canonical entry (Phase 107) │
 │  │   └── learning/                   rca_engine.py, rca_store.py            │
 │  ├── governance/                  ← Rule enforcement, compliance            │
 │  ├── knowledge/                   ← Knowledge base, domain synthesis        │
 │  ├── core/                        ← OrchestratorProtocolMixin, FileFactory  │
 │  ├── testing/                     ← Test framework, parallel runner         │
 │  ├── infrastructure/              ← Tracing, metrics, cache, security       │
 │  └── config/                      ← Settings, environment                   │
 │                                                                             │
 │  cortex-registry/                 ← Configuration as code (YAML)            │
 │  ├── core/                           55+ governance rules across core/ + governance/ │
 │  │   └── specifications/             4 wiring contract YAMLs               │
 │  ├── workflows/templates/            3-tier: primitives → templates →       │
 │  │   ├── primitives/                    composites                          │
 │  │   ├── sdlc/                                                              │
 │  │   ├── audit/                                                             │
 │  │   └── ...                                                                │
 │  └── planning/phases/                Phase specs (planned/ → completed/)    │
 │                                                                             │
 │  tests/                           ← Mirrors cortex/ structure               │
 │  ├── orchestrators/                  Unit + integration                     │
 │  ├── mcp/                            MCP tool tests                        │
 │  ├── golden/                         Deterministic truth tests             │
 │  └── preflight/                      < 10s critical wiring checks          │
 │                                                                             │
 │  cortex-docs/                     ← GitHub Pages site (HTML/CSS only)       │
 │  .github/                         ← Prompts, agents, templates, CI/CD       │
 │  .cortex-runtime/                 ← Runtime data (7 SQLite DBs, traces)     │
 │  scripts/                         ← Build tools, test runner, refresh       │
 └─────────────────────────────────────────────────────────────────────────────┘
```

**Key principle:** One package (`cortex`), one registry (`cortex-registry`), one test tree (`tests`). No duplicates. No scattered config.
