# IntentRouter

---
title: IntentRouter — LENS-Based Request Classification
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/core/intent_router.py
order: 3
---

## Purpose

IntentRouter classifies every incoming request into one of 12+ intent types using LENS-based intelligence. Classification takes 20–40ms.

**Location:** `cortex/orchestrators/core/intent_router.py`

**Implements:** `IOrchestrator`

## Intent Types

| Intent | Target Orchestrator |
|--------|-------------------|
| IMPLEMENT | TDDOrchestrator |
| FIX | TDDOrchestrator |
| REFACTOR | RefactoringOrchestrator |
| ANALYZE | LENS Synthesis |
| PLAN | PlanningOrchestrator |
| AUDIT | EnforcementOrchestrator |
| DESIGN | Design coordination |
| DEBUG | DebuggerOrchestrator |
| INVESTIGATE | IntelligenceOrchestrator |
| QUERY | Context-dependent |
| DIGEST | Digest coordination |
| REPHRASE | RequestRephraseOrchestrator |

## Phase 11 Enhancement

Phase 11 (Gap Remediation) added routing for 5 previously missing modes: DESIGN, QUERY, DIGEST, REPHRASE, and extended INVESTIGATE routing.

---

*Verified against intent_router.py · 20 February 2026*
