# FAQ — LENS & Intelligence

---
title: FAQ — LENS & Intelligence
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/lens/ + cortex/intelligence/
order: 4
---

> **Purpose:** Answers to questions about CORTEX's code intelligence engine (LENS) and the three-tier brain architecture (Perception → Reasoning → Action). All answers verified against live code.

---

## What is LENS?

**LENS** stands for **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. It is CORTEX's code intelligence engine — a pipeline of specialized analyzers that process raw source code into structured intelligence used by orchestrators to make informed decisions.

**Brain analogy:** LENS is the sensory cortex. Just as your visual cortex processes photons into edges and objects, LENS processes source code into patterns, metrics, and security findings.

**Live location:** `cortex/lens/` (analyzers, adapters, cache, models, schemas, discovery, extractors)

---

## How many analyzers does LENS run?

LENS ships **15 analyzer components** in `cortex/lens/analyzers/`, with 9 canonical analyzers in the core parallel pipeline documented in `02-lens/01-overview.md`:

| Analyzer | Class | What It Detects |
|----------|-------|----------------|
| **AST** | `ASTAnalyzer` | Code structure — classes, functions, imports, decorators |
| **Git History** | `GitHistoryAnalyzer` | Change patterns — hot spots, author frequency, recent edits |
| **Comment** | `CommentExtractor` | Documentation quality — coverage, TODO/FIXME density |
| **Dependency** | `DependencyAnalyzer` | Circular imports, stale imports, depth |
| **Security** | *(security module)* | Vulnerabilities — SQL injection, XSS, credentials, CVEs |
| **Pattern** | *(pattern module)* | Architecture — framework signatures, design pattern usage |
| **Metrics** | *(metrics module)* | Complexity — cyclomatic, coupling, LOC, maintainability |
| **Domain** | *(domain module)* | Business context — industry, vertical, regulatory |
| **Tech Stack** | `TechStackAnalyzer` | Framework detection — imports, config files, manifests |

Additional analyzers exist in `cortex/lens/analyzers/` (APIAnalyzer, ConfigAnalyzer, DatabaseAnalyzer, EvolutionAnalyzer, PolyglotAnalyzer, PythonAnalyzer) for specialized use cases. All 15 components run via `LENSOrchestrator.analyze_file()`.

---

## How long does a LENS analysis take?

**300–800ms** for a full parallel analysis, depending on repository size. The `CachedLENSOrchestrator` (`cortex/lens/cached_lens_orchestrator.py`) caches results with TTL, reducing repeat analysis to **< 50ms** on cache hit.

Cache statistics (hits, misses, latency) are tracked internally and available via `CachedLENSOrchestrator.get_cache_stats()`.

---

## What languages does LENS support?

| Language | AST | Security | Metrics | Pattern |
|----------|-----|----------|---------|---------|
| **Python** | ✅ Full | ✅ | ✅ | ✅ |
| **TypeScript/JavaScript** | ✅ Full | ✅ | ✅ | ✅ |
| **C# / .NET** | ✅ Full | ✅ | ✅ | ✅ |
| **Angular** | ✅ | ✅ | ✅ | ✅ |
| **React** | ✅ | ✅ | ✅ | ✅ |
| **SQL** | Partial | ✅ | — | — |

Language detection is handled by `PolyglotAnalyzer` — it identifies the primary and secondary languages before dispatching to language-specific adapters in `cortex/lens/adapters/`.

---

## What is the LENS Facade?

`cortex/lens/facade.py` provides a simplified single-import API for LENS consumers:

```python
from cortex.lens.facade import LENSFacade

facade = LENSFacade()
result = await facade.analyze(path="/path/to/repo")
# result contains: ast_data, git_patterns, security_findings,
#                  metrics, patterns, domain_context, tech_stack
```

Most orchestrators consume LENS through the facade rather than calling individual analyzers directly — this decouples orchestrators from the analyzer implementation details.

---

## What is the Brain Tier architecture?

The three-layer cognitive core of CORTEX, housed in `cortex/intelligence/`:

