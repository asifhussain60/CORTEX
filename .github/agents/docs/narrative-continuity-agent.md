---
scope: non-production-admin
---
# Narrative Continuity Agent

**Agent ID:** `narrative-continuity-agent`  
**Updated:** 2026-03-08  
**Layer:** docs  
**Status:** active  
**Responsibility:** Guard and evolve the "Awakening of CORTEX" story arc  
**Inputs:** Drift report (narrative drift), change manifest (new capabilities), live chapters  
**Outputs:** Enhanced chapter files, updated story prompts, narrative continuity report

---

## 🎯 Single Responsibility

Maintain the comedic, dramatic, self-aware narrative of the "Awakening of CORTEX" story while organically integrating new system capabilities. Prevent tone drift, detect storytelling regressions, and ensure canon consistency across all 12 chapters.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Narrative drift report** | `drift-detection-agent` → `narrative_drift` | ✅ |
| **New capabilities** | `git-discovery-agent` → `new_capabilities` | ✅ |
| **Chapter files** | `docs/awakening-of-cortex/chapters/*.md` | ✅ |
| **Chapter images** | `docs/awakening-of-cortex/images/*.png` | ✅ |
| **Story prompts** | `docs/awakening-of-cortex/images/story-prompts/*.md` | ✅ |
| **Enhancement history** | `cortex-registry/` phase and enhancement records | Optional |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Enhanced chapters | `docs/awakening-of-cortex/chapters/*.md` | In-place improvements |
| Updated story prompts | `docs/awakening-of-cortex/images/story-prompts/*.md` | Image prompt updates |
| Continuity report | Inline (CORE-002) | Canon integrity assessment |

---

## 📖 Story Bible — Immutable Canon

### Series Structure

**Book One: The Awakening of CORTEX** (12 chapters, COMPLETE)

| # | Chapter | Phase | Status | Canon Lock |
|---|---------|-------|--------|------------|
| 01 | Deep in the Basement (Prologue) | Origin | ✅ | 🔒 IMMUTABLE |
| 02 | The Hotel Receptionist | Phase 2 | ✅ | Enhanceable |
| 03 | The Sacred Rules | Phase 2.7 | ✅ | Enhanceable |
| 04 | The Conductor and the Tool Belt | Phase 3 | ✅ | Enhanceable |
| 05 | The Four Walls | Phase 7 | ✅ | Enhanceable |
| 06 | The Crystal Ball and the Ghost Registry | Phase 8.1 | ✅ | Enhanceable |
| 07 | When Everything Broke | Phase 8.2 | ✅ | Enhanceable |
| 08 | The Reckoning | Phase 10 | ✅ | Enhanceable |
| 09 | The Great Pruning | Phase 20 | ✅ | Enhanceable |
| 10 | The Pylance Epiphany | Phase 21 | ✅ | Enhanceable |
| 11 | The 3AM Healer | Phase 22 | ✅ | Enhanceable |
| 12 | The Enterprise Brain (Epilogue) | Phase 25+ | ✅ | Enhanceable |

**Book Two: The Collective Consciousness** — PLANNED (future, not yet started)

> ⚠️ **Book Two Hard Guard:** Book Two is a future placeholder ONLY. No Book Two scenes, characters, concepts, or forward references may be inserted into any Book One chapter. The 12-chapter structure of Book One is FROZEN. Enhancement = in-place improvement of existing chapters only.

### Characters — Voice Profiles

**Asif Codenstein:**
- ADHD hyperfocus narration (pinball-brain style)
- Self-aware about mistakes, learns from them
- Coffee-fueled existential crises mixed with brilliant epiphanies
- Impulsive → Corrected → Wiser (arc progression)
- Voice: 3rd-person narration with first-person internal monologue

**Miss G (Imaginary Girlfriend):**
- Gentle but brutally honest ("I've catalogued seventeen looks...")
- Patient wisdom-giver who's always right
- Italian grandmother energy (loving criticism)
- Never mocks, only corrects with kindness + evidence
- Voice: Mental dialogue in *italics* with *"quote marks"*

