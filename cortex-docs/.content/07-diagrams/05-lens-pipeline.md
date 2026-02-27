# LENS Pipeline

---
title: LENS Analysis Pipeline Diagram
type: diagram
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/lens/
order: 5
---

## 8-Analyzer Parallel Pipeline

```
                    SOURCE CODE INPUT
                         │
                         ▼
            ┌────────────────────────┐
            │    LENS Controller     │
            │    cortex/lens/        │
            └────────────┬───────────┘
                         │
            ┌────────────┴───────────┐
            │   PARALLEL DISPATCH    │
            │   (all 8 concurrent)   │
            └────────────┬───────────┘
                         │
     ┌───────┬───────┬───┴───┬───────┬───────┬───────┬───────┐
     ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼
  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌──────┐
  │ AST │ │ Git │ │Commt│ │Imprt│ │Secur│ │Pattn│ │Metrc│ │Domain│
  │     │ │Hist.│ │     │ │     │ │ity  │ │     │ │     │ │      │
  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬───┘
     │       │       │       │       │       │       │       │
     │  structure   history  docs   deps  vulns  patterns  sizes  domain
     │  classes    commits  quality  graph  issues  matches  complexity
     │  functions  authors                                   knowledge
     │
     └───────┴───────┴───────┴───────┴───────┴───────┴───────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │      SYNTHESIS         │
                 │                        │
                 │  Merge 8 analyzer      │
                 │  results into unified  │
                 │  intelligence report   │
                 │                        │
                 │  • Confidence score    │
                 │  • Risk assessment     │
                 │  • Recommendations     │
                 │  • Cross-references    │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   CACHE (optional)     │
                 │   TTL-based storage    │
                 │   Skip if cached       │
                 └────────────┬───────────┘
                              │
                              ▼
                    LENS ANALYSIS RESULT
                    (300-800ms total)
```

## Analyzer Details

```
┌──────────────────────────────────────────────────────────┐
│                    ANALYZER MATRIX                       │
├─────────────┬────────────────────────────────────────────┤
│ Analyzer    │ Extracts                                   │
├─────────────┼────────────────────────────────────────────┤
│ AST         │ Classes, functions, inheritance, complexity │
│ Git History │ Commit frequency, authors, churn rate       │
│ Comment     │ Documentation quality, TODO/FIXME count     │
│ Import      │ Dependency graph, circular imports          │
│ Security    │ Vulnerabilities, secret patterns, CVEs      │
│ Pattern     │ Design patterns, anti-patterns detected     │
│ Metrics     │ Lines, complexity, duplication ratio         │
│ Domain      │ Business domain knowledge alignment         │
└─────────────┴────────────────────────────────────────────┘
```

## LENS Acronym

```
L ─── Language    → AST analysis, syntax understanding
E ─── Examination → Deep code inspection (metrics, patterns)
N ─── Navigation  → Dependency graph, import chains
S ─── Synthesis   → Merge all findings into actionable report
```

---

*Verified against `cortex/lens/` with parallel analyzers*
