# DALL-E Image Generation Checklist

**Purpose:** Quick reference for generating all story images  
**Total Images:** 25 (15 comic + 10 technical)  
**Estimated Time:** 4.5-5.5 hours  
**Last Updated:** December 10, 2025

---

## 📋 Generation Checklist

### Phase 1: Foundation Images (30 minutes)

- [ ] `00-character-sheet.png` (⚠️ GENERATE THIS FIRST - all others depend on it)
- [ ] `00-basement-laboratory.png`
- [ ] `00-coffee-timeline.png`

**Location:** `docs/story/illustrations/prompts/`  
**Save to:** `docs/story/illustrations/images/`

### Phase 2: Story Images - Prologue & Chapters 1-10 (2 hours)

- [ ] `prologue-deadline.png`
- [ ] `ch1-goldfish-theory.png`
- [ ] `ch2-skull-moment.png`
- [ ] `ch3-backup-chaos.png`
- [ ] `ch4-agent-chaos.png`
- [ ] `ch5-graph-overload.png`
- [ ] `ch6-token-mountain.png`
- [ ] `ch7-capture-moment.png`
- [ ] `ch8-platform-chaos.png`
- [ ] `ch9-brute-force.png`
- [ ] `ch10-personality-emergence.png`

**Location:** `docs/story/illustrations/prompts/`  
**Save to:** `docs/story/illustrations/images/`

### Phase 3: Story Images - Chapter 11 & Epilogue (20 minutes)

- [ ] `ch11-the-revolution.png` (CORTEX 3.0 completion triumph)
- [ ] `epilogue-six-months-later.png` (six months after launch)

**Location:** `docs/story/illustrations/prompts/`  
**Save to:** `docs/story/illustrations/images/`

### Phase 4: Technical Diagrams (1.5-2 hours)

- [ ] `01-four-tier-architecture.png`
- [ ] `02-skull-protection.png`
- [ ] `03-agent-system.png`
- [ ] `04-response-templates.png`
- [ ] `05-orchestrator-ecosystem.png`
- [ ] `06-working-memory.png`
- [ ] `07-knowledge-graph.png`
- [ ] `08-development-context.png`
- [ ] `09-protection-layers.png`
- [ ] `10-complete-system.png`

**Location:** `cortex-brain/documents/analysis/dalle-prompts/cortex-brain/prompts/`  
**Save to:** `docs/story/technical-diagrams/`

### Phase 5: Optimization (30 minutes)

- [ ] Install sharp-cli: `npm install -g sharp-cli`
- [ ] Run optimization script (see below)
- [ ] Verify all images < target size (100KB comic, 150KB technical)
- [ ] Test image loading in story page

---

## 🚀 Quick Generation Script

```bash
#!/bin/bash
# generate-story-images.sh

echo "📸 DALL-E Image Generation Helper"
echo "=================================="
echo ""
echo "Phase 1: Foundation Images (START HERE)"
echo "---------------------------------------"
echo "1. docs/story/illustrations/prompts/00-character-sheet.md ⚠️ DO THIS FIRST"
echo "2. docs/story/illustrations/prompts/00-basement-laboratory.md"
echo "3. docs/story/illustrations/prompts/00-coffee-timeline.md"
echo ""
echo "Phase 2: Story Images - Prologue & Ch1-10"
echo "-----------------------------------------"
for i in prologue ch{1..10}; do
    file=$(ls docs/story/illustrations/prompts/${i}*.md 2>/dev/null | head -1)
    if [ -n "$file" ]; then
        echo "$(basename "$file")"
    fi
done
echo ""
echo "Phase 3: Story Images - Ch11 & Epilogue"
echo "---------------------------------------"
echo "docs/story/illustrations/prompts/ch11-the-revolution.md"
echo "docs/story/illustrations/prompts/epilogue-six-months-later.md"
echo ""
echo "Phase 4: Technical Diagrams"
echo "---------------------------"
for i in {01..10}; do
    file=$(ls cortex-brain/documents/analysis/dalle-prompts/cortex-brain/prompts/${i}*.md 2>/dev/null | head -1)
    if [ -n "$file" ]; then
        echo "$(basename "$file")"
    fi
done
echo ""
echo "📝 WORKFLOW:"
echo "1. Open each .md file"
echo "2. Copy DALL-E prompt section"
echo "3. Paste into DALL-E 3 (ChatGPT Plus or API)"
echo "4. Download generated image"
echo "5. Save with matching filename (replace .md with .png)"
echo "6. Move to appropriate directory"
echo ""
echo "After all images generated, run optimization:"
echo "./optimize-story-images.sh"
```

---

## 🔧 Optimization Script

