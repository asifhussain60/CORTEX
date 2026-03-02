---
id: governance-rule-enforcement-tiers
title: Governance rule enforcement (4-tier precedence)
purpose: Show how 32 CORE governance rules are enforced at 3 checkpoints with a 4-tier precedence hierarchy that prevents compliance gaps.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/core/
  - cortex/governance/
  - cortex/orchestrators/core/enforcement_orchestrator.py
last_verified: 2026-03-02
diagram_type: Governance
render: ascii
---

# Governance Rule Enforcement — 4-Tier Precedence

## 32 Rules Enforced at 3 Checkpoints

```
 ═══════════════════════════════════════════════════════════════════════════════
  Code changes must pass through ALL 3 enforcement checkpoints.
  No bypass. No exceptions. No "ship it anyway."
 ═══════════════════════════════════════════════════════════════════════════════

  Developer writes code
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CHECKPOINT 1: PRE-EXECUTION (Stage 0 Governance Audit)              │
  │                                                                      │
  │  Runs BEFORE any orchestrator receives the request.                  │
  │  Checks: TDD bypass attempt, .md file scope, audit trail integrity   │
  │                                                                      │
  │  ⛔ VIOLATION → request rejected before work begins                  │
  └──────────────────────────┬───────────────────────────────────────────┘
                             │ PASS ✅
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CHECKPOINT 2: PRE-COMMIT (EnforcementOrchestrator)                  │
  │                                                                      │
  │  Runs AFTER implementation, BEFORE code enters version control.      │
  │                                                                      │
  │  Validates:                                                          │
  │  • CORE-008: TDD cycle completed (RED → GREEN → REFACTOR)           │
  │  • CORE-011: Type hints on all functions                             │
  │  • CORE-012: Docstrings on all public APIs                           │
  │  • CORE-028: File naming — snake_case only                           │
  │  • CORE-035: No duplicate implementations                            │
  │  • CORE-064: Sweep catalogue — all instances fixed                   │
  │  • CORE-068: Convergence gate passed                                 │
  │  • Security: no credentials, no vulnerable dependencies              │
  │                                                                      │
  │  ⛔ VIOLATION → commit blocked, remediation steps shown inline       │
  └──────────────────────────┬───────────────────────────────────────────┘
                             │ PASS ✅
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CHECKPOINT 3: CI / RUNTIME (Continuous Enforcement)                  │
  │                                                                      │
  │  Runs in CI pipeline and during /audit fix scans.                    │
  │                                                                      │
  │  20-point production readiness audit                                 │
  │  Convergence loop: detect → fix → rescan (CORE-068)                  │
  │  Health check: all orchestrator endpoints responsive                 │
  │                                                                      │
  │  ⛔ VIOLATION → P0/P1 issues block release                           │
  └──────────────────────────────────────────────────────────────────────┘
```

## 4-Tier Rule Precedence (Conflict Resolution)

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  TIER 0: IMMUTABLE (highest — cannot be overridden by anyone)       │
  │  ═══════════════════════════════════════════                         │
  │  CORE-008 TDD Mandatory                                             │
  │  CORE-011 Type Hints                                                │
  │  CORE-035 No Duplicates                                             │
  │  CORE-064 Sweep Completeness                                        │
  │  CORE-068 Convergence Gate                                          │
  │  ──────────────────────────────────────────────────────             │
  │                         ▲ WINS over all below                       │
  │                                                                     │
  │  TIER 1: BUSINESS (set by leadership)                               │
  │  ═══════════════════════════════════                                 │
  │  Company security policies                                          │
  │  Compliance requirements (SOX, HIPAA, etc.)                         │
  │  ──────────────────────────────────────────────────────             │
  │                         ▲ WINS over Tier 2 and 3                    │
  │                                                                     │
  │  TIER 2: ENGINEERING (team conventions)                              │
  │  ═════════════════════════════════════                               │
  │  Code style, import ordering, naming patterns                       │
  │  ──────────────────────────────────────────────────────             │
  │                         ▲ WINS over Tier 3                          │
  │                                                                     │
  │  TIER 3: LEARNED (patterns from experience)                          │
  │  ═══════════════════════════════════════════                         │
  │  Heuristics discovered via RCA and usage patterns                   │
  │  Grow stronger with evidence, weakest by default                    │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘

  When rules conflict: highest tier ALWAYS wins.
  Like federal law overriding city ordinances.
```

**Business impact:** Compliance is automated, not aspirational. Rules are enforced at 3 checkpoints — before work, before commit, and in CI. No human discipline required. Tier 0 rules are literally impossible to bypass.
