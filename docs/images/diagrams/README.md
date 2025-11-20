# CORTEX Diagram Image Generation Guide

**Purpose:** Generate professional technical diagrams for CORTEX documentation using DALL-E  
**Last Updated:** 2025-11-20 17:45:12  
**Status:** Production Ready

---

## 📋 Overview

This directory contains:
- **Enhanced DALL-E prompts** (500-800 words each) in `../prompts/`
- **Placeholder markers** for pending image generation
- **Generated PNG images** (after DALL-E generation)

---

## 🎨 How to Generate Images

### Step 1: Access DALL-E

Use ChatGPT Plus (includes DALL-E 3 access):
1. Go to https://chat.openai.com/
2. Ensure you have ChatGPT Plus subscription
3. Select GPT-4 model with DALL-E capabilities

### Step 2: Use Enhanced Prompts

For each diagram:

1. **Open prompt file:** `docs/diagrams/prompts/[NN]-[name]-prompt.md`
2. **Copy DALL-E Generation Instruction** (last section of prompt)
3. **Paste into ChatGPT** with prefix: "Generate an image using DALL-E:"
4. **Review output** - regenerate if needed with adjustments
5. **Download image** (right-click → Save Image As)
6. **Save to appropriate subfolder:**
   - `architectural/` - Core architecture diagrams
   - `strategic/` - Conceptual/strategic diagrams
   - `operational/` - Workflow/process diagrams
   - `integration/` - Integration/interaction diagrams

### Step 3: Optimize Images

Before committing:

```bash
# Install optimization tools
pip install pillow

# Run optimization script (reduces file size)
python scripts/optimize_images.py docs/images/diagrams/
```

**Requirements:**
- Format: PNG with transparency
- Resolution: 1920x1080 (Full HD minimum)
- Max Size: 500KB (optimized)
- Color Space: sRGB

### Step 4: Verify Integration

```bash
# Build MkDocs to check image references
cd docs
mkdocs build

# Serve locally to preview
mkdocs serve
# Visit http://localhost:8000
```

---

## 📂 Image Mapping

| DALL-E Prompt | Output Path | Category | Status |
|---------------|-------------|----------|--------|
| 01-tier-architecture-prompt.md | architectural/tier-architecture.png | Architectural | 📝 Pending |
| 02-agent-coordination-prompt.md | strategic/agent-coordination.png | Strategic | 📝 Pending |
| 03-information-flow-prompt.md | strategic/information-flow.png | Strategic | 📝 Pending |
| 04-conversation-tracking-prompt.md | strategic/conversation-tracking.png | Strategic | 📝 Pending |
| 05-plugin-system-prompt.md | strategic/plugin-system.png | Strategic | 📝 Pending |
| 06-brain-protection-prompt.md | strategic/brain-protection.png | Strategic | 📝 Pending |
| 07-operation-pipeline-prompt.md | operational/operation-pipeline.png | Operational | 📝 Pending |
| 08-setup-orchestration-prompt.md | operational/setup-orchestration.png | Operational | 📝 Pending |
| 09-documentation-generation-prompt.md | operational/documentation-generation.png | Operational | 📝 Pending |
| 10-feature-planning-prompt.md | operational/feature-planning.png | Operational | 📝 Pending |
| 11-testing-strategy-prompt.md | integration/testing-strategy.png | Integration | 📝 Pending |
| 12-deployment-pipeline-prompt.md | operational/deployment-pipeline.png | Operational | 📝 Pending |
| 13-user-journey-prompt.md | integration/user-journey.png | Integration | 📝 Pending |
| 14-system-architecture-prompt.md | integration/system-architecture.png | Integration | 📝 Pending |

**Update status:** Change `📝 Pending` to `✅ Complete` after generating

---

## 🎯 Quality Checklist

Before finalizing each image:

- [ ] High resolution (1920x1080 minimum)
- [ ] Clear labels (readable at 100% zoom)
- [ ] Color palette matches prompt specifications
- [ ] Technical accuracy verified
- [ ] Professional aesthetic maintained
- [ ] File size optimized (<500KB)
- [ ] Alt text added in documentation
- [ ] Referenced in appropriate architecture doc

---

## 🔄 Regeneration Process

If an image needs updates:

1. **Update DALL-E prompt** with refinements
2. **Regenerate image** using updated prompt
3. **Replace old image** (keep filename same)
4. **Commit changes** with clear message
5. **Verify documentation** still renders correctly

---

## 📝 Naming Convention

- Lowercase with hyphens: `tier-architecture.png`
- Descriptive: `agent-coordination.png`
- No version numbers (use git for versioning)
- Match prompt file names (without `-prompt` suffix)

---

## 🛠️ Troubleshooting

**DALL-E won't generate:** Prompt too long  
→ Use "DALL-E Generation Instruction" section only (condensed version)

**Image quality poor:** Resolution too low  
→ Request "high resolution, 4K quality" in prompt

**Colors don't match:** DALL-E interpretation varies  
→ Specify hex codes explicitly: "Use #ff6b6b for red components"

**File size too large:** Over 500KB  
→ Run optimization script: `python scripts/optimize_images.py`

---

## 📊 Progress Tracking

Total Images: 14  
Generated: 0  
Pending: 14  
Completion: 0%

**Next Steps:**
1. Generate all 14 images using DALL-E
2. Optimize images for web
3. Update architecture documentation with image references
4. Build and preview MkDocs site
5. Commit images to repository

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Generated:** 2025-11-20 17:45:12
