# Feature: Cross-Session Continuation
**F006** | 🟡 MEDIUM | Phase 5

## Purpose
Resume long-running epics across sessions via Tier 1 integration and state persistence.

## Components
- CONTINUATION-PROMPT.md generation
- PlanningStateDB persistence
- progress-tracker.json updates
- Tier 1 working memory queries
- Last completed phase tracking
- Next phase to execute

## Dependencies
F001 (Planning)
