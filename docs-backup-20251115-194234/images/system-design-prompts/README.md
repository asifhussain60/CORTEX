# CORTEX System Design Image Prompts

**Purpose:** ChatGPT DALL-E prompts for generating print-ready CORTEX architecture diagrams  
**Format:** Individual prompt files for each diagram  
**Target:** Professional technical documentation and presentations  
**Created:** 2025-11-13  

---

## 📊 Available Prompts

| # | Diagram | Dimensions | File |
|---|---------|------------|------|
| 01 | System Overview | 17"x11" Landscape | [01-cortex-system-overview.md](./01-cortex-system-overview.md) |
| 02 | Four-Tier Brain Architecture | 17"x11" Portrait | [02-four-tier-brain-architecture.md](./02-four-tier-brain-architecture.md) |
| 03 | Agent System (Dual Hemisphere) | 17"x11" Landscape | [03-agent-system-dual-hemisphere.md](./03-agent-system-dual-hemisphere.md) |
| 04 | Conversation Flow Sequence | 17"x11" Portrait | [04-conversation-flow-sequence.md](./04-conversation-flow-sequence.md) |
| 05 | Token Optimization Impact | 17"x11" Landscape | [05-token-optimization-impact.md](./05-token-optimization-impact.md) |
| 06 | Plugin Architecture | 17"x11" Landscape | [06-plugin-architecture.md](./06-plugin-architecture.md) |
| 07 | SKULL Protection System | 17"x11" Landscape | [07-skull-protection-system.md](./07-skull-protection-system.md) |
| 08 | Memory Integration Flow | 17"x11" Landscape | [08-memory-integration-flow.md](./08-memory-integration-flow.md) |
| 09 | Intent Routing System | 17"x11" Landscape | [09-intent-routing-system.md](./09-intent-routing-system.md) |
| 10 | Development Lifecycle | 17"x11" Landscape | [10-development-lifecycle.md](./10-development-lifecycle.md) |
| 11 | PR Intelligence Automation | 17"x11" Landscape | [11-pr-intelligence-automation.md](./11-pr-intelligence-automation.md) |
| 12 | Token Optimization Logic | 17"x11" Landscape | [12-token-optimization-logic.md](./12-token-optimization-logic.md) |

---

## 🎯 How to Use

### Step 1: Choose a Diagram
Select the diagram prompt file you want to generate.

### Step 2: Copy the Prompt
Open the markdown file and copy the entire ChatGPT prompt (the text between triple backticks).

### Step 3: Generate Image
1. Go to ChatGPT (requires GPT-4 with DALL-E access)
2. Paste the prompt
3. ChatGPT will generate the image

### Step 4: Download & Save
1. Download the generated image at highest resolution
2. Save to: `docs/images/print-ready/[filename].png`

### Step 5: Verify Quality
- Check resolution is 300 DPI minimum
- Verify text is readable when printed
- Confirm colors match specifications

---

## 📐 Print Specifications

All prompts are designed for high-quality printing:

**Resolution:**
- 300 DPI minimum (print quality)
- Some prompts specify 600 DPI for extra clarity

**Common Sizes:**
- **Letter (8.5" x 11")**: 2550 x 3300 pixels @ 300 DPI
- **Tabloid (11" x 17")**: 3300 x 5100 pixels @ 300 DPI
- **Large Tabloid (17" x 11")**: 5100 x 3300 pixels @ 300 DPI

**Formats:**
- PNG for presentations and documentation
- Consider PDF export for professional printing

---

## 🎨 Design Standards

### Color Palette (Consistent across all diagrams)

| Component | Color Name | Hex Code |
|-----------|-----------|----------|
| Tier 0 (Instinct) | Red | `#ff6b6b` |
| Tier 1 (Memory) | Teal | `#4ecdc4` |
| Tier 2 (Knowledge) | Blue | `#45b7d1` |
| Tier 3 (Context) | Green | `#96ceb4` |
| LEFT Brain | Teal | `#4ecdc4` |
| RIGHT Brain | Green | `#96ceb4` |
| Coordination | Gold | `#ffd93d` |
| Critical | Dark Red | `#d63031` |
| Success | Mint | `#55efc4` |
| Warning | Yellow | `#fdcb6e` |

### Typography

**Recommended Fonts:**
- Headings: Inter, Helvetica, Arial (Bold)
- Body: Inter, Helvetica, Arial (Regular)
- Code: Fira Code, Consolas, Monaco (Monospace)

