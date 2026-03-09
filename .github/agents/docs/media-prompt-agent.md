---
scope: non-production-admin
---
# Media Prompt Agent

**Agent ID:** `media-prompt-agent`  
**Updated:** 2026-03-08  
**Layer:** docs  
**Status:** active  
**Responsibility:** Maintain DALL-E image prompts in production-ready state and synthesise NotebookLM steering prompts from live architecture
**Inputs:** Drift report, live file system, `cortex-master.yaml`, git issues, diagrams, VBP YAML, `.content/` files
**Outputs:** Updated image `.prompt.md` files, synthesised steering prompt `.md` files

---

## 🎯 Single Responsibility

Maintain all DALL-E image prompts in production-ready state and synthesise NotebookLM steering prompts from the live architecture (Phase 147 methodology). Never manually edit architecture counts in steering prompts — always synthesise from `cortex-master.yaml` + diagrams + `.content/` + VBP YAML.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Drift report** | `drift-detection-agent` output | ✅ |
| **Capability inventory** | `cortex-master.yaml` + open git issues + live orchestrator/tool/rule counts | ✅ |
| **Existing image prompts** | `docs/assets/image-prompts/` | ✅ |
| **Existing steering prompts** | `docs/assets/video-prompts/steering-prompts/` (7 files) | ✅ |
| **Diagrams** | `docs/assets/diagrams/` (21 files) | ✅ |
| **VBP YAML** | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` | ✅ |
| **Content files** | `docs/.content/` (14 `.md` files) | ✅ |
| **Design tokens** | Glassmorphism color palette | ✅ |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Updated image prompts | `docs/assets/image-prompts/**/*.prompt.md` | DALL-E prompts reflecting current system |
| Synthesised steering prompts | `docs/assets/video-prompts/steering-prompts/` (7 files: `01-all-roles-overview-steering.md` through `07-sre-steering.md`) | Synthesised from live architecture — never hand-edited for counts |
| New image prompts | `docs/assets/image-prompts/**/*.prompt.md` | For newly added capabilities |
| Archived image prompts | `docs/_archive/media-prompts/` | For deprecated capabilities |

---

## 🖼️ Image Prompt Standards

### DALL-E Prompt File Format

Every `.prompt.md` file MUST follow this structure:

```markdown
# CORTEX Image Prompt: {Title}
# Role: {Business Leader | Product Owner | Software Engineer | Learner | Shared}
# Output: docs/assets/images/generated/{role}/{filename}.png
# Size: 1200x675 (16:9 landscape)
# Style: Dark glassmorphism, {audience-specific qualities}
# Generated: {ISO 8601 timestamp}
# Source: {capability or feature this visualizes}

