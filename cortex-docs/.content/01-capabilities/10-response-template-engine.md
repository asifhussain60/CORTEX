# Response Template Engine — Architecture & Design

---
title: CORTEX Response Template Engine
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-27
source_of_truth: .github/templates/cortex-response-templates.md + cortex-registry/artifacts/templates/responses/response-templates.yaml + cortex-registry/workflows/templates/governance/copilot-chat-response-template.yaml
order: 10
---

> **Brain analogy:** The Response Template Engine is the **prefrontal formatting cortex** — it takes raw intelligence from all 51 orchestrators and shapes it into a consistent, scannable, ≤60-second-readable output rendered live in VS Code GitHub Copilot Chat.

---

## Executive Summary

CORTEX's Response Template Engine is a **composable, LEGO-block rendering system** that standardises every user-facing output in VS Code Copilot Chat. It solves a fundamental problem: 51 orchestrators producing 13 execution modes need consistent, non-repetitive, executive-ready responses — without any `.md` or `.txt` file generation (CORE-002).

The system evolved through 28+ git commits from raw text output → tree-character rendering → fenced code blocks → the current **5-Section Golden Format** with composable blocks, adaptive density, and Copilot Chat-specific rendering rules.

---

## Architecture Overview

### Three-Layer SSOT Hierarchy

The engine operates through three canonical files, each at a different abstraction level:

| Layer | File | Purpose | Audience |
|-------|------|---------|----------|
| **L1 — Specification** | `.github/templates/cortex-response-templates.md` | Full template library + rendering rules + block content | Prompts, agents, humans |
| **L2 — Machine-Readable** | `cortex-registry/artifacts/templates/responses/response-templates.yaml` | YAML-structured templates for programmatic rendering | Orchestrators, test harnesses |
| **L3 — Governance Binding** | `cortex-registry/workflows/templates/governance/copilot-chat-response-template.yaml` | CORE-066 enforcement + section matrix per mode | Workflow engine, audit pipeline |

**SSOT Rule:** L1 is the canonical source. L2 and L3 pointer-reference L1 — never duplicate content.

### Data Flow

```
User Request
  → MasterOrchestrator routes to Domain Orchestrator
    → Orchestrator produces structured result
      → Response Template Engine selects template (intent-based)
        → Adaptive Density adjusts depth (simple / medium / complex)
          → Copilot Chat Rendering Rules applied
            → Live Markdown rendered in VS Code chat panel
```

---

## Template Categories

### 1. The 5-Section Golden Format (Primary)

Used for all non-autonomous responses. Every section adds NEW information only — no repetition across sections.

| Section | H2 Header | Required | Max Length | Purpose |
|---------|-----------|----------|-----------|---------|
| **Summary** | `📋 Summary` | ✅ Always | 2 sentences | Answer-first: state what was asked and the bottom-line result |
| **Analysis** | `🔍 Analysis` | ✅ Always | 200 words | Findings, trade-offs, comparison tables |
| **Recommendation** | `💡 Recommendation` | ✅ Always | 150 words | ONE primary recommendation + numbered implementation steps |
| **Benefits & Risks** | `⚖️ Benefits & Risks` | 🟡 Medium+ | 1 table | 4-column comparison — skip for simple requests |
| **Next Steps** | `🎯 Next Steps` | ✅ Always | 150 words | Immediate actions (numbered) + `proceed` execution plan |

### 2. Silent Autonomous Mode (Execution)

Activated when user types `proceed`, `implement`, `yes`, or `continue`. Progress bars + stage bullet lists only — zero narration.

**Progress bar:** Exactly 10 blocks (`[████████░░]` 80%), rendered as plain markdown, never fenced in code blocks.

**Stage status:** Markdown bullet lists with status icons:
- ✅ Complete
- 🔵 In Progress
- ⚪ Pending
- 🔴 Failed/Blocked

### 3. Composable Content Blocks (Educational)

Seven reusable blocks that assemble like LEGO for educational/onboarding scenarios:

| Block | Purpose | Word Limit |
|-------|---------|------------|
| BLOCK-INTRO | Role-based welcome with persona selection | 150 |
| BLOCK-CAPABILITIES | What CORTEX does (7 capabilities table) | 200 |
| BLOCK-LENS | Intelligence system deep-dive (4 layers) | 150 |
| BLOCK-ORCHESTRATORS | Architecture overview (3 tiers) | 200 |
| BLOCK-TUTORIAL | 5-minute quick start | 150 |
| BLOCK-ONBOARDING | First-time MCP + venv setup | 150 |
| BLOCK-NEXT-STEPS | Context-aware suggestions | 80 |

