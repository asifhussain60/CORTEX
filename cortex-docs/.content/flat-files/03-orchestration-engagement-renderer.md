# EngagementRenderer — Orchestrator Visibility System

---
title: EngagementRenderer — SSOT Breadcrumb Formatting and Orchestrator Visibility
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/response/engagement_renderer.py + .github/templates/cortex-response-templates.md
order: 15
synced_from: 03-orchestration/15-engagement-renderer.md
---

> **The central idea:** Users should always know which orchestrators are active, why, and how long each step took. The EngagementRenderer is the single canonical component that formats all engagement signals — breadcrumbs, timelines, and phase roadmaps.

---

## Why This Exists

Before EngagementRenderer, each orchestrator formatted its own engagement output differently — some used arrows, some used slashes, some omitted routing context entirely. Phase 92 introduced EngagementRenderer as the SSOT formatter for all engagement blocks, ensuring consistent visibility across all operations.

---

## Architecture

**Location:** `cortex/orchestrators/response/engagement_renderer.py`

EngagementRenderer provides three core capabilities:

### 1. Pre-built Command Chains

For the fourteen most common CORTEX commands, EngagementRenderer maintains pre-built routing chains:

| Command | Engagement Chain |
|---------|-----------------|
| `/audit fix` | `IntentRouter → AuditOrchestrator → EnforcementOrchestrator → HealthOrchestrator → VacuumOrchestrator` |
| `/vacuum` | `IntentRouter → VacuumOrchestrator` |
| `/health` | `IntentRouter → HealthOrchestrator` |
| `/debug` | `IntentRouter → DebuggerOrchestrator → MarkerInjectionEngine` |
| `/totalrecall` | `IntentRouter → MasterOrchestrator (7-phase)` |
| `/train` | `IntentRouter → TrainerOrchestrator` |
| `/sync` | `IntentRouter → GitOrchestrator → WorkflowOrchestrator` |
| `/onboard` | `IntentRouter → OnboardingOrchestrator → LENS` |

### 2. Breadcrumb Formatting

`breadcrumb_for_command(command)` returns the canonical `→`-separated breadcrumb for a command. `format_breadcrumb(chain)` renders any routing chain as a formatted breadcrumb string.

### 3. InteractionOrchestrator Integration

Stage 1 of the 4-stage pipeline (InteractionOrchestrator) emits the breadcrumb via EngagementRenderer, ensuring the routing chain is visible from the very first response.

---

## Three Engagement Blocks

| Block | When Rendered | Behaviour |
|-------|-------------|-----------|
| **BLOCK-ENGAGEMENT-BREADCRUMB** | Every response with 2+ hop routing chains | Always visible |
| **BLOCK-ENGAGEMENT-TIMELINE** | After 3+ step operations | Collapsible (`<details>`) |
| **BLOCK-PHASE-ROADMAP** | Start of multi-phase operations (N≥2) | Rendered once, updates on completion |

**SSOT:** `.github/templates/cortex-response-templates.md`

---

*Verified against engagement_renderer.py and Phase 92 wiring*
