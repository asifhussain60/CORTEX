# Video Prompt 09 — Response Templates and Orchestrator Engagement

## Target Tool: Google Gemini Video Generator / NotebookLM Video Editor

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism motion style, typography, and CORTEX logo watermark rules.

## Narrative Summary

**Title:** "How CORTEX Talks To You — Response Templates and Orchestrator Engagement"
**Duration:** 90 seconds
**Phase:** Phase 85 — Unified Response Template Standardization + Orchestrator Engagement

This video explains how CORTEX formats every response using a canonical template system — and how developers can see exactly which orchestrators handled their request, how long each step took, and where they are in a multi-phase operation.

---

## Scene-by-Scene Script

### Scene 1 — The Problem (0–15s)

**Visual:** Two VS Code chat windows side by side.
- Left window: A raw LLM response — unstructured text, no context about what ran, no progress feedback. Label: "❌ Without CORTEX Templates"
- Right window: A CORTEX response — clean structure, breadcrumb trail, progress bar. Label: "✅ CORTEX Response Templates"

**Narration (overlay text only — no voice):**
"Most AI responses are black boxes. CORTEX responses are structured governance contracts."

---

### Scene 2 — The Template System (15–35s)

**Visual:** An animated block library appears — glassmorphic cards floating in space, each card being a named response block:
- `BLOCK-INTENT-REFLECTION` — cyan glow
- `BLOCK-ENGAGEMENT-BREADCRUMB` — purple glow
- `BLOCK-PHASE-ROADMAP` — amber glow
- `BLOCK-ENGAGEMENT-TIMELINE` — blue glow
- `BLOCK-METRICS-DASHBOARD` — green glow

Cards arrange themselves like LEGO blocks assembling into a complete response. Camera zooms into the assembled response.

**Text overlay:** "16 composable blocks. One SSOT. Every orchestrator references the same template file."

---

### Scene 3 — Orchestrator Engagement Visibility (35–60s)

**Visual:** A CORTEX response rendering in real-time in a VS Code chat panel.

First the Breadcrumb appears (always visible, single line):
```
🧭 Route: IntentRouter → MasterOrchestrator → TDDOrchestrator
```

Then a collapsible timeline expands:
```
⏱ Timing (click to collapse)
  Stage 1 — Intent Classification:   42ms  ✅
  Stage 2 — LENS Analysis:          387ms  ✅
  Stage 3 — Governance Gate:         89ms  ✅
  Stage 4 — TDD Execution:          2,340ms 🔵 (running)
```

Then the Phase Roadmap appears at the top of a multi-phase operation:
```
⚙️ [████████░░] 80% — Stage 4 of 5

1. ✅ Environment check      (1.2s)
2. ✅ Governance pre-flight  (3.4s)
3. ✅ LENS analysis          (0.8s)
4. 🔵 Wiring validation      (running…)
5. ⚪ Test gate              —
```

**Text overlay:** "Three tiers of visibility. Breadcrumb always on. Timeline collapsible. Roadmap at the start of long operations."

---

### Scene 4 — The Three Engagement Tiers (60–80s)

**Visual:** Three concentric rings, each representing an engagement tier:

- **Inner ring (Tier 1 — Breadcrumb):** Always visible. Single line. Shows routing chain.
  Icon: 🧭 — compass
  
- **Middle ring (Tier 2 — Timeline):** Collapsible. Shows per-orchestrator timing.
  Icon: ⏱ — stopwatch

- **Outer ring (Tier 3 — Roadmap):** Long operations only. Full phase list.
  Icon: 🗺️ — map

Each ring pulses with cyan light as it's described. Orchestrator names appear at the connection points.

**Text overlay:** "Subtle. Professional. Never intrusive."

---

### Scene 5 — Call to Action (80–90s)

**Visual:** Full-frame glassmorphic card with:
- CORTEX logo (large, centered)
- Three bullet points:
  - "Breadcrumb: always visible — `BLOCK-ENGAGEMENT-BREADCRUMB`"
  - "Timeline: collapsible — `BLOCK-ENGAGEMENT-TIMELINE`"
  - "Roadmap: multi-phase — `BLOCK-PHASE-ROADMAP`"
- SSOT reference: `.github/templates/cortex-response-templates.md`

**Footer:** "Phase 85 — Unified Response Template Standardization"

---

## Production Notes

| Property | Value |
|----------|-------|
| Duration | 90 seconds |
| Dimensions | 1920×1080 |
| Style | Glassmorphism, dark-blue palette |
| Text language | English only |
| Voice | None — text overlay only |
| Music | Subtle ambient electronic — low BPM, non-distracting |
| Transitions | Smooth ease-in-out 300ms between scenes |

## Cross-Reference

| Related | Location |
|---------|----------|
| Phase 85 spec | `cortex-registry/_cortex-master/phases/planned/phase-85-unified-response-orchestrator-engagement.yaml` |
| Response templates SSOT | `.github/templates/cortex-response-templates.md` |
| Flat-file | `flat-files/04-capabilities.md` §8 |
