# Video Prompt 07 — Cross-Domain Intelligence
### CORTEX: The Enterprise Intelligence Series

> **Duration:** 8 minutes · **Audience:** Product Owners → Software Engineers (bridge), Enterprise Architects
> **Depth:** 🟡→🔴 Starts conceptual, ends with real analysis output
> **Core Executive Theme:** Pattern recognition across business units, reusable architectural intelligence, continuous improvement that compounds across the organization
> **No overlap:** Image prompt-03 shows LENS anatomy; this video shows LENS performing a *live scan* with results building in real-time, plus how the Brain tiers make decisions

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

## ⚠️ VIDEO DESIGN BEST PRACTICES — MANDATORY

> **VBP-001:** One idea per frame — never duplicate text across multiple regions of the same frame.
> **VBP-004:** Progressive disclosure — build complexity through animation, simple → detailed.
> **VBP-006:** Contrast-based storytelling — "Intelligence" ≠ Neural Network (cross-out animation).
> **VBP-007:** Scene transitions every ~90-120 seconds to maintain attention.
> **VBP-009:** Data visualizations animated incrementally — LENS scan results build badge-by-badge.
> **VBP-011:** Strategic silence when the workspace profile card completes.
> See `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` for the full codified reference.

## ⚠️ HERO INTRO SLIDE — MANDATORY (VBP-014)

> **Scene 0 — Title Card (0:00 – 0:05):** Full-screen `#0a0e27` deep navy background. CORTEX logo (`cortex-docs/assets/images/cortex-logo-200.png`) displayed as a **large central hero image** with a subtle cyan glow pulse. Above the logo: **"Cross-Domain Intelligence"** in Space Grotesk Bold, white. Below the logo: **"Patterns that compound. Intelligence that travels across teams."** in Inter, `#a0a6c0`. Series badge top-right: `07 of 10 · The Enterprise Intelligence Series`. Hold 5 seconds. Transition: logo shrinks to watermark position as Scene 1 fades in.

## ⚠️ BREADCRUMB NAVIGATION — MANDATORY (VBP-015)

> **Scene 4 (Repository Onboarding) presents 4 sequential steps.** Display a persistent **breadcrumb bar** during Scene 4:
> `Clone & Scan → Security Assessment → Pattern Detection → Dashboard Generation`
> - **Current step:** Full brightness, bold, cyan highlight
> - **Completed steps:** ✅ checkmark, dimmed to 60% opacity
> - **Upcoming steps:** Muted outlines at 30% opacity
>
> **Scene 2 (LENS acronym build) has implicit sequential flow.** Show each letter building as a mini breadcrumb:
> `L → E → N → S` — each letter highlights as it's explained, previous letters stay lit but dimmed.

## ⚠️ TYPOGRAPHY, COLOR & VOICE — MANDATORY (VBP-016, VBP-017, VBP-018, VBP-019)

> **Bold Key Words:** On every text card and glassmorphic panel, **bold the 1–3 most important words** in cyan (`#00d4ff`).
> **Color Intelligence:** Cyan for perception tier, purple for reasoning tier, amber for action tier — consistent with the three-brain architecture across all videos.
> **Voice:** 🎙️ **Female narrator** (odd-numbered video — V07). Confident, conversational, honest tone.
> **Acronym Expansion (first use in this video):**
> - CORTEX = **CO**gnitive **R**eal-**T**ime **EX**ecution (Scene 1)
> - LENS = **L**anguage → **E**xamination → **N**avigation → **S**ynthesis (Scene 2 — letter-by-letter build)
> - LLM = **L**arge **L**anguage **M**odel (Scene 1 diagram)
> - MCP = **M**odel **C**ontext **P**rotocol (Scene 4 onboarding)
> - CVE = **C**ommon **V**ulnerabilities and **E**xposures (Scene 4 if referenced)

---

## PROMPT

Create an 8-minute animated explainer video titled **"Cross-Domain Intelligence"**. Show how CORTEX *thinks* — from understanding a workspace to generating recommendations — and how those insights compound across teams, repositories, and business domains.

