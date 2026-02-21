# LENS Synthesis

---
title: LENS Synthesis — Combining Analyzer Outputs
type: explanation
audience: [Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/lens/lens_orchestrator.py
order: 4
---

## What Is Synthesis?

Synthesis is the final stage of the LENS pipeline — combining the outputs of all 8 parallel analyzers into a unified `LENSContext` that feeds the Brain.

**Brain analogy:** This is the **association cortex** — where separate sensory streams (vision, hearing, touch) are combined into a coherent perception. LENS Synthesis merges AST structure with git patterns with security findings into one unified understanding.

## How It Works

1. All 8 analyzers produce independent results
2. The `lens_orchestrator.py` waits for all results (parallel completion)
3. Results are merged into a single `LENSContext` object
4. Conflicts are resolved (e.g., different confidence scores for the same module)
5. The unified context is passed to the Brain's Perception tier

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

---

*Verified against lens pipeline · 20 February 2026*
