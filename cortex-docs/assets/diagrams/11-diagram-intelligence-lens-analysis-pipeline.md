---
id: intelligence-lens-analysis-pipeline
title: LENS intelligence pipeline (4-layer code analysis)
purpose: Show how CORTEX understands codebases through evidence-based multi-layer analysis before making any decision.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/lens/
  - cortex/intelligence/provider.py
last_verified: 2026-03-01
diagram_type: Intelligence
render: ascii
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
