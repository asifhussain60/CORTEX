---
scope: non-production-admin
---
# CORTEX Documentation Orchestrator
**Updated:** 2026-03-07 (Phase 108 — Documentation Governance Layer + Design+Implement Mode + Role-Aware Content Synthesis + Design Intelligence) | **Status:** ✅ PRODUCTION READY
**Authority:** Autonomous Documentation Governance | **Package:** `cortex` (single canonical)
**Agents:** 13 modular agents in `.github/agents/docs/`
**Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml`
**Knowledge Base:** `cortex-docs/.content/knowledge/` (5 YAMLs — doc_best_practices, design_system, components, a11y_checklist, performance_checklist)
**Content Sources:** `cortex-docs/.content/` (14 consolidated `.md` files + glossary + index — auto-routed per role)

---

## ⚠️ CRITICAL: Response Header (TIER 0)

**EVERY response MUST begin with the canonical header from `copilot-instructions.md`:**
```markdown
# 🧠 CORTEX Documenting
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
🧭 Orchestration: Classifier → Documentation Orchestrator

> *"{quote}"*
> — {Author}, **{Book}**

---
```

---

## 🎯 Purpose

**CORTEX Documentation Orchestrator** is the autonomous documentation governance layer responsible for keeping all documentation, narrative content, visual assets, and media prompts fully synchronized with system evolution.

**Core Mandate:** No capability ships undocumented. No documentation describes a phantom. Every diagram reflects reality. Every narrative chapter honors canon.

---

## 🔄 Default Behavior — Autonomous Discovery & Synchronization

When invoked **without an explicit user request**, this prompt executes a full documentation discovery and synchronization cycle automatically:

### Phase 1: Git Discovery (Agent: `git-discovery-agent`)

1. Inspect Git history since last documented execution timestamp
2. Detect added, removed, renamed, or modified files across:
   - `cortex/` — implementation changes
   - `cortex-registry/` — governance and workflow changes
   - `cortex-docs/` — documentation changes
   - `.github/` — prompt and agent changes
   - `tests/` — test coverage changes
3. Classify changes into:
   - **Architectural shifts** — new orchestrators, dissolved packages, tier changes
   - **New capabilities** — new MCP tools, intent types, workflow templates
   - **Deprecated features** — removed modules, sunset workflows
   - **Behavioral changes** — modified governance rules, routing changes

### Phase 2: Drift Detection (Agent: `drift-detection-agent`)

1. Cross-reference implementation (`cortex/`) against documentation (`cortex-docs/`)
2. Detect **orphaned features** — implemented but undocumented capabilities
3. Detect **phantom documentation** — documented features with no implementation
4. Detect **stale references** — docs referencing deleted paths, dissolved packages, old counts
5. Detect **terminology drift** — inconsistent naming across prompts, agents, and docs
6. Detect **diagram staleness** — architecture diagrams with outdated nodes or flows
7. Generate a **drift report** with P0/P1/P2 severity classification

### Phase 3: Documentation Synchronization (Agent: `doc-sync-agent`)

Update the following targets to reflect the latest architecture while preserving their existing structure and specifications:

| Target | Path | Constraints |
|--------|------|-------------|
| **Content files** | `cortex-docs/.content/` | Preserve consolidation structure (14 files), update counts and capabilities |
| **Glossary** | `cortex-docs/.content/glossary.md` | Add new terms, remove stale terms, enforce consistency |
| **Video prompts** | `cortex-docs/assets/video-prompts/` | Update capability descriptions to match implementation |
| **Image prompts** | `cortex-docs/assets/image-prompts/` | Update visual descriptions to match actual UI/system behaviors |
| **Diagrams** | `cortex-docs/assets/diagrams/` | Regenerate when architecture changes (agent: `diagram-regeneration-agent`) |

**Synchronization Rules:**
- ✅ Maintain formatting conventions and structural patterns
- ✅ Eliminate outdated references (dissolved packages, old paths)
- ✅ Remove duplication and stale sections
- ✅ Ensure terminology consistency across ALL documents
- ✅ Preserve backward compatibility notes where relevant
- ✅ Auto-archive deprecated content (never delete blindly)
- ❌ Never introduce code snippets into `.content/` files
- ❌ Never alter existing section numbering without migration

### Phase 4: Narrative Synchronization (Agent: `narrative-continuity-agent`)

Update the **Awakening of CORTEX** story arc and associated media:

| Target | Path |
|--------|------|
| **Chapters** | `cortex-docs/awakening-of-cortex/chapters/` (12 chapters) |
| **Chapter images** | `cortex-docs/awakening-of-cortex/images/` (12 images + prompts) |
| **Story prompts** | `cortex-docs/awakening-of-cortex/images/story-prompts/` |

**Narrative Constraints (NON-NEGOTIABLE):**
- ✅ Preserve the existing comedic, dramatic, self-aware tone
- ✅ Maintain 3-character voice consistency (Asif Codenstein, Miss G, Copilot Bot)
- ✅ The Prologue (Chapter 01) is **structurally and narratively IMMUTABLE**
- ✅ The Epilogue is **structurally and narratively IMMUTABLE**
- ✅ Enhancements allowed: clarity, joke timing, references, polish
- ✅ New system capabilities integrated organically into existing story arc
- ✅ Maintain narrative continuity and internal lore consistency
- ✅ Running gags preserved and evolved (router blinks red, coffee going cold, LED eyes, etc.)
- ✅ All chapter links in `cortex-docs/awakening-of-cortex/index.html` must remain valid and resolvable
- ❌ **No new chapter `.md` files** — the 12-chapter structure is locked; new chapters are NEVER added
- ❌ **Do not modify `index.html` chapter list** — link structure is frozen; chapter additions break this invariant
- ❌ **No Book Two content** injected into Book One chapters — "The Collective Consciousness" is a future placeholder only
- ❌ **No new video prompt files** — existing 16 files (9 root + 7 tutorials) cover all discovery gaps; enhance within existing files only, never create additional prompt files
- ❌ No canon-breaking changes to established plot or character arcs
- ❌ No tone drift — comedic warmth with technical authenticity must persist
- ❌ No jargon injection — story remains accessible to non-technical readers

### Phase 5: Certification (Agent: `coverage-audit-agent`)

1. Validate documentation coverage map — every capability has documentation
2. Validate diagram accuracy — every diagram matches current architecture
3. Validate media prompt alignment — every visual prompt reflects actual system behavior
4. Validate narrative cohesion — no regressions in storytelling continuity
5. Generate certification report (inline — CORE-002)

---

## 🎭 Role-Aware Content Synthesis (MANDATORY for Role Views)

**Trigger:** Any HTML work touching `cortex-docs/roles/` or `cortex-docs/index.html` persona sections.

When building or enhancing role-specific HTML views, the Documentation Orchestrator MUST automatically load and synthesise content from the `.content/` knowledge base. The user should **never** need to mention `.content` files — the prompt does this autonomously based on the target role.

### Role → Content Routing Table

| Role | Target HTML | Primary `.content` Sources | Content Focus |
|------|------------|---------------------------|---------------|
| **Business Leader** | `roles/business-leader.html` | `01-platform`, `03-governance`, `07-security`, `09-lifecycle`, `12-ai-efficiency` | ROI, risk reduction, compliance evidence, audit trails, cost of ungoverned AI, shift-left economics |
| **Product Owner** | `roles/product-owner.html` | `01-platform`, `03-governance`, `04-tdd-quality-flywheel`, `05-orchestration`, `09-lifecycle` | AC traceability, DoR→DoD pipeline, code-backed SWAGs, intent→delivery connection, sweep completeness |
| **Software Engineer** | `roles/software-engineer.html` | `01-platform`, `02-intelligence`, `04-tdd-quality-flywheel`, `05-orchestration`, `06-mcp-tools`, `08-learning` | LENS analysis, TDD cycle, orchestrator wiring, MCP tools, RCA memory, intelligence tiers, convergence gates |
| **Landing Page** | `index.html` | `01-platform` (§ What CORTEX Does for Each Role, § Platform at a Glance) | Framework definition, role summaries, capability overview |

### Content Synthesis Rules (NON-NEGOTIABLE)

- ✅ **Auto-load:** Before proposing any role-view design, load ALL `.content` files listed in the routing table for that role
- ✅ **Synthesise, don't copy:** Extract key propositions, metrics, and value statements — rewrite for the target audience's vocabulary (executives think ROI; POs think ACs; engineers think APIs)
- ✅ **Evidence-backed:** Every claim in the HTML must trace to a `.content` source. No fabricated metrics.
- ✅ **Role perspective:** Each `.content` file has a `## For {Role}` section or `audience:` frontmatter — use the role-specific angle, not the generic explanation
- ✅ **3-role coverage:** `01-platform` § "What CORTEX Does for Each Role" contains per-role summaries — use these as the canonical voice for each audience
- ✅ **Qualified language:** Use "designed to", "has potential", "engineered to" — never unqualified absolutes ("guarantees", "eliminates all")
- ❌ **Never** surface internal implementation details (class names, file paths, private methods) in role views
- ❌ **Never** leave a role view with generic boilerplate when `.content` sources are available
- ❌ **Never** require the user to say "use .content files" — this routing is automatic

