/CORTEX /cortex-architect /cortex-doc

# CORTEX University — Learning Path Implementation Plan

**Last Updated:** 2026-03-08
**Status:** ✅ COMPLETE — Level 1 + Level 2 + Level 3 all done, cleanup done
**Chat History:** `_workspaces/.chats/chat01.md`
**Content Models:** `docs/.content/knowledge/learning-path-architecture.yaml`, `docs/.content/15-learning-path.md`

---

## Governing Rules

Follow all rules defined in:

- `cortex-doc.prompt.md` (documentation orchestrator — inline CSS, ISSA spacing, glassmorphism, D3.js only)
- cortex-doc agents (15 agents in `.github/agents/docs/`)
- `cortex-registry` governance
- `design_system.yaml` (ISSA tokens, typography, glass identity)
- `software-engineer.html` (THE reference structural pattern for all learning pages)

---

## Design System (IMMUTABLE — apply to every page)

| Token | Value |
|-------|-------|
| Page background | `#020617` |
| Glass background | `rgba(10,15,30,0.7)` |
| Glass border | `rgba(255,255,255,0.08)` |
| Accent teal | `#14b8a6` |
| Accent emerald | `#10b981` |
| Text main | `#f8fafc` |
| Text muted | `#94a3b8` |
| Hero font | `Space Grotesk` (500/600/700) |
| Body font | `Inter` (300–900) |
| Code font | `JetBrains Mono` (400/500/700) |
| ISSA content-content | `3rem` (48px) |
| ISSA content-panel | `2rem` (32px) |
| ISSA panel-panel | `1.5rem` (24px) |
| ISSA hero-first | `3rem` (48px) |
| ISSA mobile (≤640px) | `2rem` |
| ISSA tablet (641-1023px) | `3rem` |

### CDN Stack (every page)

```html
<script>const _tw=console.warn;console.warn=function(){if(arguments[0]&&typeof arguments[0]==='string'&&arguments[0].includes('cdn.tailwindcss.com'))return;_tw.apply(console,arguments)};</script>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://unpkg.com/lucide@latest"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Page Structure Pattern (from software-engineer.html)

```
<nav breadcrumb aria-label="Breadcrumb"> → <main max-w-7xl mx-auto px-4 md:px-6 space-y-12 md:space-y-16>
→ hero section → alternating glass panels (section.relative.py-8.my-4 with absolute bg + backdrop-blur)
and plain sections (section.space-y-10) → footer → <script> with window.onload for Lucide + D3
```

### Mandatory Compliance

- ALL CSS inline in `<style>` blocks — NO external CSS files
- `:root` with ISSA tokens in every page
- `prefers-reduced-motion` gate on all animations/transitions
- Skip link: `sr-only focus:not-sr-only`
- `scroll-margin-top: 4rem` on focus targets
- `aria-label="Breadcrumb"` on nav
- D3.js v7 ONLY — Mermaid BANNED
- Radial gradient backgrounds with domain accent color
- `window.onload` for Lucide icon initialization

---

## Folder Structure (canonical)

```
docs/learning/
├── index.html                                         ← Level 1: Portal
├── architecture-patterns/
│   ├── index.html                                     ← Level 2: Domain Explorer
│   └── concepts/
│       ├── orchestrator-domains.html                  ← Level 3: Deep Dive
│       └── five-step-lifecycle.html                   ← Level 3: Deep Dive
├── ai-orchestration/
│   ├── index.html                                     ← Level 2: Domain Explorer
│   └── concepts/
│       └── lens-sensory-system.html                   ← Level 3: Deep Dive
├── workflow-automation/
│   ├── index.html                                     ← Level 2: Domain Explorer
│   └── concepts/                                      ← Level 3: Future deep-dives
├── governance-quality/
│   ├── index.html                                     ← Level 2: Domain Explorer
│   └── concepts/                                      ← Level 3: Future deep-dives
├── tdd-development/
│   ├── index.html                                     ← Level 2: Domain Explorer
│   └── concepts/                                      ← Level 3: Future deep-dives
└── intelligence-learning/
    ├── index.html                                     ← Level 2: Domain Explorer
    └── concepts/                                      ← Level 3: Future deep-dives
