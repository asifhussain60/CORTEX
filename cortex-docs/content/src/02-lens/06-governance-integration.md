# LENS Governance Integration

---
title: LENS + Governance — Intelligence-Driven Rule Enforcement
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/lens/ + cortex/orchestrators/core/enforcement_orchestrator.py
order: 6
---

## How LENS Feeds Governance

LENS analyzer output directly informs governance enforcement:

| LENS Analyzer | Governance Rule | What Gets Checked |
|---------------|----------------|-------------------|
| AST | CORE-011 (Type Hints) | Functions without type annotations flagged |
| AST | CORE-012 (Docstrings) | Public APIs without docstrings flagged |
| Import | CORE-035 (Single Canonical) | Duplicate imports detected |
| Security | CORE-013 (Error Handling) | Unhandled exceptions flagged |
| Metrics | CORE-001 (Incremental) | Excessive complexity flagged |
| Comment | CORE-012 (Docstrings) | Documentation coverage below threshold |

The EnforcementOrchestrator's 7 agents consume LENS data to make enforcement decisions. Without LENS, governance would be static rule-checking. With LENS, it's **intelligence-driven**.

**Brain analogy:** LENS is the perception feeding the immune system. Your immune system needs to "see" the threat (via antibodies binding to antigens) before it can mount a response. LENS provides the "sight" for governance enforcement.

---

*Verified against enforcement integration · 20 February 2026*