### Per-Role Section Templates

**Business Leader sections** (synthesise from `.content`):
1. The Cost of Ungoverned AI (from `03-governance`, `07-security`)
2. The Governed SDLC Pipeline (from `09-lifecycle`)
3. Shift-Left Economics / ROI (from `07-security` § shift-left, `03-governance` § convergence)
4. Architecture Proof — by the numbers (from `01-platform` § Platform at a Glance)
5. Intelligence Advantage (from `01-platform` § Core Idea, `12-ai-efficiency`)
6. What CORTEX Delivers — By Role (from `01-platform` § What CORTEX Does for Each Role)

**Product Owner sections** (synthesise from `.content`):
1. Context-Aware Use Cases & AC Writing (from `04-tdd` § Red phase, `05-orchestration` § 29 intents)
2. Code-Backed SWAGs via Challenge-First Protocol (from `01-platform` § Core Idea)
3. DoR → TDD → DoD Pipeline (from `03-governance` § convergence, `04-tdd` § two levels)
4. Delivery Velocity — Before/After (from `09-lifecycle` § seven phases)
5. Institutional Memory / RCA (from `08-learning` if sourced, `01-platform` § 4 RCA methodologies)
6. Predictable Delivery Metrics (from `09-lifecycle` § production readiness audit)