**Assembly rules:** No duplicate headers, no repeated content, max 800 words total, NEXT-STEPS only once at end.

### 4. Specialised Blocks (Domain-Specific)

| Block | Trigger Mode | Key Feature |
|-------|-------------|-------------|
| BLOCK-ANALYSIS | INVESTIGATE / ANALYZE | Hypothesis table + root cause + recommended actions |
| BLOCK-DESIGN-DECISION | DESIGN / ARCHITECTURE | ADR format + trade-off matrix (1–5 scale) + STRIDE/OWASP |
| BLOCK-CODE-REVIEW | REFACTOR / FIX / REVIEW | Findings by severity + quality gates + verdict |
| BLOCK-SECURITY-ASSESSMENT | SECURITY_AUDIT | STRIDE threat model + OWASP Top 10 coverage |

### 5. Intent Reflection Block (Pre-Execution)

Rendered ONCE before any work begins. Mirrors CORTEX's understanding back to the user in first-person business language:

- 3–6 numbered action items
- Confidence signal (🟢 High / 🟡 Medium / 🔴 Low)
- Approval prompt: `> ✅ This looks right? Type proceed.`

---

## Response Header Contract

Every response begins with a canonical header — displayed ONCE, never repeated:

```
## {icon} CORTEX {mode}
**Author:** Asif Hussain | **Orchestrator:** {OrchestratorName} ✅

---
```

**Icons by mode:** 🔧 PRE-FLIGHT · 🔍 AUDIT/QUERY · 📚 DIGEST · 📋 PLAN · 🎨 DESIGN · ⚡ IMPLEMENT · 📝 LIST

**Enforcement:** Missing author or empty orchestrator name = CORE-066 P1 violation. Auto-fix restores from SSOT.

---

## Adaptive Density System

The same 5-section structure scales to request complexity:

| Complexity | Summary | Analysis | Recommendation | Benefits & Risks | Next Steps |
|-----------|---------|----------|----------------|-----------------|------------|
| **Simple** (1–2 files) | 1 sentence | 2–3 bullets | 1 sentence | ⚪ Skip | 1 action |
| **Medium** (feature) | 2 sentences | Findings table | Numbered steps | 3-row table | 2–3 actions |
| **Complex** (multi-step) | 2 sentences + scope | Full analysis + alternatives | Strategy + steps | Full table | Immediate + Later split |

---

## VS Code Copilot Chat Rendering Rules

These rules were discovered empirically through 28+ iterations (visible in git history) and are critical for correct visual output:

### Reliable Elements

| ✅ Always Works | ❌ Fragile / Broken |
|----------------|---------------------|
| `- ✅ bullet list` | `├─ └─` tree characters (collapse to one line) |
| `**bold**` / `*italic*` | Trailing-space line breaks |
| `---` horizontal rule | `<hr>` HTML tag |
| Standard markdown tables (≤5 cols) | >5 column tables (truncate/scroll) |
| `##` / `###` headings | `#####`+ deep headings |
| Emoji icons (✅ 🔵 ⚪ 🔴) | Unicode box-drawing characters |
| Fenced code blocks | Inline HTML (limited) |
| `<details>` / `<summary>` | Complex HTML structures |

### Critical Rules

1. **Bullet lists for stage status** — tree characters collapse into one unreadable line
2. **`---` for section dividers** — `<hr>` tags may not render
3. **`━━━` (U+2501) for autonomous execution separators** — visually distinct from HR
4. **Max 4–5 table columns** — wider tables overflow
5. **Never fence progress bars in code blocks** — renders as 100% grey box regardless of percentage
6. **1 blank line between paragraphs** — single newlines become soft wraps
7. **`<details>` for collapsible content** — keeps long responses scannable

---

## Mode → Section Matrix

Which template sections are required (✅) or optional (⚪) per execution mode:

| Mode | Header | Progress | Pre-Manifest | Stage Table | Violations | Post-Diff | Session Pause |
|------|--------|----------|-------------|-------------|------------|-----------|---------------|
| IMPLEMENT | ✅ | ✅ | ✅ | ⚪ | ⚪ | ✅ | if paused |
| FIX | ✅ | ✅ | ✅ | ⚪ | ✅ | ✅ | if paused |
| AUDIT | ✅ | ✅ | ⚪ | ✅ | ✅ | ⚪ | if paused |
| DESIGN | ✅ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | never |
| QUERY | ✅ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | never |
| VACUUM | ✅ | ✅ | ⚪ | ✅ | ⚪ | ⚪ | if paused |
| DEBUG | ✅ | ✅ | ✅ | ⚪ | ✅ | ✅ | if paused |

