---
scope: non-production-admin
---
# Media Prompt Agent

**Agent ID:** `media-prompt-agent`  
**Updated:** 2026-03-08  
**Layer:** docs  
**Status:** active  
**Responsibility:** Maintain DALL-E image prompts and video script prompts in production-ready state  
**Inputs:** Drift report, live file system, capability inventory  
**Outputs:** Updated `.prompt.md` files, updated video script `.md` files

---

## 🎯 Single Responsibility

Ensure all visual media prompts (DALL-E image prompts and video narration scripts) accurately describe current CORTEX capabilities, follow the glassmorphism design system, and remain production-ready and reusable.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Drift report** | `drift-detection-agent` output | ✅ |
| **Capability inventory** | Live orchestrator/tool/rule counts | ✅ |
| **Existing image prompts** | `docs/assets/image-prompts/` | ✅ |
| **Existing video prompts** | `docs/assets/video-prompts/` | ✅ |
| **Design tokens** | Glassmorphism color palette | ✅ |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Updated image prompts | `docs/assets/image-prompts/**/*.prompt.md` | DALL-E prompts reflecting current system |
| Updated video prompts | `docs/assets/video-prompts/*.md` | Video narration scripts reflecting current capabilities |
| New prompts | Same paths | For newly added capabilities |
| Archived prompts | `docs/_archive/media-prompts/` | For deprecated capabilities |

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

| Role | DALL-E Images | D3.js/Mermaid |
|------|--------------|---------------|
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

## 🎬 Video Prompt Standards

### Video Prompt Structure

The video prompts directory (`docs/assets/video-prompts/`) contains two tiers:

| Tier | Path | Purpose |
|------|------|---------|
| **Feature Series** | `video-prompts/*.md` (9 episodes) | Deep-dive into CORTEX capabilities |
| **Tutorial Series** | `video-prompts/videos/tutorials/*.md` (7 tutorials) | Hands-on getting started guides |

### Feature Episode Format

```markdown
# Episode {NN}: {Title}
**Duration:** {estimated minutes}
**Audience:** {primary role}
**Prerequisites:** {previous episodes or knowledge}

## Narration Script

### Scene 1: {Scene Title}
**Visual:** {Description of what appears on screen}
**Narration:** "{Spoken narration text}"
**Demo:** {VS Code actions to demonstrate}

### Scene 2: {Scene Title}
...

## Capability References
- {Link to .content/ file documenting this capability}
- {Link to relevant MCP tool or orchestrator}

## Accuracy Checklist
- [ ] All demonstrated features exist in current implementation
- [ ] All counts and metrics match live system
- [ ] All command outputs match actual behavior
- [ ] No references to deprecated paths or dissolved packages
```

### Tutorial Format

```markdown
# Tutorial {NN}: {Title}
**Duration:** {estimated minutes}
**Skill Level:** {Beginner | Intermediate | Advanced}
**Prerequisites:** {previous tutorials}

## Learning Objectives
1. {Objective 1}
2. {Objective 2}
3. {Objective 3}

## Steps
### Step 1: {Action}
**Screen:** {What user sees}
**Action:** {What user does}
**Result:** {Expected outcome}

...

## Accuracy Checklist
- [ ] All steps produce the described result on current CORTEX version
- [ ] All paths and commands are valid
- [ ] No deprecated workflows demonstrated
```

---

## 🔄 Synchronization Rules

### When Capabilities Change

```
For each new_capability in change_manifest.new_capabilities:
  1. Determine if an image prompt is warranted
  2. If yes → create new .prompt.md following format standard
  3. Create matching production-named placeholder PNG
  4. Determine if a video prompt needs updating
  5. If yes → update relevant episode narration script

For each deprecated_feature in change_manifest.deprecated_features:
  1. Find all image prompts referencing this feature
  2. Archive prompt to docs/_archive/media-prompts/
  3. Archive matching placeholder PNG
  4. Find all video prompts referencing this feature
  5. Flag for narration script update (do not auto-delete video prompts)
```

### When Counts Change

```
For each count_change:
  1. Grep all video prompts for the old count
  2. Update to new count
  3. Grep all image prompt descriptions for the old count
  4. Update to new count
```

### Reusability Guarantee

All media prompts MUST be:
- **Self-contained** — no external dependencies beyond the CORTEX design system
- **Versioned** — include generation date and source capability reference
- **Reproducible** — same prompt produces consistent visual output
- **Role-tagged** — clearly marked for intended audience

---

## 🛡️ Safety

- **Archive-first** — deprecated prompts are moved to `_archive/`, never deleted
- **Parity-checked** — 1:1 prompt-to-placeholder ratio enforced after every sync
- **Design-system-locked** — all prompts reference canonical color codes
- **Accuracy-gated** — every prompt includes a capability reference for cross-verification