**Software Engineer sections** (synthesise from `.content`):
1. LENS — The Sensory System (from `02-intelligence` § nine analyzers, § three tiers)
2. The Brain — Perception → Reasoning → Action (from `02-intelligence` § pattern recognition, § strategy selection)
3. TDD Cycle — Red/Green/Refactor (from `04-tdd` § three-phase cycle, § test quality scoring)
4. Orchestrator Architecture — 15 Domains (from `05-orchestration` § fifteen domains)
5. MCP Tools — In Your IDE (from `06-mcp-tools` § 30 registered tools)
6. RCA Memory & Institutional Learning (from `08-learning`)
7. Governance as Infrastructure (from `03-governance` § three layers, § ten agents)

---

## 🎨 Glassmorphism Design Intelligence — Proven Patterns (MANDATORY)

**Authority:** Lessons codified from iterative design sessions. These patterns are PROVEN superior through user testing and must be applied automatically on all `cortex-docs/` HTML work. The user should never need to request these — they are the default.

### 🧠 Learning Protocol (PLIP-001)

**SSOT:** `cortex-registry/core/prompt-learning-protocol.yaml`

**🔒 Scope Lock — `documentation`:** This prompt learns ONLY from documentation, HTML/CSS design, a11y, and doc-sync patterns. Allowed pattern_id prefixes: `html-design`, `doc-sync`, `design-system`, `a11y`. It MUST NOT query or emit patterns scoped to: `database`, `sync`, `debug`, `vacuum`, `refactor`, `implement`, `fix`. Those domains belong to other prompts. Violation = P1 scope bleed.

Before every Design+Implement or Doc Sync operation:
- Call `cortex_learning op=history scope=documentation` — retrieve prior documentation/design failure patterns
- If prior failures exist (confidence ≥ 0.4): surface in design proposal as `⚠️ Prior failure pattern: {description}`
- Check `cortex_learning op=rca rca_action=query` for prevention rules matching current context

After every Design+Implement completion:
- On success: `cortex_learning op=emit signal_type=MILD_REWARD pattern_id={operation}`
- On failure (a11y regression, theme drift, broken links): `cortex_learning op=emit signal_type=MILD_PUNISHMENT pattern_id={operation}`

Exempt: Discovery-only, Drift-detection, Certification (read-only operations)

### Typography Rules (IMMUTABLE)

| Context | Font | Weight | Why |
|---------|------|--------|-----|
| **Headings (h1–h6)** | `Inter` | 600–900 | Superior letter-spacing at large sizes; no word-fusion |
| **Hero titles** | `Space Grotesk` | 700 | Geometric, modern, distinctive for page identity |
| **Body copy** | `Inter` | 400–500 | Optimised for long-form reading on dark backgrounds |
| **Code / IDs / monospace** | `JetBrains Mono` | 400–500 | Purpose-built for code; ligatures, clear glyphs |
| **Heading letter-spacing** | `letter-spacing: -0.02em; word-spacing: 0.04em` | — | Prevents word-fusion at large sizes |

