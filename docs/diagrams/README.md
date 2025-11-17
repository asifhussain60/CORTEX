# CORTEX Diagram Generation Workflow

**Generated:** November 17, 2025, 08:24 AM

## Directory Structure

```
docs/diagrams/
├── prompts/           # AI generation prompts (INPUT)
│   ├── 01-tier-architecture.md
│   ├── 02-agent-system.md
│   ├── 03-plugin-architecture.md
│   ├── 04-memory-flow.md
│   ├── 05-agent-coordination.md
│   ├── 06-basement-scene.md
│   └── 07-cortex-one-pager.md
├── narratives/        # Human-readable explanations (CONTEXT)
│   ├── 01-tier-architecture.md
│   ├── 02-agent-system.md
│   └── ... (matching prompts)
├── generated/         # AI-generated images (OUTPUT)
│   ├── 01-tier-architecture-v1.png
│   ├── 02-agent-system-v1.png
│   └── ... (versions tracked)
└── README.md         # This file
```

## Workflow

### Step 1: Generate Prompts (AUTOMATED)
```bash
# Run EPM documentation generator
python scripts/generate_docs.py --profile comprehensive
# Image prompts generated automatically
```

### Step 2: Create Images (MANUAL - Use AI)

For each prompt file in `prompts/`:

1. **Open prompt file** (e.g., `prompts/01-tier-architecture.md`)
2. **Copy prompt content** (everything after "AI Generation Instructions")
3. **Paste into Gemini/ChatGPT:**
   - Gemini: https://gemini.google.com
   - ChatGPT: https://chat.openai.com (with DALL-E)
4. **Download generated image**
5. **Save to `generated/` directory:**
   - Naming: `##-diagram-name-v1.png`
   - Version tracking: v1, v2, v3 (for iterations)
6. **Repeat if quality issues:**
   - Tweak prompt if needed
   - Save as new version (v2)

### Step 3: Merge Images (AUTOMATED - GitHub Copilot)

```bash
# After images are in generated/ directory
# GitHub Copilot can automatically embed them in docs

# Example: In markdown file, reference:
![Tier Architecture](diagrams/generated/01-tier-architecture-v1.png)

# Copilot will:
# 1. Detect image path
# 2. Verify file exists
# 3. Insert proper markdown syntax
# 4. Suggest alt text from narrative
```

### Step 4: Review & Iterate

1. **Check image quality:**
   - Resolution (300 DPI minimum)
   - Color accuracy (use color picker)
   - Text legibility
   - Icon clarity

2. **Review narratives:**
   - Match image content
   - Technical accuracy
   - Clarity for audience

3. **Iterate if needed:**
   - Update prompt in `prompts/` directory
   - Regenerate image
   - Save as new version

## Diagram Specifications

| Diagram | ID | Aspect Ratio | Size | Priority |
|---------|----|--------------|----- |----------|
| Tier Architecture | 01 | 16:9 (landscape) | 3840x2160 | Critical |
| Agent System | 02 | 1:1 (square) | 2160x2160 | Critical |
| Plugin Architecture | 03 | 1:1 (square) | 2160x2160 | High |
| Memory Flow | 04 | 16:9 (landscape) | 3840x2160 | High |
| Agent Coordination | 05 | 9:16 (portrait) | 1620x2880 | Medium |
| Basement Scene | 06 | 16:9 (landscape) | 3840x2160 | Optional |
| CORTEX One-Pager | 07 | 16:9 (landscape) | 3840x2160 | Critical |

## Color Palette (Consistent Branding)

```yaml
Tier 0 (Instinct):    #6B46C1  (Deep Purple)
Tier 1 (Memory):      #3B82F6  (Bright Blue)
Tier 2 (Knowledge):   #10B981  (Emerald Green)
Tier 3 (Context):     #F59E0B  (Warm Orange)
LEFT Brain:           #3B82F6  (Cool Blue)
RIGHT Brain:          #F59E0B  (Warm Orange)
Connections:          #6B7280  (Gray)
```

## Quality Checklist

Before finalizing each diagram:

- [ ] Resolution: 300 DPI minimum
- [ ] Colors match palette (use color picker)
- [ ] Text is legible at 50% zoom
- [ ] Icons are distinct and recognizable
- [ ] Layout follows prompt specifications
- [ ] Aspect ratio correct
- [ ] File size reasonable (<5MB per PNG)
- [ ] Narrative matches image content
- [ ] Technical accuracy verified
- [ ] Appropriate for target audience

## Troubleshooting

**Issue: AI-generated image doesn't match prompt**
- Solution: Refine prompt with more specific instructions
- Try different AI (Gemini vs ChatGPT)
- Iterate 2-3 times for best results

**Issue: Colors don't match palette**
- Solution: Specify exact hex codes in prompt
- Use "Color: #RRGGBB" format explicitly
- May need post-processing in image editor

**Issue: Text unreadable**
- Solution: Request larger font sizes
- Increase canvas size (e.g., 4K → 8K)
- Simplify diagram (fewer elements)

**Issue: Layout wrong (portrait vs landscape)**
- Solution: Explicitly state aspect ratio in prompt
- Use canvas size examples (3840x2160 = 16:9)
- Specify orientation ("landscape" or "portrait")

## Next Steps

1. ✅ Prompts generated (automated by EPM)
2. ⏳ Create images using AI (manual, ~30 min per diagram)
3. ⏳ Save to `generated/` directory
4. ⏳ Review quality against checklist
5. ⏳ Iterate if needed (v2, v3)
6. ⏳ Embed in documentation (Copilot-assisted)
7. ⏳ Publish to MkDocs site

**Estimated Total Time:** 4-5 hours for all 7 diagrams

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Last Updated:** November 17, 2025