```

---

## Progress Tracker

### ✅ COMPLETED — Content Models

| File | Description |
|------|-------------|
| `docs/.content/knowledge/learning-path-architecture.yaml` | Knowledge registry: 3-level arch, 6 domains, issue-derived knowledge, diagram specs |
| `docs/.content/15-learning-path.md` | Content model: domain descriptions, pedagogical philosophy |

### ✅ COMPLETED — Level 1 Portal

| File | Description |
|------|-------------|
| `docs/learning/index.html` | CORTEX University portal — hero with logo, journey pipeline (Orientation → Exploration → Mastery), 6 domain cards, role-based paths (SE/Tech Lead/PO/Curious Learner), philosophy panel, CTA section, footer. **Recreated clean (465 lines) — was corrupted with dual-HTML merge in prior session.** |

### ✅ COMPLETED — Level 2 Domain Explorers (all 6)

| File | Accent | Difficulty | D3 Graph | Concepts | Key Features |
|------|--------|-----------|----------|----------|-------------|
| `architecture-patterns/index.html` | Teal `#14b8a6` | Intermediate | 12-node force-directed (domains, lifecycle, intent-router, master-orch, protocol, ac-markers, cape, self-sustain, enforcement, tdd-orch, workflow-comp, health-orch) | 8 cards | CSS lifecycle pipeline (Prepare→Govern→Execute→Validate→Close), 2 deep-dive links |
| `ai-orchestration/index.html` | Violet `#8b5cf6` | Intermediate | 10-node force-directed (lens, facade, intent, master, tiers, session, mcp, kal, urs, rca) | 7 cards | Perception→Reasoning→Action pipeline with code blocks, 1 deep-dive link |
| `workflow-automation/index.html` | Emerald `#10b981` | Advanced | None (CSS tier hierarchy instead) | 6 cards | 3-tier hierarchy cards (Primitives/Mode Workflows/Composites), intent→workflow mapping display |
| `governance-quality/index.html` | Amber `#f59e0b` | Beginner | 11-node D3 governance concept map | 9 cards | 3 enforcement layer bars (Pre-Commit/CI/Runtime) with rule badges |
| `tdd-development/index.html` | Red `#ef4444` | Beginner | 10-node D3 TDD concept map | 5 cards | Red→Green→Refactor cycle UI, 4-tier test execution grid |
| `intelligence-learning/index.html` | Purple `#a78bfa` | Advanced | 11-node D3 intelligence concept map | 8 cards | Perceive→Reason→Act→Learn pipeline, 3-tier intelligence grid, 1 deep-dive link |

### ✅ COMPLETED — Level 3 Deep-Dive Pages

| File | Lines | D3 Diagram | Key Content |
|------|-------|-----------|-------------|
| `docs/learning/architecture-patterns/concepts/orchestrator-domains.html` | 472 | Bubble chart (14 domains, size-proportional) | Hospital analogy (6 departments), domain table with bars, directory structure, IOrchestrator protocol code, inter-domain communication rules |
| `docs/learning/architecture-patterns/concepts/five-step-lifecycle.html` | 524 | State diagram (5 nodes, loop arc Validate→Execute) | Surgical analogy, per-phase detail with primitive YAML tags + code blocks, AC marker anatomy, SQLite persistence, CORE-048/064/068 callouts |
| `docs/learning/ai-orchestration/concepts/lens-sensory-system.html` | 592 | Radial (LENS centre + 9 analyser nodes on orbit) | Medical-lab analogy, L/E/N/S acronym breakdown, 9 analyser cards, 3 intelligence tier cards, AnalysisContext dataclass, InteractionOrchestrator trigger flow |

### ~~❌ NOT YET CREATED — Level 3 Deep-Dive Pages~~

> **✅ All three Level 3 pages completed — see section above.**

#### ~~3a.~~ `docs/learning/architecture-patterns/concepts/orchestrator-domains.html` ✅

**Linked from:** architecture-patterns/index.html concept card 01
**Accent:** Teal `#14b8a6`
**Content required:**