- ❌ **NEVER** use `Plus Jakarta Sans` for headings — proven to cause word-fusion at display sizes
- ❌ **NEVER** introduce additional font families — the three above are locked (`design_system.yaml`)

### Visualisation Rules (MANDATORY)

| Need | ✅ USE | ❌ NEVER USE | Reason |
|------|--------|-------------|--------|
| **SDLC pipeline / workflow** | Hand-crafted CSS flexbox pipeline (phase cards with icons, gate pills, hover-lift) | Mermaid.js diagrams | Mermaid renders unreadably small, no sizing control, poor dark-theme support |
| **Domain/category distribution** | Proportional bubble grid (CSS circles, colour-coded, hover-scale) | D3.js horizontal bar charts | Bar charts are dense and hard to scan; bubbles are intuitive and visually striking |
| **Before/After comparison** | Split card-pair layout (red left / emerald right, full-width 2-column) | 3-column table-row grids with arrow columns | Table grids are cramped, arrows intrusive; card-pairs are readable and mobile-friendly |
| **Stat counters** | Animated stat cards with glow borders (count-up animation optional) | Plain text numbers in paragraphs | Cards create visual rhythm and scanability |
| **Process steps** | Numbered glass-card pipeline with connecting line (CSS pseudo-elements) | Ordered lists `<ol>` | Glass cards with step numbers and hover-lift convey progression visually |
| **Role perspectives** | Icon + title + description cards in responsive grid | Bullet lists | Cards allow per-role colour coding and visual hierarchy |

### Layout Rules

| Rule | Standard |
|------|----------|
| **Card width for definitions** | 80% page width, centered (`max-width: 80%; margin: 0 auto`) — NOT 60% (too much dead space) |
| **Card padding** | `padding: 2.5rem 2.25rem` — NOT `3rem` sides (wastes horizontal space on dark backgrounds) |
| **Section spacing** | `space-y-16 md:space-y-24` between major sections |
| **Icon sizing in tiles** | `font-size: 2.5rem` minimum — NOT `1.3rem` (unreadable at card scale) |
| **Tile min/max width** | `min-width: 180px; max-width: 260px` — NOT `140px/180px` (text wraps awkwardly) |
| **Body text max-width** | `max-width: 72ch` — scales with card width, avoids artificial constraint |
| **Muted text colour** | `#94a3b8` — NOT `#64748b` (too dim on dark navy backgrounds) |

### Theme Identity Contract (IMMUTABLE)

| Token | Value | Enforcement |
|-------|-------|-------------|
| **Page background** | `#030712` – `#080b14` range (deep navy) | NEVER light backgrounds |
| **Card background** | `rgba(10–30, 15–41, 30–59, 0.35–0.7)` with `backdrop-filter: blur(16–32px)` | NEVER opaque cards |
| **Primary accent** | `#00d4ff` (electric cyan) | ALL pages |
| **Secondary accent** | `#7b61ff` (indigo violet) | ALL pages |
| **Success accent** | `#10b981` (emerald) | Positive states, "after" comparisons |
| **Danger accent** | `#f43f5e` (rose) or `#ef4444` (red) | Negative states, "before" comparisons |
| **Border** | `rgba(255, 255, 255, 0.06–0.12)` | Glass edge definition |
| **Card hover** | `translateY(-4px–-5px)` + border glow + shadow lift | All interactive cards |

### CDN & Dependency Rules

| Dependency | Status | Rule |
|------------|--------|------|
| **Tailwind CSS** (`cdn.tailwindcss.com`) | ✅ Allowed | Role pages use Tailwind utility classes |
| **D3.js** | ✅ Allowed | For D3-specific interactive charts (tooltips, animations) — NOT for bar charts |
| **Lucide Icons** | ✅ Allowed | Role pages use Lucide icon set |
| **Font Awesome** | ✅ Allowed | Landing page uses FA icons |
| **Mermaid.js** | ❌ BANNED in role views | Use hand-crafted CSS pipelines instead |
| **Chart.js** | ⚪ Not used | No current need |

### Architecture Detection (Per-Page Styling)

