# NotebookLM Video Prompt — 01 — What is CORTEX? (Business Leader Edition)

**Target length:** 7–10 minutes
**Audience:** C-suite, VPs of Engineering, business stakeholders — decision-makers who own delivery risk
**Narrator gender:** Female (Video 01 — odd, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Cyan #00d4ff accent
**Series position:** The identity video — the only video answering "what is it and why does it exist?"

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- The business definition of CORTEX (what it is, what it is not)
- The leadership-level problem framing (delivery risk, invisible debt)
- The "Governance. Orchestration. Reliability." brand statement

No other video in the series restates these. Videos 02–10 build on this foundation.

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create a 7–10 minute technical documentary for business and engineering leaders. Answer three questions in sequence: What is CORTEX? What delivery problem does it solve? How does it close the loop? Tone: a senior project lead speaking to a board room — calm, authoritative, precise. Avoid superlatives. Use only engineering verbs: validate, constrain, enforce, audit, trace, converge. CORTEX is not a replacement for Copilot — it gives Copilot a rulebook and verifies the rulebook was followed. Use only the provided sources; do not speculate on any capability not explicitly documented."

---

## Ground-truth constraints
- CORTEX is a **production-grade AI engineering framework** — a governance and orchestration layer between the developer and the LLM.
- Live-count callouts (use as lower-thirds, one at a time, never stacked):
  - `"186+ orchestrators"` across 9 domains, Python
  - `"29 MCP tools"` — VS Code stdio (Pylance-style, auto-detected)
  - `"32 governance YAML rules"` — enforced at pre-commit, CI, and runtime
- CORTEX orchestrates the host LLM (GitHub Copilot / GPT) — it does **not** embed its own ML model.
- Claims permitted: "fewer regressions", "verifiable audit trail", "clearer definition of done"
- Claims forbidden: "eliminates bugs", "replaces Copilot", "game-changing", "revolutionary"

---

## Visual ingredients
Upload these as PNG/JPG into your NotebookLM Notebook before generating:
1. `cortex-docs/assets/diagrams/01-architecture-system-architecture-layers.md` (hero diagram — Scene 2)
2. `cortex-docs/assets/diagrams/03-workflow-sdlc-pipeline.md` (loop diagram — Scene 4)
3. `cortex-docs/assets/image-prompts/business-leader/01-roi-executive-dashboard.prompt.md` (outcomes — Scene 5)

**Glassmorphism treatment (mandatory for all frames):**
- Background: deep navy #0a0e27, subtle grid rgba(255,255,255,0.03)
- Panels: rgba(26,31,58,0.7), 1px rgba(255,255,255,0.1) border, 12px radius, 16px blur
- Accent glow: cyan #00d4ff with 0 0 20px rgba(0,212,255,0.3)
- Camera: slow dolly, gentle parallax — no whip pans, no aggressive zoom
- CORTEX logo watermark: bottom-right, 20% opacity, ~80px wide

---

## Scene-by-scene breakdown

**SCENE 1 — "The Cost of Fast" [0:00–1:30]**
Visual: Split canvas — LEFT side: AI-generated code appearing instantly, line by line, cursor blinking.
RIGHT side: a production incident timeline — three red markers labeled "Deploy", "Rollback", "Hotfix" at 11pm, 12:15am, 3am.
No CORTEX branding. No solution. Let the tension breathe.
Narrator (female, measured): *"AI tools make code fast. But fast code and production-ready code are different problems — and they require different discipline."*
On-screen callout (bottom-center, glassmorphic pill): `Speed ≠ Reliability`
VBP-002: first 8 seconds must hook before any branding appears.

**SCENE 2 — "What CORTEX Is" [1:30–3:30]**
Visual: The architecture layer diagram rises from dark — four layers materialise one at a time (VBP-004 progressive disclosure):
  Layer 1: Developer · VS Code (dim white)
  Layer 2: CORTEX Framework — MCP tools, IntentRouter, Orchestrators (cyan glow, brightens last)
  Layer 3: Host LLM — GitHub Copilot / GPT (purple accent)
  Layer 4: Governed Output — code + tests + audit trace (green)
Each layer label fades in only when the camera settles on that layer.
Lower-thirds appear sequentially as layers light up:
  → `"186+ orchestrators"` when CORTEX layer activates
  → `"29 MCP tools"` when MCP sublayer activates
  → `"32 governance YAML rules"` when enforcement sublayer activates
Narrator: *"CORTEX is the layer between the developer and the AI. It doesn't replace Copilot. It gives Copilot a rulebook — and verifies the rulebook was followed."*

**SCENE 3 — "Four Delivery Problems" [3:30–5:30]**
Visual: Four glassmorphic problem cards materialise one at a time — each card dims to 40% before the next appears (VBP-009 signaling):
  Card 1 — `Invisible debt` — "AI suggestions with no audit trail"
  Card 2 — `Inconsistent done` — "Definition of done shifts per sprint, per team"
  Card 3 — `Late regressions` — "Issues surface at deployment, not at commit"
  Card 4 — `No repeatability` — "Last quarter's process cannot be reconstructed"
Narrator speaks to each card's *business impact* — cost, risk, team trust — not to its technical cause. No jargon.
Analogies (one per card): "Like building without blueprints." / "Like a contract with no signature line." / "Like finding a leak after the ceiling collapses." / "Like a recipe that only lives in the chef's memory."

**SCENE 4 — "The Closed Loop" [5:30–7:30]**
Visual: SDLC pipeline diagram. Show Audit → Fix → Rescan as a single closed circuit with a violation counter.
The circuit does not open until the counter reaches 0. Animate: 4 violations → 2 → 0. Green checkmark. Timestamp.
YAML workflow config card appears briefly alongside: show structure (rule_id, severity, remediation) — not a vague blob.
Narrator: *"Every change goes through a closed loop. CORTEX audits, constrains the fix, then rescans. The loop doesn't close at 'good enough' — it closes at zero critical violations."*
On-screen callout: `Closed only at zero critical violations (CORE-068)`

**SCENE 5 — "What Leaders Measure" [7:30–End]**
Visual: Four outcome stat cards — plain language, no invented numbers, no percentages:
  `"Fewer regressions at deployment"` — governance gates catch issues before merge
  `"Clearer definition of done"` — TDD-first gates enforce the standard
  `"Verifiable audit trail"` — every orchestrator invocation logged with timestamp
  `"Team alignment by default"` — shared rules = shared expectations, across every member
Strategic silence: 1.5 seconds before closing line (VBP-011).
Narrator: *"CORTEX doesn't make AI smarter. It makes AI-assisted development accountable — at every step, for every team member, in every commit."*
Final frame: CORTEX logo (full, centered) + `"Governance. Orchestration. Reliability."` in Space Grotesk.

---

## Audio direction
- Ambient synth bed: ~60 BPM, low and steady — never louder than the narrator
- Strategic silence: 1.5 sec before the Scene 5 closing line (emotional peak — VBP-011)
- Keyboard foley: Scene 4 only (loop walkthrough), subtle
- No dramatic trailer stings, no orchestral swells

---

## Production note
Use NotebookLM for narrative + slide generation. For Scene 4's loop counter animation, record the real `/audit fix` output in a terminal and stitch in post. Do not fabricate terminal output — plausible only.
