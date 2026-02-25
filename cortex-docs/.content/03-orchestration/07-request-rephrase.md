# RequestRephraseOrchestrator

---
title: RequestRephraseOrchestrator — Automatic Request Enrichment
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-25
source_of_truth: cortex/orchestrators/core/request_rephrase_orchestrator.py
order: 7
---

## Purpose

RequestRephraseOrchestrator runs at **Stage -1** — before any other orchestrator sees the request. It enriches the raw user request with:

- Relevant CORE governance rules
- Breaking-risk assessment
- Design pillar considerations
- Challenge gate flags for high-risk operations

**Location:** `cortex/orchestrators/core/request_rephrase_orchestrator.py`

## Why It Matters

**Business Leader:** "Every request gets a pre-flight safety check — risk assessed, governance rules attached, design implications surfaced. Automatically."

**Product Owner:** "I don't need to remind developers about governance. The system injects the right rules into every request before processing begins."

**Developer:** "When I type 'fix the auth module', Stage -1 enriches it with: CORE-008 (TDD mandatory), CORE-013 (error handling), security context from LENS. By the time MasterOrchestrator sees it, the request is fully contextualised."

---

*Verified against request_rephrase_orchestrator.py · 25 February 2026*
