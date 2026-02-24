# LENS Overview

---
title: LENS — Language Examination Navigation Synthesis
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-24
source_of_truth: cortex/lens/
order: 1
---

> **Brain analogy:** LENS is CORTEX's **sensory cortex** — the brain region that processes raw sensory input into structured perception. Just as your visual cortex processes photons into edges, shapes, and objects, LENS processes source code into patterns, metrics, and intelligence.

---

## What Is LENS?

**L**anguage → **E**xamination → **N**avigation → **S**ynthesis

LENS is CORTEX's code intelligence engine. It runs **9 specialized analyzers in parallel** against any codebase and produces a unified context — structured intelligence that feeds the Brain's Perception → Reasoning → Action pipeline.

**Live location:** `cortex/lens/` (analyzers, adapters, cache, models, schemas, discovery, extractors)

---

## The Four Stages

| Stage | What Happens | Brain Equivalent |
|-------|-------------|-----------------|
| **Language** | Detect programming language, framework, patterns | Visual cortex identifying shapes |
| **Examination** | Deep AST analysis, security scan, metric collection | Pattern recognition centres |
| **Navigation** | Dependency graph, import chains, call hierarchy | Spatial awareness |
| **Synthesis** | Combine all analyzer outputs into unified context | Association cortex — making sense of it all |

---

## 9 Parallel Analyzers

| Analyzer | What It Detects | Output |
|----------|----------------|--------|
| **AST** | Code structure — classes, functions, imports, decorators | Syntax tree, symbol table |
| **Git History** | Change patterns — hot spots, author frequency, recent edits | Change heatmap, risk indicators |
| **Comment** | Documentation quality — coverage, TODO/FIXME density | Documentation score, gap list |
| **Import** | Dependencies — circular imports, stale imports, depth | Dependency graph, import health |
| **Security** | Vulnerabilities — SQL injection, XSS, credentials, CVEs | Finding list with severity |
| **Pattern** | Architecture — framework signatures, design pattern usage | Pattern match list with confidence |
| **Metrics** | Complexity — cyclomatic, coupling, LOC, maintainability | Metric dashboard |
| **Domain** | Business context — industry, vertical, regulatory context | Domain classification |
| **Tech Stack** | Framework detection — imports, config files, dependency manifests | Tech stack fingerprint, framework list |

All 9 run **in parallel**. Combined latency: 300–800ms.

---

## Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Analyzers** | `cortex/lens/analyzers/` | The 8 specialized analysis engines |
| **Adapters** | `cortex/lens/adapters/` | Language-specific adapters (Python, TS, C#) |
| **Cache** | `cortex/lens/cache/` + `cortex/lens/cache.py` | Analysis result caching |
| **Models** | `cortex/lens/models/` | Data models for LENS output |
| **Schemas** | `cortex/lens/schemas/` | Validation schemas for analyzer output |
| **Discovery** | `cortex/lens/discovery/` | File and module discovery |
| **Extractors** | `cortex/lens/extractors/` | Specialized data extraction |
| **Templates** | `cortex/lens/templates/` | Output formatting templates |
| **Orchestrator** | `cortex/lens/lens_orchestrator.py` | LENS pipeline coordinator |
| **Cached Orchestrator** | `cortex/lens/cached_lens_orchestrator.py` | Cache-aware orchestration |
| **Facade** | `cortex/lens/facade.py` | Simplified API for consumers |

---

## Languages Supported

| Language | AST | Security | Metrics | Pattern |
|----------|-----|----------|---------|---------|
| **Python** | ✅ Full | ✅ | ✅ | ✅ |
| **TypeScript/JavaScript** | ✅ Full | ✅ | ✅ | ✅ |
| **C# / .NET** | ✅ Full | ✅ | ✅ | ✅ |
| **Angular** | ✅ | ✅ | ✅ | ✅ |
| **React** | ✅ | ✅ | ✅ | ✅ |
| **Vue** | ✅ | ✅ | ✅ | ✅ |

---

## Practical Examples

**Business Leader:** "LENS gives every repository an instant health scan — like a blood test for code. 8 dimensions, one report, under a second."

**Product Owner:** "Before sprint planning, I run LENS on the target modules. The security analyzer found 3 credential exposure patterns last week that nobody caught in review."

**Developer:** "I call `cortex_onboard_repository` and LENS runs all 8 analyzers. The import analyzer found a circular dependency chain 4 levels deep. The AST analyzer showed 12 functions without type hints. I fixed both before the PR."

---

*All component paths verified against live codebase · 20 February 2026*
