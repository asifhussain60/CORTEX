# Media Prompt Agent

**Agent ID:** `media-prompt-agent`  
**Updated:** 2026-03-02  
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
| **Existing image prompts** | `cortex-docs/assets/image-prompts/` | ✅ |
| **Existing video prompts** | `cortex-docs/assets/video-prompts/` | ✅ |
| **Design tokens** | Glassmorphism color palette | ✅ |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Updated image prompts | `cortex-docs/assets/image-prompts/**/*.prompt.md` | DALL-E prompts reflecting current system |
| Updated video prompts | `cortex-docs/assets/video-prompts/*.md` | Video narration scripts reflecting current capabilities |
| New prompts | Same paths | For newly added capabilities |
| Archived prompts | `cortex-docs/_archive/media-prompts/` | For deprecated capabilities |

---

## 🖼️ Image Prompt Standards

### DALL-E Prompt File Format

Every `.prompt.md` file MUST follow this structure:

```markdown
# CORTEX Image Prompt: {Title}
# Role: {Business Leader | Product Owner | Software Engineer | Learner | Shared}
# Output: cortex-docs/assets/images/generated/{role}/{filename}.png
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

## 🎬 Video Prompt Standards

### Video Prompt Structure

The video prompts directory (`cortex-docs/assets/video-prompts/`) contains two tiers:

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
  2. Archive prompt to cortex-docs/_archive/media-prompts/
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
