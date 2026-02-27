# Video Prompt 10 — Multi-Stack Debugging

## Target Tool: Google Gemini Video Generator / NotebookLM Video Editor

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism motion style, typography, and CORTEX logo watermark rules.

## Narrative Summary

**Title:** "Debugging Any Stack — CORTEX Multi-Stack Debug Pipeline"
**Duration:** 90 seconds
**Phase:** Phase 86 — Multi-Stack Debug Pipeline

This video demonstrates CORTEX's universal debugging capability — how the same inject → capture → analyze → fix-plan → cleanup workflow applies to Python, JavaScript/TypeScript, REST APIs, SQL databases, and C#/.NET services.

---

## Scene-by-Scene Script

### Scene 1 — The Universal Problem (0–15s)

**Visual:** Five technology stack icons arranged in a horizontal row (left to right):
- 🐍 Python (cyan)
- 🟨 JavaScript/TypeScript (amber)
- 🌐 REST API (purple)
- 🗄️ SQL Database (blue)
- 🔷 C#/.NET (green)

A bug icon (red 🐛) appears over ALL FIVE simultaneously. A developer looks confused — different tools required for each stack.

**Text overlay:** "Every stack has bugs. Most tools only debug one."

Then the CORTEX logo swoops in, and a single command appears:

```
/debug src/
```

**Text overlay:** "CORTEX detects your stack. Selects the right strategy. One command."

---

### Scene 2 — The 5-Phase Pipeline (15–35s)

**Visual:** The five phases appear left to right as animated glassmorphic nodes connected by cyan arrows:

```
[INJECT] → [CAPTURE] → [ANALYZE] → [FIX-PLAN] → [CLEANUP]
```

Each node glows as it's highlighted:

- **INJECT:** Markers inserted into source code — `# CORTEX_DEBUG: entry point`
- **CAPTURE:** Runtime output flows into a collector — logs, stack traces, performance data
- **ANALYZE:** LENS + Brain tiers process captured data — pattern matching, anomaly detection
- **FIX-PLAN:** Prioritised fix plan generated — P0/P1/P2 severity, remediation steps
- **CLEANUP:** All markers removed — code returns to production state

**Text overlay:** "Five phases. Stack-agnostic. Fully reversible."

---

### Scene 3 — 8 Strategies (35–60s)

**Visual:** Eight strategy cards appear in a grid (2 rows × 4 cols), each with a tech stack icon and label:

Row 1 (Live ✅):
- `TestFailureStrategy` — Python pytest
- `RefactorRegressionStrategy` — Python refactor
- `GovernanceViolationStrategy` — Python CORE rules
- *(empty placeholder — reserved)*

Row 2 (Phase 86 ⚪):
- `FrontendConsoleStrategy` — JS/TS/React/Angular/Vue
- `HtmlVisionMappingStrategy` — Vision API + DOM
- `ApiTraceStrategy` — REST/GraphQL/gRPC
- `SqlTraceStrategy` — SQL Server/Oracle/PostgreSQL

A 9th card slides in below: `DotNetTraceStrategy` — C#/.NET (Phase 86 ⚪)

Camera zooms into `FrontendConsoleStrategy`. Code appears showing `console.log("[CORTEX_DEBUG]", ...)` injected into a React component.

**Text overlay:** "3 Python strategies live today. 5 multi-stack strategies in Phase 86."

---

### Scene 4 — Vision API Mapping (60–75s)

**Visual:** The `HtmlVisionMappingStrategy` strategy is highlighted.

A browser screenshot appears. A Vision API "eye" overlays the screenshot, identifying DOM elements:
- Red box: failing button (opacity issue)
- Purple line: CSS selector path
- Cyan annotation: "rgba(0,0,0,0) background — invisible on dark theme"

A fix plan card appears:
```
P1 — FIX: button.submit-btn { background: #00d4ff; }
Confidence: 0.89 | Strategy: CSS specificity override
```

**Text overlay:** "The Vision API maps screenshots to DOM. CORTEX sees what the user sees."

---

### Scene 5 — Call to Action (75–90s)

**Visual:** Full-frame glassmorphic card:
- Title: "CORTEX Multi-Stack Debug Pipeline"
- Three commands:
  - `/debug {path}` — Full 5-phase cycle
  - `/debug-inject {path}` — Markers only
  - `/debug-cleanup` — Remove all markers
- Phase 86 status: "🔵 Planned — Zero new orchestrators · Zero new MCP tools · Strategy Pattern extension"

**Footer:** "Phase 86 — Multi-Stack Debug Pipeline"

---

## Production Notes

| Property | Value |
|----------|-------|
| Duration | 90 seconds |
| Dimensions | 1920×1080 |
| Style | Glassmorphism, code animation, dark-blue palette |
| Text language | English only |
| Voice | None — text overlay only |
| Music | Subtle electronic, slightly faster BPM (debugging = urgency resolved) |
| Transitions | Smooth ease-in-out; code injection shows character-by-character typewriter effect |

## Cross-Reference

| Related | Location |
|---------|----------|
| Phase 86 spec | `cortex-registry/_cortex-master/phases/planned/phase-86-multi-stack-debug-pipeline.yaml` |
| Debugger agent | `.github/agents/support/cortex-debugger.md` |
| Flat-file | `flat-files/04-capabilities.md` §7 |