### Scene 1 — What "Intelligence" Means (0:00 – 1:30)

**Open on:** The word "Intelligence" in Space Grotesk. It shimmers between cyan and purple.

**Clarification:** Cross out "Neural Network" (red strikethrough), cross out "Machine Learning Model" (red strikethrough). Replace with: **"Heuristic + LLM-Orchestrated Pipelines"** in cyan.

Glassmorphic info card: "CORTEX doesn't contain AI models. It orchestrates your existing AI — structuring problems, routing to specialists, and validating results."

**Second info card fades in below:** "But here's what makes it compound: every pattern detected in one team's codebase becomes available intelligence for every other team. Intelligence isn't siloed — it's *shared*."

**Diagram builds:** LLM (large orb at top) → CORTEX sends structured prompts UP → LLM sends results DOWN → CORTEX validates, routes, applies. **A horizontal layer at the bottom shows a "Shared Intelligence Layer"** where patterns, anti-patterns, and confidence scores flow between multiple repository icons.

**Analogy:** *"CORTEX is not the surgeon — it's the operating room coordinator who hands the surgeon the right tools at the right time. And when one surgeon discovers a better technique, every operating room knows about it."*

### Scene 2 — LENS: The Diagnostic Scan (1:30 – 3:30)

**LENS acronym builds** letter by letter:
- **L**anguage → File extensions light up by language (`.py` cyan, `.yaml` amber, `.ts` purple)
- **E**xamination → Magnifying glass scans files; complexity scores float out
- **N**avigation → Dependency graph materializes — nodes are files, edges are imports
- **S**ynthesis → All data compresses into a unified "workspace profile" card

**Live scan animation (2:30–3:30):** A realistic workspace file tree appears. LENS beam sweeps top-to-bottom. As it passes each area, badges appear: orchestrator count, test coverage percentage, governance rule status, dependency health. Results aggregate into a **Workspace Intelligence Card**.

**Narration:** "By the time you've typed a request, LENS already knows which files are involved, what patterns they use, and what the test coverage looks like. That context is what separates a useful response from a generic one."

### Scene 3 — The Three Brain Tiers: Cross-Domain Pattern Recognition (3:30 – 5:00)

**From the workspace profile, the three tiers activate sequentially:**

**Tier 1 — Perception (cyan):**
- Enterprise pattern icons light up as signatures match: Mediator, Strategy, Observer, Factory, etc.
- Each matched pattern shows a confidence score (0.0 – 1.0)
- **Cross-domain callout:** A small badge on each pattern reads "Seen in 12 repos" or "First detection" — showing the shared intelligence layer at work
- "What patterns exist in this code — and where else have we seen them?"

**Tier 2 — Reasoning (purple):**
- A strategy ranking table materializes. Strategies sorted by historical success rate.
- Candidate strategies: "tdd-incremental" (89%), "refactor-extract-service" (76%), "security-audit-first" (92%)
- **Cross-domain callout:** Success rates are drawn from outcomes across ALL teams, not just the current one — a subtle "based on 47 outcomes across 8 teams" label
- "Which approach will work best — based on what EVERY team has learned?"

**Tier 3 — Action (amber):**
- A step-by-step execution plan with numbered steps, TDD gates between each, and rollback checkpoints
- "How exactly should we execute this?"

**Narration:** "Perception reads the signals. Reasoning selects the strategy. Action builds the plan. Three tiers, working in sequence — and the difference between each tier is the difference between a guess and a judgment. But here's the compounding effect: that 89% success rate isn't from one team's history. It's from every team that's ever faced a similar problem. Intelligence that travels across domains is intelligence that improves faster than any single team could achieve alone."

### Scene 4 — Intelligence in Action: Repository Onboarding (5:00 – 7:00)

**Scenario:** `/onboard https://github.com/example/project`

**Step-by-step:**

1. **Clone & Scan** — Repository appears as a glass cube. LENS beam scans it. File counts, language distribution, and structure materialize.

2. **Security Assessment** — Three priority tiers as concentric shields:
   - P0 (red): "Hardcoded API key in config" — flashing danger
   - P1 (amber): "No input sanitization in API routes"
   - P2 (blue): "Dependencies need updating"