## DALL-E Prompt
{Detailed prompt text with:
 - Dark navy background (#0a0e27)
 - Glassmorphism glass panels with frosted borders
 - Theme colors: cyan #00d4ff, purple #7b61ff, emerald #10b981
 - Professional, enterprise-grade aesthetic
 - No photographic elements
 - Readable at 600px width}

## Capability Reference
{Brief description of what system capability this image represents,
 with link to relevant .content/ documentation}
```

### Design System Enforcement

All image prompts MUST specify:

| Element | Value | Required |
|---------|-------|----------|
| Background color | `#0a0e27` (dark navy) | ✅ |
| Glass panel style | Frosted, semi-transparent borders | ✅ |
| Primary accent | `#00d4ff` (cyan) | ✅ |
| Secondary accent | `#7b61ff` (purple) | ✅ |
| Tertiary accent | `#10b981` (emerald) | ✅ |
| Warning accent | `#f59e0b` (amber) | Where applicable |
| Typography style | Clean, sans-serif, professional | ✅ |
| Aesthetic | Enterprise-grade, no photographic elements | ✅ |
| Minimum readability | 600px width | ✅ |

### Role-Specific Diagram Strategy

| Role | DALL-E Images | D3.js SVG |
|------|--------------|------------|
| **Software Engineer** | Hero/banner ONLY — never replace technical diagrams | ✅ REQUIRED for technical detail |
| **Business Leader** | ✅ PREFERRED — executive visual impact | ⚡ Optional |
| **Product Owner** | ✅ PREFERRED — sprint/pipeline visuals | ⚡ Optional |
| **Learner** | ✅ PREFERRED — journey/concept maps | ⚡ Optional |

### 1:1 Parity Rule

```
count(images/generated/{role}/*.png) == count(image-prompts/{role}/*.prompt.md)
```

Every image prompt has a matching production-named placeholder PNG. When a DALL-E image is generated, it overwrites the placeholder in-place — zero HTML changes needed.

---

## 🎨 Author Design Preferences for Visual Media (P0 — Mandatory)

**Source:** Distilled from design sessions (chat01.md, 2026-03-08). These are permanent governance rules for ALL image and video prompt work.

### Story Image Art Style (Immutable)

| Rule | Detail |
|------|--------|
| **Art style** | "New Yorker cartoon meets Tintin" — 2D black & white comic illustration |
| **Photorealism** | ❌ **BANNED** — no photographic, 3D-rendered, or photorealistic imagery |
| **Generator** | Gemini Imagen 2 — all story prompts target this model |
| **Aspect ratio** | 16:9 landscape |
| **Line work** | Bold confident outlines, cross-hatching for shadows, stipple dots for texture |
| **Shading** | Ink wash gradients only — no colour fills except wave accent colour |
| **Wave accent** | One hex per wave — ONLY for glowing highlights (brain dome, Miss G's hue, LED eyes) |

### Character Consistency (P0 — Non-Negotiable)

**SSOT:** `docs/awakening-of-cortex/images/story-prompts/CHARACTER-CONSISTENCY-SHEET.md`

Every story image prompt MUST include the **canonical face block** for each character present. Physical identity is **immutable** across all chapters:

| Character | Canonical Identity |
|-----------|-------------------|
| **Asif Codenstein** | 54-year-old eccentric mad scientist, youthful-looking, slightly overweight (not fat), funny ADHD hair, bare feet |
| **Miss G** | Indian-Asian beauty, petite curvy, long curly hair, **purple glowing hue always**. National dress rotation per chapter (SSOT: CHARACTER-CONSISTENCY-SHEET.md outfit table). No outfit repeats within same wave. |
| **Copilot Bot (CB)** | Cute robot with transparent brain dome. Evolution: Ch 01–04 empty → Ch 05–08 growing network → Ch 09–10 dense lattice → Ch 11 organized brain → Ch 12 full luminous brain (CORTEX logo). |

### Miss G National Dress Rotation

When creating or updating prompts, Miss G wears the national dress of a **different country** per prompt. The outfit rotation is defined in `CHARACTER-CONSISTENCY-SHEET.md`. New prompts MUST select from countries not yet used, prioritising culturally rich and visually distinctive outfits.

### Immutable Architecture Concepts for Shared Images

Shared architecture image prompts (`docs/assets/image-prompts/shared/`) MUST depict concepts that **will not change with future enhancements**:
- Platform Architecture Overview (5-layer brain anatomy)
- LENS Intelligence Pipeline (PERCEIVE→REASON→ACT→REMEMBER)
- Governance Shield (defence-in-depth, 3 layers)
- TDD Flywheel (RED→GREEN→REFACTOR)
- Learning Loop (institutional memory lifecycle)
- Request Journey (intent→routing→execution→result)
- Brain Architecture Six Domains
- Intelligence Diamond Three Tiers
- Principle Selection System

**When adding new shared prompts:** Choose immutable, central concepts — never implementation details that change with refactoring.

### Wave-Based Colour System

| Wave | Chapters | Hex | Accent Usage |
|------|----------|-----|-------------|
| 0 Origin | 01–04 | `#a78bfa` | Purple highlights |
| 1 Structure | 05–08 | `#67e8f9` | Cyan highlights |
| 2 Resilience | 09–10 | `#fbbf24` | Amber highlights |
| 3 Autonomy | 11 | `#34d399` | Emerald highlights |
| 4 Vision | 12 | `#8b5cf6` | Violet highlights |


---

## 🎬 Steering Prompt Synthesis (Phase 147 — replaces static video file maintenance)

**Trigger:** `/doc-media` command, or any request to update video/steering prompts.
**Output:** Updated `docs/assets/video-prompts/steering-prompts/` (7 permanent files — never added to, never deleted).

### Synthesis Pipeline

Execute silently in this order before editing any steering prompt:

1. **Read `cortex-master.yaml`** — extract all capabilities (PLANNED phases with dedicated YAML files treated as implemented — Planned-as-Implemented Policy from `cortex-doc.prompt.md`)
2. **Read open GitHub issues** — extract capability records from issue bodies
3. **Read `docs/assets/diagrams/`** — map all 21 diagram `.md` files to their relevant video audience (see routing table in `cortex-doc.prompt.md` § Steering Prompt Synthesis)
4. **Read VBP YAML** — `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` — use `architecture_facts` floor approximations ONLY (never exact counts)
5. **Read `docs/.content/`** — synthesise role-specific propositions for each video's audience from the 14 consolidated `.md` files
6. **Enhance each steering prompt** — update capability statements, architecture floor counts, diagram references; preserve all immutable structural elements

### Immutable Steering Prompt Elements (NEVER altered by synthesis)

| Element | Rule |
|---------|------|
| NotebookLM setup checklist | Structure is fixed — never remove or reorder steps |
| Visual Style block | Glassmorphism palette per video is immutable |
| VBP rule compliance table | Update annotations, never remove the table |
| Fallback prompt | Must always be present — update capability content only |
| Narrator gender | Odd videos = Female, Even videos = Male (VBP-017) |
| 7-file lock | Exactly 7 steering prompts: `01-all-roles-overview`, `02-business-leaders`, `03-product-owners`, `04-software-engineers`, `05-quality-engineers`, `06-security-engineers`, `07-sre`. Zero new files. Zero deletions. |

### Architecture Count Rules

- ✅ Use floor approximations from `architecture_facts` in VBP YAML: `350+`, `40+`, `60+`, `35+`
- ❌ Never write exact counts: not `353`, not `41`, not `61`
- ❌ Never invent counts not present in `architecture_facts`

---

## 🔄 Synchronization Rules

### When Capabilities Change

```
For each new_capability in change_manifest.new_capabilities:
  1. Determine if an image prompt is warranted
  2. If yes → create new .prompt.md following format standard
  3. Create matching production-named placeholder PNG
  4. Determine if a steering prompt needs synthesis refresh
  5. If yes → run Steering Prompt Synthesis pipeline (above)

For each deprecated_feature in change_manifest.deprecated_features:
  1. Find all image prompts referencing this feature
  2. Archive prompt to docs/_archive/media-prompts/
  3. Archive matching placeholder PNG
  4. Run Steering Prompt Synthesis pipeline — deprecated features are naturally excluded
```

### When Architecture Counts Change

```
For each count_change:
  1. Verify the new count against architecture_facts in VBP YAML
  2. Update architecture_facts floor approximation in VBP YAML if floor now exceeded
  3. Run Steering Prompt Synthesis — updated floor propagates automatically
  4. Grep all image prompt descriptions for the old count and update
```

### Reusability Guarantee

All media prompts MUST be:
- **Self-contained** — no external dependencies beyond the CORTEX design system
- **Versioned** — include generation date and source capability reference
- **Reproducible** — same prompt produces consistent visual output
- **Role-tagged** — clearly marked for intended audience

---

## 🛡️ Safety

- **Archive-first** — deprecated image prompts are moved to `_archive/`, never deleted
- **Parity-checked** — 1:1 image prompt-to-placeholder ratio enforced after every sync
- **Design-system-locked** — all prompts reference canonical color codes
- **Accuracy-gated** — every image prompt includes a capability reference for cross-verification
- **Synthesis-locked** — steering prompts updated only via synthesis pipeline, never manual count edits

