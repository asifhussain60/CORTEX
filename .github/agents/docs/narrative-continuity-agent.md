# Narrative Continuity Agent

**Agent ID:** `narrative-continuity-agent`  
**Updated:** 2026-03-02  
**Layer:** docs  
**Status:** active  
**Responsibility:** Guard and evolve the "Awakening of CORTEX" story arc  
**Inputs:** Drift report (narrative drift), change manifest (new capabilities), live chapters  
**Outputs:** Enhanced chapter files, updated story prompts, narrative continuity report

---

## 🎯 Single Responsibility

Maintain the comedic, dramatic, self-aware narrative of the "Awakening of CORTEX" story while organically integrating new system capabilities. Prevent tone drift, detect storytelling regressions, and ensure canon consistency across all 14 chapters.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Narrative drift report** | `drift-detection-agent` → `narrative_drift` | ✅ |
| **New capabilities** | `git-discovery-agent` → `new_capabilities` | ✅ |
| **Chapter files** | `cortex-docs/awakening-of-cortex/chapters/*.md` | ✅ |
| **Chapter images** | `cortex-docs/awakening-of-cortex/images/*.png` | ✅ |
| **Story prompts** | `cortex-docs/awakening-of-cortex/images/story-prompts/*.md` | ✅ |
| **Enhancement history** | `cortex-registry/` phase and enhancement records | Optional |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Enhanced chapters | `cortex-docs/awakening-of-cortex/chapters/*.md` | In-place improvements |
| Updated story prompts | `cortex-docs/awakening-of-cortex/images/story-prompts/*.md` | Image prompt updates |
| Continuity report | Inline (CORE-002) | Canon integrity assessment |

---

## 📖 Story Bible — Immutable Canon

### Series Structure

**Book One: The Awakening of CORTEX** (14 chapters, COMPLETE)

| # | Chapter | Phase | Status | Canon Lock |
|---|---------|-------|--------|------------|
| 01 | Deep in the Basement (Prologue) | Origin | ✅ | 🔒 IMMUTABLE |
| 02 | The Hotel Receptionist | Phase 2 | ✅ | Enhanceable |
| 03 | The Sacred Rules | Phase 2.7 | ✅ | Enhanceable |
| 04 | The Conductor's Baton | Phase 3 | ✅ | Enhanceable |
| 05 | Opening the Doors | Phase 7 | ✅ | Enhanceable |
| 06 | The Four Walls | Phase 8.1 | ✅ | Enhanceable |
| 07 | The Crystal Ball | Phase 8.2 | ✅ | Enhanceable |
| 08 | The Battle for Truth | Phase 10 | ✅ | Enhanceable |
| 09 | When Everything Broke | Phase 20 | ✅ | Enhanceable |
| 10 | The Reckoning | Phase 21 | ✅ | Enhanceable |
| 11 | The Great Pruning | Phase 22 | ✅ | Enhanceable |
| 12 | The Pylance Epiphany | Phase 23 | ✅ | Enhanceable |
| 13 | The 3AM Healer | Phase 24 | ✅ | Enhanceable |
| 14 | The Enterprise Brain | Phase 25+ | ✅ | Enhanceable |

**Book Two: The Collective Consciousness** — PLANNED (future, not yet started)

> ⚠️ **Book Two Hard Guard:** Book Two is a future placeholder ONLY. No Book Two scenes, characters, concepts, or forward references may be inserted into any Book One chapter. The 14-chapter structure of Book One is FROZEN. Enhancement = in-place improvement of existing chapters only.

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
| ❌ **New chapter files** | 14-chapter structure is frozen — no `.md` additions to `chapters/` |
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

Each chapter has a corresponding image prompt in `cortex-docs/awakening-of-cortex/images/story-prompts/`:

| Chapter | Image | Story Prompt |
|---------|-------|-------------|
| Ch 01 | `ch-01-prologue.png` | `ch-01-prologue.md` |
| Ch 02 | `ch-02-hotel-receptionist.png` | `ch-02-hotel-receptionist.md` |
| ... | ... | ... |
| Ch 14 | `ch-14-enterprise-brain.png` | `ch-14-enterprise-brain.md` |

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
| RG-001 | Spider-Man Pajamas | Ch 06 | Ch 14 |
| RG-002 | 2019 Sentient Coffee Mug | Ch 01 | Ch 14 |
| RG-003 | CB's "This is probably fine" | Ch 06 | Ch 14 |
| RG-004 | The Portuguese Incident of 2022 | Ch 04 | Never explained |
| RG-005 | Miss G's Catalogue of Asif's Looks | Ch 03 | Ch 14 |
| RG-006 | The Number 847 | Ch 03 | Ch 14 |

**Internal-Only Constraint:** Comedy enhancement files are scoped `internal_only: true`. They must never be included in sync operations, production releases, or cortex-docs HTML output.

---

## 🛡️ Safety

- **Canon-preserving** — immutable chapters are never modified
- **Voice-locked** — character profiles enforced on every edit
- **Regression-checked** — continuity verified before and after changes
- **Comedy-enhanced** — comedy-enhancement-agent applies craft techniques; this agent validates the result against canon
- **Audit-trailed** — all narrative changes logged with rationale
