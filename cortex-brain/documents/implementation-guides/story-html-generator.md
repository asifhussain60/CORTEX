# Story HTML Generator - Implementation Guide

**Purpose:** Automated generation of story/index.html from THE-AWAKENING-OF-CORTEX-MASTER.md using template-based orchestration.

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION

---

## Overview

The Story HTML Generator is an orchestrator-level tool that converts the master narrative markdown into a visually enhanced HTML story page. It maintains clean separation between structure (template) and content (markdown), enabling easy regeneration and future story additions.

## Architecture

```
Template System Architecture:
┌─────────────────────────────────────────────┐
│  THE-AWAKENING-OF-CORTEX-MASTER.md         │
│  (Source: cortex-brain/documents/narratives)│
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│  generate_story_html.py                     │
│  - Parse chapters (# Chapter X:)            │
│  - Smart content detection                  │
│  - Apply visual styling classes             │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│  story-template.html                        │
│  - Navigation, TOC, Hero                    │
│  - {{STORY_CHAPTERS}} placeholder           │
│  - Styles, Scripts, Footer                  │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│  story/index.html (GENERATED)               │
│  - Complete HTML with 12 chapters           │
│  - Enhanced visual styling                  │
│  - 175KB final output                       │
└─────────────────────────────────────────────┘
```

## Usage

### Basic Generation

```bash
python3 scripts/generate_story_html.py
```

### Dry Run (Test Without Writing)

```bash
python3 scripts/generate_story_html.py --dry-run
```

### Verbose Output

```bash
python3 scripts/generate_story_html.py --verbose
```

## Visual Styling Features

The generator applies smart content detection to automatically style different narrative elements:

### Content Type Detection

| Content Type | Detection Pattern | CSS Class | Visual Effect |
|--------------|-------------------|-----------|---------------|
| **G's Voice** | Italic + quotes | `.miss-g-voice` | Purple glow, ethereal |
| **Dialogue** | Starts with `"` | `.story-dialogue` | Cyan tint, italic |
| **Technical Terms** | In backticks | `.tech-term` | Monospace, green |
| **Coffee Refs** | Contains "coffee"/"mug" | `.coffee-ref` | Brown tones |
| **Dramatic Moments** | Short impactful sentences | `.dramatic` | Large, centered, bold |
| **Whiteboard Notes** | Code-like blocks | `.whiteboard-note` | Dashed border, code font |
| **Git Commits** | Contains git keywords | `.git-commit` | Terminal style |
| **Tier Labels** | "Tier 0/1/2/3" | `.tier-label` | Gradient background |
| **Metrics** | Numbers + units | `.metric-number` | Glow effect |
| **Timestamps** | Time with AM/PM | `.timestamp` | Subtle gray |

### Typography Enhancements