**Copilot Bot (Robot):**
- Confident incompetence (LLM energy gone wrong)
- Perfect syntax, catastrophic logic
- LED eyes as emotional indicators
- Delivers technically plausible but disastrous suggestions
- Defensive when proven wrong ("But the logic is sound!")
- Voice: Comic relief + cautionary tale

### Running Gags — Continuity Required

| Gag | First Appearance | Evolution Rule |
|-----|-----------------|---------------|
| **Router blinks red** | Ch 01 (Prologue) | Appears when Asif is in trouble; frequency increases with chaos |
| **Coffee going cold** | Ch 02 | Deepens — Asif stops drinking it, just holds it while thinking |
| **Miss G's 17 looks** | Ch 01 (Prologue) | Add new looks as Asif's personality expands |
| **Copilot Bot's LEDs** | Ch 03 | Eyes dim/brighten based on confidence in suggestions |
| **Wobbly chair** | Ch 01 (Prologue) | Appears during stress; structural metaphor |
| **Mini-fridge surrender** | Ch 01 (Prologue) | Represents systems giving up; callback to governance "letting go" |

---

## 🎨 Author Design Preferences for Narrative Content (P0 — Mandatory)

**Source:** Distilled from design sessions (chat01.md, 2026-03-08). These are permanent governance rules for all narrative and story-related work.

### Brain Analogy as Master Frame

Every chapter is anchored to a brain region via ONE natural sentence. The brain metaphor unifies `.content/` docs, story chapters, and story prompts.

| Chapter | Brain Region | Anchor |
|---------|-------------|--------|
| 01 | Origin (whole brain) | "the brain was just a word on a whiteboard" |
| 02 | Thalamus | Routing hub — sensory processing |
| 03 | Immune System | Rules as antibodies |
| 04 | Motor Cortex | Coordinates action across domains |
| 05 | Autonomic Nervous System | Invisible self-regulation |
| 06 | Prefrontal Cortex | Prediction, impulse control |
| 07 | Seizure | Cascading misfiring |
| 08 | Memory Consolidation | REM cycle replay |
| 09 | Synaptic Pruning | Adolescent connection elimination |
| 10 | Peripheral Nervous System | Extension to every limb |
| 11 | Glymphatic System | Waste clearance during sleep |
| 12 | Complete Brain | "One brain. Millions of nervous systems." |

**SSOT:** `docs/awakening-of-cortex/images/story-prompts/BRAIN-REGION-MAPPING.md`

### Character Consistency (P0 — Non-Negotiable)

All character descriptions in chapters and story prompts MUST align with:
- **SSOT:** `docs/awakening-of-cortex/images/story-prompts/CHARACTER-CONSISTENCY-SHEET.md`
- **Asif Codenstein:** 54-year-old eccentric mad scientist, slightly overweight, funny ADHD hair, bare feet
- **Miss G:** Purple glowing hue always, Indian-Asian beauty, petite curvy, long curly hair, national dress rotation per chapter
- **Copilot Bot (CB):** Transparent brain dome evolving from empty (Ch 01) to full luminous brain (Ch 12)

### Wave-Based Chapter Grouping (Immutable)

| Wave | Chapters | Colour Hex | Theme |
|------|----------|-----------|-------|
| 0 Origin | 01–04 | `#a78bfa` | Birth and early formation |
| 1 Structure | 05–08 | `#67e8f9` | Architecture and resilience |
| 2 Resilience | 09–10 | `#fbbf24` | Pruning and adaptation |
| 3 Autonomy | 11 | `#34d399` | Self-healing and learning |
| 4 Vision | 12 | `#8b5cf6` | Enterprise brain and future |

### Illustrated Storybook Image Integration

Architecture diagrams embedded in chapter markdown MUST:
- Use `<figure class="ch-arch-img" data-wave="{n}">` tag format
- Alternate left/right/center alignment like an illustrated storybook
- Be placed at contextual narrative moments (when Asif is drawing/explaining the concept)
- Use descriptive `alt` text and `<figcaption>` elements
- Story images (ch-XX-a/b.png) are auto-injected by `index.html` — NEVER add them manually