3. **Pattern Detection** — Enterprise patterns detected with confidence scores. Architecture diagram auto-generates.

4. **Dashboard Generation** — Findings compress into a database icon. A glassmorphic dashboard materializes with charts, tables, health scores.

**Narration:** "A security finding at onboarding costs minutes to fix. The same finding in production costs days of incident response, customer trust, and sleep. That's the real value of what you just watched."

### Scene 5 — Closing: Intelligence That Compounds (7:00 – 8:00)

Three trust principles as glassmorphic cards:

1. **Transparent** — "Every recommendation traces back to evidence" (citation animation)
2. **Cross-Domain** — "Patterns from one team strengthen every team" (network graph pulse — nodes lighting up across repositories)
3. **Continuously Improving** — "Outcomes feed back to improve future confidence scores" (circular arrow with rising confidence graph: 72% → 81% → 89% over 3 iterations)

**Closing text:** **"Intelligence isn't magic. It's orchestrated methodology — and it compounds."**

**Narration:** "Every output from this system traces back to evidence — a pattern, a rule, a historical outcome. But the real power is what happens over time: each team's experience raises the intelligence floor for every other team. That's not automation. That's institutional learning."

---

## Animated Diagram Flow Directives

### 📐 Mermaid Diagram Sources (bundle with this prompt in NotebookLM)

| Diagram File | Type | Scene Reference | Purpose |
|---|---|---|---|
| `07-d-orchestrator-dispatch-flow.md` | Flowchart | Scene 3 — Three Brain Tiers | Shows how Master Orchestrator routes through intelligence tiers to target orchestrators |
| `07-d-c4-component-master-orchestrator.md` | C4-Component | Scene 3 deep-dive | Internal components of Master Orchestrator — zoom-in when explaining Perception/Reasoning/Action |

> **Video Producer:** Import BOTH `07-d-orchestrator-dispatch-flow.md` and `07-d-c4-component-master-orchestrator.md` alongside this prompt in NotebookLM. The dispatch flow is the OVERVIEW (Scene 3 establishing shot). The C4 component diagram is the ZOOM-IN when the narration drills into how the Master Orchestrator routes internally. Start with the flow diagram, then "camera zoom" into the Master Orchestrator node to reveal the component diagram. Both files contain `animation_notes` in their frontmatter with frame-by-frame rendering instructions.

**Diagram: LLM Orchestration (Scene 1)**
- Flow direction: CORTEX (center) sends structured prompts UP to LLM (top) → LLM sends results DOWN
- Key visual: CORTEX is the coordinator, not the surgeon — arrows show direction of control

**Diagram: LENS Scan (Scene 2)**
- LENS beam sweeps top-to-bottom across file tree
- Results aggregate into Workspace Intelligence Card (progressive disclosure)

**Diagram: Three Brain Tiers (Scene 3) — from `07-d-orchestrator-dispatch-flow.md`**
- Perception (cyan) → Reasoning (purple) → Action (amber) — sequential activation
- Each tier shows 3-second activity with specific outputs before passing to next
- Pattern confidence scores float beside Perception nodes
- Strategy ranking table materializes at Reasoning
- Execution plan with TDD gates builds at Action

---

## Notes
- **Cross-Domain Intelligence framing** — The original "Intelligence Engine" video is preserved in full (LLM-orchestration diagram, LENS scan, three brain tiers, repo onboarding). The cross-domain theme adds the *compounding* layer: patterns recognized in one team's code inform recommendations for all teams, confidence scores draw from cross-organizational outcomes, and the shared intelligence layer means institutional learning persists beyond any individual contributor. This reframing speaks directly to enterprise architects and CTOs evaluating organization-wide value.
- This video bridges product owners and engineers — starts conceptual, ends with real output
- The LLM-orchestration diagram in Scene 1 prevents the "embedded AI" misconception
- Repository onboarding in Scene 4 is a practical capability that makes CORTEX immediately useful
- **No hardcoded counts** — analyzers and patterns described by function, not number
- **Voice:** Female (V07 — odd-numbered)
