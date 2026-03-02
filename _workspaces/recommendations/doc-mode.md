You are CORTEX running challenge-first protocol. Add a Design + Implement mode to the existing #file:cortex-docs prompt and its #file:agents (do not delete/recreate). Goal: enforce modern HTML documentation best practices + consistent site design for cortex-docs/index.html.

Constraints (must follow)

No new markdown files (no summaries/reports written to repo). All feedback stays inline in Copilot Chat.

Preserve current dark blue glassmorphism theme; evolve it into a more professional, impressive design (no theme drift).

All styling must be in CSS files (never inline style= attributes).

Agents must treat cortex-docs/ as the doc workspace and read pregenerated doc data from:

cortex-docs/.content/

cortex-docs/assets/diagrams/

any other folders within cortex-docs/

Ensure MCP-first exposure, orchestrator integrity, and zero regression risk.

Phase 0: Challenge-first audit (before changing anything)

Audit current capabilities and architecture patterns by reading:

#file:cortex-docs prompt

all #file:agents used by cortex-docs

cortex-docs/index.html + existing CSS/JS/assets layout

Identify what already exists vs what’s missing for “Design + Implement mode”.

Identify architectural fit: where to add the mode without breaking existing workflows.

Deliver your SINGLE BEST recommendation that balances the ask vs challenge tension (inlined into your plan), evaluated against CORTEX design pillars:

extensibility, scalability, accuracy, team collaboration, long-term maintainability

Phase 1: Acquire best-practice sources (web + synthesis)

Propose a short, high-signal list of documentation sites/pattern libraries to study (include reasons), e.g.:

MDN Web Docs (IA + accessibility patterns)

GitHub Docs / Microsoft Learn / Stripe Docs (layout + navigation + content hierarchy)

Docusaurus / Nextra / VitePress (component patterns even if we stay static HTML)

WCAG + ARIA Authoring Practices (accessibility)

(Add your own recommendations)

“Download”/capture the key best practices relevant to static HTML doc sites:

information architecture, navigation, search UX, content patterns

accessibility (keyboard, contrast, semantics)

performance (CSS/JS structure, asset loading)

maintainable CSS architecture (BEM/utility layers/design tokens)

responsive layout & typography scale

Synthesize these into knowledge YAMLs stored under cortex-docs/.content/knowledge/:

doc_best_practices.yaml

design_system.yaml (tokens: colors, spacing, typography, elevation, blur, borders)

components.yaml (nav, sidebar, cards, callouts, code blocks, tables, diagrams)

a11y_checklist.yaml

performance_checklist.yaml
Keep YAMLs concise, structured, and directly actionable.

Phase 2: Update cortex-docs prompt + agents to enforce the mode
Required behavior changes

Add a “Design + Implement mode” that triggers when a user asks to update any HTML view (especially cortex-docs/index.html):

Design step: propose layout/components using the YAML knowledge base + existing theme constraints.

Implement step: apply changes to HTML/CSS/JS files with clean structure.

Enforce:

no inline styles

CSS in dedicated files under cortex-docs/assets/css/ (or existing equivalent)

semantic HTML + accessibility

reusable components/classes aligned to design_system.yaml

stable DOM hooks for future automation/tests (if present in repo patterns)

Agent responsibilities (update existing agents; add new ones only if needed)

best-practices-harvester (sources → distilled notes)

knowledge-yaml-author (notes → YAMLs)

design-system-enforcer (tokens + component rules)

html-view-designer (structure/IA for requested views)

css-architect (modular CSS files, naming scheme, no inline)

doc-data-integrator (reads .content + diagrams; binds into views)

a11y-perf-guardian (checklists + regression prevention)

regression-sentinel (diff review + “no theme drift/no broken links/no layout regressions”)

All agent interactions must preserve orchestrator determinism and reuse current CORTEX patterns.

Phase 3: Implement on the current site (first target)

Apply the mode to improve cortex-docs/index.html using the new best-practice YAMLs while preserving the dark blue glassmorphism identity.

Ensure diagrams from cortex-docs/assets/diagrams/ are presented cleanly (responsive, captions, lightbox if appropriate, but keep JS minimal and maintainable).

Ensure .content data drives the page where applicable (no duplication of source-of-truth content).

Output format (Copilot Chat response requirements)

Executive-ready, ≤60 seconds read time.

Clear sections with strong visual hierarchy optimized for VS Code Copilot Chat.

Include one compact comparison table (e.g., “Current vs Proposed” or “Options A/B”).

Inline only: show what files you will change and why, then proceed with edits.

Do not generate or suggest creating markdown reports/summaries in the repo.

Proceed now: audit first, then implement the plan with zero regression risk.