- **Font Sizes:** 1.05rem - 1.4rem (varied for emphasis)
- **Colors:** Cyan (#00d4ff), Purple (#c864ff), Green (#00ff88), Brown (#d4a574)
- **Effects:** Text shadows, glows, gradients, animations
- **Spacing:** Increased line-height (1.7-1.8) for readability

## File Structure

```
docs/story/
├── story-template.html    # Structure only (158 lines)
├── index.html            # Generated output (12 chapters, 175KB)
└── illustrations/
    └── images/           # 16 WebP + 16 PNG illustrations

scripts/
└── generate_story_html.py # Orchestrator (487 lines)

docs/assets/css/
└── story.css             # +229 lines story-specific styles
```

## Chapter Mapping

| Chapter | Source Heading | Word Count | Status |
|---------|---------------|------------|--------|
| Prologue | `## Prologue: The Basement Laboratory` | 1,270 | ✅ |
| Chapter 1 | `# Chapter 1: The Amnesia Crisis` | 1,351 | ✅ |
| Chapter 2 | `# Chapter 2: Tier 0 - The Gatekeeper Incident` | 1,988 | ✅ |
| Chapter 3 | `# Chapter 3: Tier 1 - The SQLite Intervention` | 1,402 | ✅ |
| Chapter 4 | `# Chapter 4: The Agent Uprising` | 1,167 | ✅ |
| Chapter 5 | `# Chapter 5: The Knowledge Graph Incident` | 1,091 | ✅ |
| Chapter 6 | `# Chapter 6: The Token Crisis` | 1,352 | ✅ |
| Chapter 7 | `# Chapter 7: The Conversation Capture` | 1,162 | ✅ |
| Chapter 8 | `# Chapter 8: The Cross-Platform Nightmare` | 1,007 | ✅ |
| Chapter 9 | `# Chapter 9: The Performance Awakening` | 1,059 | ✅ |
| Chapter 10 | `# Chapter 10: The Awakening` | 1,231 | ✅ |
| Chapter 11 | `# Chapter 11: The 3.0 Revolution` | 3,171 | ✅ |
| Epilogue | `## Epilogue: Six Months Later` | N/A | ⏳ Pending |

**Total:** 12 chapters, ~16,000 words

## Regeneration Workflow

### When to Regenerate

- Master markdown updated with new content
- Visual styling needs adjustment
- Template structure changes
- Image references updated

### Steps

1. **Update Source:** Edit `cortex-brain/documents/narratives/THE-AWAKENING-OF-CORTEX-MASTER.md`
2. **Test Changes:** `python3 scripts/generate_story_html.py --dry-run --verbose`
3. **Generate:** `python3 scripts/generate_story_html.py`
4. **Verify:** Open `http://localhost:8080/story/index.html`
5. **Commit:** Git commit generated index.html

### Quality Checks

- [ ] All chapters render correctly
- [ ] TOC navigation works (13 links)
- [ ] Images load (16 WebP + 16 PNG)
- [ ] Visual styling applies correctly
- [ ] Sidebar doesn't overlay content (z-index: 20 > 10)
- [ ] Reading progress bar functions
- [ ] Coffee mug counter displays
- [ ] Responsive design works (mobile/tablet)

## Technical Details

### Parser Logic

```python
# Chapter detection
- H1 headings: `# Chapter X:` → chapter{X}
- H2 prologue: `## Prologue:` → prologue
- H2 epilogue: `## Epilogue:` → epilogue

# Content processing
- Split by `\n\n` (paragraph breaks)
- Apply regex patterns for content type
- Inject CSS classes dynamically
- Preserve markdown formatting (bold, italic)
```

### Template Injection

```html
<!-- Template placeholder -->
<main class="story-content">
    {{STORY_CHAPTERS}}
</main>

<!-- Gets replaced with -->
<main class="story-content">
    <article id="prologue" class="story-chapter">...</article>
    <article id="chapter1" class="story-chapter">...</article>
    ...
</main>
```

### Z-Index Protection

```css
.story-toc {
    z-index: 10;  /* Sidebar */
}

.story-content {
    z-index: 20;  /* Content sits above */
    position: relative;
    background: var(--bg-primary);
}
```

## Future Enhancements

### Planned Features

- [ ] Epilogue chapter integration
- [ ] PDF export capability
- [ ] ePub generation for e-readers
- [ ] Multi-language support
- [ ] Interactive timeline view
- [ ] Character glossary generation
- [ ] Chapter-specific music/audio
- [ ] Dark mode enhancements

### Template Reusability

The template system supports multiple stories:

```bash
# Future: Additional stories
python3 scripts/generate_story_html.py --story "cortex-2.0-legacy"
python3 scripts/generate_story_html.py --story "copilot-diaries"
```

## Troubleshooting

### Common Issues

**Problem:** Chapters not appearing
- **Solution:** Check `# Chapter X:` format in markdown (H1, not H2)

**Problem:** Styling not applied
- **Solution:** Clear browser cache, check story.css loaded

**Problem:** Sidebar covers content
- **Solution:** Verify `.story-content` has `z-index: 20`

**Problem:** Images missing
- **Solution:** Check `docs/story/illustrations/images/` directory

**Problem:** Template placeholder visible
- **Solution:** Ensure `{{STORY_CHAPTERS}}` replaced in output

## Integration with CORTEX Operations

This generator should be added to `cortex-operations.yaml`:

```yaml
regenerate_story_docs:
  name: "Regenerate Story Documentation"
  category: "documentation"
  execution_method: "cli_wrapper"
  description: "Generate story/index.html from THE-AWAKENING-OF-CORTEX-MASTER.md"
  cli_script: "scripts/generate_story_html.py"
  admin_only: true
  manifest: "cortex-brain/orchestrator-manifests/story-generator-manifest.yaml"
```

---

**Last Updated:** December 10, 2025
**Generator Version:** 1.0.0
**Output Size:** 175KB (12 chapters)
**Generation Time:** <2 seconds
