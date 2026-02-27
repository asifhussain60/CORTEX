# LENS Synthesis

---
title: LENS Synthesis — Combining Analyzer Outputs
type: explanation
audience: [Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/lens/lens_orchestrator.py + cortex/intelligence/provider.py
order: 4
---

## What Is Synthesis?

Synthesis is the final stage of the LENS pipeline — combining the outputs of all 15 parallel analyzer components into a unified `LENSContext`, then feeding that into `UnifiedIntelligenceProvider` which layers in company domain knowledge, ADO sprint context, and CORTEX best practices before delivering a `UnifiedIntelligenceContext` to MasterOrchestrator.

**Brain analogy:** This is the **association cortex** — where separate sensory streams (vision, hearing, touch) are combined into a coherent perception. LENS Synthesis merges AST structure with git patterns with security findings into one unified understanding.

## How It Works

1. All 15 analyzer components produce independent results
2. The `lens_orchestrator.py` waits for all results (parallel completion)
3. Results are merged into a single `LENSContext` object
4. Conflicts are resolved (e.g., different confidence scores for the same module)
5. The unified context passes to `UnifiedIntelligenceProvider` for enrichment
6. Enriched `UnifiedIntelligenceContext` is delivered to MasterOrchestrator

## UnifiedIntelligenceProvider — 3-Tier Execution Model

`cortex/intelligence/provider.py` exposes three execution tiers with latency SLAs:

| Tier | Latency | Scope | Used by |
|------|---------|-------|---------|
| **quick()** | <200ms | Cached CORE rules + company domain YAML (TTL cache) | Stage 1 — Interaction |
| **targeted()** | <2s | LENS git+AST+comments + company domains + domain profile | IMPLEMENT / FIX / REFACTOR |
| **full()** | <10s | All of targeted + ADO sprint context + KG entity indexing + cross-domain synthesis | INVESTIGATE (deep analysis) |

## Company Domain Layer (Phase 18)

`UnifiedIntelligenceProvider` loads `cortex-registry/company/domains/*.yaml` on every call via `CompanyDomainLoader` (5-minute TTL cache). Company knowledge takes **precedence over CORTEX defaults** (`CompanyKnowledge.precedence = "OVERRIDE"`).

Sources loaded per tier:

| Source | Quick | Targeted | Full |
|--------|-------|----------|------|
| CORE rules (22 active, 35 defined) | ✅ | ✅ | ✅ |
| company/domains/*.yaml | ✅ | ✅ | ✅ |
| knowledge-base/profiles/{domain}.yaml | — | ✅ | ✅ |
| patterns/*.yaml (9 canonical patterns) | — | ✅ | ✅ |
| ADO sprint context (ADO_ORG_URL guard) | — | — | ✅ |
| KG entity indexing (profiles + repos) | — | — | ✅ |

## ADO Sprint Context (Phase 20)

When `ADO_ORG_URL` is set, `full()` calls `ADOWorkItemProvider.fetch_user_stories()` and maps the result through `ADOContextMapper` to extract:
- `sprint_name` — from `System.IterationPath` (last path segment)
- `stories` — list of `{id, title, state, area_path}`
- `open_count` / `in_progress_count`

Sprint context is injected into `company_knowledge.domain_rules["sprint_context"]`. When `ADO_ORG_URL` is absent, the call is silently skipped.

## LENSContext Contents

| Field | Source Analyzer | Type |
|-------|----------------|------|
| code_structure | AST | Syntax tree, symbols |
| change_patterns | Git History | Heatmap, authors |
| documentation | Comment | Coverage score, gaps |
| dependencies | Import | Graph, circular chains |
| security_findings | Security | Vulnerabilities with severity |
| architecture_patterns | Pattern | Matches with confidence |
| quality_metrics | Metrics | Complexity, coupling |
| domain_context | Domain | Industry, regulations |
| tech_stack | Tech Stack | Framework list, detected tools |

---

*Verified against LENS pipeline and UnifiedIntelligenceProvider · 25 February 2026*