**Sizes (when printed):**
- Titles: 18-24pt
- Subtitles: 14-18pt
- Body text: 10-12pt
- Captions: 8-10pt
- Minimum readable: 8pt

### Visual Style
- Clean, modern business aesthetic
- Rounded rectangles for components
- Subtle drop shadows for depth
- Clear directional arrows
- Sufficient white space
- Professional color schemes
- Print-ready quality

---

## 📁 Output Directory Structure

```
docs/images/
├── print-ready/              # Final generated images
│   ├── 01-system-overview.png
│   ├── 02-brain-architecture.png
│   ├── 03-agent-system.png
│   ├── 04-conversation-flow.png
│   ├── 05-token-optimization-impact.png
│   ├── 06-plugin-architecture.png
│   ├── 07-skull-protection.png
│   ├── 08-memory-integration.png
│   ├── 09-intent-routing.png
│   ├── 10-development-lifecycle.png
│   ├── 11-pr-intelligence.png
│   └── 12-token-optimization-logic.png
│
└── system-design-prompts/    # ChatGPT prompt files (this folder)
    ├── README.md
    ├── 01-cortex-system-overview.md
    ├── 02-four-tier-brain-architecture.md
    ├── 03-agent-system-dual-hemisphere.md
    ├── 04-conversation-flow-sequence.md
    ├── 05-token-optimization-impact.md
    ├── 06-plugin-architecture.md
    ├── 07-skull-protection-system.md
    ├── 08-memory-integration-flow.md
    ├── 09-intent-routing-system.md
    ├── 10-development-lifecycle.md
    ├── 11-pr-intelligence-automation.md
    └── 12-token-optimization-logic.md
```

---

## 🔄 Regeneration

To regenerate any diagram:
1. Open the corresponding prompt file
2. Copy the latest version of the prompt
3. Generate in ChatGPT
4. Replace the old image in `print-ready/`

---

## ✏️ Customization

Each prompt file includes:
- **Color specifications** - Adjust hex codes
- **Layout details** - Modify dimensions
- **Content sections** - Add/remove components
- **Visual style** - Change aesthetic preferences

To customize:
1. Edit the prompt markdown file
2. Adjust specifications as needed
3. Regenerate the image
4. Save customized prompt for future use

---

## 🎯 Use Cases

**Technical Documentation:**
- System architecture documentation
- API reference guides
- Technical white papers
- Design specification documents

**Presentations:**
- Conference talks
- Team presentations
- Investor pitches
- Training materials

**Marketing:**
- Product overview materials
- Case studies
- Blog post illustrations
- Social media graphics

**Academic:**
- Research papers
- Thesis documentation
- Academic presentations
- Educational materials

---

## 📊 Quality Checklist

Before using generated images:

- [ ] Resolution is 300 DPI minimum
- [ ] Text is readable at print size
- [ ] Colors match brand specifications
- [ ] All components are clearly labeled
- [ ] Arrows and connections are clear
- [ ] No pixelation or artifacts
- [ ] File size is reasonable (<10 MB for PNG)
- [ ] Saved in correct directory
- [ ] Filename follows naming convention

---

## 🆘 Troubleshooting

**Issue: Text too small when printed**
- Solution: Increase font size specifications in prompt
- Minimum recommended: 10pt for body text

**Issue: Colors don't match specifications**
- Solution: Explicitly specify hex codes in prompt
- Include color palette reference table

**Issue: Image resolution too low**
- Solution: Specify exact pixel dimensions (e.g., 3300x5100)
- Always include "300 DPI" in specifications

**Issue: Layout doesn't match expectations**
- Solution: Provide more detailed layout specifications
- Include ASCII diagram of desired layout in prompt

**Issue: Generated image differs from prompt**
- Solution: Regenerate with more specific constraints
- Break complex diagrams into simpler components

---

## 📝 Contributing

To add new diagram prompts:

1. Create new `.md` file with sequential number
2. Follow existing prompt structure
3. Include full specifications section
4. Add color palette table
5. Add layout diagram
6. Include usage instructions
7. Update this README index table

---

## 📚 Related Resources

- **Mermaid Diagrams:** `docs/architecture/diagrams/` - Code-based diagrams
- **Architecture Docs:** `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml`
- **Brand Guidelines:** (If created) Brand colors and typography

---

## 📄 License

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  

Images generated using these prompts are part of the CORTEX project and follow the same license terms.

---

*Created: 2025-11-13 | Print-ready architecture diagram prompts for ChatGPT DALL-E*
