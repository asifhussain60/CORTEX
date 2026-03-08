---
id: quality-code-review-multi-pass-pipeline
title: Code Review Orchestrator — 5-pass automated review pipeline
purpose: Show how the Code Review Orchestrator runs five sequential review passes with cumulative findings and priority-ranked output.
audience:
  - Software Developers
  - Quality Engineers
  - Product Owners
source_of_truth:
  - cortex/orchestrators/domain/code_review_orchestrator.py
  - cortex-registry/workflows/templates/sdlc/implement-workflow.yaml
last_verified: 2026-03-04
diagram_type: Workflow
render: ascii
---

# Code Review Orchestrator — 5-Pass Automated Pipeline

## From Changeset to Priority-Ranked Findings

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX CODE REVIEW ORCHESTRATOR — 5-PASS MULTI-DIMENSION REVIEW
 ═══════════════════════════════════════════════════════════════════════════════

  Git Changeset / PR Diff
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PASS 1 — STRUCTURAL ANALYSIS                                       │
  │  ┌────────────────────────────────────────────────────────────┐      │
  │  │  • Cyclomatic complexity per function                      │      │
  │  │  • Class/function size thresholds (SOLID)                  │      │
  │  │  • Dependency coupling metrics                             │      │
  │  │  • Import graph analysis                                   │      │
  │  └────────────────────────────────────────────────────────────┘      │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │ findings[]
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PASS 2 — SECURITY SCAN                                              │
  │  ┌────────────────────────────────────────────────────────────┐      │
  │  │  • Hardcoded secrets / PII detection (CORE-028)            │      │
  │  │  • SQL/command injection patterns                          │      │
  │  │  • Unvalidated input paths                                 │      │
  │  │  • Auth/authz coverage verification                        │      │
  │  └────────────────────────────────────────────────────────────┘      │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │ findings[]
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PASS 3 — GOVERNANCE COMPLIANCE                                      │
  │  ┌────────────────────────────────────────────────────────────┐      │
  │  │  • 60+ CORE rules (type hints, docstrings, naming)        │      │
  │  │  • Error handling on every path                            │      │
  │  │  • Logging and observability standards                     │      │
  │  │  • TDD requirement validation (CORE-008)                   │      │
  │  └────────────────────────────────────────────────────────────┘      │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │ findings[]
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PASS 4 — TEST COVERAGE                                              │
  │  ┌────────────────────────────────────────────────────────────┐      │
  │  │  • Branch coverage analysis on changed lines               │      │
  │  │  • Missing edge-case tests                                 │      │
  │  │  • Mutation testing suggestions                            │      │
  │  │  • Integration test gap detection                          │      │
  │  └────────────────────────────────────────────────────────────┘      │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │ findings[]
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PASS 5 — STYLE & CONSISTENCY                                        │
  │  ┌────────────────────────────────────────────────────────────┐      │
  │  │  • Naming convention adherence (snake_case)                │      │
  │  │  • Code formatting (ruff/black alignment)                  │      │
  │  │  • Documentation completeness                              │      │
  │  │  • API contract consistency                                │      │
  │  └────────────────────────────────────────────────────────────┘      │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PRIORITY-RANKED OUTPUT                                              │
  │                                                                      │
  │  P0 ████████ BLOCKING   — merge blocked until resolved               │
  │  P1 ██████   REQUIRED   — must fix within this PR                    │
  │  P2 ████     SUGGESTED  — recommended improvement                    │
  │  P3 ██       NOTED      — tracked as tech debt                       │
  │                                                                      │
  │  Quality Score: 87/100                                               │
  │  → Feeds into Quality Analysis Engine composite scoring              │
  └──────────────────────────────────────────────────────────────────────┘
```

## Integration Points

```
  Code Review Orchestrator
         │
         ├── cortex_review MCP tool (developer-facing)
         ├── Quality Analysis Engine (score aggregation)
         ├── Governance Engine (rule enforcement)
         └── URS Learning Loop (review pattern refincement)
```
