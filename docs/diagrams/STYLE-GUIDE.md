# CORTEX Visual Style Guide

**Version:** 1.0  
**Generated:** November 17, 2025

## Color Palette

### Primary Colors (Tiers)

| Tier | Color Name | Hex Code | RGB | Usage |
|------|-----------|----------|-----|-------|
| Tier 0 | Deep Purple | `#6B46C1` | rgb(107, 70, 193) | Instinct/Governance |
| Tier 1 | Bright Blue | `#3B82F6` | rgb(59, 130, 246) | Working Memory |
| Tier 2 | Emerald Green | `#10B981` | rgb(16, 185, 129) | Knowledge Graph |
| Tier 3 | Warm Orange | `#F59E0B` | rgb(245, 158, 11) | Context Intelligence |

### Secondary Colors (Agents)

| Element | Color Name | Hex Code | Usage |
|---------|-----------|----------|-------|
| LEFT Brain | Cool Blue | `#3B82F6` | Execution agents |
| RIGHT Brain | Warm Orange | `#F59E0B` | Strategy agents |
| Connections | Gray | `#6B7280` | Arrows, links |
| Background | White/Light Gray | `#FFFFFF` / `#F9FAFB` | Canvas |

## Typography

### Font Families

**Primary Font:** Inter, system-ui, sans-serif
**Monospace Font:** 'Courier New', Consolas, monospace

### Font Sizes

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Diagram Titles | 24pt | Bold | Main diagram heading |
| Section Headers | 18pt | Bold | Tier names, agent groups |
| Body Text | 14pt | Regular | Labels, descriptions |
| Small Text | 11pt | Regular | Annotations, metadata |
| Code Samples | 12pt | Regular | Monospace code |

### Text Contrast

- Dark text on light backgrounds: Minimum contrast ratio 4.5:1
- Light text on dark backgrounds: Minimum contrast ratio 7:1
- Use color picker to verify accessibility

## Layout Principles

### Spacing

- **Margin:** 40px minimum from canvas edge
- **Padding:** 20px inside boxes/containers
- **Gap:** 30px between major elements
- **Line spacing:** 1.5x for readability

### Alignment

- **Left-align:** Text within boxes
- **Center-align:** Diagram titles
- **Consistent:** Grid-based alignment for elements

### Visual Hierarchy

1. **Primary:** Main diagram elements (tiers, agents)
2. **Secondary:** Connecting arrows, relationships
3. **Tertiary:** Labels, annotations
4. **Quaternary:** Metadata, timestamps

## Iconography

### Standard Icons

| Concept | Icon | Unicode | Usage |
|---------|------|---------|-------|
| Database | 🗄️ | U+1F5C4 | Tier 1 storage |
| Network | 🔗 | U+1F517 | Tier 2 relationships |
| Analytics | 📊 | U+1F4CA | Tier 3 metrics |
| Shield | 🛡️ | U+1F6E1 | Tier 0 protection |
| Code | 💻 | U+1F4BB | Code Executor |
| Test | ✅ | U+2705 | Test Generator |
| Wrench | 🔧 | U+1F527 | Error Corrector |
| Heart | ❤️ | U+2764 | Health Validator |
| Git | 🌿 | U+1F33F | Commit Handler |

### Icon Guidelines

- **Size:** 32x32px minimum
- **Style:** Outlined or flat (consistent within diagram)
- **Color:** Match element color or neutral gray
- **Placement:** Top-left or center of container

## Diagram Types

### 1. Architecture Diagrams (Vertical Stacks)

**Best for:** Tier architecture, layered systems

**Layout:**
- Vertical orientation (bottom to top)
- Boxes with rounded corners (8px radius)
- Upward arrows showing data flow
- Legend in bottom-right corner

**Aspect Ratio:** 16:9 (landscape)

### 2. Agent System Diagrams (Dual Hemispheres)

**Best for:** LEFT/RIGHT brain agents, coordination

**Layout:**
- Split canvas vertically (LEFT | RIGHT)
- Color-coded hemispheres
- Central bridge (Corpus Callosum)
- Agents in vertical lists

**Aspect Ratio:** 1:1 (square)

### 3. Flow Diagrams (Left-to-Right)

**Best for:** Process flows, transformations

**Layout:**
- Horizontal orientation (left to right)
- Stages as boxes
- Arrows showing progression
- Example data at each stage

**Aspect Ratio:** 16:9 (landscape)

### 4. Sequence Diagrams (Top-to-Bottom)

**Best for:** Multi-agent workflows, time sequences

**Layout:**
- Vertical swimlanes
- Time flows downward
- Messages as horizontal arrows
- Step numbers in circles

**Aspect Ratio:** 9:16 (portrait)

## Technical Specifications

### Resolution

- **Minimum:** 300 DPI for print quality
- **Recommended:** 3840x2160 (4K) for 16:9
- **Web:** 1920x1080 acceptable for online use

### File Formats

- **Primary:** PNG (lossless, transparency support)
- **Alternative:** SVG (vector, scalable)
- **Avoid:** JPEG (lossy compression)

### File Naming

Pattern: `##-diagram-name-vN.ext`

Examples:
- `01-tier-architecture-v1.png`
- `02-agent-system-v2.svg`
- `05-agent-coordination-v1.png`

### Version Control

- **v1:** Initial version
- **v2:** First revision
- **v3+:** Subsequent iterations
- Keep all versions (storage is cheap)

## Accessibility

### Color Blindness

- Don't rely solely on color to convey information
- Use patterns, textures, or icons as backups
- Test with color blindness simulators

### Screen Readers

- Provide alt text for all images
- Use descriptive filenames
- Include text transcripts in narratives

### Zoom/Magnification

- Text legible at 200% zoom
- Icons recognizable at 150% zoom
- Layout doesn't break at high zoom levels

## Examples

### Good Practices ✅

- Clear visual hierarchy
- Consistent color usage
- Readable text (legible at 50% zoom)
- Proper spacing (not cramped)
- Aligned to grid
- Appropriate aspect ratio

### Bad Practices ❌

- Inconsistent colors (random palette)
- Tiny unreadable text
- Cluttered layout (too many elements)
- Poor contrast (gray on white)
- Misaligned elements
- Wrong aspect ratio (stretched)

## Quality Checklist

Before finalizing any diagram:

- [ ] Colors match style guide palette
- [ ] Text is readable at 50% zoom
- [ ] Icons are distinct (32x32px minimum)
- [ ] Spacing is consistent (20-40px)
- [ ] Alignment follows grid
- [ ] Aspect ratio correct
- [ ] Resolution 300 DPI or higher
- [ ] File naming follows convention
- [ ] Alt text provided
- [ ] Narrative matches diagram

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Last Updated:** November 17, 2025
