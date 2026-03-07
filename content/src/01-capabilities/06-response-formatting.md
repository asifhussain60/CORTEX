# Response Formatting & Content Blocks

---
title: CORTEX Response Formatting Standards
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex-registry/core/ + .github/templates/cortex-response-templates.md
order: 6
---

> **Brain analogy:** Response formatting is the **Broca's area** — the brain region responsible for speech production. It doesn't decide *what* to say (that's Reasoning); it decides *how* to say it clearly, consistently, and appropriately for the audience.

---

## Formatting Principles

CORTEX responses follow strict formatting standards (loaded from `cortex-registry/`):

1. **Inline delivery** — CORE-002: never create `.md` or `.txt` report files
2. **Structured output** — tables, code blocks, and hierarchical sections
3. **Role-aware** — different detail levels for Business Leaders, Product Owners, and Developers
4. **Silent execution** — CORE-049: progress bars only, no verbose chatter

---

## Response Structure

Every CORTEX response follows this structure:

```
## 🧠 CORTEX {Mode}
**Author:** Asif Hussain | **Orchestrator:** {OrchestratorName} ✅

---

### 📋 Intent Classification
| Field     | Value                    |
|-----------|--------------------------|
| Intent    | {IMPLEMENT/FIX/ANALYZE}  |
| Handler   | {OrchestratorClass}      |
| Confidence| {score}                  |

---

{Content delivered inline}

---

### ✅ Summary
- Tests: {count} passing
- Governance: {PASS/WARNING}
- Duration: {time}
```

---

## Workflow Templates

Workflow templates in `cortex-registry/workflows/templates/` define execution patterns:

| Template Category | Location | Purpose |
|------------------|----------|---------|
| **lifecycle/** | CORTEX-internal workflows | Phase execution, master plan orchestration |
| **production/** | External workflows | Production deployment, rollback |

Templates are read by the WorkflowEngine (`cortex/core/workflow_engine.py`) and executed as phase sequences.

---

## Practical Examples

**Product Owner:** "Every response I see follows the same format — intent classification, content, summary. I always know what orchestrator handled it, what tests passed, and what governance checks ran."

**Developer:** "Responses are inline (CORE-002). I never need to hunt for a generated report file. Everything appears directly in my IDE."

---

*Verified against response template standards · 20 February 2026*