- Real-world analogy: Hospital departments (ER=core, ICU=health, Lab=intelligence, Admin=governance, Pharmacy=support)
- The 14 orchestrator domains table/visualization (core:132, domain:29, support:54, health:27, intelligence:16, persona:6, workflow:6, validation:12, git:4, response:5, _top_level:2, registry:1, synthesis:1, tools:1)
- D3 bubble chart showing domain sizes (proportional to file count)
- Code example: domain directory structure from `cortex/orchestrators/`
- How domains communicate via MasterOrchestrator routing
- IOrchestrator protocol contract explanation
- Breadcrumb: CORTEX / University / Architecture Patterns / Orchestrator Domains

#### 3b. `docs/learning/architecture-patterns/concepts/five-step-lifecycle.html`

**Linked from:** architecture-patterns/index.html concept card 02
**Accent:** Teal `#14b8a6`
**Content required:**

- D3 state diagram: Prepare → Govern → Execute → Validate → Close (with transition labels)
- Each phase explained with what happens inside it:
  - **Prepare:** AC_START marker, git checkpoint, DoR display
  - **Govern:** Holistic validation gate (CORE-048), challenge gate, sweep catalogue open
  - **Execute:** TDD cycle, implementation, workflow template execution
  - **Validate:** Convergence loop (CORE-068), detect→fix→rescan until 0 P0/P1
  - **Close:** AC_COMPLETE marker, sweep catalogue close, metrics emit
- Real-world analogy: Surgery preparation→approval→operation→recovery→discharge
- Code example: AC marker format `AC-{DOMAIN}-{SEQUENCE}`
- Primitive YAML snippets for each phase
- Breadcrumb: CORTEX / University / Architecture Patterns / Five-Step Lifecycle

#### 3c. `docs/learning/ai-orchestration/concepts/lens-sensory-system.html`

**Linked from:** ai-orchestration/index.html concept card 01 AND intelligence-learning/index.html concept card 01
**Accent:** Violet `#8b5cf6`
**Content required:**

- What LENS stands for: Language → Examination → Navigation → Synthesis
- The 9 analysers (list each with what it detects)
- D3 radial/tree diagram: LENS at center, 9 analysers as children, each with detected artifacts
- Tiered analysis explanation (Tier 1 per-turn fast, Tier 2 on-demand deep, Tier 3 investigation)
- How LENS builds AnalysisContext (the data structure passed to orchestrators)
- Real-world analogy: Medical diagnostic lab (blood test=language analyser, X-ray=structure analyser, MRI=deep investigation)
- Code example: AnalysisContext fields
- How InteractionOrchestrator triggers Tier 1 on every turn
- Breadcrumb: CORTEX / University / AI Orchestration / LENS Sensory System

### ✅ DONE — Cleanup

| Task | Description |
|------|-------------|
| ✅ Remove `docs/learning/beginner/` | Removed — was empty legacy placeholder |
| ✅ Remove `docs/learning/intermediate/` | Removed — was empty legacy placeholder |
| ✅ Remove `docs/learning/advanced/` | Removed — was empty legacy placeholder |

---

## Navigation Chain (Level 2 prev/next)

```
Architecture Patterns ↔ AI Orchestration ↔ Workflow Automation ↔ Governance & Quality ↔ TDD Development ↔ Intelligence & Learning → (back to All Domains)
```

---

## Future Expansion (not in current scope)

These Level 3 deep-dives are NOT yet linked from Level 2 pages but could be added later:

| Domain | Potential Deep-Dives |
|--------|---------------------|
| Architecture Patterns | AC Markers, IOrchestrator Protocol, CAPE Planning, Self-Sustaining Architecture |
| AI Orchestration | IntelligenceFacade, Intent Classification, MCP Tool Registry, Session Context Chain |
| Workflow Automation | Declarative Templates, Universal Primitives, Convergence Loops, WorkflowComposer Engine, PO Change Intelligence |
| Governance & Quality | CORE-048 Holistic Gate, CORE-064 Sweep Completeness, CORE-068 Convergence, Meta-Audit Pipeline |
| TDD Development | TDDOrchestrator internals, Test Quality Scoring, Golden Test Promotion, 3-Layer Acceleration |
| Intelligence & Learning | URS Reinforcement, RCA Memory Engine, KAL Knowledge Acquisition, CAPE Complexity, PLIP Protocol, Deep Intelligence |

