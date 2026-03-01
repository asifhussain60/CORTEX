# Tutorial 04 — Onboarding & Customization

> **Duration:** ~8 minutes · **Audience:** Tech Leads, Platform Engineers
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorials 01–03 complete
> **Goal:** Viewer can onboard their own repository and customize CORTEX for their team

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a ~8 minute hands-on tutorial for tech leads/platform engineers showing how to onboard a repository and customize CORTEX safely. Narration must focus on why each step matters (risk control, repeatability, governance) rather than reading commands. Keep examples realistic and plausible. For any true VS Code interactions, plan to use screen capture inserts and stitch after export." 

## Visual guidance (NotebookLM-friendly)
- Use simple before/after visuals and one-step-at-a-time progression.
- Prefer diagram/config screenshots as ingredients.
- Use screen capture for real UI moments; stitch later.

## CORTEX voice (tutorial)
- Narrator should sound like a **calm senior project lead**: honest about risk, focused on repeatability.
- Avoid hype. Emphasize “safe adoption” and “clear next steps.”

## SDLC templates visual
- Show workflow templates and custom rules as **YAML/JSON config** cards (what teams actually review).

## Define the closure rule (Audit → Fix → Rescan)
- **Audit**: identify issues in the onboarded repo (security/governance/testing gaps).
- **Fix**: remediate under constraints.
- **Rescan**: re-run checks/tests until critical violations are **0**.

---

## ⚠️ VISUAL IDENTITY — TUTORIAL THEME

> See tutorials `README.md` for amber/gold palette and tutorial visual rules.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Every narration line must add something the viewer cannot get from reading the screen: the *why it matters*, the *gotcha to watch for*, the *non-obvious implication*, or the *discipline behind the mechanic*. See tutorials `README.md` §Narration Philosophy for full guidance and examples.

---

