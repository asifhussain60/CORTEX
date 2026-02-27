# Video Prompt 03 — The Intelligence Engine

> **Duration:** 9 minutes · **Audience:** Product Owners → Software Engineers (bridge)
> **Depth:** 🟡→🔴 Starts conceptual, ends with architecture
> **No overlap:** Image prompt-11 shows the Intelligence Matrix as a static PCB; this video shows LENS performing a *live workspace analysis* with results building in real-time

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 9-minute animated explainer video titled **"The Intelligence Engine"** using the visual identity above. Show how CORTEX *thinks* — from understanding a workspace to generating insights and recommendations.

### Scene 1 — What Does "Intelligence" Mean Here? (0:00 – 1:30)

**Open on:** The word "Intelligence" in large Space Grotesk font, centered on `#0a0e27`. It shimmers between cyan and purple.

**Clarification animation:**
- Cross out "Neural Network" (red strikethrough), cross out "Machine Learning Model" (red strikethrough).
- Replace with: **"Heuristic + LLM-Orchestrated Pipelines"** — each word fades in with cyan underline.
- A glassmorphic info card appears: "CORTEX doesn't embed AI models. It orchestrates the host LLM (GitHub Copilot/GPT) as the AI engine."

**Daily-life analogy** (`#a0a6c0`): *"CORTEX is not the brain surgeon — it's the operating room coordinator who hands the surgeon the right tools at the right time."*

**Diagram builds:** Show the LLM (a large glowing orb at top) connected by cyan lines down to CORTEX (a network of glass panels). Arrows show: CORTEX sends structured prompts UP → LLM sends results DOWN → CORTEX validates, routes, applies.

**Narration:** "When we say intelligence, we don't mean CORTEX has its own AI. We mean it knows how to *use* AI effectively — structuring problems, routing to specialists, and validating results."

### Scene 2 — LENS: The Diagnostic Eye (1:30 – 3:30)

**Transition:** Camera zooms into the CORTEX network, entering the LENS module.

**LENS acronym builds** letter by letter on screen:
- **L**anguage → A file tree appears; file extensions light up by language (`.py` cyan, `.yaml` amber, `.md` green, `.html` purple)
- **E**xamination → A magnifying glass scans individual files; complexity scores float out as badges
- **N**avigation → A dependency graph materializes — nodes are files, edges are import relationships, flowing cyan particles travel the edges
- **S**ynthesis → All data compresses into a unified "workspace profile" card — a glassmorphic dashboard with metrics

**Live analysis animation (2:30 – 3:30):**
Show a realistic CORTEX workspace (simplified file tree on the left, code panels center).

1. LENS beam sweeps top-to-bottom (like an MRI scanner).
2. As the beam passes each directory:
   - `cortex/orchestrators/` → badge: "51 orchestrators, 4 tiers" (cyan)
   - `cortex/mcp/tools/` → badge: "28 MCP tools registered" (purple)
   - `tests/` → badge: "16,942 tests, 92% coverage" (green)
   - `cortex-registry/` → badge: "38 CORE rules active" (amber)
3. Results aggregate into a glassmorphic **Workspace Intelligence Card** at the bottom of screen.

**Analogy overlay:** *"An MRI machine doesn't just take a photo — it builds a complete 3D model of your body. LENS does the same for your codebase."*

### Scene 3 — Knowledge Synthesis (3:30 – 5:00)

**From the workspace profile, branches grow upward like a knowledge tree.**

Show three intelligence pipelines:

1. **Blind Spot Detection** — Red nodes (`#ff4444`) appear on the tree where coverage gaps exist. A magnifying glass icon zooms into one: "Module `secrets/` has no integration tests." Glassmorphic alert card appears with suggested action.

2. **Domain Brain** — Purple (`#7b61ff`) neural-like connections form between related modules. Show: `orchestrators/core/tdd_orchestrator.py` ↔ `testing/quality_gate.py` ↔ `governance/rule_enforcement.py`. A holographic label: "TDD Domain Cluster — 3 modules, 12 shared concepts."

