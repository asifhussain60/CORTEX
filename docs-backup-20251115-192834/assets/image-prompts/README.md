# CORTEX Image Prompts for Gemini

**Purpose:** Professional image generation prompts for CORTEX technical documentation  
**Target:** Gemini Image Generator  
**Created:** 2025-11-12  
**Author:** Asif Hussain

---

## Available Image Prompts

### 1. Token Optimization Flow Diagram
**File:** `token-optimization-diagram-prompt.md`  
**Name:** Token Optimization Flow with Real Results  
**Purpose:** Visualize CORTEX's 97.2% token reduction achievement

**Key Metrics Shown:**
- Before: 74,047 tokens → After: 2,078 tokens
- Cost: $2.22/request → $0.06/request
- Performance: 2.3s → 80ms load time
- Annual savings: $25,920/year

**Use Cases:**
- Technical presentations
- Architecture documentation
- Cost-benefit analysis
- Performance case studies
- Stakeholder reports

**Style:** Professional technical diagram (AWS/GitLab inspired)  
**Dimensions:** 1920x1080 (16:9)  
**Format:** High contrast, print-ready (300 DPI)

---

## How to Use These Prompts

### Step 1: Choose Your Prompt
Browse the available prompt files in this directory and select the diagram you need.

### Step 2: Copy the Prompt Section
Open the prompt file and copy the section titled "Image Prompt for Gemini" (everything under that heading).

### Step 3: Generate in Gemini
1. Open Gemini image generation interface
2. Paste the full prompt
3. Specify style: "technical diagram" or "architecture diagram"
4. Request "professional" and "high contrast"
5. Set resolution: 1920x1080 for presentations
6. Generate image

### Step 4: Save and Reference
- Save generated image with the suggested filename
- Place in `docs/assets/images/`
- Use in documentation via relative path

---

## Prompt Structure

Each prompt file includes:

1. **Image Prompt for Gemini**: Detailed technical specifications
   - Layout and sections
   - Color palette (hex codes)
   - Typography specifications
   - Visual elements and icons
   - Dimensions and resolution

2. **Human-Readable Description**: What the diagram shows
   - Problem statement
   - Solution explanation
   - Results and impact
   - Key takeaways

3. **Technical Implementation Notes**: Context for accuracy
   - Data sources
   - Real vs conceptual metrics
   - Implementation details

4. **Usage Instructions**: How to generate and use
   - Generation steps
   - File naming conventions
   - Documentation references
   - Presentation tips

---

## Quality Standards

All CORTEX image prompts follow these standards:

**Visual Quality:**
- ✅ High contrast (WCAG AAA compliant)
- ✅ Print-ready resolution (300 DPI)
- ✅ Professional color palette
- ✅ Consistent typography
- ✅ Accessible design

**Content Quality:**
- ✅ Real measured data (not estimates)
- ✅ Accurate technical details
- ✅ Source documentation referenced
- ✅ Clear visual hierarchy
- ✅ Appropriate for audience

**Usability:**
- ✅ Multiple use cases identified
- ✅ Clear generation instructions
- ✅ Suggested file naming
- ✅ Documentation integration
- ✅ Presentation-ready format

---

## Contributing New Prompts

When creating new image prompts:

1. **Follow the Template**: Use existing prompts as examples
2. **Include All Sections**: Prompt, description, notes, instructions
3. **Use Real Data**: Reference actual metrics from CORTEX
4. **Specify Completely**: Color palette, typography, dimensions
5. **Test Generation**: Verify the prompt produces expected results
6. **Document Sources**: Link to data sources in CORTEX codebase

---

## Prompt Catalog (Planned)

### Current (✅ Complete)
- Token Optimization Flow Diagram

### Planned (📋 Future)
- CORTEX Brain Architecture (4-tier system)
- Agent Coordination Flow (10 specialists + corpus callosum)
- Conversation Memory System (Tier 1 working memory)
- Knowledge Graph Structure (Tier 2 patterns)
- Development Context Dashboard (Tier 3 metrics)
- Plugin System Architecture (extensibility model)
- SKULL Protection Layer (validation workflow)
- Cost Savings Timeline (monthly/annual projections)
- Performance Benchmarks (before/after comparisons)
- User Journey Map (developer workflow)

---

## File Naming Convention

**Prompt Files:**
```
[diagram-name]-prompt.md
```

**Generated Images:**
```
[diagram-name].png
```

**Examples:**
- `token-optimization-diagram-prompt.md` → `token-optimization-flow.png`
- `brain-architecture-prompt.md` → `brain-architecture.png`
- `agent-coordination-prompt.md` → `agent-coordination-flow.png`

---

## Directory Structure

```
docs/assets/
├── image-prompts/          # This directory
│   ├── README.md           # This file
│   ├── token-optimization-diagram-prompt.md
│   └── [future-prompts].md
│
└── images/                 # Generated images go here
    ├── token-optimization-flow.png
    └── [future-images].png
```

---

## License & Copyright

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Part of CORTEX documentation  
**Usage:** Internal CORTEX documentation and presentations only

---

## Support

For questions about:
- **Prompt creation**: Review existing prompts as templates
- **Image generation**: Follow "How to Use" instructions above
- **Technical accuracy**: Reference source files in `cortex-brain/`
- **Visual design**: Follow quality standards section

---

*Last Updated: 2025-11-12*  
*Version: 1.0*
