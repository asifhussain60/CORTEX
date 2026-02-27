# Prompt 08 — Git-Backed Registry as an Ancient Library

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create an illustration of a grand ancient library (Alexandria-inspired) reimagined as a Git-backed configuration registry, rendered with the CORTEX dark glassmorphism aesthetic.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with warm cyan (#00d4ff) ambient lighting from crystal lanterns (NOT warm amber — stay on brand)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~50px, subtle inner shadow

THE LIBRARY INTERIOR (dark stone walls with glassmorphic shelf labels):

LEFT WALL — "core/" (shelving with cyan #00d4ff glow):
- Books labeled in JetBrains Mono: "skull-rules.yaml", "tier0-skull/", "specifications/"
- Glassmorphic caption: "The Constitution — 38 immutable governance rules"
- Muted analogy (#a0a6c0): "Like the law library in a courthouse"

CENTER WALL — "planning/" (shelving with purple #7b61ff glow):
- Books labeled: "cortex-master.yaml (≤500 lines)", "phases/planned/", "phases/completed/"
- A large open book on a lectern with glassmorphic holographic display above it showing the plan index
- Glassmorphic caption: "The project roadmap — every phase documented"
- Muted analogy: "Like an architect's blueprint room"

RIGHT WALL — "workflows/" (shelving with blue #3b82f6 glow):
- Scroll tubes representing workflow templates
- Books labeled: "templates/", "primitives/", "audit/"
- Glassmorphic caption: "The playbooks — reusable recipes for every operation"
- Muted analogy: "Like a chef's recipe collection"

BACK WALL — "knowledge-base/" (shelving with green #00ff88 glow):
- Books glowing with subtle green aura
- Labels: "patterns/", "company/", "knowledge/"
- Glassmorphic caption: "Institutional wisdom — patterns learned across projects"
- Muted analogy: "Like a university's research archives"

CENTER OF THE ROOM:
- A large desk with a Git logo hologram floating above it in cyan (#00d4ff)
- The desk has a ledger (git log) with cyan-highlighted timestamped entries
- Glassmorphic caption: "Every change versioned. Every change reversible. rollback = git revert"

A LIBRARIAN FIGURE (translucent, glassmorphic silhouette representing GitBackedRegistry class):
- Standing at the desk, organizing glowing scroll tubes
- Muted caption: "The librarian doesn't use a database — every book is on the shelf, readable by anyone"

Glassmorphic footer bar:
"cortex-registry/ · No PostgreSQL · No MongoDB · Just YAML + Git"
Muted subtitle: "Like a library where every book checkout is recorded — forever"

Style: Ancient library with dark glassmorphism tech overlay. Cyan/purple glowing shelves. Frosted glass info panels. Deep navy atmosphere. Educational and inviting.

Dimensions: 800×600
Format: PNG
```

## Notes for Generation
- The registry lives at `cortex-registry/`
- No database is used — all config is YAML files versioned in Git
- `cortex-master.yaml` is capped at ≤500 lines (THIN INDEX CONTRACT)
- The registry is the single source of truth for governance, planning, and knowledge