## Cinematic simulation notes (optional; use as inspiration)

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floor
- **Accent neon:** Warm amber (#f5a623) primary; gold (#FFD700) accent for knowledge/pattern elements; organization-specific colors for multi-repo
- **Dashboard panels:** Frosted glassmorphism with amber neon borders, internal data visualizations visible through frosted glass
- **LENS beam:** Amber Lidar sweep (horizontal laser line) for repository scanning
- **Lighting:** Volumetric amber fog, ray-traced caustics from dashboard neon, bioluminescent knowledge particles
- **Feedback cues:** Green flash = scan phase complete, gold pulse = knowledge integrated, holographic glitch = security finding, Lidar sweep = pattern detection
- **Temporal evolution:** Environment evolves from single-repo (small, focused) → multi-repo (expansive, compound) — space literally expands as scope grows

**SCENE 1 — "The Awakening" (0:00–0:04)**
Camera: Static center-frame, locked on ray-traced glassmorphism floor.
Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric amber fog at ground level.
CORTEX logo fades in as hero image with amber electric-aura. Hold 3s. Logo shrinks to
bottom-right watermark with amber "TUTORIAL" label.

**SCENE 2 — "Repository Onboarding — The Four Phases" (0:30–2:30)**
Camera: FPV drone approach from above at 45° angle, descending through volumetric fog.
`/onboard` command types with amber cursor. Four-phase pipeline materializes as a
horizontal track of glassmorphic nodes with time-lapse mechanical assembly:

Phase 1 — Scan: LENS beam (amber Lidar laser) sweeps across a holographic file tree
representation. Language distribution badge materializes as a glassmorphic pie chart
with colored neon segments (Python blue, TypeScript cyan, YAML amber). File count and
line count float as holographic numbers with ray-traced glass surfaces. Particle
condensation animates the scan results forming.

Phase 2 — Security Assessment: Three priority tier shelves materialize with parallax
depth separation. P0 shelf (red neon, closest) carries critical finding cards with
holographic glitch effect. P1 shelf (amber neon, middle) carries important findings.
P2 shelf (blue neon, furthest) carries recommendations. Each card has file path + line
number visible through frosted glass. Ray-traced red caustics from P0 findings ripple
across the floor — urgency visualized.

Phase 3 — Pattern Detection: Enterprise patterns materialize as holographic confidence
badges — "Repository (0.91)" brightest, "Strategy (0.78)" moderate, "Observer (0.84)"
strong. Bioluminescent knowledge particles flow between detected patterns, forming
connection lines. An architecture diagram auto-assembles with time-lapse construction
from the detected patterns — nodes and edges drawing themselves with amber neon trails.

Phase 4 — Dashboard Generation: Findings compress — particle streams converge into a
central glassmorphic dashboard that assembles with mechanical construction animation.
Health score materializes as a large holographic number with ray-traced glass surface.
Sub-panels (dependency graph, security findings, pattern map, test coverage) fill in
with particle condensation. The dashboard glows with warm amber luminosity.

**SCENE 3 — "Reading the Dashboard" (2:30–3:30)**
Camera: Slow dolly-in with macro zoom on each dashboard section.
Each section gains amber neon border emphasis when the camera focuses on it. Camera
pans methodically: Health Score (holographic number pulses), Security Panel (P0 cards
elevate with parallax), Pattern Map (connections glow with bioluminescence), Dependency
Graph (interactive node hover simulation), Action Items (prioritized list with amber
step numbers).
Ray-traced reflections of the active section shimmer on adjacent panels — the dashboard
feels alive, interconnected.

**SCENE 4 — "Custom Governance Rules" (3:30–5:00)**
Camera: Tracking shot to a new workspace area — the governance workshop.
YAML editor materializes as a glassmorphic code panel with amber left border. Rule YAML
types character by character with amber cursor trail — `TEAM-001-rate-limiting.yaml`.
The rule structure highlights key fields with amber neon emphasis: `rule_id`, `severity`,
`pattern`, `remediation`.
Save: the YAML panel seals with a magnetic iris animation. `/audit` runs — the new rule
appears in the governance scan as a fresh glassmorphic card with amber "NEW" badge.
A route file without rate limiting triggers the rule — violation card materializes with
holographic glitch (amber, not red — it's a team rule, P1 severity). The violation card
shows the file path and the remediation message, visible through frosted glass.
Camera: Macro zoom hero moment on the remediation field — the guidance is specific,
actionable, with a link to the reference implementation.

**SCENE 5 — "Team Knowledge Preservation" (5:00–6:00)**
Camera: Slow dolly to a knowledge base area. Knowledge YAML types with gold (#FFD700)
cursor trail — the gold accent signals premium institutional knowledge.
`payment-timeout.yaml` materializes — the `anti-pattern` type badge glows red briefly,
then the `remediation` field glows gold with bioluminescent emphasis.
Particle evolution: the YAML entry transforms into a LENS-scannable knowledge node —
gold bioluminescent particles flow from the YAML card into the knowledge base network,
brightening the overall knowledge graph. A connection line forms between the knowledge
node and the related files (`payment_gateway.py`, `retry_handler.py`) — amber neon
conduits with visible data particles flowing.
Future scan simulation: a new developer's code triggers the pattern — the knowledge
card surfaces automatically with a gold holographic overlay. Tribal knowledge made
searchable.

**SCENE 6 — "Company Overrides" (6:00–6:45)**
Camera: Tracking shot. Overrides YAML types — `overrides.yaml`. Three sections
materialize as glassmorphic panels: naming convention, import restrictions, commit format.
Live demonstration: `import requests` types in a code panel — governance intercepts with
a holographic glitch and an amber info card materializes: "Use httpx for async HTTP.
See: docs/http-guide.md" — the card is a signpost, not a wall. The blocked import
dissolves with particle fragmentation; the correct import suggestion appears with
green glow.

**SCENE 7 — "Multi-Repository Scale" (6:45–7:30)**
Camera: Dramatic slow pull-back — the environment literally expands. Volumetric fog
parts to reveal additional repository dashboards materializing in the distance with
time-lapse mechanical construction. Three repos side by side, each with its own
glassmorphic dashboard, connected by shared governance neon conduits (amber) and
shared knowledge neon conduits (gold).
Bioluminescent knowledge particles flow between repositories — patterns learned in
repo-1 travel along gold conduits to repo-2 and repo-3. The compound effect: each
repo's health score ticks upward slightly as shared knowledge integrates.
Landing page materializes center-frame as a glassmorphic overview dashboard — all
repositories listed with health scores, security postures, and shared pattern counts.
Ray-traced reflections of all three repo dashboards create a warm amber pool on the
glass floor — the compound effect visualized as light.

**SCENE 8 — "Series Complete" (7:30–8:00)**
Camera: 360-degree orbital pan at 30° downward angle with parallax depth around the
complete multi-repo landscape. All dashboards glowing, governance conduits pulsing,
knowledge particles flowing.
Glassmorphic completion card assembles with time-lapse construction: four checkmarks
(onboarded, custom rules, knowledge preserved, overrides applied) each illuminate
green with bioluminescent flash.
Three paths forward materialize as glassmorphic cards with amber icons: 🔄 Iterate,
📊 Measure, 🏢 Scale.
Closing text: "Your code. Your rules. CORTEX adapts." — gold (#FFD700) text on dark
pill with holographic shimmer.
Series completion badge: "🎉 All 4 Tutorials Complete" with gold particle celebration.
Fade to black with ray-traced reflections dimming last.

---

## PROMPT

Create an ~8-minute tutorial video titled **"Onboarding & Customization"** using the amber/gold tutorial theme. Show how to bring your own codebase into CORTEX and tailor it to your organization.

### Intro — Why Onboard? (0:00 – 0:30)

**Glassmorphic card:**

> **You have existing code.** CORTEX needs to understand it before it can help. Onboarding creates a living intelligence model of your codebase — architecture, patterns, dependencies, security posture.

### Step 1 — Repository Onboarding (0:30 – 2:30)

**Run the onboard command:**

```
/onboard /path/to/your/project
```

**Show the 4-phase onboarding process:**

**Phase 1 — Scan (0:30 – 1:00):**
- LENS beam sweeps the file tree
- Language distribution badge: Python 65%, TypeScript 20%, YAML 10%, Other 5%
- File count, total lines, directory depth

**Phase 2 — Security Assessment (1:00 – 1:30):**
- Three priority tiers materialize:
  - P0 (red): Critical findings — hardcoded secrets, known vulnerable dependencies
  - P1 (amber): Important — missing input validation, no rate limiting
  - P2 (blue): Recommended — documentation gaps, naming inconsistencies
- Each finding has: file path, line number, description, remediation

**Phase 3 — Pattern Detection (1:30 – 2:00):**
- Enterprise patterns identified with confidence scores:
  - Repository pattern (0.91) — data access layer
  - Strategy pattern (0.78) — payment processing
  - Observer pattern (0.84) — event system
- Architecture diagram auto-generates from detected patterns

**Phase 4 — Dashboard Generation (2:00 – 2:30):**
- Findings compress into a SQLite database
- Glassmorphic dashboard materializes:
  - Health score (overall + per-category)
  - Dependency graph (interactive nodes)
  - Security findings prioritized
  - Pattern map
  - Test coverage overlay

**Narration:** "One command. Four phases. A complete intelligence model of your codebase. This isn't a report that gathers dust — it's a living dashboard."

**Narration (on Phase 2 — Security Assessment):** "P0 findings are the ones that need attention today — not in the next sprint. The priority tier tells you the urgency; the file path and line number tell you exactly where to go."

### Step 2 — Reading the Dashboard (2:30 – 3:30)

**Walk through each dashboard section:**

1. **Health Score** — Overall score with breakdown. Explain what each sub-score means.
2. **Security Panel** — P0s at the top. Click to see file path and remediation.
3. **Pattern Map** — Detected architecture patterns with confidence. Hover for details.
4. **Dependency Graph** — Visual import map. Highlight circular dependencies (if any).
5. **Action Items** — Prioritized list. Start with P0s.

**Dark pill:** *"The dashboard isn't the goal. The ACTION ITEMS are. Focus on P0s first."*

**Narration:** "A health score is a number. The action items are a work order. Navigate to the action items first — the score will follow."

### Step 3 — Adding Custom Governance Rules (3:30 – 5:00)

**Your organization has standards. Teach them to CORTEX.**

**Example: "All API endpoints must have rate limiting"**

**Create a governance rule YAML:**

```yaml
# cortex-registry/core/tier1-business/TEAM-001-rate-limiting.yaml
rule_id: TEAM-001
title: API Rate Limiting Required
tier: 1  # Business Logic
severity: P1
description: All API endpoints must implement rate limiting
pattern:
  file_match: "**/routes/**/*.py"
  must_contain: "rate_limit"
  error_if_missing: "No rate limiting detected in API route"
remediation: "Add @rate_limit decorator from cortex.tools.security"
```

**Save and verify:**
- Run `/audit` — the new rule appears in the governance scan
- If a route file is missing rate limiting, it's flagged as P1

**Narration:** "One YAML file. Your rule is now enforced automatically — at every commit, every audit, every CI run."

**Narration (on the violation card appearing):** "This is the moment every code review comment becomes unnecessary. The rule enforces itself — the feedback arrives before the PR, not during it."

### Step 4 — Adding Team Knowledge (5:00 – 6:00)

**Your team has learned things. Preserve that knowledge.**

**Example: "Our payment service has a known issue with timeout handling"**

**Add to the knowledge base:**

```yaml
# cortex-registry/knowledge-base/payment-timeout.yaml
domain: payment-processing
type: anti-pattern
title: Payment Timeout Race Condition
description: |
  When payment gateway timeout exceeds 30s, the retry logic
  can create duplicate charges. Always use idempotency keys.
severity: P0
related_files:
  - "services/payment_gateway.py"
  - "services/retry_handler.py"
remediation: |
  Wrap all payment calls with IdempotencyGuard.
  See: services/payment_gateway.py:45 for reference implementation.
```

**Result:** LENS now detects this pattern in future scans. New team members are warned automatically.

**Narration:** "Tribal knowledge becomes searchable, enforceable knowledge. When your senior engineer leaves, their wisdom stays."

**Narration (on the YAML entry):** "The remediation field is the part that makes this genuinely useful: not just 'this is a problem' but 'here's how to fix it, and here's a reference implementation.' That's institutional knowledge, not a wiki entry."

### Step 5 — Company Overrides (6:00 – 6:45)

**Customize default behavior without forking:**

```yaml
# cortex-registry/company/overrides.yaml
naming_convention:
  style: snake_case          # Enforce your standard
  exceptions:
    - "*.test.ts"            # Allow test file naming flexibility

import_restrictions:
  blocked:
    - "import requests"      # Use httpx instead
  message: "Use httpx for async HTTP. See: docs/http-guide.md"

commit_format:
  type: conventional
  scopes:
    - auth
    - payment
    - inventory
    - shipping
```

**Show the effect:** A developer tries `import requests` — governance catches it with a helpful message pointing to the team's HTTP guide.

**Narration:** "That message isn't a wall. It's a signpost — pointing the developer to what the team has already decided, rather than leaving them to discover it in a review comment two days later."

### Step 6 — Multi-Repository Setup (6:45 – 7:30)

**For teams with multiple repositories:**

1. Onboard each repository individually: `/onboard /path/to/repo-1`, `/onboard /path/to/repo-2`
2. Shared governance rules apply across all repos (from the registry)
3. Shared knowledge base means patterns learned in one repo benefit all repos
4. Unified dashboard shows organization-wide health

**Show the landing page** — all repositories with health scores, security posture, shared patterns.

**Narration:** "Each repository you onboard makes the platform smarter. Shared governance, shared knowledge, compound benefits."

**Narration (on the landing page):** "The landing page is the thing that changes conversations with leadership. Instead of 'I think our security posture is okay,' you have a dashboard that answers the question."

### Step 7 — What's Next (7:30 – 8:00)

**Glassmorphic completion card:**

- ✅ Repository onboarded with full intelligence model
- ✅ Custom governance rules enforced
- ✅ Team knowledge preserved and searchable
- ✅ Company overrides applied without forking

**Three paths forward:**

1. 🔄 **Iterate** — Run `/audit fix` regularly. Watch metrics improve over time.
2. 📊 **Measure** — Track quality metrics across sprints. Use the dashboard.
3. 🏢 **Scale** — Onboard more repositories and team members. The compound effect (Video 8) begins.

**Closing text:** **"Your code. Your rules. CORTEX adapts."**

**Final card:** Series complete. All 4 tutorials finished. 🎉

**Narration:** "You've completed the full learning path — from installation to organizational customization. The tutorials are done. The rest is practice. Run `/audit fix` on your real codebase. That's where it starts to feel like yours."

---

## Notes
- This tutorial closes the learning journey — from installation to organizational customization
- The governance rule YAML example is realistic and immediately usable
- Knowledge base entry shows how tribal knowledge becomes institutional knowledge
- Company overrides demonstrate customization WITHOUT forking — a key platform engineering principle
- **No hardcoded architecture counts** — customization is described by capability
- The multi-repository setup connects back to Video 7 (Extensibility & Onboarding) without repeating it
