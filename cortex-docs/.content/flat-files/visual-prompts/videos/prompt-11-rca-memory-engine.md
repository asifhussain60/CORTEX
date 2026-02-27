# Video Prompt 11 — RCA Memory Engine

## Target Tool: Google Gemini Video Generator / NotebookLM Video Editor

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism motion style, typography, and CORTEX logo watermark rules.

## Narrative Summary

**Title:** "Never Repeat a Mistake — CORTEX RCA Memory Engine"
**Duration:** 90 seconds
**Phase:** Phase 87 — RCA Memory Engine

This video explains how the RCA Memory Engine transforms one-time failure analysis into compounding institutional knowledge — and how the Prevention Gate stops the same root cause from recurring automatically.

---

## Scene-by-Scene Script

### Scene 1 — The Recurring Bug Problem (0–15s)

**Visual:** A timeline spanning 12 months. Every 2–3 months, a red bug icon appears at the same position on the timeline. Each time, a developer icon appears, fixes it, and leaves. The bug reappears.

Text appears above each bug: "Bug #1", "Bug #23", "Bug #67", "Bug #102" — all the same root cause.

**Text overlay:** "The same bug. Different developer. Same root cause. Every time."

---

### Scene 2 — OPJ Meets RCA Engine (15–35s)

**Visual:** The OPJ (Operational Pattern Journal) appears as a glowing book. A failure entry appears:

```python
_opj_record_failure(
    root_cause="Missing async error boundary",
    avoid_in_future="Always await before accessing .data",
    rca=True  # ← Phase 87: triggers RCA Engine
)
```

The `rca=True` flag lights up in cyan. The RCA Engine activates — shown as a rotating analytical gear.

Four methodology icons appear:
- 🔍 **Five Whys** — chain of downward arrows
- 🐟 **Fishbone** — skeleton diagram
- 🌳 **Fault Tree** — branching tree
- ⏱️ **Causal Chain** — timeline with events

The engine selects "Five Whys" (highlighted in cyan). A chain unfolds:

```
Why 1: AttributeError in response handler
Why 2: .data accessed before await
Why 3: Missing `await` keyword
Why 4: No async linting in CI  ← ROOT CAUSE
```

**Text overlay:** "Four methodologies. Auto-selected based on failure type."

---

### Scene 3 — The Recurrence Signature (35–50s)

**Visual:** A fingerprint scan animation. The RCA result generates a signature:

```
RCA-SIG-FIVE_WHYS-TECHNOLOGY-a3f9b2c1
```

This signature is stored in a glowing hexagonal node in the Memory Shield (center frame). More nodes appear around it — each representing a different RCA — forming a growing knowledge lattice.

A similarity meter appears (0–100%). As new failures arrive, the meter spins and settles:
- 95% match → "RECURRENCE DETECTED" in amber
- 30% match → "Novel failure" in cyan

**Text overlay:** "Every failure gets a fingerprint. Every new failure is checked against all previous ones."

---

### Scene 4 — Prevention Gate in Action (50–75s)

**Visual:** Split screen. Left: developer typing a new feature. Right: Prevention Gate monitoring in background.

The developer's code triggers an async operation without proper error handling. The Prevention Gate detects a 95% signature match.

Three scenarios play out in sequence (each 5 seconds):

**Scenario A (1st occurrence):**
A subtle info banner in VS Code Copilot Chat:
```
💡 Advisory: Similar past failure detected (RCA-2026-001)
   Root cause: Missing async error boundary
   Previous fix: Add try/catch with await
```

**Scenario B (2nd occurrence):**
The governance gate response includes a warning:
```
⚠️ Warning: 2nd recurrence of this root cause class
   See: cortex_learning op="rca" action="query" id="RCA-2026-001"
```

**Scenario C (3rd P0 occurrence):**
Operation halts. Red stop signal:
```
🛑 Blocked: P0 root cause recurrence × 3
   Structured review required before proceeding.
   cortex_learning op="rca" action="review_required"
```

**Text overlay:** "Advisory → Warning → Blocked. CORTEX escalates with each recurrence."

---

### Scene 5 — Institutional Memory Compounds (75–85s)

**Visual:** The Memory Shield from a distance. More and more nodes appear over time — the lattice grows. A counter in the corner:

```
RCA Analyses: 247
Prevention Rules Active: 89
Recurrences Blocked: 34
False Positive Rate: 2.1%
```

**Text overlay:** "The longer CORTEX runs, the smarter it gets. Every failure makes the next prevention more precise."

---

### Scene 6 — Call to Action (85–90s)

**Visual:** Full-frame glassmorphic card:
- Title: "CORTEX RCA Memory Engine — Phase 87"
- Three key facts:
  - "Four structured RCA methodologies: Five Whys · Fishbone · Fault Tree · Causal Chain"
  - "Prevention Gate: Advisory → Warning → Blocking (P0 × 3)"
  - "Zero new orchestrators · Zero new MCP tools · Purely additive"

**Footer:** "Phase 87 — Root Cause Analysis · Prevention Gate · Recurrence Detection"

---

## Production Notes

| Property | Value |
|----------|-------|
| Duration | 90 seconds |
| Dimensions | 1920×1080 |
| Style | Glassmorphism, dark-blue palette, fingerprint scan animation |
| Text language | English only |
| Voice | None — text overlay only |
| Music | Subtle ambient — slightly mysterious, then resolving to confidence |
| Key visual | Hexagonal Memory Shield with growing knowledge lattice |
| Transitions | Smooth ease-in-out; fingerprint scan uses radial reveal effect |

## Cross-Reference

| Related | Location |
|---------|----------|
| Phase 87 spec | `cortex-registry/_cortex-master/phases/planned/phase-87-rca-memory-engine.yaml` |
| RCA flat-file | `flat-files/21-rca-memory-engine.md` |
| RCA diagram | `flat-files/diagrams/diagram-24-rca-prevention-flow.md` |
| Image prompt | `flat-files/visual-prompts/images/prompt-13-rca-memory-shield.md` |
| Capabilities | `flat-files/04-capabilities.md` §9 |