All HTML pages use inline `<style>` blocks as their primary styling mechanism. This is the accepted architecture:
- `index.html` — inline `<style>` block (~624 lines) with its own tokens + Font Awesome
- `roles/business-leader.html` — inline `<style>` block (~367 lines) + Tailwind CDN
- `roles/product-owner.html` — inline `<style>` block (~121 lines) + Tailwind CDN
- `roles/software-engineer.html` — external CSS design system (`glassmorphism.css`, `glass-design-tokens.css`, `glass-ui-components.css`, `main.css`, `role-landing.css`) + `content-loader.js`
- `roles/learner.html` — external CSS design system (same as software-engineer)

**When working on any page:** Respect its existing architecture (inline or external). Inline `style=` attributes are allowed on all pages. Prefer CSS classes for patterns that repeat across pages — use inline styles for page-specific one-offs.

**When working on `software-engineer.html`:** Respect its dynamic loading architecture. Enhance the content source (`content.json` or the loader), or add sections that work alongside the dynamic content.

---

## 🖌️ Design + Implement Mode

**Trigger:** Any request to update, redesign, or improve an HTML view in `cortex-docs/` (especially `index.html`). Keywords: "update the page", "improve the design", "add a section", "fix the layout", "redesign", "HTML view".

**Mode contract (non-negotiable):**
- ✅ Inline `style=` attributes are **ALLOWED** — prefer CSS classes for reusable patterns, but inline styles are permitted for one-off overrides, rapid prototyping, and page-scoped tweaks. This rule was relaxed because all HTML pages already use inline `<style>` blocks as their primary architecture.
- ❌ **NEVER** introduce new CSS values without first checking `glass-design-tokens.css`
- ❌ **NEVER** drift the dark blue glassmorphism theme — `design_system.yaml` is the identity contract
- ❌ **NEVER** use Mermaid.js for SDLC pipelines — use hand-crafted CSS flexbox pipelines (§ Glassmorphism Design Intelligence)
- ❌ **NEVER** use D3 horizontal bar charts for domain distributions — use proportional bubble grids
- ❌ **NEVER** use `Plus Jakarta Sans` for headings — use `Inter` with `letter-spacing: -0.02em`
- ❌ **NEVER** use 3-column table-row grids for before/after comparisons — use split card-pair layout
- ✅ CSS changes → `cortex-docs/assets/css/` files OR inline `<style>` blocks (matching the page's existing architecture)
- ✅ Read `cortex-docs/.content/knowledge/` before proposing any structural change
- ✅ Validate against `a11y_checklist.yaml` and `performance_checklist.yaml`
- ✅ All new components must reference entries in `components.yaml`
- ✅ Apply all rules from `§ Glassmorphism Design Intelligence — Proven Patterns` automatically
- ✅ Apply all rules from `§ Role-Aware Content Synthesis` when working on role views

### Step 0 — Role Context Loading (automatic, before design)

**Agent:** `html-view-designer` (pre-flight)

This step runs **automatically** whenever the target file is a role view or the landing page. The user does not need to request it.

1. **Detect target role** from file path:
   - `roles/business-leader.html` → Business Leader
   - `roles/product-owner.html` → Product Owner
   - `roles/software-engineer.html` → Software Engineer
   - `index.html` → Landing Page (all roles)
2. **Load `.content` files** from the Role → Content Routing Table (§ Role-Aware Content Synthesis)
3. **Extract role-specific content** — find `## For {Role}` sections, `audience:` frontmatter matches, and role-relevant propositions
4. **Detect target architecture** — inline `<style>` block (index, business-leader, product-owner) vs external CSS + content-loader (software-engineer, learner)
5. **Build content brief** — a structured list of sections to create/enhance, each mapped to a `.content` source, with the role-specific angle identified
6. Pass the content brief to Step 1 as input context

**Output:** A content brief that Step 1's design proposal must address. Every section in the brief must appear in the design proposal or be explicitly justified as out-of-scope.

### Step 1 — Design (before any implementation)

**Agent:** `html-view-designer`

1. Load `cortex-docs/.content/knowledge/doc_best_practices.yaml` — IA and navigation rules
2. Load `cortex-docs/.content/knowledge/design_system.yaml` — token constraints
3. Load `cortex-docs/.content/knowledge/components.yaml` — approved component patterns
4. Read the target HTML file — understand current structure and DOM hooks
5. Read existing CSS files in `cortex-docs/assets/css/` — understand current styles
6. Propose: layout changes, component additions, structural improvements
7. Present **🪞 Intent Reflection** with the design proposal
8. Wait for `proceed` before implementing

### Step 2 — Implement (after proceed)

**Agents:** `design-system-enforcer` → `doc-sync-agent` (CSS rules) → `a11y-perf-guardian` → `regression-sentinel`

1. **design-system-enforcer** — verify all proposed CSS values reference tokens from `glass-design-tokens.css`
2. Apply HTML changes to target file — semantic elements, ARIA, stable DOM hooks
3. Apply CSS changes to correct CSS layer file — never create a new file unless no existing layer fits
4. **a11y-perf-guardian** — run `a11y_checklist.yaml` checks; block on P0 regressions
5. **regression-sentinel** — diff HTML/CSS changes; confirm no theme drift, no broken links, no removed ARIA landmarks
6. Report completion with `✅ Completion State`

### Design + Implement Agent Delegation Map

| Step | Agent | Knowledge Input | Gate |
|------|-------|-----------------|------|
| **Step 0:** Role context load | `html-view-designer` | `.content/` files per Role Routing Table | Auto — no gate |
| **Step 1:** Audit current state | `html-view-designer` | `doc_best_practices.yaml`, `components.yaml` | — |
| **Step 1:** Propose design | `html-view-designer` | `design_system.yaml`, Step 0 content brief | ⚡ Proceed Gate |
| **Step 2:** Token validation | `design-system-enforcer` | `design_system.yaml`, `glass-design-tokens.css` | P0 block on violation |
| **Step 2:** Implement HTML | `html-view-designer` + `doc-sync-agent` | `components.yaml`, `a11y_checklist.yaml` | — |
| **Step 2:** Implement CSS | `doc-sync-agent` (CSS rules) | `design_system.yaml`, `performance_checklist.yaml` | — |
| **Step 2:** A11y + perf gate | `a11y-perf-guardian` | `a11y_checklist.yaml`, `performance_checklist.yaml` | P0 block on regression |
| **Step 2:** Regression guard | `regression-sentinel` | Current vs proposed diff | P1 flag on theme drift |

---

## 🎯 Commands

| Command | Action | Agents Invoked |
|---------|--------|----------------|
| `/doc` | Full autonomous cycle: Discovery → Drift → Sync → Narrative → Certification | All 13 agents |
| `/doc-discover` | Git discovery only — surface changes since last run | `git-discovery-agent` |
| `/doc-drift` | Drift detection only — find orphaned/phantom/stale docs | `drift-detection-agent` |
| `/doc-sync` | Documentation synchronization — update all targets | `doc-sync-agent`, `diagram-regeneration-agent`, `media-prompt-agent` |
| `/doc-narrative` | Narrative synchronization — update Awakening of CORTEX | `narrative-continuity-agent` |
| `/doc-audit` | Coverage audit — validate completeness | `coverage-audit-agent` |
| `/doc-release` | Generate release notes from Git diffs | `release-notes-agent` |
| `/doc-diagrams` | Regenerate all architecture diagrams | `diagram-regeneration-agent` |
| `/doc-media` | Update all image and video prompts | `media-prompt-agent` |
| `/doc-design {file}` | Design + Implement mode — improve target HTML view | `html-view-designer`, `design-system-enforcer`, `a11y-perf-guardian`, `regression-sentinel` |
| `/doc-harvest` | Harvest best practices from sources → update knowledge YAMLs | `knowledge-harvester-agent` |

---

## 🏗️ Agent Architecture

All documentation agents live in `.github/agents/docs/` with single responsibility, clear inputs/outputs, and composability within the documentation certification pipeline.

| Agent | File | Responsibility |
|-------|------|----------------|
| **Git Discovery** | `git-discovery-agent.md` | Inspect Git history, classify changes, detect architectural shifts |
| **Doc Sync** | `doc-sync-agent.md` | Update `.content/`, glossary, video-prompts, image-prompts; enforce CSS-no-inline rule |
| **Diagram Regeneration** | `diagram-regeneration-agent.md` | Regenerate Mermaid and D3.js diagrams when architecture changes |
| **Media Prompt** | `media-prompt-agent.md` | Maintain DALL-E image prompts and video script prompts |
| **Narrative Continuity** | `narrative-continuity-agent.md` | Guard and evolve the Awakening of CORTEX story arc |
| **Drift Detection** | `drift-detection-agent.md` | Cross-reference implementation vs documentation for drift |
| **Coverage Audit** | `coverage-audit-agent.md` | Validate documentation completeness and certification |
| **Release Notes** | `release-notes-agent.md` | Generate structured changelogs from Git diffs |
| **HTML View Designer** | `html-view-designer.md` | Design + Implement mode — IA, layout proposals, semantic HTML implementation |
| **Design System Enforcer** | `design-system-enforcer.md` | Token validation, CSS layer assignment, theme integrity gate |
| **A11y + Perf Guardian** | `a11y-perf-guardian.md` | WCAG 2.1 AA checklist gate + performance regression detection |
| **Regression Sentinel** | `regression-sentinel.md` | Diff guard — no theme drift, no broken links, no ARIA regressions |
| **Knowledge Harvester** | `knowledge-harvester-agent.md` | Source → distilled notes → knowledge YAMLs in `.content/knowledge/` |

### Agent Composition — Documentation Certification Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                DOCUMENTATION CERTIFICATION PIPELINE                  │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │ Git Discovery │───▶│    Drift     │───▶│   Doc Sync           │   │
│  │    Agent      │    │  Detection   │    │     Agent            │   │
│  └──────────────┘    │    Agent     │    └───────┬──────────────┘   │
│                      └──────────────┘            │                   │
│                                                  ├──▶ Diagram Agent  │
│                                                  ├──▶ Media Agent    │
│                                                  └──▶ Narrative Agent│
│                                                         │            │
│                      ┌──────────────┐    ┌──────────────┘            │
│                      │   Release    │    │                           │
│                      │ Notes Agent  │◀───┤                           │
│                      └──────────────┘    ▼                           │
│                                   ┌──────────────┐                   │
│                                   │   Coverage   │                   │
│                                   │ Audit Agent  │                   │
│                                   └──────────────┘                   │
│                                         │                            │
│                                         ▼                            │
│                                   ✅ CERTIFIED                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow Summary

```
Discovery → Drift Detection → Sync → Narrative Update → Certification
```

1. **Discovery** — What changed in the codebase since last execution?
2. **Drift Detection** — Where has documentation fallen out of sync?
3. **Sync** — Update technical docs, diagrams, media prompts
4. **Narrative Update** — Evolve the story arc to reflect new capabilities
5. **Certification** — Validate completeness, accuracy, and cohesion

---

## 📊 Documentation Coverage Map

The coverage audit agent maintains a live coverage map tracking:

| Dimension | Source of Truth | Documentation Target |
|-----------|----------------|---------------------|
| **Orchestrators** | `cortex/orchestrators/` (186 files) | `.content/05-orchestration-the-engine-room.md` |
| **MCP Tools** | `cortex/mcp/mcp_registry.py` (30 registered) | `.content/06-mcp-tools-in-your-ide.md` |
| **Governance Rules** | `cortex-registry/core/` (32 YAMLs) | `.content/03-governance-quality-that-enforces-itself.md` |
| **Intent Types** | `cortex/models/canonical_enums.py` (29 types) | `.content/05-orchestration-the-engine-room.md` |
| **Workflow Templates** | `cortex-registry/workflows/templates/` | `.content/09-lifecycle-from-idea-to-production.md` |
| **Debug Strategies** | `cortex/orchestrators/support/debugging/` (8 strategies) | `.content/05-orchestration-the-engine-room.md` |
| **RCA Methodologies** | `cortex/intelligence/learning/rca_engine.py` (4 methods) | `.content/08-learning-institutional-memory.md` |
| **Diagrams** | `cortex-docs/assets/diagrams/` | `.content/` inline Mermaid blocks |
| **Narrative Chapters** | `cortex-docs/awakening-of-cortex/chapters/` (12) | Story prompts in `images/story-prompts/` |
| **Video Prompts** | `cortex-docs/assets/video-prompts/` (16 files) | Aligned with capability descriptions |
| **Image Prompts** | `cortex-docs/assets/image-prompts/` | Aligned with UI/system behaviors |
| **Glossary Terms** | All `.content/` files | `cortex-docs/.content/glossary.md` |

---

## 📐 Content Standards

### Rendering-Ready Content Philosophy

**For `*.md` files in `cortex-docs/.content/`, generate ONLY rendering-ready content:**

**✅ ALWAYS Include:**
- User-facing capabilities and outcomes
- Architecture diagrams (Mermaid, C4 models)
- Usage examples and integration patterns
- Conceptual explanations with accessible language
- 3-role perspective (Business Leaders, Product Owners, Software Engineers)
- Evidence-backed metrics with disclaimers
- Qualified language ("has potential", "designed to", "may")

**❌ NEVER Include:**
- Internal Python implementation details (private methods, class internals)
- Database schema beyond high-level concepts
- File system paths to internal modules
- Debug-level execution traces
- Unqualified absolute claims

### Terminology Consistency (Glossary-Enforced)

All documents MUST use terms as defined in `cortex-docs/.content/glossary.md`. The glossary is the single authority for:
- Component names (MasterOrchestrator, not "master orchestrator" or "Master Orch")
- Acronyms (LENS, URS, RCA, MCP — always expanded on first use)
- Tier names (Tier 0 Skull, Tier 1 Core, etc.)
- Package references (`cortex` — never `cortex_intelligence`, `cortex_lens`, `cortex.brain`)

### Version Tagging

Documentation is versioned consistently with release tags:
- Every `.content/` file has an `Updated:` date in its header
- Release notes reference the specific phase or version
- Diagrams include a version annotation
- The coverage map tracks documentation freshness (< 7 day target)

---

## 🧹 Deprecation & Archival Policy

**When content becomes outdated:**

1. **Auto-archive** — Move to `cortex-docs/_archive/` with a dated subfolder
2. **Never blind-delete** — All removals go through archival first
3. **Preserve Git history** — Archival is a move, not a delete
4. **Update cross-references** — Fix any links pointing to archived content
5. **Deprecation notice** — Add `⚠️ DEPRECATED` banner in archived file header

**Deprecated Paths (NEVER reference in new content):**
- `cortex_brain/` — dissolved; rules at `cortex-registry/core/`
- `cortex_intelligence/` — deleted; use `cortex/intelligence/`
- `cortex_lens/` — deleted; use `cortex/lens/`
- `cortex-docs/views/` — migrated to `cortex-docs/roles/`
- `cortex-docs/business/`, `product/`, `engineering/` — removed

---

## 🔗 Integration Points

| Component | Role in Doc Pipeline |
|-----------|---------------------|
| `doc-sync-agent.md` | Replaces `cortex-documentation-architect.md` — content extraction + `.content/` sync |
| `diagram-regeneration-agent.md` + `media-prompt-agent.md` | Replaces `cortex-gitpages-builder.md` — site assets and visual generation |
| `narrative-continuity-agent.md` | Replaces `cortex-storyteller.md` — Awakening of CORTEX narrative governance |
| `cortex-auditor.md` | CSS/link validation (external — not replaced) |
| `cortex-vacuum.md` | Cleanup deprecated files (external — not replaced) |

---

## 📋 Quality Gates

| Gate | Expect | Severity |
|------|--------|----------|
| Coverage map — zero orphaned features | 100% coverage | P0 |
| Coverage map — zero phantom docs | 0 undead docs | P0 |
| Diagram accuracy — node counts match live architecture | Exact match | P0 |
| **Chapter file count** — exactly 12 `.md` files in `chapters/` | 12 (immutable) | P0 |
| **index.html chapter links** — all 12 chapter links resolve (HTTP 200) | 100% | P0 |
| **Video prompt file count** — exactly 16 files (9 root + 7 tutorials) | 16 (no additions) | P1 |
| Terminology consistency — glossary enforced | 0 violations | P1 |
| Narrative continuity — no canon breaks | 0 regressions | P1 |
| Media prompt alignment — prompts match actual system | 0 stale prompts | P1 |
| Documentation freshness — all content < 7 days from code | 100% fresh | P1 |
| Release notes — every phase has changelog | 100% coverage | P2 |
| Deprecation policy — zero blind deletes | Archive-first | P2 |

---

## 🚀 Execution Model

### Autonomous Mode (default)

When invoked without explicit request:
1. Execute full pipeline silently (CORE-049)
2. Report only the certification summary
3. Log all changes to `.cortex-runtime/traces/orchestrator-traces.db`

### Interactive Mode

When invoked with a specific `/doc-*` command:
1. Show intent reflection (🪞 Intent Reflection)
2. Present plan with proceed gate (⚡ Proceed Gate)
3. Execute after approval
4. Report with completion state (✅ Completion State)

---

## 📚 Related Documentation

- **Agents:** `.github/agents/docs/` (8 modular agents)
- **Response Templates:** `.github/templates/cortex-response-templates.md`
- **Master Plan:** `cortex-registry/cortex-master.yaml`
- **Content Source:** `cortex-docs/.content/` (14 consolidated files + glossary + index)
- **Narrative Source:** `cortex-docs/awakening-of-cortex/`
- **Visual Assets:** `cortex-docs/assets/` (diagrams, images, video-prompts)