---

## Issue-Derived Knowledge (extracted from GitHub Issues #14, #15)

### Issue #14 — CAPE, KAL, Deep Intelligence, Git Safety

| Feature | Key Concepts |
|---------|-------------|
| **CAPE** | Complexity triage → auto plan → 5 execution gates → loop |
| **KAL** | Coverage assessor → 6-step pipeline → knowledge scoring |
| **Deep Intelligence** | CCL query engine, capability verifier, facade extension |
| **Git Safety** | Checkpoint injector, rollback manager |

### Issue #15 — PO Change Intelligence (Phase 142)

| Feature | Key Concepts |
|---------|-------------|
| **3 Orchestrators** | ChangeIntelligenceOrchestrator, ImpactAnalysisOrchestrator, StakeholderBriefingOrchestrator |
| **7 Templates** | change-impact-analysis, stakeholder-briefing, sprint-risk-assessment, dependency-mapping, regression-prediction, release-readiness, backlog-prioritization |

*(Issue #16 returned 404 — skipped)*

---

## Continuation Instructions

To resume this work in a new session:

1. Say: **"Follow instructions in cortex-doc.prompt.md. Read #file:learning-path.md and continue the CORTEX University implementation. Create the Level 3 deep-dive pages listed in the NOT YET CREATED section."**

2. The agent should:
   - Read this file for full context (progress tracker, design system, page specs)
   - Read `docs/.content/knowledge/learning-path-architecture.yaml` for knowledge registry
   - Read any completed Level 2 page as a structural reference
   - Read `docs/roles/software-engineer.html` lines 1-400 + 680-881 for the canonical inline CSS pattern
   - Create the 3 Level 3 deep-dive pages per the specifications above
   - Clean up the 3 empty legacy directories
   - Verify all internal links resolve

3. Each Level 3 page MUST follow this template:
   - Tailwind CDN suppression script → CDN imports → inline `<style>` with `:root` ISSA tokens
   - `body` bg `#020617` with radial gradients using domain accent color
   - Glass-card styles → breadcrumb-nav → skip link
   - `<main max-w-7xl mx-auto px-4 md:px-6 space-y-12 md:space-y-16>`
   - Hero section with concept title + domain badge
   - Real-world analogy in a glass panel
   - CORTEX implementation explanation with code blocks
   - D3.js interactive diagram (force-directed, tree, radial, or state diagram)
   - Navigation back to parent Level 2 page
   - Footer → D3.js script block → `prefers-reduced-motion` gate → ISSA responsive overrides

---

## Pedagogical Principles (apply to all content)

| Principle | Application |
|-----------|------------|
| Progressive Disclosure | Level 1 = What (choose a path), Level 2 = Why (explore concepts), Level 3 = How (deep understanding) |
| Active Learning | Interactive D3.js graphs — drag, zoom, click nodes |
| Visual Knowledge Mapping | Every Level 2 page has a concept graph showing relationships |
| Multi-Diagram Teaching | Different diagram types per domain: force-directed, tree, state, bubble, pipeline |
| Real-World Analogies | Every Level 3 page opens with a familiar analogy before technical content |

---

## External Research References

Enhance explanations using authoritative sources (synthesize, never copy):

- Martin Fowler Architecture Catalog: https://martinfowler.com
- Refactoring Guru: https://refactoring.guru/design-patterns
- Microsoft Architecture Center: https://learn.microsoft.com/azure/architecture
- D3 Visualization Examples: https://observablehq.com/@d3

---

## Technology Stack (actual, not original spec)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Markup | HTML5 with inline CSS | No React — static HTML matching existing CORTEX docs pattern |
| Styling | Tailwind CDN + inline `<style>` | ISSA spacing tokens, glassmorphism identity |
| Icons | Lucide (via unpkg CDN) | NOT FontAwesome — Lucide matches existing site |
| Visualization | D3.js v7 (cdnjs) | Force-directed, tree, state, bubble charts. Mermaid BANNED. |
| Fonts | Google Fonts CDN | Inter, Space Grotesk, JetBrains Mono |
| Knowledge Source | `cortex-registry/` YAML files | YAML remains single source of truth |