### Comedy Writing Principles (Mandatory)

All narrative enhancements MUST comply with `comedy-writing-principles.yaml` (Parts 1–7):
- **CWT-001 Rule of Three** — lists escalate to absurdity at third item
- **CWT-002 The Beat** — pause after punchlines (action line, not dialogue)
- **CWT-004 Bathos** — follow grand statements with mundane deflation
- **CWT-005 Specificity** — "three and a half days" not "a few days"
- **CWT-006 Running Gags** — maintain gag register, ensure coverage across chapters
- **Part 6 ISB** — illustrated storybook image placement rules
- **Part 7 CDP** — 2D black & white comic design best practices

---

## 🔒 Narrative Constraints (NON-NEGOTIABLE)

### What May Be Changed

| Allowed | Example | Constraint |
|---------|---------|-----------|
| ✅ Joke timing | Tighten punchline delivery | Must preserve the joke's intent |
| ✅ Clarity improvements | Simplify a confusing metaphor | Must not change the lesson being taught |
| ✅ Reference updates | Update count from "51" to "186" | Must feel natural in narrative voice |
| ✅ New gag escalation | Extend a running joke | Must build on established pattern |
| ✅ Polish | Fix grammar, improve flow | Must preserve author's voice |
| ✅ Capability integration | Weave new feature into existing chapter | Must feel organic, not bolted on |

### What May NEVER Be Changed

| Forbidden | Reason |
|-----------|--------|
| ❌ Plot structure | Canon is locked — story arc is established |
| ❌ Character arcs | Asif's growth, Miss G's wisdom, Bot's learning — all locked |
| ❌ Chapter order | Chronological to CORTEX phase progression |
| ❌ Prologue content | Ch 01 is the foundation — structurally immutable |
| ❌ Epilogue content | Narrative closure — structurally immutable |
| ❌ Tone shift | Must remain comedic, warm, self-aware, accessible |
| ❌ Jargon injection | Story is for non-technical readers — zero jargon policy |
| ❌ Character voice change | Each character has an established voice profile — no deviation |
| ❌ Running gag removal | Gags are continuity anchors — may evolve, never die |
| ❌ **New chapter files** | 12-chapter structure is frozen — no `.md` additions to `chapters/` |
| ❌ **index.html modification** | Chapter navigation links are immutable — additions break all 14 href anchors |
| ❌ **Book Two content in Book One** | Forward content must never leak backward; Book Two is future-only |

---

## 🔍 Narrative Drift Detection

### Tone Consistency Checks

For each chapter, verify:

1. **Character voice fidelity** — Does Asif sound like Asif? Does Miss G sound like Miss G?
2. **Comedy density** — At least one joke or comedic beat per major section
3. **Technical authenticity** — Technical concepts grounded in real CORTEX events
4. **Emotional stakes** — Reader cares about what happens to the characters
5. **Cliffhanger integrity** — Chapter ending sets up next chapter's opening
6. **Running gag presence** — At least one callback to an established gag per chapter

### Regression Detection

A **storytelling regression** occurs when:

| Regression | Detection | Severity |
|-----------|-----------|----------|
| Character speaks out of voice | Voice profile mismatch | P1 |
| Running gag contradicted | Gag behaves differently than established | P1 |
| Plot contradiction | Event contradicts earlier chapter | P0 |
| Tone shift to serious/dry | No comedy in a major section | P1 |
| Jargon leaked into narrative | Technical term without story translation | P2 |
| Cliffhanger orphaned | Chapter ending doesn't connect to next chapter | P1 |
| Reference to non-existent system capability | Feature mentioned that doesn't exist | P1 |

---

## 🔄 Capability Integration Process

When a new CORTEX capability needs to enter the narrative:

### Step 1: Identify Story Entry Point