3. **Knowledge Base Search** — A search query types in: "How does governance enforcement work?" Glass panels fan out like index cards — each showing a relevant file with highlighted excerpt. Top result glows cyan.

**Analogy overlay:** *"A detective's investigation board — red pins for gaps, purple strings connecting related clues, and a search index to find anything instantly."*

**Narration:** "LENS doesn't just scan — it synthesizes. It finds what's missing, connects what's related, and makes everything searchable."

### Scene 4 — Intelligence in Action: A Real Scenario (5:00 – 7:00)

**Scenario setup:** A glassmorphic terminal shows the command `/onboard https://github.com/example/project`

**Step-by-step animated flow:**

1. **Clone & Scan** (5:15) — Repository appears as a dark glass cube. LENS beam scans it. File counts, language distribution, and structure materialize as floating stats.

2. **Security Assessment** (5:45) — Three priority tiers appear as concentric shields:
   - P0 (inner, red): "Hardcoded API key in `config.py`" — flashing danger
   - P1 (middle, amber): "No input sanitization in `api/routes.py`"
   - P2 (outer, blue): "Dependencies 6 months old"
   - Each finding slides into the shield at its tier level.

3. **Architecture Mapping** (6:15) — A C4-style component diagram auto-generates. Boxes appear for each major module, connection lines draw themselves. The diagram uses glassmorphic boxes with cyan borders.

4. **SQLite Dashboard Generation** (6:45) — All findings compress into a database icon. Then a glassmorphic dashboard materializes — charts, tables, health scores. The dashboard is interactive — panels glow on hover.

**Analogy overlay:** *"A home inspector doesn't just look at the kitchen — they check the foundation, wiring, plumbing, and roof, then give you a complete report with priorities."*

### Scene 5 — The Intelligence Matrix (7:00 – 8:00)

**Camera pulls back** to show a matrix grid — the Intelligence Matrix from a bird's-eye view.

- **Rows:** Different intelligence domains (LENS, Knowledge, Security, Architecture, Testing)
- **Columns:** Different actions (Scan, Analyze, Recommend, Execute)
- Each cell is a glassmorphic tile. As the camera pans across, tiles light up showing which capabilities exist.
- Active cells glow cyan, planned cells show a dashed purple border.

This is NOT a repeat of image prompt-11's PCB — this is a **functional capability matrix** showing what intelligence can DO, viewed as an animated grid that builds cell by cell.

**Narration:** "Every intelligence capability maps to this matrix. Scan, analyze, recommend, execute — across every domain CORTEX understands."

### Scene 6 — Closing: Intelligence You Can Trust (8:00 – 9:00)

**Three trust principles** appear as large glassmorphic cards:

1. **Transparent** — "Every recommendation traces back to evidence" (show a citation link animation)
2. **Governed** — "38 rules validate every intelligence output" (shield shimmer)
3. **Tested** — "16,942 tests verify intelligence accuracy" (green heartbeat pulse)

**Closing text** (Space Grotesk): **"Intelligence isn't magic. It's orchestrated methodology."**

**Vision callback:**
> *"CORTEX: $8,600 saved per team, per year. Zero guesswork."*

Logo pulse. End card.

---

## Notes

- Image prompt-03 shows LENS as a static diagnostic eye anatomy. This video shows LENS **performing a live scan** with results appearing in real-time.
- Image prompt-11 shows the Intelligence Matrix as a static PCB layout. This video shows it as an **animated capability matrix** being populated — different visual metaphor.
- The LLM-orchestration architecture diagram in Scene 1 is critical — it corrects the common misconception that CORTEX contains embedded ML models.
- Code and file paths shown should be realistic (match actual CORTEX structure).
- Sound design: scanning beam has a subtle electronic sweep sound; findings appear with soft notification pings.