---

## Evolution History (Git Archaeology)

The response template engine evolved through four distinct phases, traceable in git history:

### Phase 1 — Ad-Hoc Output (Early)
Raw text responses with inconsistent formatting. Each orchestrator produced its own style.

### Phase 2 — Tree Characters & Box Drawing
Introduced `├─ └─` tree characters for stage display. **Failed** — Copilot Chat collapsed them into one line. Commits: `029473188`, `dd85ebc5b`, `1b29cde97`.

### Phase 3 — Template Explosion (A–E Templates)
Created five separate templates per intent type (A through E). **Failed** — duplication, inconsistency, impossible to maintain. Commit: `867ea4f58`. Retired by: `991d3b465`.

### Phase 4 — Golden Format Consolidation (Current)
Single 5-section format with adaptive density + composable blocks for education. Key commits:

| Commit | Change |
|--------|--------|
| `991d3b465` | CORE-050: 5-Section Golden Format established |
| `f85f0dae1` | CORE-049: Autonomous templates consolidated to SSOT |
| `b1a44d439` | CORE-050: All templates consolidated to single SSOT file |
| `6d9aa877d` | Fix: 0% progress bar must be `[░░░░░░░░░░]` not solid blocks |
| `fe5a943c5` | Fix: Remove fenced code blocks from golden template |
| `bbaab7822` | Feat: Execution plan preview in Next Steps |
| `b83822bfc` | Feat: LIST/SUMMARY mode + author header restoration |

---

## Anti-Patterns (Lessons Learned)

| Anti-Pattern | Why It Failed | Correct Alternative |
|--------------|--------------|---------------------|
| `├─ └─` tree characters | Collapse in Copilot Chat | `- ✅` Markdown bullet lists |
| Fenced progress bars | Renders as 100% grey box | Plain markdown `[████░░░░░░]` |
| Multiple `##` headers per response | Visual confusion | ONE `##` header, `###` for sub-sections |
| Separate template per intent | Duplication, drift | Single Golden Format with adaptive density |
| `<hr>` in autonomous output | May not render | `━━━` (U+2501, 44 chars) |
| >5 column tables | Overflow/truncation | Split into 2 tables |
| Tool narration ("I'll now search...") | Wastes read time | Present findings directly |
| Report file generation | CORE-002 violation | All output inline in chat |
| Trailing-space line breaks | Copilot ignores them | 1 blank line between paragraphs |

---

## Programmatic Integration

### Python Generator

`scripts/response-template-generator.py` provides programmatic template rendering:

```python
from scripts.response_template_generator import ResponseTemplate, SectionStatus, EnhancedHeader

header = EnhancedHeader(title="Implementation Complete", status=SectionStatus.COMPLETE)
print(header.render())  # ## ✅ Implementation Complete
```

### YAML Template Registry

`cortex-registry/artifacts/templates/responses/response-templates.yaml` defines machine-readable templates:

- `completion_report` — Post-implementation progress + metrics
- `challenge_response` — Design review with agreements/challenges/recommendations
- `phase_progress` — Silent autonomous progress metadata
- `query_response` — Q&A format with evidence
- `list_response` — Concise tabular/numbered responses

### Governance Enforcement (CORE-066)

`cortex-registry/workflows/templates/governance/copilot-chat-response-template.yaml` enforces:

- Header validation: author must be `Asif Hussain`, orchestrator non-empty
- Progress bar: exactly 10 blocks if multi-step
- No raw dict output — all structured through template sections
- Session pause banner required if sweep has open items at session end

---

## Quality Checklist

Every response is validated against this checklist before delivery:

1. Response header present with correct orchestrator
2. Intent Reflection block rendered (for actionable requests)
3. Confidence signal present (🟢 / 🟡 / 🔴)
4. Status icons used correctly (✅=done, ⚪=planned, 🔵=active)
5. Stage status uses Markdown bullet lists — never tree characters
6. Linear narrative: Context → Analysis → Action → Result (no repetition)
7. Completion confirmation used when work is done (not "Next Steps")
8. No exit options during holistic implementation
9. Continuation prompt only at >90% token budget
10. ≤60 second read time — answer first, tables for data

---

*Verified against live SSOT files*