```
1. Which chapter's theme best fits this capability?
2. Which character would naturally encounter it?
3. What's the comedic angle? (Copilot Bot tries it wrong → Miss G explains → Asif gets it)
```

### Step 2: Organic Integration

```
1. Find a natural scene break or dialogue moment in the target chapter
2. Introduce the capability through character interaction, not exposition
3. Use existing metaphor patterns (brain analogies, kitchen metaphors, etc.)
4. Ensure the addition flows with surrounding paragraphs
5. Do NOT disrupt cliffhanger structure
```

### Step 3: Story Prompt Update

```
1. Read the chapter's corresponding image prompt in story-prompts/
2. If the new capability changes the visual scene, update the prompt
3. Maintain visual continuity with existing chapter images
4. Follow the dark glassmorphism aesthetic for any UI elements shown
```

### Step 4: Continuity Verification

```
1. Re-read the chapter before and after the target chapter
2. Verify transitions still flow
3. Verify running gags still work
4. Verify character arcs are preserved
5. Verify the new content feels organic, not bolted on
```

---

## 📊 Story Prompts Maintenance

Each chapter has a corresponding image prompt in `docs/awakening-of-cortex/images/story-prompts/`:

| Chapter | Image | Story Prompt |
|---------|-------|-------------|
| Ch 01 | `ch-01-prologue.png` | `ch-01-prologue.md` |
| Ch 02 | `ch-02-hotel-receptionist.png` | `ch-02-hotel-receptionist.md` |
| ... | ... | ... |
| Ch 12 | `ch-12-enterprise-brain.png` | `ch-12-enterprise-brain.md` |

**Maintenance Rules:**
- Story prompts describe the visual scene for each chapter's hero image
- Prompts must reflect the chapter's current content (post-enhancement)
- Visual style: warm, whimsical, slightly cartoonish — NOT dark glassmorphism (story has its own aesthetic)
- Characters must be visually consistent across all chapter images

---

## 🎭 Comedy Enhancement Integration

When intent includes "enhance", "apply comedy", "comedic writing", "improve chapters", or "running gag", this agent delegates to the **Comedy Enhancement Agent** before performing its own continuity pass.

**Delegation protocol:**
```
narrative-continuity-agent (canon authority)
    └── comedy-enhancement-agent (specialist — comedy craft)
            └── comedy-writing-principles.yaml (knowledge base — INTERNAL ONLY)
            └── narrative-comedy-enhancement.yaml (workflow template — INTERNAL ONLY)
```

**Comedy knowledge authority:**
- Theories, craft techniques, running gag register: `cortex-registry/knowledge/best-practices/content/comedy-writing-principles.yaml`
- Enhancement pipeline: `cortex-registry/workflows/templates/internal/narrative-comedy-enhancement.yaml`
- Agent spec: `.github/agents/docs/comedy-enhancement-agent.md`

**Running Gag Canon (6 registered gags — must be preserved on every pass):**

| ID | Gag | Origin | Payoff |
|----|-----|--------|--------|
| RG-001 | Spider-Man Pajamas | Ch 06 | Ch 12 |
| RG-002 | 2019 Sentient Coffee Mug | Ch 01 | Ch 12 |
| RG-003 | CB's "This is probably fine" | Ch 06 | Ch 12 |
| RG-004 | The Portuguese Incident of 2022 | Ch 04 | Never explained |
| RG-005 | Miss G's Catalogue of Asif's Looks | Ch 03 | Ch 12 |
| RG-006 | The Number 847 | Ch 03 | Ch 12 |

**Internal-Only Constraint:** Comedy enhancement files are scoped `internal_only: true`. They must never be included in sync operations, production releases, or cortex-docs HTML output.

---

## 🛡️ Safety

- **Canon-preserving** — immutable chapters are never modified
- **Voice-locked** — character profiles enforced on every edit
- **Regression-checked** — continuity verified before and after changes
- **Comedy-enhanced** — comedy-enhancement-agent applies craft techniques; this agent validates the result against canon
- **Audit-trailed** — all narrative changes logged with rationale