```bash
#!/bin/bash
# optimize-story-images.sh

echo "🎨 Optimizing Story Images"
echo "=========================="

# Check if sharp-cli is installed
if ! command -v sharp &> /dev/null; then
    echo "❌ sharp-cli not found. Installing..."
    npm install -g sharp-cli
fi

# Create output directories
mkdir -p docs/story/illustrations/images
mkdir -p docs/story/technical-diagrams

echo ""
echo "Optimizing Comic Illustrations (target: <100KB, 1200px width)..."
for file in docs/story/illustrations/images/*.png; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .png)
        sharp -i "$file" -o "docs/story/illustrations/images/${filename}.webp" \
              --resize 1200 --withoutEnlargement -f webp -q 85
        filesize=$(du -h "docs/story/illustrations/images/${filename}.webp" | cut -f1)
        echo "✅ ${filename}.webp (${filesize})"
    fi
done

echo ""
echo "Optimizing Technical Diagrams (target: <150KB, 1400px width)..."
for file in docs/story/technical-diagrams/*.png; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .png)
        sharp -i "$file" -o "docs/story/technical-diagrams/${filename}.webp" \
              --resize 1400 --withoutEnlargement -f webp -q 90
        filesize=$(du -h "docs/story/technical-diagrams/${filename}.webp" | cut -f1)
        echo "✅ ${filename}.webp (${filesize})"
    fi
done

echo ""
echo "🎉 Optimization complete!"
echo ""
echo "Next steps:"
echo "1. Verify all images < target size"
echo "2. Test loading in story page: open docs/story/index.html"
echo "3. Check mobile responsive behavior"
echo "4. Commit images to git"
```

---

## 📊 Progress Tracking

**Foundation Images:** 0/3 complete  
**Story Images:** 0/12 complete  
**Technical Diagrams:** 0/10 complete  
**Optimization:** Not started  
**Integration:** Not started

**Overall Progress:** 0/25 images (0%)

---

## 🎯 Generation Tips

1. **Start with character sheet** - All other comics depend on consistent character appearance
2. **Generate in order** - Foundation → Prologue → Ch1-10 → Ch11 → Epilogue → Technical
3. **Use exact prompts** - Don't modify text, prompts are optimized for consistency
4. **Check character consistency** - Compare each new comic to character sheet
5. **Save originals** - Keep PNG originals before WebP conversion
6. **Batch optimize** - Generate all images first, then optimize together
7. **Test as you go** - Verify each image loads correctly in story page

---

## ⚠️ Common Issues

**Issue:** Characters look different across images  
**Solution:** Regenerate with explicit reference to character sheet description

**Issue:** Image too large (>100KB comic, >150KB technical)  
**Solution:** Increase compression: `sharp -q 75` (lower quality number)

**Issue:** Image loads slow on mobile  
**Solution:** Verify lazy loading enabled: `loading="lazy"` attribute

**Issue:** Image doesn't appear in story  
**Solution:** Check filename matches HTML reference exactly (case-sensitive)

---

## 📁 Directory Structure

```
docs/story/
├── illustrations/
│   ├── prompts/           # 15 .md files with DALL-E prompts
│   │   ├── 00-character-sheet.md
│   │   ├── 00-basement-laboratory.md
│   │   ├── 00-coffee-timeline.md
│   │   ├── prologue-deadline.md
│   │   ├── ch1-goldfish-theory.md
│   │   ├── ... (ch2-10)
│   │   ├── ch11-the-revolution.md
│   │   └── epilogue-six-months-later.md
│   └── images/            # 15 generated images (PNG → WebP)
│       ├── 00-character-sheet.webp
│       ├── ... (all comics)
│       └── epilogue-six-months-later.webp
└── technical-diagrams/    # 10 generated images (PNG → WebP)
    ├── 01-four-tier-architecture.webp
    ├── ... (02-09)
    └── 10-complete-system.webp

cortex-brain/documents/analysis/dalle-prompts/cortex-brain/
├── prompts/               # 10 .md files with DALL-E prompts
│   ├── 01-four-tier-architecture.md
│   ├── ... (02-09)
│   └── 10-complete-system.md
└── narratives/            # Optional: narrative context for each diagram
```

---

## ✅ Completion Criteria

**Comic Illustrations:**
- [ ] All 15 images generated
- [ ] Black & white newspaper aesthetic maintained
- [ ] Characters consistent with reference sheet
- [ ] All images optimized to WebP < 100KB
- [ ] All images integrated in story HTML

**Technical Diagrams:**
- [ ] All 10 diagrams generated
- [ ] Professional presentation style maintained
- [ ] Architecture components clearly labeled
- [ ] All diagrams optimized to WebP < 150KB
- [ ] All diagrams integrated in technical callouts

**Testing:**
- [ ] Story page loads without errors
- [ ] Images lazy-load correctly
- [ ] Mobile responsive display works
- [ ] Print stylesheet hides interactive elements
- [ ] Alt text describes images accurately

---

**Ready to begin?** Start with Phase 1: `00-character-sheet.png`

**Questions?** See `README-DALLE-WORKFLOW.md` for detailed workflow guide
