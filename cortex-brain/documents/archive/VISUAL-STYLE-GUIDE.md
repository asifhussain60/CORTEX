# DALL-E Architecture Prompts - Visual Style Guide

**Created:** December 8, 2025  
**Purpose:** 10 distinct visual styles for CORTEX architecture diagrams

---

## Overview

Redesigned all 10 CORTEX architecture prompts with radically different visual metaphors to ensure each diagram looks unique and memorable.

---

## Visual Styles Used

### 1. Four-Tier Architecture → **Isometric Cutaway Technical Drawing**
- **Style:** Architectural blueprint with CAD precision
- **Colors:** Blueprint blue lines, gold accents, white background
- **Metaphor:** Transparent glass tower with each floor visible
- **Similar to:** SpaceX/Tesla technical schematics
- **Key feature:** 45-degree isometric view with dimension callouts

### 2. SKULL Protection → **Security Operations Center Dashboard**
- **Style:** Modern cybersecurity command center
- **Colors:** Dark slate, neon green success, red critical, gold borders
- **Metaphor:** SOC with multiple monitoring screens
- **Similar to:** Splunk/Datadog security dashboards
- **Key feature:** Real-time threat monitoring panels

### 3. Agent System → **Circuit Board PCB Schematic**
- **Style:** Electronics engineering diagram
- **Colors:** PCB green background, copper traces, gold pads
- **Metaphor:** 10 agent chips on motherboard
- **Similar to:** Professional electronics documentation
- **Key feature:** Circuit traces connecting components

### 4. Response Templates → **Library Card Catalog System**
- **Style:** Vintage filing system meets modern UI
- **Colors:** Warm wood tones, brass hardware, paper white
- **Metaphor:** 62-drawer card catalog with pneumatic sorting
- **Similar to:** Mid-century library with Wes Anderson symmetry
- **Key feature:** Mechanical template selector with brass tubes

### 5. Orchestrator Ecosystem → **Subway/Metro Transit Map**
- **Style:** Modern transit authority map
- **Colors:** Colored lines on white background (London Underground style)
- **Metaphor:** 20 orchestrator lines with station stops
- **Similar to:** NYC Subway / London Tube maps
- **Key feature:** Transfer stations and line frequencies

### 6. Working Memory → **Data Flow Sankey Diagram**
- **Style:** Modern information design with flowing ribbons
- **Colors:** Cyan flows, gradient transitions, white background
- **Metaphor:** FIFO queue as flowing data streams
- **Similar to:** D3.js visualizations, Edward Tufte style
- **Key feature:** Ribbon thickness = data volume

### 7. Knowledge Graph → **Force-Directed 3D Graph**
- **Style:** Scientific visualization with physics simulation
- **Colors:** Vibrant nodes by community, dark space background
- **Metaphor:** 3D network with floating nodes
- **Similar to:** Gephi/Neo4j graph browser
- **Key feature:** Community clusters with colored halos

### 8. Development Context → **Thermal Infrared Heatmap**
- **Style:** Scientific thermal imaging camera
- **Colors:** Blue cold → green → yellow → red hot gradient
- **Metaphor:** Code files shown as thermal signatures
- **Similar to:** FLIR thermal camera imagery
- **Key feature:** Temperature = commit activity intensity

### 9. Protection Layers → **Medieval Castle Cross-Section**
- **Style:** Illuminated manuscript meets technical diagram
- **Colors:** Stone gray, gold leaf, royal blue, parchment
- **Metaphor:** 8 castle walls protecting central keep
- **Similar to:** Bayeux Tapestry technical drawings
- **Key feature:** Medieval fortifications with guard towers

### 10. Complete System → **Academic Conference Poster**
- **Style:** IEEE/ACM scientific poster
- **Colors:** White background, academic blue headers, clean text
- **Metaphor:** Research presentation with diagrams and data
- **Similar to:** University conference posters
- **Key feature:** 3-column layout with abstract, diagrams, conclusions

---

## Why Different Styles Matter

**Problem:** Original prompts all used circular/concentric patterns with similar node-based layouts. Generated images looked too similar.

**Solution:** Each prompt now uses a completely different visual metaphor:
- Technical drawing vs dashboard vs circuit board
- Library system vs transit map vs data flow
- Graph network vs thermal imaging vs medieval castle
- Conference poster (comprehensive overview)

**Result:** 10 distinctly recognizable diagrams that don't look alike.

---

## Generation Instructions

### For Each Prompt:

1. Open prompt file (e.g., `01-four-tier-architecture.md`)
2. Copy text under "Copy This Prompt to ChatGPT DALL-E:" section
3. Paste into ChatGPT with DALL-E enabled
4. Generate image
5. Save as PNG: `{same-filename}.png` (e.g., `01-four-tier-architecture.png`)
6. Place in same folder as prompt file

### File Structure:
```
cortex-brain/documents/analysis/dalle-prompts/
├── cortex-brain/
│   ├── 01-four-tier-architecture.md
│   ├── 01-four-tier-architecture.png  ← Generate and save here
│   ├── 02-skull-protection.md
│   ├── 02-skull-protection.png        ← Generate and save here
│   └── ... (10 total)
└── user-features/
    ├── 01-tdd-mastery.md
    ├── 01-tdd-mastery.png             ← Generate and save here
    └── ... (9 total)
```

---

## Visual Design Principles

All prompts follow these quality standards:

1. **Enterprise Quality:** Reference professional tools (AWS, Splunk, GitHub, etc.)
2. **Precise Specifications:** Exact colors (hex codes), dimensions, layouts
3. **No Human Figures:** Pure abstract/technical visualization
4. **Clear Labeling:** All elements labeled, annotated, explained
5. **Professional Polish:** Magazine/presentation quality output
6. **1792x1024 Landscape:** Optimized for technical diagrams
7. **HD Quality:** Maximum DALL-E 3 detail setting

---

## Comparison: Before vs After

### Before (All Similar):
- ❌ Circular concentric layers
- ❌ Node-based network graphs
- ❌ Similar color palettes
- ❌ Glowing orbs and shields
- ❌ Neural connections everywhere

### After (All Unique):
- ✅ 10 completely different visual metaphors
- ✅ Each uses distinct drawing style
- ✅ Varied color palettes per context
- ✅ Unique spatial layouts
- ✅ Easily distinguishable at a glance

---

## Expected Outcomes

When all 20 images are generated (10 architecture + 10 user features):

**Architecture Set:** Will show CORTEX internals using diverse technical visualization methods
**User Features Set:** Will show capabilities using consistent enterprise dashboard style

**Together:** Create comprehensive visual documentation that's both varied (not repetitive) and cohesive (same quality level).

---

**Status:** ✅ All 10 architecture prompts redesigned with unique visual styles  
**Next:** Generate images via ChatGPT DALL-E using updated prompts