| Tier | Location | Role | Brain Analogy |
|------|----------|------|--------------|
| **Perception** | `cortex/intelligence/perception/` | Recognizes patterns in LENS data | Sensory cortex — what is happening? |
| **Reasoning** | `cortex/intelligence/reasoning/` | Selects strategies based on patterns | Prefrontal cortex — what should we do? |
| **Action** | `cortex/intelligence/action/` | Builds step-by-step execution plans | Motor cortex — how do we execute? |

LENS feeds the Perception tier. Perception feeds Reasoning. Reasoning feeds Action. Action feeds the orchestrator dispatch layer.

---

## What are confidence scores and how do they affect routing?

Every classification and pattern match produces a **confidence score** (0.0–1.0):

| Range | Behaviour |
|-------|-----------|
| **≥ 0.7** | Auto-execute — CORTEX proceeds without asking |
| **0.5–0.7** | May ask for clarification or present options |
| **< 0.5** | Prompts the user before acting |

Confidence scores are produced by:
- IntentRouter's `detect_intent()` method
- Perception tier's pattern matcher (`cortex/intelligence/perception/`)
- LENS analyzer outputs (security severity, pattern confidence)

---

## What is the Domain Brain?

`cortex/intelligence/domain_brain/` is a domain-specific knowledge module that provides business context for decisions. It maps detected domain classifications (from the LENS Domain analyzer) to:

- Industry-specific governance constraints (e.g. HIPAA, PCI-DSS patterns)
- Domain-relevant architecture patterns
- Regulatory context for security findings

The Domain Brain is populated by `cortex/core/brain_populator.py` from `cortex/intelligence/` data.

---

## What is Company Domain Synthesis?

**Company Domain Synthesis** (`02-lens/05-company-domain-synthesis.md`) is LENS's ability to build a composite domain model from an entire organization's codebase — not just a single repository.

When CORTEX onboards multiple repositories (via `BulkDigestOrchestrator`), LENS synthesizes cross-repo patterns into a unified company domain model. This enables:
- Detecting the same vulnerability pattern across 5 repos simultaneously
- Identifying shared architectural drift
- Recommending consistent refactoring patterns org-wide

---

## How does LENS caching work?

LENS uses a two-level cache (`cortex/lens/cache/` + `cortex/lens/cache.py`):

1. **In-memory LRU cache** — for the current session. Zero latency on hit.
2. **Persistent SQLite cache** — survives session restarts. Sub-50ms on hit.

Cache keys are derived from the file path + content hash. A file modification invalidates only that file's cached entries — the rest of the analysis remains valid.

`CachedLENSOrchestrator` wraps `LENSOrchestrator` with transparent caching. If the cache is stale or corrupted, it falls back to a fresh analysis gracefully.

---

## Can I run LENS on an external repository?

Yes — via `cortex_onboard` (MCP tool) or `RepositoryOnboardingOrchestrator`:

```python
# Via MCP tool in Copilot Chat:
# Call cortex_onboard with {"path": "/path/to/external/repo"}

# Via orchestrator:
from cortex.orchestrators.support.repository_onboarding_orchestrator import RepositoryOnboardingOrchestrator
orch = RepositoryOnboardingOrchestrator()
result = await orch.execute({"path": "/path/to/external/repo"})
```

The onboarding pipeline runs LENS (full 15-component pass), scores security findings (P0/P1/P2), and stores results in `.cortex-runtime/` for subsequent queries.

---

## What is LENS Governance Integration?

LENS feeds directly into governance enforcement (`02-lens/06-governance-integration.md`):

1. **Security findings** → EnforcementOrchestrator's SecurityScanAgent evaluates severity
2. **Complexity metrics** → High cyclomatic complexity triggers architectural review suggestions
3. **Import graph** → ImportValidationAgent uses LENS dependency data to detect circular imports
4. **Pattern matches** → Pattern registry validates against 9 enterprise patterns

LENS doesn't make governance decisions — it provides the data. Governance decisions are made by EnforcementOrchestrator's agents.

---

*Verified against `cortex/lens/` + `cortex/intelligence/`*
